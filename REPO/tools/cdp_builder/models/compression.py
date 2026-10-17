"""
Compression constitutive models for UHPC CDP.

IMPLEMENTED (reference):
  REF_POPOVICS  Popovics (1973) — ascending verified; post-peak linear ADOPTED.
                FAILS for Batch 2 (α=0.988 < 1; degenerate).

IMPLEMENTED (named project models):
  C1  Graybeal (FHWA) ascending + Fakeh et al. (2025) Eq.9 post-peak.
      Source: Fakeh et al. (2025) Table 3 — equations in 01_SOURCES/02_SECONDARY_REFERENCE.
      εin = ε×αb ≥ 0 always; no degeneracy. Post-peak M uses ASSUMED fiber dims (λf).
  C2  Zhao et al. (2013) — linear ascending (εin≡0 on ascending), αc=0.35 softening.
      Source: Fakeh et al. (2025) Table 3.
      εc0_model = fc/Ec (model-derived, may differ from reported ecp).

BLOCKED for CDP table (raw σ–ε curves available for comparison):
  C3  Wang et al. (2016) — ascending parabolic. ε0 from Wang Eq.(7); ε20 from Eq.(10)-(11).
      Initial slope = 2×f_peak/ε0 >> Ec → εin < 0 for ~94–100% of ascending (all batches).
      Source: Wang et al. (2016) Adv Mech Eng 8(2):1687814016633411 (primary).
      Use raw_sigma_eps_curve() / eps_in_analysis() for diagnostic comparison.
  C4  Yan (2010) via Fakeh (2025) — rational formula ascending/descending.
      αa ∈ [1.1, 1.138] > k = Ec×εcp/fc ≈ 0.988–1.091 → εin < 0 for ~49–100% of ascending.
      αa/αd given as ranges only (secondary source); no Yan (2010) original in repo.
      Use raw_sigma_eps_curve(alpha_a, alpha_d) for diagnostic comparison.
"""

import math
from .base import BaseModel, ModelStatus, ModelNotAvailableError
from ..batch_data import lambda_f_from_batch, M_graybeal_descent_from_batch

# ── TOLERANCE ────────────────────────────────────────────────────────────────
_FLOAT_NOISE_TOL = 1e-10   # machine-precision noise at initial tangent
_BATCH2_CLIP_TOL = 5e-5    # approved CHANGELOG C-001 engineering clip


class PopovicsCompression(BaseModel):
    """
    Popovics (1973) ascending + linear post-peak descent.
    Post-peak slope is ADOPTED (placeholder).
    """
    MODEL_ID = "REF_POPOVICS"
    STATUS = ModelStatus.IMPLEMENTED_REFERENCE
    SOURCE_PAPER = "Popovics (1973) Cem Concr Res 3(5):583-599"

    def __init__(self, batch_data, eps_u_factor=4.0, sigma_res_ratio=0.05):
        self.b = batch_data
        self.eps_u_factor = eps_u_factor
        self.sigma_res_ratio = sigma_res_ratio

    def _alpha(self):
        return self.b["Ec_mpa"] * self.b["ecp"] / self.b["fc_mpa"]

    def _r(self):
        a = self._alpha()
        if a <= 1.0:
            raise ModelNotAvailableError(
                f"Popovics degenerate for this batch: "
                f"alpha = Ec*ecp/fc = {a:.4f} ≤ 1.0. "
                "Near-elastic ascending branch; use C1-C4 instead."
            )
        return a / (a - 1.0)

    def sigma_ascending(self, eps):
        r = self._r()
        if eps <= 0:
            return 0.0
        eta = eps / self.b["ecp"]
        return self.b["fc_mpa"] * r * eta / (r - 1.0 + eta ** r)

    def sigma_descending(self, eps):
        ecp = self.b["ecp"]
        fc = self.b["fc_mpa"]
        eps_u = self.eps_u_factor * ecp
        sigma_res = self.sigma_res_ratio * fc
        if eps >= eps_u:
            return sigma_res
        t = (eps - ecp) / (eps_u - ecp)
        return fc * (1.0 - t) + sigma_res * t

    def generate_table(self, n_asc=25, n_desc=15):
        Ec = self.b["Ec_mpa"]
        ecp = self.b["ecp"]
        fc = self.b["fc_mpa"]
        use_clip = self.b.get("batch2_peak_clip", False)
        rows = []

        for i in range(n_asc + 1):
            eps = ecp * i / n_asc
            sigma = self.sigma_ascending(eps) if eps > 0 else 0.0
            eps_in = eps - sigma / Ec

            if eps_in < 0:
                if abs(eps_in) <= _FLOAT_NOISE_TOL:
                    eps_in = 0.0
                    note = "DERIVED"
                elif use_clip and abs(eps_in) <= _BATCH2_CLIP_TOL:
                    eps_in = 0.0
                    note = "APPROXIMATED: max(0,-0.000039)=0 per CHANGELOG C-001"
                else:
                    raise ModelNotAvailableError(
                        f"Negative inelastic strain {eps_in:.6e} at eps={eps:.5f} "
                        "exceeds clip tolerance. Use C1-C4 model instead."
                    )
            else:
                note = "DERIVED"

            tag = "REPORTED" if i == n_asc else "DERIVED"
            rows.append({
                "stress_mpa": round(sigma, 4),
                "inelastic_strain": round(eps_in, 8),
                "tag": note if note.startswith("APPROX") else tag,
            })

        eps_u = self.eps_u_factor * ecp
        for j in range(1, n_desc + 1):
            eps = ecp + (eps_u - ecp) * j / n_desc
            sigma = self.sigma_descending(eps)
            if sigma <= 0:
                break
            eps_in = eps - sigma / Ec
            rows.append({
                "stress_mpa": round(sigma, 4),
                "inelastic_strain": round(eps_in, 8),
                "tag": "ADOPTED",
            })

        cleaned = []
        prev = -1.0
        for row in rows:
            if row["stress_mpa"] <= 0:
                continue
            ei = row["inelastic_strain"]
            if ei <= prev:
                ei = prev + 1e-8
                row = dict(row, inelastic_strain=round(ei, 8))
            cleaned.append(row)
            prev = ei
        return cleaned


# ── C1 GRAYBEAL–FAKEH ────────────────────────────────────────────────────────

class C1GraybealFakehCompression(BaseModel):
    """
    C1: Graybeal (FHWA 2005/2007) ascending + Fakeh (2025) Eq.9 linear post-peak.
    Source: Fakeh et al. (2025) Engineering Structures 333:120154, Table 3.

    Ascending: σ(ε) = Ec × ε × (1 − αb)
      αb = ac × exp(ε × Ec / (bc × f'c)) − ac,  ac=0.011, bc=0.44
      εin = ε × αb ≥ 0 for all ε ≥ 0 (guaranteed; no degeneracy).
      Ec: REPORTED from Hosseini 2026 (not Graybeal formula 3840√f'c).
      Note: Graybeal formula gives Ec≈47400–49500 MPa; deviation from reported
      Ec (45400–47300 MPa) is 0–9%. Using REPORTED Ec for fidelity to data.

    Post-peak (Fakeh Eq.9): σ(ε) = σ_peak − M × (ε − εc0_model)
      M = 7061.5 × λf^(−0.411),  λf = vf × (l/df)
      Fiber dims ASSUMED: l=13mm, df=0.2mm (not reported in Hosseini 2026).
      λf tags: ADOPTED (depends on ASSUMED fiber geometry).

    εc0_model: found numerically (where dσ/dε = 0). May differ from reported ecp.
    σ_peak: model peak stress (may differ from reported f'c by ≤5% typical).
    """
    MODEL_ID = "C1"
    STATUS = ModelStatus.IMPLEMENTED
    SOURCE_PAPER = (
        "Graybeal (FHWA) ascending + Fakeh et al. (2025) Eq.9 post-peak; "
        "Table 3 in Fakeh et al. (2025) Engineering Structures 333:120154"
    )

    _ac = 0.011
    _bc = 0.44

    def __init__(self, batch_data, sigma_res_ratio=0.05, n_asc=25, n_desc=15):
        self.b = batch_data
        self.sigma_res_ratio = sigma_res_ratio
        self._n_asc = n_asc
        self._n_desc = n_desc

    def _alpha_b(self, eps):
        """αb = ac × exp(ε × Ec / (bc × f'c)) − ac. Always ≥ 0."""
        if eps <= 0:
            return 0.0
        return self._ac * math.exp(eps * self.b["Ec_mpa"] / (self._bc * self.b["fc_mpa"])) - self._ac

    def _sigma_asc(self, eps):
        """Ascending stress: σ = Ec × ε × (1 − αb)."""
        if eps <= 0:
            return 0.0
        return self.b["Ec_mpa"] * eps * (1.0 - self._alpha_b(eps))

    def _eps_in_asc(self, eps):
        """Inelastic strain on ascending = ε × αb ≥ 0."""
        if eps <= 0:
            return 0.0
        return eps * self._alpha_b(eps)

    def _find_peak(self):
        """
        Return (ecp_model, sigma_peak) by bisecting on dσ/dε = 0.
        Bracket: [0.5 × fc/Ec, 6.0 × fc/Ec].
        """
        fc = self.b["fc_mpa"]
        Ec = self.b["Ec_mpa"]
        eps_lo = 0.5 * fc / Ec
        eps_hi = 6.0 * fc / Ec
        h = eps_lo * 1e-5 + 1e-12
        for _ in range(60):
            eps_mid = 0.5 * (eps_lo + eps_hi)
            dsigma_mid = (self._sigma_asc(eps_mid + h) - self._sigma_asc(eps_mid - h)) / (2 * h)
            if dsigma_mid > 0:
                eps_lo = eps_mid
            else:
                eps_hi = eps_mid
        ecp_m = 0.5 * (eps_lo + eps_hi)
        return ecp_m, self._sigma_asc(ecp_m)

    def generate_table(self, n_asc=None, n_desc=None):
        n_asc = n_asc or self._n_asc
        n_desc = n_desc or self._n_desc
        Ec = self.b["Ec_mpa"]
        fc = self.b["fc_mpa"]
        ecp_model, sigma_peak = self._find_peak()
        M = M_graybeal_descent_from_batch(self.b)
        sigma_res = self.sigma_res_ratio * sigma_peak
        rows = []

        # Ascending: n_asc points from eps=ecp_model/n_asc to ecp_model
        # First row: (sigma_start, 0.0) — initial yield, eps_in set to 0
        # (natural eps_in at first point ≈ O((eps)²) << 1e-9 but we set explicitly)
        for i in range(1, n_asc + 1):
            eps = ecp_model * i / n_asc
            sigma = self._sigma_asc(eps)
            eps_in = self._eps_in_asc(eps)
            if i == 1:
                # Force first row eps_in = 0 (initial yield onset)
                eps_in = 0.0
                tag = "DERIVED"
            elif i == n_asc:
                tag = "DERIVED"  # peak from model (may differ from reported ecp/fc)
            else:
                tag = "DERIVED"
            rows.append({
                "stress_mpa": round(sigma, 4),
                "inelastic_strain": round(eps_in, 8),
                "tag": tag,
            })

        # Post-peak: linear descent from (ecp_model, sigma_peak) to sigma_res
        eps_end = ecp_model + (sigma_peak - sigma_res) / M
        for j in range(1, n_desc + 1):
            eps = ecp_model + (eps_end - ecp_model) * j / n_desc
            sigma = sigma_peak - M * (eps - ecp_model)
            if sigma <= 0:
                break
            eps_in = eps - sigma / Ec
            rows.append({
                "stress_mpa": round(sigma, 4),
                "inelastic_strain": round(eps_in, 8),
                "tag": "ADOPTED",  # M from ASSUMED fiber dims via Fakeh Eq.9
            })

        # Enforce strict monotone eps_in
        cleaned = []
        prev = -1.0
        for row in rows:
            if row["stress_mpa"] <= 0:
                continue
            ei = row["inelastic_strain"]
            if ei <= prev:
                ei = prev + 1e-8
                row = dict(row, inelastic_strain=round(ei, 8))
            cleaned.append(row)
            prev = ei
        return cleaned

    def model_vs_reported_deviation(self):
        """Return dict of model-predicted vs reported ecp/fc for quality check."""
        ecp_m, sigma_peak = self._find_peak()
        ecp_rep = self.b["ecp"]
        fc_rep = self.b["fc_mpa"]
        return {
            "ecp_model": ecp_m,
            "ecp_reported": ecp_rep,
            "ecp_dev_pct": 100.0 * (ecp_m - ecp_rep) / ecp_rep,
            "sigma_peak": sigma_peak,
            "fc_reported": fc_rep,
            "fc_dev_pct": 100.0 * (sigma_peak - fc_rep) / fc_rep,
        }


# ── C2 ZHAO ──────────────────────────────────────────────────────────────────

class C2ZhaoCompression(BaseModel):
    """
    C2: Zhao et al. (2013) — linear ascending + linear softening.
    Source: Fakeh et al. (2025) Table 3.

    Ascending: σ(ε) = Ec × ε  (purely linear → εin ≡ 0 on ascending)
    Peak: at εc0_zhao = fc/Ec (model-derived; may differ from reported ecp).
    Descending: σ(ε) = fc × [1 − αc × (ε/εc0_zhao − 1)],  αc = 0.35
    εin_desc = 1.35 × (ε − εc0_zhao)  (linear, always ≥ 0)

    Abaqus CDP table starts at (fc, 0.0) — initial yield = peak stress.
    Note: Zhao Ec formula = 8010 × (fc)^0.36 [MPa]; reported Ec from Hosseini
    used for εc0_zhao = fc/Ec. Deviation from reported ecp noted in table.
    """
    MODEL_ID = "C2"
    STATUS = ModelStatus.IMPLEMENTED
    SOURCE_PAPER = "Zhao et al. (2013), via Fakeh et al. (2025) Table 3"

    _alpha_c = 0.35

    def __init__(self, batch_data, sigma_res_ratio=0.05, n_desc=15):
        self.b = batch_data
        self.sigma_res_ratio = sigma_res_ratio
        self._n_desc = n_desc

    def generate_table(self, n_desc=None):
        n_desc = n_desc or self._n_desc
        Ec = self.b["Ec_mpa"]
        fc = self.b["fc_mpa"]
        # Model peak strain from purely linear ascending
        ecp_zhao = fc / Ec
        sigma_res = self.sigma_res_ratio * fc

        rows = []

        # First row: initial compressive yield at peak (εin = 0)
        rows.append({
            "stress_mpa": round(fc, 4),
            "inelastic_strain": 0.0,
            "tag": "REPORTED",  # fc is REPORTED; εc0_zhao DERIVED from fc/Ec
        })

        # Descending: σ = fc × [1 − 0.35 × (ε/εc0_zhao − 1)]
        # Stops when σ ≤ sigma_res
        # εin = 1.35 × (ε − εc0_zhao)  →  ε = εc0_zhao + εin/1.35
        # σ = 0 when 0.35 × (ε/εc0_zhao − 1) = 1 → ε/εc0 = 3.857
        eps_zero = ecp_zhao * (1.0 + 1.0 / self._alpha_c)  # ε at σ=0
        eps_res = ecp_zhao + (fc - sigma_res) / (self._alpha_c * fc / ecp_zhao)
        # σ(ε) = fc - fc × αc/εc0 × (ε - εc0) → slope = αc × fc / εc0
        # More precisely: σ = fc × [1 - 0.35 × (ε/εc0 - 1)]
        # σ = sigma_res when: 1 - 0.35(ε/εc0-1) = sigma_res/fc
        # 0.35(ε/εc0-1) = 1 - sigma_res/fc
        # ε = εc0 × [1 + (1 - sigma_res/fc)/0.35]
        eps_end = ecp_zhao * (1.0 + (1.0 - sigma_res / fc) / self._alpha_c)

        for j in range(1, n_desc + 1):
            eps = ecp_zhao + (eps_end - ecp_zhao) * j / n_desc
            sigma = fc * (1.0 - self._alpha_c * (eps / ecp_zhao - 1.0))
            if sigma <= 0:
                break
            # εin = (1 + αc) × (ε − εc0) = 1.35 × (ε − εc0)
            eps_in = (1.0 + self._alpha_c) * (eps - ecp_zhao)
            rows.append({
                "stress_mpa": round(sigma, 4),
                "inelastic_strain": round(eps_in, 8),
                "tag": "DERIVED",
            })

        # Enforce strict monotone (should be automatic but belt-and-suspenders)
        cleaned = [rows[0]]
        prev = rows[0]["inelastic_strain"]
        for row in rows[1:]:
            if row["stress_mpa"] <= 0:
                continue
            ei = row["inelastic_strain"]
            if ei <= prev:
                ei = prev + 1e-8
                row = dict(row, inelastic_strain=round(ei, 8))
            cleaned.append(row)
            prev = ei
        return cleaned

    def ecp_model_vs_reported(self):
        ecp_zhao = self.b["fc_mpa"] / self.b["Ec_mpa"]
        ecp_rep = self.b["ecp"]
        return {
            "ecp_zhao": ecp_zhao,
            "ecp_reported": ecp_rep,
            "dev_pct": 100.0 * (ecp_zhao - ecp_rep) / ecp_rep,
        }


# ── C3 WANG 2016 ─────────────────────────────────────────────────────────────

class C3WangCompression(BaseModel):
    """
    C3: Wang et al. (2016) — source equations implemented; CDP TABLE BLOCKED.

    Source: Wang et al. (2016) Adv Mech Eng 8(2):1687814016633411, Eqs.(3)–(11).

    Equations (ADAPTED: f_peak = fc_reported; Wang Eq.4 lambda_sh NOT applied):
      Ascending  (η = ε/ε0, 0 ≤ η ≤ 1):  σ = f_peak × (2η − η²)
      Descending (ε0 < ε < ε20):           σ = f_peak × [1 − (1−λrs)×(ε−ε0)/(ε20−ε0)]
      Residual   (ε ≥ ε20):                σ = λrs × f_peak  (λrs = 0.30)
      ε0 from Wang Eq.(7): ε0_µε = 0.5×[1950 + 14.6×fp + 763×fp^0.25]; ε0 = ε0_µε×1e-6
      ε20 from Wang Eq.(10)-(11): ε20 = (0.65−λrs)×fp/10300 + 0.65×fp/Ec

    CDP BLOCKER — Ascending εin < 0 (systematic):
      Initial slope = 2×f_peak/ε0 >> Ec for all batches.
      εin = ε − σ/Ec = ε0×η − (f_peak/Ec)×(2η−η²)
      Crossover η_cross = 2 − alpha_wang, where alpha_wang = Ec×ε0/f_peak.
      B1: alpha_wang≈1.034 → η_cross≈0.966 → εin < 0 for ~96.6% of ascending.
      B2: alpha_wang≈1.061 → η_cross≈0.939 → εin < 0 for ~93.9% of ascending.
      B3: alpha_wang≈0.971 → η_cross≈1.029 > 1 → εin < 0 for entire ascending (100%).
      Cannot generate valid Abaqus CDP table without engineering decision.
      Use raw_sigma_eps_curve() and eps_in_analysis() for diagnostic comparison.
    """
    MODEL_ID = "C3"
    STATUS = ModelStatus.BLOCKED
    SOURCE_PAPER = "Wang et al. (2016) Adv Mech Eng 8(2):1687814016633411"
    BLOCKED_REASON = (
        "Ascending parabolic model (initial slope = 2×f_peak/ε0 >> Ec). "
        "εin = ε − σ/Ec < 0 for ~94–100% of ascending branch in all 3 batches "
        "(Wang Eq.7 ε0; B1:~96.6%, B2:~93.9%, B3:100%). "
        "Expert engineering decision required before generating CDP table. "
        "A rewritten ascending branch is a different hybrid law — use new model ID."
    )
    _lambda_rs = 0.30

    def __init__(self, batch_data):
        self.b = batch_data

    def _f_peak(self):
        """ADAPTED: use reported fc; Wang Eq.4 lambda_sh NOT applied."""
        return self.b["fc_mpa"]

    def _eps0_wang(self):
        """Wang Eq.(7) peak strain [dimensionless]. f_peak in MPa."""
        fp = self._f_peak()
        microstrain = 0.5 * (1950.0 + 14.6 * fp + 763.0 * (fp ** 0.25))
        return microstrain * 1e-6

    def _eps20_wang(self):
        """Wang Eq.(10)-(11) residual-onset strain [dimensionless]."""
        fp = self._f_peak()
        Ec = self.b["Ec_mpa"]
        return (0.65 - self._lambda_rs) * fp / 10300.0 + 0.65 * fp / Ec

    def sigma(self, eps):
        """Wang piecewise σ(ε). Returns stress in MPa."""
        eps0 = self._eps0_wang()
        eps20 = self._eps20_wang()
        fp = self._f_peak()
        if eps <= 0:
            return 0.0
        if eps <= eps0:
            eta = eps / eps0
            return fp * (2.0 * eta - eta ** 2)
        elif eps < eps20:
            return fp * (1.0 - (1.0 - self._lambda_rs) * (eps - eps0) / (eps20 - eps0))
        else:
            return self._lambda_rs * fp

    def raw_sigma_eps_curve(self, n_asc=30, n_desc=25):
        """
        Full raw σ–ε curve (NOT Abaqus CDP). Returns list of dicts with keys:
        eps_total, sigma_mpa, eta, eps_in, branch, tag.
        f_peak = fc_reported (ADAPTED).
        """
        eps0 = self._eps0_wang()
        eps20 = self._eps20_wang()
        Ec = self.b["Ec_mpa"]
        pts = []
        for i in range(n_asc + 1):
            eps = eps0 * i / n_asc
            s = self.sigma(eps)
            eta = i / n_asc
            pts.append({
                "eps_total": round(eps, 8), "sigma_mpa": round(s, 4),
                "eta": round(eta, 6), "eps_in": round(eps - s / Ec, 8),
                "branch": "ascending", "tag": "ADAPTED",
            })
        for j in range(1, n_desc + 1):
            eps = eps0 + (eps20 - eps0) * j / n_desc
            s = self.sigma(eps)
            eta = eps / eps0
            pts.append({
                "eps_total": round(eps, 8), "sigma_mpa": round(s, 4),
                "eta": round(eta, 6), "eps_in": round(eps - s / Ec, 8),
                "branch": "descending", "tag": "ADAPTED",
            })
        for k in range(1, 4):
            eps = eps20 * (1.0 + 0.1 * k)
            s = self.sigma(eps)
            eta = eps / eps0
            pts.append({
                "eps_total": round(eps, 8), "sigma_mpa": round(s, 4),
                "eta": round(eta, 6), "eps_in": round(eps - s / Ec, 8),
                "branch": "residual", "tag": "ADAPTED",
            })
        return pts

    def eps_in_analysis(self):
        """
        Analytical εin profile on ascending branch.
        εin(η) = ε0×η − (f_peak/Ec)×(2η−η²)
        Crossover: η_cross = 2 − alpha_wang = 2 − Ec×ε0/f_peak
        Returns dict with quantitative analysis.
        """
        eps0 = self._eps0_wang()
        fp = self._f_peak()
        Ec = self.b["Ec_mpa"]
        alpha_wang = Ec * eps0 / fp
        eta_cross = 2.0 - alpha_wang
        frac_neg = min(max(eta_cross, 0.0), 1.0)
        # Minimum εin: dεin/dη = 0 → η_min = 1 − alpha_wang/2
        eta_min = 1.0 - alpha_wang / 2.0
        if 0.0 < eta_min < 1.0:
            eps_in_min = eps0 * eta_min - (fp / Ec) * (2.0 * eta_min - eta_min ** 2)
        else:
            eps_in_min = min(0.0, eps0 - fp / Ec)
        return {
            "eps0_wang": round(eps0, 8),
            "eps20_wang": round(self._eps20_wang(), 8),
            "alpha_wang": round(alpha_wang, 6),
            "eta_crossover": round(eta_cross, 6),
            "pct_ascending_negative": round(100.0 * frac_neg, 2),
            "eps_in_at_peak": round(eps0 - fp / Ec, 8),
            "eps_in_min": round(eps_in_min, 8),
            "initial_slope_mpa": round(2.0 * fp / eps0, 1),
            "tag": "ADAPTED: f_peak=fc_reported; Wang Eq.7 ε0; Eq.10-11 ε20; lambda_rs=0.30",
        }


# ── C4 YAN 2010 (VIA FAKEH 2025) ─────────────────────────────────────────────

class C4YanCompression(BaseModel):
    """
    C4: Yan (2010) rational formulas — source equations verified; CDP TABLE BLOCKED.

    Source: Fakeh et al. (2025) Table 3 (SECONDARY; Yan 2010 original not in repo).
    Provenance: Yan G., Experimental Study on Strength and Deformation of Reactive
    Powder Concrete Under Triaxial Compression, Yantai, China, pp.383-386 (2010).

    Equations (η = ε/εc0, εc0 = reported ecp):
      Ascending  (0 ≤ η ≤ 1):  σ = fc × (αa×η − η²) / [1 + (αa−2)×η]
      Descending (η ≥ 1):      σ = fc × (αd×η) / [1 + (αd−2)×η + η²]
      Continuity: both branches give fc at η=1; both have zero slope at peak. ✓
      αa ∈ [1.1, 1.138] (range only — no unique value for Hosseini batches)
      αd ∈ [0.193, 0.312] (range only)
      Initial tangent: dσ/dε|0 = αa × fc/εc0

    CDP BLOCKER — Initial tangent > Ec for all batches:
      k = Ec×εcp/fc: B1=1.054, B2=0.988, B3=1.091; all < αa ≥ 1.1.
      Crossover η_cross = (αa−k) / [1 + k×(αa−2)].
      For αa=1.1 (lower bound): B1 η_cross≈0.895 (89.6% negative),
        B2 η_cross≈1.011 (100% negative), B3 η_cross≈0.489 (48.9% negative).
      For αa=1.138 (upper bound): B1 ~91.9%, B2 100%, B3 ~78.8%.
      Use raw_sigma_eps_curve() / eps_in_analysis() for comparison.
    """
    MODEL_ID = "C4"
    STATUS = ModelStatus.BLOCKED
    SOURCE_PAPER = "Yan (2010) via Fakeh et al. (2025) Table 3 [SECONDARY SOURCE]"
    BLOCKED_REASON = (
        "Ascending rational formula: initial tangent αa×fc/εc0 > Ec for all batches "
        "(αa ∈ [1.1,1.138]; k=Ec×εcp/fc ≈ 0.988–1.091). "
        "εin < 0 for ~49–100% of ascending branch (batch/αa-dependent). "
        "αa, αd are parameter ranges only from secondary source (Fakeh Table 3); "
        "no unique calibration for Hosseini batches without Yan (2010) original paper."
    )
    ALPHA_A_RANGE = (1.1, 1.138)
    ALPHA_D_RANGE = (0.193, 0.312)

    def __init__(self, batch_data):
        self.b = batch_data

    def sigma_ascending(self, eps, alpha_a):
        """Yan ascending: σ = fc×(αa×η−η²)/[1+(αa−2)×η], η=ε/εc0."""
        ecp = self.b["ecp"]
        fc = self.b["fc_mpa"]
        if eps <= 0:
            return 0.0
        eta = min(eps / ecp, 1.0)
        denom = 1.0 + (alpha_a - 2.0) * eta
        if abs(denom) < 1e-12:
            return fc
        return fc * (alpha_a * eta - eta ** 2) / denom

    def sigma_descending(self, eps, alpha_d):
        """Yan descending: σ = fc×(αd×η)/[1+(αd−2)×η+η²], η=ε/εc0."""
        ecp = self.b["ecp"]
        fc = self.b["fc_mpa"]
        eta = max(eps / ecp, 1.0)
        denom = 1.0 + (alpha_d - 2.0) * eta + eta ** 2
        if abs(denom) < 1e-12:
            return 0.0
        return max(fc * alpha_d * eta / denom, 0.0)

    def raw_sigma_eps_curve(self, alpha_a=1.1, alpha_d=0.193, n_asc=30, n_desc=40):
        """
        Full raw σ–ε curve (NOT Abaqus CDP). Returns list of dicts with keys:
        eps_total, sigma_mpa, eta, eps_in, branch, tag.
        alpha_a and alpha_d must be specified from ALPHA_A_RANGE / ALPHA_D_RANGE.
        Descending truncated when σ < 0.05×fc or η > 6.
        """
        ecp = self.b["ecp"]
        Ec = self.b["Ec_mpa"]
        fc = self.b["fc_mpa"]
        pts = []
        # Ascending
        for i in range(n_asc + 1):
            eps = ecp * i / n_asc
            s = self.sigma_ascending(eps, alpha_a) if eps > 0 else 0.0
            eta = i / n_asc
            pts.append({
                "eps_total": round(eps, 8), "sigma_mpa": round(s, 4),
                "eta": round(eta, 6), "eps_in": round(eps - s / Ec, 8),
                "branch": "ascending",
                "tag": f"SECONDARY (αa={alpha_a})",
            })
        # Descending to σ = 0.05×fc or η = 6
        for j in range(1, n_desc + 1):
            eps = ecp * (1.0 + 5.0 * j / n_desc)
            s = self.sigma_descending(eps, alpha_d)
            if s < 0.05 * fc:
                break
            eta = eps / ecp
            pts.append({
                "eps_total": round(eps, 8), "sigma_mpa": round(s, 4),
                "eta": round(eta, 6), "eps_in": round(eps - s / Ec, 8),
                "branch": "descending",
                "tag": f"SECONDARY (αd={alpha_d})",
            })
        return pts

    def eps_in_analysis(self, alpha_a_list=None):
        """
        Analytical εin crossover on ascending branch for given αa values.
        Crossover: η_cross = (αa−k) / [1 + k×(αa−2)], k = Ec×εcp/fc.
        Returns dict keyed by alpha_a value.
        """
        if alpha_a_list is None:
            alpha_a_list = list(self.ALPHA_A_RANGE)
        ecp = self.b["ecp"]
        fc = self.b["fc_mpa"]
        Ec = self.b["Ec_mpa"]
        k = Ec * ecp / fc
        results = {}
        for aa in alpha_a_list:
            denom = 1.0 + k * (aa - 2.0)
            eta_cross = (aa - k) / denom if abs(denom) > 1e-12 else 1.0
            frac_neg = min(max(eta_cross, 0.0), 1.0)
            results[aa] = {
                "k": round(k, 6),
                "alpha_a": aa,
                "eta_crossover": round(eta_cross, 6),
                "pct_ascending_negative": round(100.0 * frac_neg, 2),
                "initial_tangent_mpa": round(aa * fc / ecp, 1),
            }
        return results


# ── C4 YAN EC-ADAPTED ────────────────────────────────────────────────────────

class C4YanEcAdaptedCompression(BaseModel):
    """
    C4_YAN_EC_ADAPTED: Yan (2010) rational formula, eps_c0 ADAPTED for Ec-compatibility.

    Source: Yan (2010) via Fakeh (2025) Table 3 [SECONDARY; original paper not in repo].
    Engineering decision: set eps_c0_model = alpha_a × fc / Ec (not reported ecp).
    → initial tangent = alpha_a × fc / eps_c0_model = Ec  (exact, by construction)
    → eps_in ≥ 0 on entire ascending branch (proven analytically):
        eps_in(eta) = (fc/Ec) × eta² × (alpha_a−1)² / (1+(alpha_a−2)×eta) ≥ 0  ∀ eta∈[0,1]
        since (alpha_a−1)² > 0, numerator ≥ 0; denominator > 0 for alpha_a∈[1.1,1.138], eta∈[0,1]

    Formulas (eta = eps / eps_c0_model):
      Ascending  (0 ≤ eta ≤ 1): sigma = fc × (alpha_a×eta − eta²) / [1+(alpha_a−2)×eta]
      Descending (eta ≥ 1):     sigma = fc × (alpha_d×eta) / [1+(alpha_d−2)×eta+eta²]
      Continuity at peak: both branches give fc at eta=1; both have zero slope. ✓
      eps_in at peak: (alpha_a−1) × fc / Ec  (positive, consistent ascending→descending)

    Peak strain deviation from reported ecp:
      eps_c0_model / ecp = alpha_a / k,  k = Ec×ecp/fc
      B1 k=1.054: LB dev=+4.4%, UB dev=+8.1%
      B2 k=0.988: LB dev=+11.4%, UB dev=+15.2%
      B3 k=1.091: LB dev=+0.8%, UB dev=+4.3%

    Note: This adaptation changes the peak strain. Report as ADAPTED throughout.
    Do NOT change reported fc or Ec; do NOT use for holdout comparison without approval.
    """
    MODEL_ID = "C4_YAN_EC_ADAPTED"
    STATUS = ModelStatus.IMPLEMENTED
    SOURCE_PAPER = (
        "Yan (2010) via Fakeh (2025) Table 3 [SECONDARY]; "
        "eps_c0 ADAPTED: alpha_a × fc / Ec (not reported ecp)"
    )
    ALPHA_A_RANGE = (1.1, 1.138)
    ALPHA_D_RANGE = (0.193, 0.312)

    def __init__(self, batch_data, alpha_a=1.1, alpha_d=0.193, sigma_res_ratio=0.05):
        self.b = batch_data
        self.alpha_a = alpha_a
        self.alpha_d = alpha_d
        self.sigma_res_ratio = sigma_res_ratio

    def _eps_c0_model(self):
        """ADAPTED: eps_c0_model = alpha_a × fc / Ec.  Initial tangent = Ec exactly."""
        return self.alpha_a * self.b["fc_mpa"] / self.b["Ec_mpa"]

    def sigma_ascending(self, eps):
        eps_c0 = self._eps_c0_model()
        fc = self.b["fc_mpa"]
        if eps <= 0:
            return 0.0
        eta = min(eps / eps_c0, 1.0)
        aa = self.alpha_a
        denom = 1.0 + (aa - 2.0) * eta
        return fc * (aa * eta - eta ** 2) / denom

    def sigma_descending(self, eps):
        eps_c0 = self._eps_c0_model()
        fc = self.b["fc_mpa"]
        eta = max(eps / eps_c0, 1.0)
        ad = self.alpha_d
        denom = 1.0 + (ad - 2.0) * eta + eta ** 2
        if abs(denom) < 1e-12:
            return 0.0
        return max(fc * ad * eta / denom, 0.0)

    def generate_table(self, n_asc=25, n_desc=20):
        eps_c0 = self._eps_c0_model()
        fc = self.b["fc_mpa"]
        Ec = self.b["Ec_mpa"]
        aa = self.alpha_a
        ad = self.alpha_d
        sigma_res = self.sigma_res_ratio * fc
        rows = []

        # Ascending: n_asc rows from eta=1/n_asc to eta=1
        # eps_in exact formula: (fc/Ec) × eta² × (aa-1)² / (1+(aa-2)×eta) ≥ 0
        for i in range(1, n_asc + 1):
            eta = i / n_asc
            denom_a = 1.0 + (aa - 2.0) * eta
            sigma = fc * (aa * eta - eta ** 2) / denom_a
            eps_in = 0.0 if i == 1 else (fc / Ec) * eta ** 2 * (aa - 1.0) ** 2 / denom_a
            rows.append({
                "stress_mpa": round(sigma, 4),
                "inelastic_strain": round(eps_in, 8),
                "tag": "ADAPTED",
            })

        # Descending: binary-search eta_end where sigma = sigma_res, then distribute
        eta_lo, eta_hi = 1.0, 8.0
        for _ in range(55):
            eta_mid = 0.5 * (eta_lo + eta_hi)
            denom = 1.0 + (ad - 2.0) * eta_mid + eta_mid ** 2
            s = fc * ad * eta_mid / denom if abs(denom) > 1e-12 else 0.0
            if s > sigma_res:
                eta_lo = eta_mid
            else:
                eta_hi = eta_mid
        eta_end = 0.5 * (eta_lo + eta_hi)

        for j in range(1, n_desc + 1):
            eta = 1.0 + (eta_end - 1.0) * j / n_desc
            denom_d = 1.0 + (ad - 2.0) * eta + eta ** 2
            sigma = fc * ad * eta / denom_d if abs(denom_d) > 1e-12 else 0.0
            if sigma <= 0:
                break
            eps_in = (aa * fc / Ec) * eta - sigma / Ec
            rows.append({
                "stress_mpa": round(sigma, 4),
                "inelastic_strain": round(eps_in, 8),
                "tag": "ADAPTED",
            })

        # Belt-and-suspenders: enforce strict monotone eps_in
        cleaned = []
        prev = -1.0
        for row in rows:
            if row["stress_mpa"] <= 0:
                continue
            ei = row["inelastic_strain"]
            if ei <= prev:
                ei = prev + 1e-8
                row = dict(row, inelastic_strain=round(ei, 8))
            cleaned.append(row)
            prev = ei

        # Add eps_pl column: eps_pl = eps_in when dc=0 (no damage table defined at G1).
        # With damage: eps_pl = eps_in - dc/(1-dc) × sigma/Ec (deferred to G2).
        for row in cleaned:
            row["eps_pl"] = row["inelastic_strain"]  # dc=0 assumption, tag NODAMAGE
            row["eps_pl_tag"] = "dc=0 (no damage table at G1)"
        return cleaned

    def peak_strain_deviation(self):
        """Deviation of adapted eps_c0 from reported ecp."""
        eps_c0_model = self._eps_c0_model()
        ecp_rep = self.b["ecp"]
        k = self.b["Ec_mpa"] * ecp_rep / self.b["fc_mpa"]
        return {
            "eps_c0_model": round(eps_c0_model, 7),
            "ecp_reported": ecp_rep,
            "dev_pct": round(100.0 * (eps_c0_model - ecp_rep) / ecp_rep, 2),
            "k": round(k, 6),
            "alpha_a": self.alpha_a,
            "alpha_d": self.alpha_d,
            "eps_in_at_peak": round((self.alpha_a - 1.0) * self.b["fc_mpa"] / self.b["Ec_mpa"], 8),
            "tag": "ADAPTED: eps_c0_model = alpha_a × fc / Ec; not reported ecp",
        }


class C4YanEcAdaptedLB(C4YanEcAdaptedCompression):
    """C4 Yan Ec-adapted: alpha_a=1.100, alpha_d=0.193 (ascending LB, descending LB)."""
    MODEL_ID = "C4_ADAPTED_LB"

    def __init__(self, batch_data):
        super().__init__(batch_data, alpha_a=1.100, alpha_d=0.193)


class C4YanEcAdaptedLAHD(C4YanEcAdaptedCompression):
    """C4 Yan Ec-adapted: alpha_a=1.100, alpha_d=0.312 (ascending LB, descending UB)."""
    MODEL_ID = "C4_ADAPTED_LA_HD"

    def __init__(self, batch_data):
        super().__init__(batch_data, alpha_a=1.100, alpha_d=0.312)


class C4YanEcAdaptedHALD(C4YanEcAdaptedCompression):
    """C4 Yan Ec-adapted: alpha_a=1.138, alpha_d=0.193 (ascending UB, descending LB)."""
    MODEL_ID = "C4_ADAPTED_HA_LD"

    def __init__(self, batch_data):
        super().__init__(batch_data, alpha_a=1.138, alpha_d=0.193)


class C4YanEcAdaptedUB(C4YanEcAdaptedCompression):
    """C4 Yan Ec-adapted: alpha_a=1.138, alpha_d=0.312 (ascending UB, descending UB)."""
    MODEL_ID = "C4_ADAPTED_UB"

    def __init__(self, batch_data):
        super().__init__(batch_data, alpha_a=1.138, alpha_d=0.312)


# ── MODEL REGISTRY ───────────────────────────────────────────────────────────
# 4 C4_ADAPTED variants cover full 2×2 parameter space: alpha_a∈{1.100,1.138} × alpha_d∈{0.193,0.312}

COMPRESSION_MODELS = {
    "REF_POPOVICS":    PopovicsCompression,
    "C1":              C1GraybealFakehCompression,
    "C2":              C2ZhaoCompression,
    "C3":              C3WangCompression,         # BLOCKED (CDP); raw σ–ε reference only
    "C4":              C4YanCompression,           # BLOCKED (CDP); original ecp; raw curves
    "C4_ADAPTED_LB":   C4YanEcAdaptedLB,          # IMPLEMENTED; αa=1.100, αd=0.193
    "C4_ADAPTED_LA_HD": C4YanEcAdaptedLAHD,       # IMPLEMENTED; αa=1.100, αd=0.312
    "C4_ADAPTED_HA_LD": C4YanEcAdaptedHALD,       # IMPLEMENTED; αa=1.138, αd=0.193
    "C4_ADAPTED_UB":   C4YanEcAdaptedUB,          # IMPLEMENTED; αa=1.138, αd=0.312
}

# Convenience factory aliases (backward-compatible)
def C1_STUB(batch_data): return C1GraybealFakehCompression(batch_data)
def C2_STUB(batch_data): return C2ZhaoCompression(batch_data)
def C3_STUB(batch_data): return C3WangCompression(batch_data)
def C4_STUB(batch_data): return C4YanCompression(batch_data)
def C4_ADAPTED_LB_STUB(batch_data): return C4YanEcAdaptedLB(batch_data)
def C4_ADAPTED_LA_HD_STUB(batch_data): return C4YanEcAdaptedLAHD(batch_data)
def C4_ADAPTED_HA_LD_STUB(batch_data): return C4YanEcAdaptedHALD(batch_data)
def C4_ADAPTED_UB_STUB(batch_data): return C4YanEcAdaptedUB(batch_data)

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

BLOCKED (equations in Fakeh Table 3 but cannot generate valid εin table):
  C3  Wang et al. (2016) — ascending parabolic, initial slope = 2fc/εc0 >> Ec
      → εin < 0 for >50% of ascending (systematic, cannot clip); ε20 unknown.
  C4  Yan (2010) — αa=1.1–1.138 > alpha≈0.99–1.09 for all batches
      → εin < 0 for 78–90% of ascending; αa/αd exact values need Yan 2010 paper.
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


# ── C3 WANG — BLOCKED ────────────────────────────────────────────────────────

class _C3WangBlocked(BaseModel):
    """
    C3: Wang et al. (2016) — BLOCKED.

    BLOCKER 1 — Negative ascending εin (systematic):
      Ascending: σ = f'c × [2η − η²], η = ε/εc0.
      Initial slope dσ/dε|0 = 2f'c/εc0. For all 3 batches, 2f'c/εc0 >> Ec:
        Batch 1: 2×152.8/0.0035 = 87314 MPa >> Ec=46000 → εin < 0 for η < 0.526
        Batch 2: 2×153.2/0.0032 = 95750 MPa >> Ec=47300 → εin < 0 for η < 0.507
        Batch 3: 2×166.4/0.004  = 83200 MPa >> Ec=45400 → εin < 0 for η < 0.546
      Negative εin spans >50% of ascending — NOT clippable without expert approval.

    BLOCKER 2 — Missing parameter ε20:
      Descending: σ = f'c × [1 − (1−λrs)×(ε−εc0)/(ε20−εc0)], λrs=0.3
      ε20 not defined in Fakeh (2025) Table 3. Requires Wang (2016) original paper.

    Resolution: Obtain Wang (2016) paper + expert engineering decision on ascending εin.
    """
    MODEL_ID = "C3"
    STATUS = ModelStatus.BLOCKED
    SOURCE_PAPER = "Wang et al. (2016) — ascending εin negative, ε20 unknown"
    BLOCKED_REASON = (
        "Ascending parabolic model (initial slope = 2f'c/εc0 >> Ec) gives "
        "negative εin for >50% of ascending branch in all 3 batches. "
        "Additionally, parameter ε20 (descending endpoint) not defined in "
        "Fakeh (2025) Table 3 — requires Wang (2016) original paper."
    )

    def __init__(self, _batch_data):
        pass


class _C4YanBlocked(BaseModel):
    """
    C4: Yan (2010) — BLOCKED.

    BLOCKER 1 — αa > alpha for all batches:
      Ascending: σ = f'c × [αa×η − η²] / [1 + (αa−2)×η], η = ε/εc0
      Initial tangent = αa × f'c/εc0. For αa=1.1 (lower bound):
        Batch 1: αa/alpha = 1.1/1.054 = 1.044 → εin < 0 for η < 0.895 (89% of ascending)
        Batch 2: αa/alpha = 1.1/0.988 = 1.113 → εin < 0 for η < 0.917 (92% of ascending)
        Batch 3: αa/alpha = 1.1/1.091 = 1.008 → εin < 0 for η < 0.812 (81% of ascending)
      Negative εin spans 81–92% of ascending — NOT clippable without expert approval.

    BLOCKER 2 — Parameter ranges (not single values):
      αa = 1.1–1.138 (range, not a single value)
      αd = 0.193–0.312 (range, not a single value)
      Exact batch-specific values require Yan (2010) original paper.
      Yan (2010) is NOT in 01_SOURCES/02_SECONDARY_REFERENCE.

    Resolution: Obtain Yan (2010) paper + expert engineering decision on ascending εin.
    """
    MODEL_ID = "C4"
    STATUS = ModelStatus.BLOCKED
    SOURCE_PAPER = "Yan (2010) — αa > alpha (negative ascending εin), parameter ranges"
    BLOCKED_REASON = (
        "Yan ascending αa=1.1–1.138 > alpha≈0.988–1.091 for all batches. "
        "εin < 0 for 81–92% of the ascending branch. "
        "Additionally αa and αd given as ranges only; Yan (2010) paper not in sources."
    )

    def __init__(self, _batch_data):
        pass


# ── MODEL REGISTRY ───────────────────────────────────────────────────────────

COMPRESSION_MODELS = {
    "REF_POPOVICS": PopovicsCompression,
    "C1": C1GraybealFakehCompression,
    "C2": C2ZhaoCompression,
    "C3": _C3WangBlocked,
    "C4": _C4YanBlocked,
}

# Convenience factory aliases (backward-compatible)
def C1_STUB(batch_data): return C1GraybealFakehCompression(batch_data)
def C2_STUB(batch_data): return C2ZhaoCompression(batch_data)
def C3_STUB(batch_data): return _C3WangBlocked(batch_data)
def C4_STUB(batch_data): return _C4YanBlocked(batch_data)

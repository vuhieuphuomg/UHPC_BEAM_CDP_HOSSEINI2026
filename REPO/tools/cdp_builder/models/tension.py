"""
Tension constitutive models for UHPC CDP.

Abaqus CDP tension stiffening table: stress_mpa vs cracking_strain (εck = εtotal − σ/Ec).
First row must be (ft_cr, 0) — zero cracking strain at first crack.
All cracking strains must be strictly increasing, all stresses > 0.

IMPLEMENTED (reference):
  REF_BILINEAR  Bilinear hardening from Hosseini Table 2.
                Hardening only (ascending). Softening REVIEW_REQUIRED.

IMPLEMENTED (named project models):
  T1  Tian et al. (2023) + Fakeh et al. (2025).
      Pre-peak: bilinear (ft_cr → ft_loc) from Hosseini data (same as REF_BILINEAR).
      Post-peak: BLOCKED — requires εu (ultimate strain at 0.85×ft) from Tian 2023.
      softening_status: BLOCKED_MISSING_εu.
  T2  Zhao et al. (2013).
      Pre-peak: bilinear (ft_cr → ft_loc) from Hosseini data.
      Post-peak: σ = ft × (εt0/ε)^0.6, terminal at ftu=0.2×ft.
      Source: Fakeh (2025) Table 4, αt=0.6 verified.
      WARNING: σ–εck post-peak is mesh-dependent; see softening_status.

NOTE on σ–w conversion (Fakeh 2025 Eq.8):
  λclc = 2.078 × ft + 50.21  [mm; ft in MPa]
  wtu = εtu × λclc            [crack opening at 0.2×ft]
  wto = εt0 × lc              [crack opening at peak; mesh-dependent, lc unknown at G1]
  This conversion requires mesh characteristic length lc (not set at G1 stage).
  Do NOT use w = et_loc × GL_gauge (gauge length ≠ localization length).
"""

import math
from .base import BaseModel, ModelStatus, ModelNotAvailableError


class BilinearTensionHardening(BaseModel):
    """
    REF_BILINEAR: bilinear tensile hardening (ascending only) from Hosseini Table 2.
    Hardening only. Softening branch REVIEW_REQUIRED (no σ–w data in paper).
    """
    MODEL_ID = "REF_BILINEAR_TENSION"
    STATUS = ModelStatus.IMPLEMENTED_REFERENCE
    SOURCE_PAPER = "Table 2, Hosseini 2026 — hardening region only"

    def __init__(self, batch_data, n_hardening=10):
        self.b = batch_data
        self.n_hardening = n_hardening

    def generate_table(self):
        Ec = self.b["Ec_mpa"]
        ft_cr = self.b["ft_cr_mpa"]
        et_cr = self.b["et_cr"]
        ft_loc = self.b["ft_loc_mpa"]
        et_loc = self.b["et_loc"]

        rows = []
        rows.append({
            "stress_mpa": round(ft_cr, 4),
            "cracking_strain": 0.0,
            "tag": "REPORTED",
        })

        for i in range(1, self.n_hardening):
            t = i / self.n_hardening
            sigma = ft_cr + t * (ft_loc - ft_cr)
            eps_total = et_cr + t * (et_loc - et_cr)
            eps_ck = eps_total - sigma / Ec
            if eps_ck < 0:
                eps_ck = 0.0
            rows.append({
                "stress_mpa": round(sigma, 4),
                "cracking_strain": round(eps_ck, 8),
                "tag": "DERIVED",
            })

        eps_ck_peak = et_loc - ft_loc / Ec
        if eps_ck_peak < 0:
            eps_ck_peak = 0.0
        rows.append({
            "stress_mpa": round(ft_loc, 4),
            "cracking_strain": round(eps_ck_peak, 8),
            "tag": "REPORTED",
        })

        cleaned = [rows[0]]
        for row in rows[1:]:
            prev_ck = cleaned[-1]["cracking_strain"]
            ck = row["cracking_strain"]
            if ck <= prev_ck:
                ck = prev_ck + 1e-8
                row = dict(row, cracking_strain=round(ck, 8))
            cleaned.append(row)
        return cleaned

    @property
    def softening_status(self):
        return (
            "REVIEW_REQUIRED: post-localization softening (σ–w) not available. "
            "Gauge length GL={GL}mm converts avg tensile strain to displacement "
            "but does NOT give localized crack opening width. "
            "σ–w requires localization length lc (mesh-dependent) or experimental "
            "crack opening data. Do NOT use w = et_loc × GL as default conversion. "
            "Fakeh (2025) Eq.8: λclc = 2.078×ft + 50.21 [mm]; wtu = εtu×λclc; "
            "wto = εt0×lc (lc unknown at G1)."
        ).format(GL=self.b["GL_mm"])


def _bilinear_hardening_rows(b, n_hardening=10):
    """Shared pre-peak bilinear rows for T1 and T2 models (same as REF_BILINEAR)."""
    Ec = b["Ec_mpa"]
    ft_cr = b["ft_cr_mpa"]
    et_cr = b["et_cr"]
    ft_loc = b["ft_loc_mpa"]
    et_loc = b["et_loc"]

    rows = [{"stress_mpa": round(ft_cr, 4), "cracking_strain": 0.0, "tag": "REPORTED"}]

    for i in range(1, n_hardening):
        t = i / n_hardening
        sigma = ft_cr + t * (ft_loc - ft_cr)
        eps_total = et_cr + t * (et_loc - et_cr)
        eps_ck = max(0.0, eps_total - sigma / Ec)
        rows.append({"stress_mpa": round(sigma, 4), "cracking_strain": round(eps_ck, 8), "tag": "DERIVED"})

    eps_ck_peak = max(0.0, et_loc - ft_loc / Ec)
    rows.append({"stress_mpa": round(ft_loc, 4), "cracking_strain": round(eps_ck_peak, 8), "tag": "REPORTED"})

    cleaned = [rows[0]]
    for row in rows[1:]:
        prev_ck = cleaned[-1]["cracking_strain"]
        ck = row["cracking_strain"]
        if ck <= prev_ck:
            ck = prev_ck + 1e-8
            row = dict(row, cracking_strain=round(ck, 8))
        cleaned.append(row)
    return cleaned


# ── T1 TIAN–FAKEH ─────────────────────────────────────────────────────────────

class T1TianFakehTension(BaseModel):
    """
    T1: Tian et al. (2023) ascending + Fakeh (2025) extended softening.
    Source: Fakeh et al. (2025) Table 4.

    Pre-peak (hardening): bilinear (ft_cr → ft_loc) using Hosseini reported data.
      Same functional form as REF_BILINEAR. Parameters from Hosseini Table 2.
      Note: Tian model predicts fte, ft, εte, εt0 from fc and λf only
      (Table 4 formulas). These predictions deviate from Hosseini measured values.
      Hosseini measured values are used here as they are more accurate for these batches.

    Post-peak (Tian linear descent + Fakeh extension to 0.2×ft): BLOCKED.
      Requires εu (total strain where σ = 0.85×ft on Tian descending branch).
      εu is NOT reported in Hosseini (2026) Table 2 and is not computable
      without the Tian (2023) original paper.
      Fakeh σ–w conversion also requires lc (mesh characteristic length, unknown at G1).
    """
    MODEL_ID = "T1"
    STATUS = ModelStatus.IMPLEMENTED
    SOURCE_PAPER = "Tian et al. (2023) + Fakeh et al. (2025) Table 4"

    def __init__(self, batch_data, n_hardening=10):
        self.b = batch_data
        self.n_hardening = n_hardening

    def generate_table(self):
        """Returns hardening rows only. Post-peak BLOCKED_MISSING_εu."""
        return _bilinear_hardening_rows(self.b, self.n_hardening)

    @property
    def softening_status(self):
        return (
            "BLOCKED_MISSING_PARAM: "
            "Tian (2023) post-peak σ(ε) = ft × (1 − 0.15 × (ε−εt0)/(εu−εt0)) "
            "[Fakeh (2025) Table 4 — formula DOCUMENTED, source: Fakeh secondary]. "
            "Missing parameter: εu = total strain at σ = 0.85×ft on descending branch. "
            "εu is NOT in Hosseini (2026) Table 2. "
            "Tian (2023) original paper NOT in 01_SOURCES/02_SECONDARY_REFERENCE — "
            "εu formula (likely function of fc and λf) cannot be verified. "
            "Fakeh σ–w extension also needs lc (mesh size, unknown at G1). "
            "Do NOT use w = et_loc × GL_gauge (gauge length ≠ localization length). "
            "Fakeh (2025) Eq.8: λclc = 2.078×ft + 50.21 [mm]; wtu = εtu×λclc; "
            "wto = εt0×lc (lc unknown at G1)."
        )


# ── T2 ZHAO ───────────────────────────────────────────────────────────────────

class T2ZhaoTension(BaseModel):
    """
    T2: Zhao et al. (2013) bilinear hardening + power-law softening.
    Source: Fakeh et al. (2025) Table 4.

    Pre-peak (hardening): bilinear (ft_cr → ft_loc) using Hosseini reported data.

    Post-peak (softening): σ = ft × (εt0/ε)^αt,  αt = 0.6,  ftu = 0.2×ft
      Source: Fakeh (2025) Table 4, verified. αt = 0.6 exact.
      Terminal: εtu = εt0 × (0.2)^(−1/0.6) ≈ εt0 × 14.62 (when σ = 0.2×ft).
      εck = ε − σ/Ec (monotone increasing; dεck/dε = 1 + 0.6×σ/(Ec×ε) > 0).

    MESH DEPENDENCY WARNING:
      Post-peak σ–εck is mesh-dependent (strain localization in tension).
      Fakeh (2025) recommends σ–w approach for mesh-independent softening:
        λclc = 2.078×ft + 50.21 [mm]
        wtu = εtu × λclc  (mesh-independent crack opening at 0.2×ft)
        wto = εt0 × lc    (crack opening at peak; lc = mesh char. length, UNKNOWN at G1)
      Do NOT use w = et_loc × GL (gauge length ≠ localization length).
      σ–w table can be generated once lc is determined from mesh.
    """
    MODEL_ID = "T2"
    STATUS = ModelStatus.IMPLEMENTED
    SOURCE_PAPER = "Zhao et al. (2013), via Fakeh et al. (2025) Table 4"

    _alpha_t = 0.6

    def __init__(self, batch_data, n_hardening=10, n_softening=10, ftu_ratio=0.2):
        self.b = batch_data
        self.n_hardening = n_hardening
        self.n_softening = n_softening
        self.ftu_ratio = ftu_ratio  # residual stress / ft_loc

    def generate_table(self):
        Ec = self.b["Ec_mpa"]
        ft_loc = self.b["ft_loc_mpa"]
        et_loc = self.b["et_loc"]
        ftu = self.ftu_ratio * ft_loc

        # Pre-peak hardening rows
        rows = _bilinear_hardening_rows(self.b, self.n_hardening)

        # Post-peak: σ = ft_loc × (et_loc/ε)^0.6
        # Terminal: σ = ftu → εtu = et_loc × (ftu/ft_loc)^(-1/αt) = et_loc × (0.2)^(-1/0.6)
        eps_ratio = (self.ftu_ratio) ** (-1.0 / self._alpha_t)  # εtu/εt0
        eps_tu = et_loc * eps_ratio

        # Cracking strain at peak (last hardening row)
        eps_ck_peak = rows[-1]["cracking_strain"]

        # Generate softening points from just after et_loc to eps_tu
        prev_ck = eps_ck_peak
        for j in range(1, self.n_softening + 1):
            eps = et_loc + (eps_tu - et_loc) * j / self.n_softening
            sigma = ft_loc * (et_loc / eps) ** self._alpha_t
            if sigma <= 0:
                break
            eps_ck = eps - sigma / Ec
            # Enforce strict monotone (should hold analytically but guard against rounding)
            if eps_ck <= prev_ck:
                eps_ck = prev_ck + 1e-8
            rows.append({
                "stress_mpa": round(sigma, 4),
                "cracking_strain": round(eps_ck, 8),
                "tag": "DERIVED",
            })
            prev_ck = eps_ck

        return rows

    @property
    def softening_status(self):
        Ec = self.b["Ec_mpa"]
        ft_loc = self.b["ft_loc_mpa"]
        et_loc = self.b["et_loc"]
        eps_ratio = (self.ftu_ratio) ** (-1.0 / self._alpha_t)
        eps_tu = et_loc * eps_ratio
        lclc = 2.078 * ft_loc + 50.21
        wtu = eps_tu * lclc
        return (
            f"IMPLEMENTED (σ–εck, mesh-dependent): Zhao power law σ=ft×(εt0/ε)^0.6, "
            f"terminal at 0.2×ft (εtu≈{eps_tu:.4f}). "
            f"MESH DEPENDENCY WARNING: post-peak σ–εck is mesh-size dependent. "
            f"Fakeh (2025) σ–w: λclc=2.078×{ft_loc:.1f}+50.21={lclc:.1f}mm; "
            f"wtu=εtu×λclc≈{wtu:.1f}mm; wto=εt0×lc (lc unknown at G1). "
            f"Do NOT use w=et_loc×GL (gauge length ≠ localization length)."
        )

    def sigma_w_params(self):
        """Return Fakeh σ–w conversion parameters (requires lc from mesh)."""
        ft_loc = self.b["ft_loc_mpa"]
        et_loc = self.b["et_loc"]
        eps_ratio = (self.ftu_ratio) ** (-1.0 / self._alpha_t)
        eps_tu = et_loc * eps_ratio
        lclc = 2.078 * ft_loc + 50.21
        return {
            "ft_loc_mpa": ft_loc,
            "et_loc": et_loc,
            "eps_tu": eps_tu,
            "lambda_clc_mm": lclc,
            "wtu_mm": eps_tu * lclc,
            "wto_mm_per_lc": et_loc,  # wto = et_loc × lc; lc is mesh-dependent
            "lc_mm": "UNKNOWN — set from mesh characteristic length",
        }

    def fracture_energy_lambda_clc(self):
        """
        Estimate fracture energy GFI [N/mm = MPa·mm] using Fakeh λclc as localization length.

        This is an ESTIMATE for engineering comparison. It does NOT replace a direct
        experimental measurement of GFI. It uses Fakeh (2025) Eq.8 λclc as the localization
        length in place of the FE mesh characteristic length lc.

        Derivation (Zhao softening σ = ft × (εt0/ε)^αt, αt=0.6):
          GFI = λclc × ∫_{εt0}^{εtu} ft × (εt0/ε)^0.6 dε
              = λclc × ft × εt0 / 0.4 × ((εtu/εt0)^0.4 − 1)

        Returns: dict with GFI_nmm, wto_mm, wtu_mm, lambda_clc_mm, tag.
        """
        ft_loc = self.b["ft_loc_mpa"]
        et_loc = self.b["et_loc"]
        eps_ratio = (self.ftu_ratio) ** (-1.0 / self._alpha_t)   # εtu/εt0
        eps_tu = et_loc * eps_ratio
        lclc = 2.078 * ft_loc + 50.21  # mm, Fakeh Eq.8
        # GFI = λclc × ft × εt0 / αt × ((εtu/εt0)^αt − 1)
        gfi = lclc * ft_loc * et_loc / self._alpha_t * (eps_ratio ** self._alpha_t - 1.0)
        wto = et_loc * lclc
        wtu = eps_tu * lclc
        return {
            "GFI_nmm": round(gfi, 3),
            "wto_mm": round(wto, 3),
            "wtu_mm": round(wtu, 3),
            "lambda_clc_mm": round(lclc, 2),
            "ft_loc_mpa": ft_loc,
            "et_loc": et_loc,
            "eps_tu": round(eps_tu, 6),
            "tag": (
                "ESTIMATE using Fakeh (2025) λclc as localization length. "
                "NOT a direct measurement. For reference only. "
                "Production σ–w table requires lc from FE mesh."
            ),
        }


# ── MODEL REGISTRY ────────────────────────────────────────────────────────────

TENSION_MODELS = {
    "REF_BILINEAR": BilinearTensionHardening,
    "T1": T1TianFakehTension,
    "T2": T2ZhaoTension,
}

def T1_STUB(batch_data): return T1TianFakehTension(batch_data)
def T2_STUB(batch_data): return T2ZhaoTension(batch_data)

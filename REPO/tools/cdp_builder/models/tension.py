"""
Tension constitutive models for UHPC CDP.

IMPLEMENTED (reference only — not a named project model):
  REF_BILINEAR  Bilinear hardening from Table 2 data only.
                Ascending: linear 0→ft_cr (at et_cr), linear ft_cr→ft_loc (at et_loc).
                Abaqus format: stress vs cracking strain (eps_ck = eps - sigma/Ec).
                First crack = first row (ft_cr, 0).
                HARDENING REGION ONLY — no softening (σ-w data not in paper).
                Softening needs Gf or σ-w curve: REVIEW_REQUIRED at G1.

REVIEW_REQUIRED (source papers not in 01_SOURCES/02_SECONDARY_REFERENCE):
  T1  Tian et al. (2023), modified by Fakeh et al. (2025)
  T2  Zhao et al. (2013)

NOTE on gauge length (REVIEW-7):
  Batch 1 & 2 tensile specimens GL=700mm; Batch 3 GL=500mm.
  et_loc from Table 2 is gauge-length-dependent; crack opening w = et_loc × GL.
  This difference is preserved in batch_data but does NOT affect the hardening
  table (which is in strain). It matters for the softening crack opening table.
"""

from .base import BaseModel, ModelStatus, ModelNotAvailableError


class BilinearTensionHardening(BaseModel):
    """
    Bilinear tensile hardening table (stress vs cracking strain) from Table 2.
    Represents HARDENING only (ascending pre-localization branch).
    Softening branch (post-localization) is NOT generated — mark REVIEW_REQUIRED.

    Abaqus CDP tension hardening table format:
      yield stress (MPa),  cracking strain (dimensionless)
    where cracking strain = total strain - sigma/Ec (elastic recovery).

    First row must be (ft_cr, 0) — zero cracking strain at first crack.
    """
    MODEL_ID = "REF_BILINEAR_TENSION"
    STATUS = ModelStatus.IMPLEMENTED_REFERENCE
    SOURCE_PAPER = "Table 2, Hosseini 2026 — hardening region only"

    def __init__(self, batch_data, n_hardening=10):
        self.b = batch_data
        self.n_hardening = n_hardening

    def generate_table(self):
        """
        Returns list of dicts: stress_mpa, cracking_strain, tag.
        Followed by a REVIEW_REQUIRED sentinel for the softening branch.
        """
        Ec = self.b["Ec_mpa"]
        ft_cr = self.b["ft_cr_mpa"]
        et_cr = self.b["et_cr"]
        ft_loc = self.b["ft_loc_mpa"]
        et_loc = self.b["et_loc"]

        rows = []

        # Point 1: first crack (cracking strain = 0 by definition)
        rows.append({
            "stress_mpa": round(ft_cr, 4),
            "cracking_strain": 0.0,
            "tag": "REPORTED",
        })

        # Intermediate points between ft_cr and ft_loc
        for i in range(1, self.n_hardening):
            t = i / self.n_hardening
            sigma = ft_cr + t * (ft_loc - ft_cr)
            # linear interpolation of total strain
            eps_total = et_cr + t * (et_loc - et_cr)
            eps_ck = eps_total - sigma / Ec
            if eps_ck < 0:
                eps_ck = 0.0
            rows.append({
                "stress_mpa": round(sigma, 4),
                "cracking_strain": round(eps_ck, 8),
                "tag": "DERIVED",
            })

        # Peak (localization) point
        eps_ck_peak = et_loc - ft_loc / Ec
        if eps_ck_peak < 0:
            eps_ck_peak = 0.0
        rows.append({
            "stress_mpa": round(ft_loc, 4),
            "cracking_strain": round(eps_ck_peak, 8),
            "tag": "REPORTED",
        })

        # Enforce monotone cracking_strain
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
            "REVIEW_REQUIRED: post-localization softening (σ-w) not in paper. "
            f"Batch GL={self.b['GL_mm']}mm; crack opening w = et_loc × GL = "
            f"{self.b['et_loc']*self.b['GL_mm']:.1f}mm at localization. "
            "Provide Gf or σ-w curve to complete softening branch."
        )


# ── REVIEW_REQUIRED STUBS ─────────────────────────────────────────────────────

class _TReviewStub(BaseModel):
    STATUS = ModelStatus.REVIEW_REQUIRED
    def __init__(self, _batch_data):
        pass


class _T1Stub(_TReviewStub):
    MODEL_ID = "T1"
    SOURCE_PAPER = "Tian et al. (2023) modified Fakeh et al. (2025) — not in 01_SOURCES/02_SECONDARY_REFERENCE"


class _T2Stub(_TReviewStub):
    MODEL_ID = "T2"
    SOURCE_PAPER = "Zhao et al. (2013) — not in 01_SOURCES/02_SECONDARY_REFERENCE"


def T1_STUB(batch_data): return _T1Stub(batch_data)
def T2_STUB(batch_data): return _T2Stub(batch_data)

TENSION_MODELS = {
    "REF_BILINEAR": BilinearTensionHardening,
    "T1": _T1Stub,
    "T2": _T2Stub,
}

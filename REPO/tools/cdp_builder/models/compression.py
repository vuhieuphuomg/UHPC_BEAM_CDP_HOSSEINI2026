"""
Compression constitutive models for UHPC CDP.

IMPLEMENTED (reference only — not a named project model):
  REF_POPOVICS  Popovics (1973) Cem Concr Res 3(5):583-599
                Ascending: σ/f'c = r·η/(r-1+η^r), η=ε/εcp, r=α/(α-1), α=Ec·εcp/f'c
                Post-peak: linear descent (ADOPTED — parameters not from source paper)
                FAILS for Batch 2 (α=0.988 < 1; degenerate).

REVIEW_REQUIRED (source papers not in 01_SOURCES/02_SECONDARY_REFERENCE):
  C1  Graybeal (FHWA), modified by Fakeh et al. (2025)
  C2  Zhao et al. (2013)
  C3  Wang et al. (2016)
  C4  Yan (2010)
"""

import math
from .base import BaseModel, ModelStatus, ModelNotAvailableError

# ── TOLERANCE ────────────────────────────────────────────────────────────────
# Machine-precision noise: initial tangent = Ec, so eps_in ≈ 0 at small strains.
# Floating point gives e.g. -5e-20; safe to clip unconditionally.
_FLOAT_NOISE_TOL = 1e-10

# Engineering clip for Batch 2 peak: approved in CHANGELOG C-001.
# eps_in,peak = max(0, 0.0032 − 153.2/47300) = max(0, −3.9e-5) = 0.
_BATCH2_CLIP_TOL = 5e-5


class PopovicsCompression(BaseModel):
    """
    Popovics (1973) ascending + linear post-peak descent.
    Ascending is DERIVED from batch data.
    Post-peak slope is ADOPTED (placeholder) — must be replaced at G1 with
    source-paper post-peak when C1-C4 equations are loaded.
    """
    MODEL_ID = "REF_POPOVICS"
    STATUS = ModelStatus.IMPLEMENTED_REFERENCE
    SOURCE_PAPER = "Popovics (1973) Cem Concr Res 3(5):583-599"

    def __init__(self, batch_data, eps_u_factor=4.0, sigma_res_ratio=0.05):
        self.b = batch_data
        self.eps_u_factor = eps_u_factor        # eps_ultimate = factor * ecp
        self.sigma_res_ratio = sigma_res_ratio  # residual = ratio * f'c (ADOPTED)

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
        """
        Returns list of dicts: stress_mpa, inelastic_strain, plastic_strain (no dc),
        tag (DERIVED/ADOPTED), notes.
        First row: (sigma≈0, eps_in=0) required by Abaqus.
        """
        Ec = self.b["Ec_mpa"]
        ecp = self.b["ecp"]
        fc = self.b["fc_mpa"]
        use_clip = self.b.get("batch2_peak_clip", False)
        rows = []

        # --- ascending (0 → ecp) ---
        for i in range(n_asc + 1):
            eps = ecp * i / n_asc
            sigma = self.sigma_ascending(eps) if eps > 0 else 0.0
            eps_in = eps - sigma / Ec

            if eps_in < 0:
                if abs(eps_in) <= _FLOAT_NOISE_TOL:
                    # Machine-precision rounding at initial tangent; safe to zero.
                    eps_in = 0.0
                    note = "DERIVED"
                elif use_clip and abs(eps_in) <= _BATCH2_CLIP_TOL:
                    eps_in = 0.0
                    note = "APPROXIMATED: max(0,-0.000039)=0 per CHANGELOG C-001"
                else:
                    raise ModelNotAvailableError(
                        f"Negative inelastic strain {eps_in:.6e} at eps={eps:.5f} "
                        f"exceeds clip tolerance. Cannot auto-clip. "
                        "Use C1-C4 model instead."
                    )
            else:
                note = "DERIVED"

            tag = "REPORTED" if i == n_asc else "DERIVED"
            rows.append({
                "stress_mpa": round(sigma, 4),
                "inelastic_strain": round(eps_in, 8),
                "tag": note if note.startswith("APPROX") else tag,
            })

        # --- descending (ecp → eps_u) — ADOPTED ---
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

        # --- enforce strict monotone eps_in ---
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


# ── REVIEW_REQUIRED STUBS ─────────────────────────────────────────────────────

class _ReviewRequiredStub(BaseModel):
    STATUS = ModelStatus.REVIEW_REQUIRED
    def __init__(self, _batch_data):
        pass  # accept batch_data but do nothing


class _C1Stub(_ReviewRequiredStub):
    MODEL_ID = "C1"
    SOURCE_PAPER = "Graybeal (FHWA) modified by Fakeh et al. (2025) — not in 01_SOURCES/02_SECONDARY_REFERENCE"


class _C2Stub(_ReviewRequiredStub):
    MODEL_ID = "C2"
    SOURCE_PAPER = "Zhao et al. (2013) — not in 01_SOURCES/02_SECONDARY_REFERENCE"


class _C3Stub(_ReviewRequiredStub):
    MODEL_ID = "C3"
    SOURCE_PAPER = "Wang et al. (2016) — not in 01_SOURCES/02_SECONDARY_REFERENCE"


class _C4Stub(_ReviewRequiredStub):
    MODEL_ID = "C4"
    SOURCE_PAPER = "Yan (2010) — not in 01_SOURCES/02_SECONDARY_REFERENCE"


def C1_STUB(batch_data): return _C1Stub(batch_data)
def C2_STUB(batch_data): return _C2Stub(batch_data)
def C3_STUB(batch_data): return _C3Stub(batch_data)
def C4_STUB(batch_data): return _C4Stub(batch_data)

COMPRESSION_MODELS = {
    "REF_POPOVICS": PopovicsCompression,
    "C1": _C1Stub,
    "C2": _C2Stub,
    "C3": _C3Stub,
    "C4": _C4Stub,
}

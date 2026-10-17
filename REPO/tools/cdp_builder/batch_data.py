"""
Batch UHPC properties from G0 source audit.
Source: Hosseini et al. (2026) Table 2  DOI 10.1016/j.engstruct.2025.121810
All values REPORTED (mean ± SD).  Strains: dimensionless (not %).
"""

BATCHES = {
    1: {
        "vf_percent": 2,
        "source": "Table 2 p.4 Hosseini 2026",
        # Compression (REPORTED)
        "fc_mpa": 152.8, "fc_sd": 9.3,
        "Ec_mpa": 46000.0, "Ec_sd": 500.0,   # GPa → MPa
        "ecp": 0.0035, "ecp_sd": 0.0006,
        # Tension (REPORTED)
        "ft_cr_mpa": 9.0, "ft_cr_sd": 0.8,
        "et_cr": 0.0016, "et_cr_sd": 0.0004,
        "ft_loc_mpa": 10.0, "ft_loc_sd": 0.8,
        "et_loc": 0.0050, "et_loc_sd": 0.0004,
        "ft_cr_inv": 8.8, "fFu_inv": 12.0,
        "GL_mm": 700,  # tensile specimen gauge length
        "batch2_peak_clip": False,
    },
    2: {
        "vf_percent": 2,
        "source": "Table 2 p.4 Hosseini 2026",
        "fc_mpa": 153.2, "fc_sd": 9.6,
        "Ec_mpa": 47300.0, "Ec_sd": 2100.0,
        "ecp": 0.0032, "ecp_sd": 0.0005,
        "ft_cr_mpa": 8.8, "ft_cr_sd": 1.2,
        "et_cr": 0.0015, "et_cr_sd": 0.0003,
        "ft_loc_mpa": 9.3, "ft_loc_sd": 1.2,
        "et_loc": 0.0050, "et_loc_sd": 0.0001,
        "ft_cr_inv": 9.0, "fFu_inv": 10.8,
        "GL_mm": 700,
        # CHANGELOG C-001: eps_in,peak = max(0, -0.000039) = 0 approved as FE approx.
        "batch2_peak_clip": True,
    },
    3: {
        "vf_percent": 1,
        "source": "Table 2 p.4 Hosseini 2026",
        "fc_mpa": 166.4, "fc_sd": 4.4,
        "Ec_mpa": 45400.0, "Ec_sd": 1100.0,
        "ecp": 0.0040, "ecp_sd": 0.0004,
        "ft_cr_mpa": 6.0, "ft_cr_sd": 1.0,
        "et_cr": 0.0010, "et_cr_sd": 0.0004,
        "ft_loc_mpa": 7.5, "ft_loc_sd": 1.0,
        "et_loc": 0.0027, "et_loc_sd": 0.0002,
        "ft_cr_inv": 5.3, "fFu_inv": 7.8,
        "GL_mm": 500,  # different GL — see REVIEW-7 in G0_REVIEW_REQUEST_V5.md
        "batch2_peak_clip": False,
    },
}


def alpha_compression(batch_id):
    """Initial slope ratio alpha = Ec*ecp/fc. Returns (alpha, is_degenerate)."""
    b = BATCHES[batch_id]
    a = b["Ec_mpa"] * b["ecp"] / b["fc_mpa"]
    return a, a <= 1.0


def eps_in_peak(batch_id):
    """Nominal inelastic strain at peak compression = ecp - fc/Ec."""
    b = BATCHES[batch_id]
    return b["ecp"] - b["fc_mpa"] / b["Ec_mpa"]


def tension_eps_crack_at_loc(batch_id):
    """Cracking strain at localization = et_loc - ft_loc/Ec."""
    b = BATCHES[batch_id]
    return b["et_loc"] - b["ft_loc_mpa"] / b["Ec_mpa"]


# ── FIBER DIMENSIONS ─────────────────────────────────────────────────────────
# ASSUMED: standard straight steel UHPC fibers from Fakeh (2025) Table 1 database.
# Hosseini (2026) Table 2 does NOT report fiber cross-section diameter or length.
# Must be confirmed or revised when fiber specifications are obtained from source.
FIBER_DIMS = {
    "l_mm": 13.0,
    "df_mm": 0.2,
    "tag": "ASSUMED",
    "note": "Standard UHPC straight steel fiber 0.2mm × 13mm. NOT reported in Hosseini 2026.",
}


def lambda_f(batch_id):
    """Fiber reinforcement index λf = vf × (l/df). Uses ASSUMED fiber dimensions."""
    b = BATCHES[batch_id]
    vf = b["vf_percent"] / 100.0
    return vf * FIBER_DIMS["l_mm"] / FIBER_DIMS["df_mm"]


def lambda_f_from_batch(b):
    """λf from batch dict directly (no batch_id needed)."""
    vf = b["vf_percent"] / 100.0
    return vf * FIBER_DIMS["l_mm"] / FIBER_DIMS["df_mm"]


def M_graybeal_descent(batch_id):
    """Post-peak slope M [MPa/strain] = 7061.5 × λf^(-0.411).
    Source: Fakeh (2025) Table 3, C1 post-peak (Eq. 9).
    Uses ASSUMED fiber dimensions → tag ADOPTED."""
    lf = lambda_f(batch_id)
    return 7061.5 * (lf ** (-0.411))


def M_graybeal_descent_from_batch(b):
    """M from batch dict directly."""
    lf = lambda_f_from_batch(b)
    return 7061.5 * (lf ** (-0.411))

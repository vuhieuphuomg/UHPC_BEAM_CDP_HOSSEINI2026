"""
Specimen configurations for all 12 UHPC T-beams (Hosseini 2026).

Geometry source: G0 audit (SPECIMEN_GEOMETRY_AUDITED_V5.csv, 2026-10-17).
Support/load positions: confirmed from Figure 1 visual read (G0 session).
Experiment targets: EXPERIMENT_TARGETS_REPORTED_V5.csv.

Coordinate system (all dimensions in mm):
  X: longitudinal, 0=West beam end, 5000=East beam end
  Y: vertical, 0=soffit (beam bottom), 500=top of flange
  Z: transverse, 0=centerline

Cross-section (constant for all 12 specimens):
  Web:    width=180mm (X±90mm), height=400mm (Y=0–400mm)
  Flange: width=400mm (X±200mm), thickness=100mm (Y=400–500mm)
  Total height = 500mm

Bottom bars (all specimens):
  6×Ø32.3mm MMFX Grade 4100 (M#10)
  Centroid Y = 90mm from soffit (d_effective = 500-90 = 410mm — REPORTED)
  Arrangement: 3 bundle positions (2 bars each) at Z = -54mm, 0mm, +54mm
  NEEDS_EXPERT_REVIEW: bar_cover NOT_REPORTED; exact bundle spacing assumed.

Top bars (all specimens):
  2×Ø9.5mm MMFX Grade 4100 (M#3) — confirmed from Figure 1 A-A (G0 audit)
  Centroid Y ≈ 460mm (cover 25mm assumed — NOT_REPORTED)
  NEEDS_EXPERT_REVIEW: bar_cover NOT_REPORTED.

Stirrup geometry (stirruped specimens):
  Closed rectangular loop in web: Y=[25,375]mm, Z=[-65,65]mm (cover 25mm assumed)
  NEEDS_EXPERT_REVIEW: stirrup cover NOT_REPORTED.
"""

# ── GEOMETRY (shared, all specimens) ─────────────────────────────────────────

BEAM_GEOMETRY = {
    "total_length_mm": 5000,
    "total_height_mm": 500,
    "web_width_mm": 180,
    "web_height_mm": 400,
    "flange_width_mm": 400,
    "flange_thickness_mm": 100,
    # Coordinate system: X=longitudinal, Y=vertical(0=soffit), Z=transverse(0=CL)
    "d_effective_mm": 410,          # REPORTED (from paper d=410mm)
    "bottom_bar_centroid_Y_mm": 90, # = total_height - d = 500 - 410; DERIVED
    "bar_cover_mm": "NOT_REPORTED",
}

BOTTOM_BAR = {
    "count": 6,
    "diameter_mm": 32.3,            # M#10 MMFX Grade 4100, REPORTED
    "area_mm2": 820.0,              # π/4 × 32.3² ≈ 820mm² per bar, DERIVED
    "centroid_Y_mm": 90,            # = 500 - d_eff = 90mm from soffit, DERIVED
    # 3 bundle positions (2 bars each); Z spacing NEEDS_EXPERT_REVIEW
    "bundle_Z_positions_mm": [-54.0, 0.0, 54.0],
    "bars_per_bundle": 2,
    "bundle_area_mm2": 1640.0,      # 2 × 820 per bundle, DERIVED
    "tag": "NEEDS_EXPERT_REVIEW: bar_cover NOT_REPORTED; bundle positions assumed",
}

TOP_BAR = {
    "count": 2,
    "diameter_mm": 9.5,             # M#3 MMFX Grade 4100, REPORTED from Figure 1 A-A
    "area_mm2": 70.9,               # π/4 × 9.5² ≈ 70.9mm² per bar, DERIVED
    "centroid_Y_mm": 462,           # 500 - 25(cover) - 9.5/2 ≈ 470; use 462 as midpoint
    "Z_positions_mm": [-45.0, 45.0],
    "tag": "NEEDS_EXPERT_REVIEW: bar_cover NOT_REPORTED; Z positions assumed",
}

# ── STIRRUP GEOMETRY (for stirruped specimens) ────────────────────────────────

STIRRUP_GEOMETRY = {
    "shape": "CLOSED_RECTANGLE",
    "Y_bottom_mm": 25,              # web Y start (cover assumed 25mm — NOT_REPORTED)
    "Y_top_mm": 375,                # web Y top (cover 25mm from Y=400)
    "Z_inner_mm": 65,               # half-width (90 - 25mm cover = 65mm)
    "tag": "NEEDS_EXPERT_REVIEW: stirrup cover NOT_REPORTED; positions assumed",
}

# ── SUPPORT / LOAD POSITIONS (from G0 audit Figure 1) ────────────────────────
# All positions are X coordinates (mm from West beam end).

SUPPORT_CONFIGS = {
    "NORMAL_AD27": {
        "support_west_X_mm": 300,
        "support_east_X_mm": 4700,
        "load_X_mm": 1407,
        "clear_span_mm": 4400,      # 4700 - 300
        "shear_span_mm": 1107,      # 1407 - 300 (near West support)
        "a_over_d": 2.7,
        "source": "Figure 1(a), G0 audit 2026-10-17",
    },
    "NORMAL_AD17": {
        "support_west_X_mm": 1613,
        "support_east_X_mm": 4700,
        "load_X_mm": 4003,
        "clear_span_mm": 3087,      # 4700 - 1613
        "shear_span_mm": 697,       # 4700 - 4003 (near East support)
        "a_over_d": 1.7,
        "source": "Figure 1(b), G0 audit 2026-10-17",
    },
    "B11_SPECIAL": {
        "support_west_X_mm": 1613,
        "support_east_X_mm": 4700,
        "load_X_mm": 3387,
        "clear_span_mm": 3087,      # 4700 - 1613
        "shear_span_mm": 1313,      # 4700 - 3387 (near East support)
        "a_over_d_eff": 3.20,       # 1313 / 410
        "source": "Figure 1(c), G0 audit 2026-10-17 (B11 special support)",
    },
}

# ── MATERIAL BATCH MAPPING ────────────────────────────────────────────────────
# batch_id → vf%, fc, Ec, ecp (from BATCHES in tools/cdp_builder/batch_data.py)

BATCH_PROPERTIES = {
    1: {"vf_percent": 2, "fc_mpa": 152.8, "Ec_mpa": 46000, "ecp": 0.0035},
    2: {"vf_percent": 2, "fc_mpa": 153.2, "Ec_mpa": 47300, "ecp": 0.0032},
    3: {"vf_percent": 1, "fc_mpa": 166.4, "Ec_mpa": 45400, "ecp": 0.0040},
}

# ── STIRRUP STEEL PROPERTIES ──────────────────────────────────────────────────
# NEEDS_EXPERT_REVIEW: NSS/HSS yield and ultimate strength from Hosseini 2026 Table 1
# Values below are ASSUMED / placeholder until source-confirmed.

STIRRUP_STEEL = {
    "NSS": {
        "fy_mpa": "NEEDS_EXPERT_REVIEW",
        "fu_mpa": "NEEDS_EXPERT_REVIEW",
        "Es_mpa": 200000,
        "note": "Normal-strength stirrup steel; fy/fu not confirmed from Hosseini Table 1",
    },
    "HSS": {
        "fy_mpa": "NEEDS_EXPERT_REVIEW",
        "fu_mpa": "NEEDS_EXPERT_REVIEW",
        "Es_mpa": 200000,
        "note": "High-strength stirrup steel; fy/fu not confirmed from Hosseini Table 1",
    },
}

# ── PER-SPECIMEN CONFIGS ──────────────────────────────────────────────────────

SPECIMENS = {
    "B01": {
        "batch_id": 3, "vf_percent": 1,
        "stirrup_type": "NONE", "stirrup_ratio_pct": 0.0,
        "a_over_d": 1.7, "support_config": "NORMAL_AD17",
        "vult_kN": 884, "failure_mode": "DC+SC",
        "m1_role": "HOLDOUT",   # M1 protocol: B01 is holdout, not used for tuning
    },
    "B02": {
        "batch_id": 3, "vf_percent": 1,
        "stirrup_type": "NONE", "stirrup_ratio_pct": 0.0,
        "a_over_d": 2.7, "support_config": "NORMAL_AD27",
        "vult_kN": 478, "failure_mode": "DT",
        "m1_role": "CALIBRATION",  # M1 protocol: B02 used for material law selection
        "priority": "FIRST_FE_MODEL",
    },
    "B03": {
        "batch_id": 2, "vf_percent": 2,
        "stirrup_type": "NONE", "stirrup_ratio_pct": 0.0,
        "a_over_d": 1.7, "support_config": "NORMAL_AD17",
        "vult_kN": 1241, "failure_mode": "DC+SC",
        "m1_role": "CALIBRATION",
    },
    "B04": {
        "batch_id": 2, "vf_percent": 2,
        "stirrup_type": "NONE", "stirrup_ratio_pct": 0.0,
        "a_over_d": 2.7, "support_config": "NORMAL_AD27",
        "vult_kN": 862, "failure_mode": "DT+DC+SC",
        "m1_role": "HOLDOUT",
    },
    "B05": {
        "batch_id": 3, "vf_percent": 1,
        "stirrup_type": "NSS", "stirrup_ratio_pct": 0.6,
        "a_over_d": 1.7, "support_config": "NORMAL_AD17",
        "vult_kN": 1358, "failure_mode": "DC+SC",
        "m1_role": "HOLDOUT",
    },
    "B06": {
        "batch_id": 3, "vf_percent": 1,
        "stirrup_type": "NSS", "stirrup_ratio_pct": 0.6,
        "a_over_d": 2.7, "support_config": "NORMAL_AD27",
        "vult_kN": 888, "failure_mode": "DT+DC+SC",
        "m1_role": "HOLDOUT",
    },
    "B07": {
        "batch_id": 1, "vf_percent": 2,
        "stirrup_type": "NSS", "stirrup_ratio_pct": 0.6,
        "a_over_d": 1.7, "support_config": "NORMAL_AD17",
        "vult_kN": 1534, "failure_mode": "DC+SC",
        "m1_role": "HOLDOUT",
    },
    "B08": {
        "batch_id": 1, "vf_percent": 2,
        "stirrup_type": "NSS", "stirrup_ratio_pct": 0.6,
        "a_over_d": 2.7, "support_config": "NORMAL_AD27",
        "vult_kN": 1092, "failure_mode": "DT+DC+SC",
        "m1_role": "CALIBRATION",
    },
    "B09": {
        "batch_id": 3, "vf_percent": 1,
        "stirrup_type": "HSS", "stirrup_ratio_pct": 0.7,
        "a_over_d": 1.7, "support_config": "NORMAL_AD17",
        "vult_kN": 1600, "failure_mode": "DC+SC",
        "m1_role": "HOLDOUT",
    },
    "B10": {
        "batch_id": 3, "vf_percent": 1,
        "stirrup_type": "HSS", "stirrup_ratio_pct": 0.7,
        "a_over_d": 2.7, "support_config": "NORMAL_AD27",
        "vult_kN": 1156, "failure_mode": "DC+FL",
        "m1_role": "HOLDOUT",
    },
    "B11": {
        "batch_id": 3, "vf_percent": 1,
        "stirrup_type": "HSS", "stirrup_ratio_pct": 0.4,
        "a_over_d": 2.7, "support_config": "B11_SPECIAL",
        # a_over_d_eff = 3.20 (from B11_SPECIAL config); nominal a/d=2.7 for stirrup calc
        "vult_kN": 1125, "failure_mode": "DC+FL",
        "m1_role": "HOLDOUT",
        "note": "B11: West support shifted to X=1613mm; a_eff=1313mm, a/d_eff=3.20",
    },
    "B12": {
        "batch_id": 3, "vf_percent": 1,
        "stirrup_type": "HSS", "stirrup_ratio_pct": 0.5,
        "a_over_d": 2.7, "support_config": "NORMAL_AD27",
        "vult_kN": 1134, "failure_mode": "DC+FL",
        "m1_role": "CALIBRATION",
    },
}

# M1 protocol: calibration specimens (use for material law selection only)
M1_CALIBRATION = [sid for sid, cfg in SPECIMENS.items() if cfg["m1_role"] == "CALIBRATION"]
M1_HOLDOUT = [sid for sid, cfg in SPECIMENS.items() if cfg["m1_role"] == "HOLDOUT"]


def get_support_config(specimen_id):
    """Return the SUPPORT_CONFIGS entry for a given specimen."""
    return SUPPORT_CONFIGS[SPECIMENS[specimen_id]["support_config"]]


def get_batch_props(specimen_id):
    """Return BATCH_PROPERTIES for the batch assigned to a specimen."""
    return BATCH_PROPERTIES[SPECIMENS[specimen_id]["batch_id"]]

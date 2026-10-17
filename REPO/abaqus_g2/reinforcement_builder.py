"""
reinforcement_builder.py — Longitudinal rebar and stirrup wires for Abaqus 2022 CAE.

NOT_TESTED_IN_ABAQUS: requires `abaqus cae noGUI script=...` to verify.

Rebar strategy: wire features (Abaqus truss/beam elements) embedded in concrete solid.
Constraint: Embedded Region (perfect bond — no bond-slip model at G2).

Bottom bars (all specimens):
  6×Ø32.3mm MMFX, centroid Y=90mm (d_eff=410mm — REPORTED).
  Arranged as 3 bundles × 2 bars at Z=-54, 0, +54mm.
  NEEDS_EXPERT_REVIEW: bar_cover NOT_REPORTED; Z positions assumed.

Top bars (all specimens):
  2×Ø9.5mm MMFX M#3, centroid Y=462mm.
  NEEDS_EXPERT_REVIEW: bar_cover NOT_REPORTED; Y position assumed.

Stirrups (B05–B12 only): closed rectangular loops in web.
  NEEDS_EXPERT_REVIEW: stirrup cover NOT_REPORTED.
"""

try:
    from abaqus import mdb
    from abaqusConstants import (
        THREE_D, DEFORMABLE_BODY, ON,
        WIRE, POINT_1_AND_2,
    )
    _IN_ABAQUS = True
except ImportError:
    _IN_ABAQUS = False

import math
from configs.specimen_configs import (
    BEAM_GEOMETRY, BOTTOM_BAR, TOP_BAR, STIRRUP_GEOMETRY, SPECIMENS, SUPPORT_CONFIGS
)


def _make_wire_name(specimen_id, bar_type, index):
    return "WIRE_{0}_{1}_{2}".format(specimen_id, bar_type, index)


def build_bottom_bars(model, part, specimen_id):
    """
    Create 3 wire features for bottom longitudinal bars (3 bundles × 2 bars each).
    Each wire runs full beam length along X from 0 to 5000mm.
    Wire cross-section area = 2 × single bar area = 1640mm² per bundle.

    Returns list of wire part names added.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("reinforcement_builder must run inside Abaqus CAE kernel")

    length = BEAM_GEOMETRY["total_length_mm"]
    y_ctr = BOTTOM_BAR["centroid_Y_mm"]           # 90mm from soffit
    z_positions = BOTTOM_BAR["bundle_Z_positions_mm"]   # [-54, 0, +54]

    wire_names = []
    for idx, z in enumerate(z_positions):
        name = _make_wire_name(specimen_id, "BOT", idx)
        # Wire from (X=0, Y=y_ctr, Z=z) to (X=length, Y=y_ctr, Z=z)
        part.WirePolyLine(
            points=((0.0, y_ctr, z), (length, y_ctr, z)),
            mergeType=WIRE,
            meshable=ON,
        )
        wire_names.append(name)
    return wire_names


def build_top_bars(model, part, specimen_id):
    """
    Create 2 wire features for top longitudinal bars.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("reinforcement_builder must run inside Abaqus CAE kernel")

    length = BEAM_GEOMETRY["total_length_mm"]
    y_ctr = TOP_BAR["centroid_Y_mm"]          # ~462mm from soffit
    z_positions = TOP_BAR["Z_positions_mm"]   # [-45, +45]

    wire_names = []
    for idx, z in enumerate(z_positions):
        name = _make_wire_name(specimen_id, "TOP", idx)
        part.WirePolyLine(
            points=((0.0, y_ctr, z), (length, y_ctr, z)),
            mergeType=WIRE,
            meshable=ON,
        )
        wire_names.append(name)
    return wire_names


def _stirrup_spacing_from_ratio(rho_pct, bar_dia_mm=9.5, web_width_mm=180):
    """
    Estimate stirrup spacing s from ratio ρ = 2×Asv / (b×s).
    Returns spacing in mm. DERIVED — not read from Figure 1 directly.
    """
    Asv = 2.0 * math.pi / 4.0 * bar_dia_mm ** 2  # both legs
    rho = rho_pct / 100.0
    if rho <= 0:
        return None
    return round(Asv / (rho * web_width_mm), 1)


def build_stirrups(model, part, specimen_id):
    """
    Create stirrup wire loops along beam length.
    Only for specimens with stirrup_type != NONE.

    Loop shape: closed rectangle in YZ plane.
    Y: [STIRRUP_GEOMETRY['Y_bottom_mm'], STIRRUP_GEOMETRY['Y_top_mm']]
    Z: ±STIRRUP_GEOMETRY['Z_inner_mm']
    Loop repeated at X positions from load zone toward supports.

    NEEDS_EXPERT_REVIEW: stirrup cover and exact X-positions NOT confirmed.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("reinforcement_builder must run inside Abaqus CAE kernel")

    spec = SPECIMENS[specimen_id]
    if spec["stirrup_type"] == "NONE":
        return []

    rho_pct = spec["stirrup_ratio_pct"]
    spacing_mm = _stirrup_spacing_from_ratio(rho_pct)
    if spacing_mm is None:
        return []

    sup_cfg = SUPPORT_CONFIGS[spec["support_config"]]
    x_west = sup_cfg["support_west_X_mm"]
    x_east = sup_cfg["support_east_X_mm"]
    x_load = sup_cfg["load_X_mm"]

    y_bot = STIRRUP_GEOMETRY["Y_bottom_mm"]
    y_top = STIRRUP_GEOMETRY["Y_top_mm"]
    z_half = STIRRUP_GEOMETRY["Z_inner_mm"]

    # Stirrups placed in shear spans only (between supports and load)
    wire_names = []
    for x_start, x_end in [(x_west, x_load), (x_load, x_east)]:
        x = x_start + spacing_mm
        idx = 0
        while x < x_end - spacing_mm / 2.0:
            name = _make_wire_name(specimen_id, "STR", idx)
            # Closed rectangular loop: 4 sides in YZ plane at X=x
            loop_pts = [
                (x, y_bot, -z_half),
                (x, y_top, -z_half),
                (x, y_top,  z_half),
                (x, y_bot,  z_half),
                (x, y_bot, -z_half),  # close
            ]
            for i in range(len(loop_pts) - 1):
                part.WirePolyLine(
                    points=(loop_pts[i], loop_pts[i + 1]),
                    mergeType=WIRE,
                    meshable=ON,
                )
            wire_names.append(name)
            x += spacing_mm
            idx += 1
    return wire_names


def assign_rebar_sections(model, specimen_id, rebar_material_name):
    """
    Assign truss sections to rebar wires.
    Bottom bundle area = 1640mm²; top bar area = 70.9mm².
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("reinforcement_builder must run inside Abaqus CAE kernel")

    # Bottom bar truss section
    model.TrussSection(
        name="SEC_REBAR_BOT_{0}".format(specimen_id),
        material=rebar_material_name,
        area=BOTTOM_BAR["bundle_area_mm2"],
    )
    # Top bar truss section
    model.TrussSection(
        name="SEC_REBAR_TOP_{0}".format(specimen_id),
        material=rebar_material_name,
        area=TOP_BAR["area_mm2"],
    )
    # Stirrup section (single leg area)
    model.TrussSection(
        name="SEC_REBAR_STR_{0}".format(specimen_id),
        material=rebar_material_name,
        area=math.pi / 4.0 * 9.5 ** 2,  # M#3 area
    )

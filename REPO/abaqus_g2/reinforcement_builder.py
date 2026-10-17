"""
reinforcement_builder.py — Longitudinal rebar and stirrup wire parts for Abaqus 2022 CAE.

NOT_TESTED_IN_ABAQUS: requires `abaqus cae noGUI script=...` to verify.

Rebar strategy: SEPARATE WIRE PARTS (not geometry on the concrete solid).
  - Each rebar group is a distinct DEFORMABLE_BODY 3D Part with wire geometry.
  - Wire parts are instanced in the assembly alongside the concrete instance.
  - EmbeddedRegion constraint ties rebar edges to concrete host cells.
  - Element type T3D2 (linear truss) assigned in mesh_builder.py.

Separate parts created:
  REBAR_BOT_{spec}  — 3 bundles (3×2 M#10 bars) at Y=90mm
  REBAR_TOP_{spec}  — 2 M#3 bars at Y≈462mm
  REBAR_STR_{spec}  — stirrup loops (specimens with stirrups only)

Bottom bars (all specimens):
  6×Ø32.3mm MMFX, 3 bundles × 2 bars, Y=90mm.
  Bundle area = 2 × π/4 × 32.3² = 1640mm².
  Z positions: [-54, 0, +54]mm.  NEEDS_EXPERT_REVIEW: cover NOT_REPORTED.

Top bars (all specimens):
  2×Ø9.5mm MMFX M#3, each area 70.9mm².
  Y≈462mm (assumed: 500 − 30mm cover − 9.5/2mm dia).  NEEDS_EXPERT_REVIEW.
  Z positions: [−45, +45]mm.  NEEDS_EXPERT_REVIEW.

Stirrups (B05–B12 only):
  Closed rectangular loops in YZ plane at regular X spacings.
  NEEDS_EXPERT_REVIEW: exact stirrup cover NOT_REPORTED.
"""

import math

try:
    from abaqus import mdb
    from abaqusConstants import THREE_D, DEFORMABLE_BODY, ON, WIRE
    _IN_ABAQUS = True
except ImportError:
    _IN_ABAQUS = False

from configs.specimen_configs import (
    BEAM_GEOMETRY, BOTTOM_BAR, TOP_BAR, STIRRUP_GEOMETRY, SPECIMENS, SUPPORT_CONFIGS
)


def build_bottom_bars(model, specimen_id):
    """
    Create a separate DEFORMABLE_BODY wire Part for bottom longitudinal bars.
    3 WirePolyLine wires at Z=[-54, 0, +54]mm, Y=90mm, spanning X=[0, 5000].

    Returns the Part object.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("reinforcement_builder must run inside Abaqus CAE kernel")

    part_name = "REBAR_BOT_{0}".format(specimen_id)
    part = model.Part(name=part_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)

    length = BEAM_GEOMETRY["total_length_mm"]   # 5000
    y_ctr = BOTTOM_BAR["centroid_Y_mm"]         # 90mm from soffit
    z_positions = BOTTOM_BAR["bundle_Z_positions_mm"]   # [-54, 0, +54]

    for z in z_positions:
        part.WirePolyLine(
            points=((0.0, y_ctr, z), (length, y_ctr, z)),
            mergeType=WIRE,
            meshable=ON,
        )

    return part


def build_top_bars(model, specimen_id):
    """
    Create a separate DEFORMABLE_BODY wire Part for top longitudinal bars.
    2 WirePolyLine wires at Z=[-45, +45]mm, Y≈462mm, spanning X=[0, 5000].

    Returns the Part object.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("reinforcement_builder must run inside Abaqus CAE kernel")

    part_name = "REBAR_TOP_{0}".format(specimen_id)
    part = model.Part(name=part_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)

    length = BEAM_GEOMETRY["total_length_mm"]
    y_ctr = TOP_BAR["centroid_Y_mm"]        # ~462mm from soffit
    z_positions = TOP_BAR["Z_positions_mm"] # [-45, +45]

    for z in z_positions:
        part.WirePolyLine(
            points=((0.0, y_ctr, z), (length, y_ctr, z)),
            mergeType=WIRE,
            meshable=ON,
        )

    return part


def _stirrup_spacing_from_ratio(rho_pct, bar_dia_mm=9.5, web_width_mm=180):
    """
    Estimate stirrup spacing from volumetric ratio ρ = 2×Asv / (b×s).
    Returns spacing in mm.
    """
    Asv = 2.0 * math.pi / 4.0 * bar_dia_mm ** 2
    rho = rho_pct / 100.0
    if rho <= 0:
        return None
    return round(Asv / (rho * web_width_mm), 1)


def build_stirrups(model, specimen_id):
    """
    Create a separate DEFORMABLE_BODY wire Part for stirrups.
    Returns the Part object, or None if specimen has no stirrups.

    Stirrups are closed rectangular loops in YZ planes at regular X spacings
    in both shear spans.  NEEDS_EXPERT_REVIEW: stirrup cover NOT_REPORTED.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("reinforcement_builder must run inside Abaqus CAE kernel")

    spec = SPECIMENS[specimen_id]
    if spec["stirrup_type"] == "NONE":
        return None

    rho_pct = spec["stirrup_ratio_pct"]
    spacing_mm = _stirrup_spacing_from_ratio(rho_pct)
    if spacing_mm is None:
        return None

    sup_cfg = SUPPORT_CONFIGS[spec["support_config"]]
    x_west = sup_cfg["support_west_X_mm"]
    x_east = sup_cfg["support_east_X_mm"]
    x_load = sup_cfg["load_X_mm"]

    y_bot = STIRRUP_GEOMETRY["Y_bottom_mm"]
    y_top_s = STIRRUP_GEOMETRY["Y_top_mm"]
    z_half = STIRRUP_GEOMETRY["Z_inner_mm"]

    part_name = "REBAR_STR_{0}".format(specimen_id)
    part = model.Part(name=part_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)

    for x_start, x_end in [(x_west, x_load), (x_load, x_east)]:
        x = x_start + spacing_mm
        while x < x_end - spacing_mm / 2.0:
            # 4 sides of closed rectangular loop at this X
            loop_pts = [
                (x, y_bot, -z_half),
                (x, y_top_s, -z_half),
                (x, y_top_s,  z_half),
                (x, y_bot,  z_half),
                (x, y_bot, -z_half),
            ]
            for i in range(len(loop_pts) - 1):
                part.WirePolyLine(
                    points=(loop_pts[i], loop_pts[i + 1]),
                    mergeType=WIRE,
                    meshable=ON,
                )
            x += spacing_mm

    return part


def get_all_rebar_parts(model, specimen_id):
    """
    Return list of all rebar Part objects for this specimen
    (excludes None for stirrup-less specimens).
    Callers should instance these in the assembly.
    """
    parts = []
    for key in model.parts.keys():
        if key.startswith("REBAR_") and key.endswith("_{0}".format(specimen_id)):
            parts.append((key, model.parts[key]))
    return parts

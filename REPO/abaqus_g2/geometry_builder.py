"""
geometry_builder.py — T-beam solid part creation for Abaqus 2022 CAE.

NOT_TESTED_IN_ABAQUS: requires `abaqus cae noGUI script=...` to verify.
Source geometry: G0 audit (SPECIMEN_GEOMETRY_AUDITED_V5.csv, 2026-10-17).

Coordinate system:
  X: longitudinal (0=West end, 5000=East end)
  Y: vertical     (0=soffit, 500=top of flange)
  Z: transverse   (0=centerline; web ±90mm; flange ±200mm)

T-section in YZ plane, extruded along X:
  Web:    Z=[-90,+90], Y=[0,400]
  Flange: Z=[-200,+200], Y=[400,500]
"""

# abaqus cae noGUI imports — only available inside Abaqus kernel
try:
    from abaqus import mdb
    from abaqusConstants import (
        THREE_D, DEFORMABLE_BODY, ON, COUNTERCLOCKWISE
    )
    _IN_ABAQUS = True
except ImportError:
    _IN_ABAQUS = False

from configs.specimen_configs import BEAM_GEOMETRY

# T-section sketch vertices (YZ plane, counterclockwise)
# Y=height axis (vertical), Z=transverse axis
_T_SECTION_VERTICES = [
    (-90.0,   0.0),   # bottom-left web corner  (Z, Y)
    ( 90.0,   0.0),   # bottom-right web corner
    ( 90.0, 400.0),   # top-right web / flange junction
    (200.0, 400.0),   # flange right start
    (200.0, 500.0),   # flange right top
    (-200.0, 500.0),  # flange left top
    (-200.0, 400.0),  # flange left start
    (-90.0, 400.0),   # top-left web / flange junction
    (-90.0,   0.0),   # close back to start
]


def build_t_section_sketch(model, sheet_size=1200.0):
    """
    Create the T-section ConstrainedSketch in the YZ plane.
    Returns the sketch object.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("geometry_builder must run inside Abaqus CAE kernel")

    sketch = model.ConstrainedSketch(
        name="T_section_YZ",
        sheetSize=sheet_size,
    )
    verts = _T_SECTION_VERTICES
    for i in range(len(verts) - 1):
        z0, y0 = verts[i]
        z1, y1 = verts[i + 1]
        sketch.Line(point1=(z0, y0), point2=(z1, y1))
    return sketch


def build_beam_part(model, part_name="UHPC_T_Beam"):
    """
    Create the solid T-beam part: T-section extruded 5000mm along X.

    Abaqus BaseSolidExtrude extrudes in the direction normal to the sketch plane.
    Sketch is in the YZ plane (X=0); extrusion depth = 5000mm → part spans X=0..5000.

    Returns the Part object.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("geometry_builder must run inside Abaqus CAE kernel")

    length = BEAM_GEOMETRY["total_length_mm"]

    part = model.Part(
        name=part_name,
        dimensionality=THREE_D,
        type=DEFORMABLE_BODY,
    )
    sketch = build_t_section_sketch(model)
    part.BaseSolidExtrude(sketch=sketch, depth=length)
    return part


def get_section_sets(part):
    """
    Create named geometry sets on the beam part for BCs/loads/mesh.
    Returns dict of {set_name: set_object}.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("geometry_builder must run inside Abaqus CAE kernel")

    sets = {}

    # Top face (Y=500, load application surface / top of flange)
    # Face at Y=500 — use findAt with a point on that face
    top_face = part.faces.findAt(((0.0, 500.0, 2500.0),))
    part.Set(name="SET_TOP_FACE", faces=top_face)
    sets["SET_TOP_FACE"] = top_face

    # Bottom face (Y=0, soffit of web)
    bot_face = part.faces.findAt(((0.0, 0.0, 2500.0),))
    part.Set(name="SET_BOTTOM_FACE", faces=bot_face)
    sets["SET_BOTTOM_FACE"] = bot_face

    # West end face (X=0)
    west_face = part.faces.findAt(((0.0, 250.0, 0.0),))
    part.Set(name="SET_WEST_FACE", faces=west_face)
    sets["SET_WEST_FACE"] = west_face

    # East end face (X=5000)
    east_face = part.faces.findAt(((0.0, 250.0, 5000.0),))
    part.Set(name="SET_EAST_FACE", faces=east_face)
    sets["SET_EAST_FACE"] = east_face

    return sets

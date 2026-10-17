"""
geometry_builder.py — T-beam solid part for Abaqus 2022 CAE.

Source: G0 audit (SPECIMEN_GEOMETRY_AUDITED_V5.csv, 2026-10-17).

Coordinate system (canonical, all scripts must use this):
  X: longitudinal (0=West end, 5000=East end)
  Y: vertical     (0=soffit, 500=top of flange)
  Z: transverse   (0=centerline; web ±90mm; flange ±200mm)

Implementation:
  Cross-section sketched in the YZ plane (X=0), extruded 5000mm along +X.
  Sketch local axes: axis1 = Z (transverse), axis2 = Y (vertical).

Bounding box after build: X=[0,5000], Y=[0,500], Z=[-200,+200].
"""

try:
    from abaqus import mdb
    from abaqusConstants import (
        THREE_D, DEFORMABLE_BODY, ON, SIDE1,
        YZPLANE, YAXIS, COPLANAR_EDGES,
    )
    _IN_ABAQUS = True
except ImportError:
    _IN_ABAQUS = False

from configs.specimen_configs import BEAM_GEOMETRY

# T-section outline in YZ plane: (Z, Y) pairs, counterclockwise.
# Web:    Z=[-90,+90], Y=[0,400]
# Flange: Z=[-200,+200], Y=[400,500]
_T_VERTS = [
    (-90.0,   0.0),
    ( 90.0,   0.0),
    ( 90.0, 400.0),
    (200.0, 400.0),
    (200.0, 500.0),
    (-200.0, 500.0),
    (-200.0, 400.0),
    (-90.0, 400.0),
    (-90.0,   0.0),   # close
]


def build_beam_part(model, part_name="UHPC_T_Beam"):
    """
    Create 3D solid T-beam part.  X=longitudinal (extruded), Y=vertical, Z=transverse.

    1. Create datum plane YZPLANE at X=0 (normal = +X).
    2. Create datum axis YAXIS for sketch "up" direction.
    3. Sketch T cross-section in YZ plane (local axis1=Z, axis2=Y).
    4. BaseSolidExtrude depth=5000mm along +X.

    Returns Part object.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("geometry_builder must run inside Abaqus CAE kernel")

    length = BEAM_GEOMETRY["total_length_mm"]   # 5000

    part = model.Part(name=part_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)

    # Datum plane perpendicular to X at X=0  (= YZ plane)
    dp_feat = part.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=0.0)
    # Datum axis along Y (sketch "up")
    da_feat = part.DatumAxisByPrincipalAxis(axis=YAXIS)

    # Transform puts the sketch in the YZ plane with Y pointing up
    t = part.MakeSketchTransform(
        sketchPlane=part.datums[dp_feat.id],
        sketchUpEdge=part.datums[da_feat.id],
        sketchPlaneSide=SIDE1,
        origin=(0.0, 0.0, 0.0),
    )

    sk = model.ConstrainedSketch(name="T_section", sheetSize=1200.0, transform=t)
    part.projectReferencesOntoSketch(sketch=sk, filter=COPLANAR_EDGES)

    # Draw T profile; sketch axis1=Z (transverse), axis2=Y (vertical)
    for i in range(len(_T_VERTS) - 1):
        sk.Line(point1=_T_VERTS[i], point2=_T_VERTS[i + 1])

    # Extrude along +X: result spans X=[0, 5000]
    part.BaseSolidExtrude(sketch=sk, depth=length)
    return part


def create_geometry_sets(part):
    """
    Create named Sets on the beam part.  All findAt coords use (X, Y, Z).

    After build_beam_part():
      Top flange face:  Y=500,  X=2500 (mid), Z=0
      Soffit (web):     Y=0,    X=2500,        Z=0
      West end face:    X=0,    Y=250,          Z=0
      East end face:    X=5000, Y=250,          Z=0
    """
    if not _IN_ABAQUS:
        raise RuntimeError("geometry_builder must run inside Abaqus CAE kernel")

    sets = {}

    # Top of flange (Y=500, Z=0, X=mid)
    f = part.faces.findAt(((2500.0, 500.0, 0.0),))
    part.Set(name="FACE_TOP", faces=f)
    sets["FACE_TOP"] = f

    # Soffit of web (Y=0, Z=0, X=mid)
    f = part.faces.findAt(((2500.0, 0.0, 0.0),))
    part.Set(name="FACE_SOFFIT", faces=f)
    sets["FACE_SOFFIT"] = f

    # West end (X=0, Y=250, Z=0 — web mid-height)
    f = part.faces.findAt(((0.0, 200.0, 0.0),))
    part.Set(name="FACE_WEST", faces=f)
    sets["FACE_WEST"] = f

    # East end (X=5000)
    f = part.faces.findAt(((5000.0, 200.0, 0.0),))
    part.Set(name="FACE_EAST", faces=f)
    sets["FACE_EAST"] = f

    # All cells (for section assignment)
    part.Set(name="ALL_CELLS", cells=part.cells)

    return sets

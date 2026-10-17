"""
support_loading_builder.py — Boundary conditions and loads for Abaqus 2022 CAE.

NOT_TESTED_IN_ABAQUS: requires `abaqus cae noGUI script=...` to verify.

Load scheme: displacement-controlled monotonic push-down at load point.

Coordinate system (X=longitudinal, Y=vertical, Z=transverse):
  Support West (pin):  bottom face (Y=0) at X = x_west, Z in [-90, +90]
  Support East (roller): bottom face (Y=0) at X = x_east, Z in [-90, +90]
  Load (push-down):    top flange face (Y=500) at X = x_load, Z in [-200, +200]

Partition strategy (NO node selection before mesh — illegal in CAE scripts):
  1. partition_beam_for_bc() cuts the beam Part at ±150mm of each BC position.
  2. After partitioning, each BC zone has a distinct face in the geometry.
  3. build_supports() and build_load() use inst.faces.findAt() to locate those faces.
  4. BCs are applied to face-based geometry sets — valid pre-mesh.

Support plate / load plate half-width: 150mm (300mm plate, from Figure 1 G0 audit).
"""

try:
    from abaqus import mdb
    from abaqusConstants import (
        STEP, UNSET, SET, ON, OFF,
        DISPLACEMENT,
        YZPLANE,
    )
    _IN_ABAQUS = True
except ImportError:
    _IN_ABAQUS = False

from configs.specimen_configs import SPECIMENS, SUPPORT_CONFIGS, BEAM_GEOMETRY

_PLATE_HALF_WIDTH = 150.0   # mm — half of 300mm plate width (Figure 1)


def partition_beam_for_bc(part, specimen_id):
    """
    Partition the beam Part at ±150mm of each support/load X position.
    Creates datum planes (YZPLANE type, perpendicular to X) and applies
    PartitionCellByDatumPlane.

    MUST be called BEFORE instancing the part in the assembly.
    Modifies the Part in-place.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("support_loading_builder must run inside Abaqus CAE kernel")

    spec = SPECIMENS[specimen_id]
    sup_cfg = SUPPORT_CONFIGS[spec["support_config"]]
    x_west = sup_cfg["support_west_X_mm"]
    x_east = sup_cfg["support_east_X_mm"]
    x_load = sup_cfg["load_X_mm"]
    total_length = BEAM_GEOMETRY["total_length_mm"]

    cut_positions = sorted(set([
        x_west - _PLATE_HALF_WIDTH,
        x_west + _PLATE_HALF_WIDTH,
        x_load - _PLATE_HALF_WIDTH,
        x_load + _PLATE_HALF_WIDTH,
        x_east - _PLATE_HALF_WIDTH,
        x_east + _PLATE_HALF_WIDTH,
    ]))

    for x_cut in cut_positions:
        if 0.0 < x_cut < total_length:
            dp_feat = part.DatumPlaneByPrincipalPlane(
                principalPlane=YZPLANE, offset=x_cut
            )
            part.PartitionCellByDatumPlane(
                datumPlane=part.datums[dp_feat.id],
                cells=part.cells,
            )


def build_step(model, step_name="PUSH_DOWN", initial_inc=0.001, max_inc=0.05):
    """
    Create Static, General step for displacement-controlled push-down.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("support_loading_builder must run inside Abaqus CAE kernel")

    model.StaticStep(
        name=step_name,
        previous="Initial",
        timePeriod=1.0,
        initialInc=initial_inc,
        minInc=1e-6,
        maxInc=max_inc,
        maxNumInc=10000,
        nlgeom=ON,
    )
    return step_name


def build_supports(model, assembly, instance_name, specimen_id):
    """
    Apply pin (West) and roller (East) supports using face-based geometry regions.
    Requires partition_beam_for_bc() to have been called first on the Part.

    West pin:  UX=UY=UZ=0 on bottom face (Y=0) at X=x_west center.
    East roller: UY=0 on bottom face (Y=0) at X=x_east center.

    Face findAt uses center of the partitioned face: (x_center, 0.0, 0.0).
    Z=0 is within the web (web spans Z=[-90,+90]).
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("support_loading_builder must run inside Abaqus CAE kernel")

    spec = SPECIMENS[specimen_id]
    sup_cfg = SUPPORT_CONFIGS[spec["support_config"]]
    x_west = sup_cfg["support_west_X_mm"]
    x_east = sup_cfg["support_east_X_mm"]

    inst = assembly.instances[instance_name]

    # West pin: bottom face (Y=0) at X=x_west (partitioned zone center)
    west_face = inst.faces.findAt(((x_west, 0.0, 0.0),))
    west_set = assembly.Set(
        name="SET_SUPP_WEST_{0}".format(specimen_id),
        faces=west_face,
    )
    model.DisplacementBC(
        name="BC_SUPP_WEST_{0}".format(specimen_id),
        createStepName="Initial",
        region=assembly.sets["SET_SUPP_WEST_{0}".format(specimen_id)],
        u1=SET, u2=SET, u3=SET,
        ur1=UNSET, ur2=UNSET, ur3=UNSET,
    )

    # East roller: bottom face (Y=0) at X=x_east
    east_face = inst.faces.findAt(((x_east, 0.0, 0.0),))
    east_set = assembly.Set(
        name="SET_SUPP_EAST_{0}".format(specimen_id),
        faces=east_face,
    )
    model.DisplacementBC(
        name="BC_SUPP_EAST_{0}".format(specimen_id),
        createStepName="Initial",
        region=assembly.sets["SET_SUPP_EAST_{0}".format(specimen_id)],
        u1=UNSET, u2=SET, u3=UNSET,
        ur1=UNSET, ur2=UNSET, ur3=UNSET,
    )


def build_load(model, assembly, instance_name, specimen_id, step_name,
               target_displacement_mm=-50.0):
    """
    Apply displacement-controlled push-down on top flange face at load point.
    target_displacement_mm: total U2 applied (negative = downward).
    Requires partition_beam_for_bc() to have been called first on the Part.

    Load face findAt: (x_load, 500.0, 0.0) — top flange at load plate center.
    Z=0 is within the flange (flange spans Z=[-200,+200]).
    Returns set name for history output reference.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("support_loading_builder must run inside Abaqus CAE kernel")

    spec = SPECIMENS[specimen_id]
    sup_cfg = SUPPORT_CONFIGS[spec["support_config"]]
    x_load = sup_cfg["load_X_mm"]
    y_top = BEAM_GEOMETRY["total_height_mm"]   # 500mm

    inst = assembly.instances[instance_name]

    # Top flange face (Y=500) at X=x_load center
    load_face = inst.faces.findAt(((x_load, y_top, 0.0),))
    load_set_name = "SET_LOAD_{0}".format(specimen_id)
    assembly.Set(name=load_set_name, faces=load_face)
    model.DisplacementBC(
        name="BC_LOAD_{0}".format(specimen_id),
        createStepName=step_name,
        region=assembly.sets[load_set_name],
        u1=UNSET,
        u2=target_displacement_mm,
        u3=UNSET,
        ur1=UNSET, ur2=UNSET, ur3=UNSET,
    )
    return load_set_name

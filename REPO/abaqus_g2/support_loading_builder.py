"""
support_loading_builder.py — Boundary conditions and loads for Abaqus 2022 CAE.

NOT_TESTED_IN_ABAQUS: requires `abaqus cae noGUI script=...` to verify.

Load scheme: displacement-controlled monotonic push-down at load point.
  Rationale: force-control diverges near peak for brittle shear failure.
  Loading applied to a rigid loading plate region at top of beam (Y=500mm).

Supports: line/surface supports at West and East support positions.
  West support: pin (UX=UY=UZ=0 at bottom face, X=support_west_X).
               One node/line constrained in X to prevent rigid body motion.
  East support: roller (UY=0 only at bottom face, X=support_east_X).

Note: exact support plate width (300mm from Figure 1) applied as a region.
Support plate width: 300mm (from Figure 1, G0 audit).
Load plate width: 300mm (same).
"""

try:
    from abaqus import mdb
    from abaqusConstants import (
        STEP, UNSET, SET, ON, OFF,
        FIXED, DISPLACEMENT, PINNED, ENCASTRE,
        CONNECTOR, STRESS, FORCE, DISPLACEMENT,
        XSYMM, YSYMM, ZSYMM,
    )
    _IN_ABAQUS = True
except ImportError:
    _IN_ABAQUS = False

from configs.specimen_configs import SPECIMENS, SUPPORT_CONFIGS, BEAM_GEOMETRY

# Support and load plate half-width (mm) — from Figure 1
_PLATE_HALF_WIDTH = 150.0   # 300mm plate → ±150mm along X


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
        nlgeom=ON,          # geometric nonlinearity (large displacement)
    )
    return step_name


def _get_support_region(assembly, instance_name, x_center, y_bottom=0.0):
    """Return a face region on the beam bottom face at support X position."""
    inst = assembly.instances[instance_name]
    x_lo = x_center - _PLATE_HALF_WIDTH
    x_hi = x_center + _PLATE_HALF_WIDTH
    # findAt midpoint on bottom face in support zone
    x_mid = x_center
    face = inst.faces.findAt(((x_mid, y_bottom, 0.0),))
    return assembly.Surface(side1Faces=face,
                            name="SURF_SUPP_X{0:.0f}".format(x_center))


def _get_load_region(assembly, instance_name, x_load, y_top=500.0):
    """Return top face surface at load point."""
    inst = assembly.instances[instance_name]
    face = inst.faces.findAt(((x_load, y_top, 0.0),))
    return assembly.Surface(side1Faces=face,
                            name="SURF_LOAD_X{0:.0f}".format(x_load))


def build_supports(model, assembly, instance_name, specimen_id, step_name):
    """
    Apply pin (West) and roller (East) supports.
    Both applied to bottom face regions at support X positions.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("support_loading_builder must run inside Abaqus CAE kernel")

    spec = SPECIMENS[specimen_id]
    sup_cfg = SUPPORT_CONFIGS[spec["support_config"]]
    x_west = sup_cfg["support_west_X_mm"]
    x_east = sup_cfg["support_east_X_mm"]

    inst = assembly.instances[instance_name]

    # West pin support: UX=UY=UZ=0 at bottom face, X in [x_west ± half_plate]
    # Use node set on bottom face at west support location
    west_nodes = inst.nodes.getByBoundingBox(
        xMin=x_west - _PLATE_HALF_WIDTH, xMax=x_west + _PLATE_HALF_WIDTH,
        yMin=-1.0, yMax=1.0,
        zMin=-201.0, zMax=201.0,
    )
    assembly.Set(name="SET_SUPP_WEST_{0}".format(specimen_id), nodes=west_nodes)
    model.DisplacementBC(
        name="BC_SUPP_WEST_{0}".format(specimen_id),
        createStepName="Initial",
        region=assembly.sets["SET_SUPP_WEST_{0}".format(specimen_id)],
        u1=SET, u2=SET, u3=SET,   # pin: all translations fixed
        ur1=UNSET, ur2=UNSET, ur3=UNSET,
    )

    # East roller support: UY=0 only
    east_nodes = inst.nodes.getByBoundingBox(
        xMin=x_east - _PLATE_HALF_WIDTH, xMax=x_east + _PLATE_HALF_WIDTH,
        yMin=-1.0, yMax=1.0,
        zMin=-201.0, zMax=201.0,
    )
    assembly.Set(name="SET_SUPP_EAST_{0}".format(specimen_id), nodes=east_nodes)
    model.DisplacementBC(
        name="BC_SUPP_EAST_{0}".format(specimen_id),
        createStepName="Initial",
        region=assembly.sets["SET_SUPP_EAST_{0}".format(specimen_id)],
        u1=UNSET, u2=SET, u3=UNSET,  # roller: UY only
        ur1=UNSET, ur2=UNSET, ur3=UNSET,
    )


def build_load(model, assembly, instance_name, specimen_id, step_name,
               target_displacement_mm=-50.0):
    """
    Apply displacement-controlled push-down at load point (negative UY).
    target_displacement_mm: total displacement applied (negative = downward).
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("support_loading_builder must run inside Abaqus CAE kernel")

    spec = SPECIMENS[specimen_id]
    sup_cfg = SUPPORT_CONFIGS[spec["support_config"]]
    x_load = sup_cfg["load_X_mm"]
    y_top = BEAM_GEOMETRY["total_height_mm"]

    inst = assembly.instances[instance_name]

    # Nodes on top face at load plate region
    load_nodes = inst.nodes.getByBoundingBox(
        xMin=x_load - _PLATE_HALF_WIDTH, xMax=x_load + _PLATE_HALF_WIDTH,
        yMin=y_top - 1.0, yMax=y_top + 1.0,
        zMin=-201.0, zMax=201.0,
    )
    assembly.Set(name="SET_LOAD_{0}".format(specimen_id), nodes=load_nodes)
    model.DisplacementBC(
        name="BC_LOAD_{0}".format(specimen_id),
        createStepName=step_name,
        region=assembly.sets["SET_LOAD_{0}".format(specimen_id)],
        u1=UNSET,
        u2=target_displacement_mm,  # downward
        u3=UNSET,
        ur1=UNSET, ur2=UNSET, ur3=UNSET,
    )


def build_symmetry_bc(model, assembly, instance_name, specimen_id):
    """
    Apply Z-symmetry if modeling half-beam (Z=0 plane).
    Only use if beam modeled as half-width.
    NOT currently applied — full beam modeled.
    NOT_TESTED_IN_ABAQUS.
    """
    pass  # Reserved for half-model optimization

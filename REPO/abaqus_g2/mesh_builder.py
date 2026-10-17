"""
mesh_builder.py — Mesh configuration for UHPC T-beam in Abaqus 2022 CAE.

NOT_TESTED_IN_ABAQUS: requires `abaqus cae noGUI script=...` to verify.

Element type: C3D8R (8-node reduced-integration brick) for concrete solid.
  Hourglass control: enhanced (reduces spurious modes with C3D8R).
T2/T (truss) for rebar wires — T3D2 (2-node linear truss).

Mesh size: 25mm global seed for initial model (coarse).
  Rationale: B02 beam 5000×500mm, web 180mm wide — 25mm gives ~3 elements
  across web width. Mesh sensitivity study required after G1 material finalized.
  lc_mm ≈ 25mm should be used in T2 generate_sigma_w_table(lc_mm) for this mesh.

Refinement zone: load and support regions — 15mm seed.
  X range: [support_west - 200, load + 200] and [load - 200, support_east + 200].

NEEDS_EXPERT_REVIEW: final mesh size must be confirmed by engineer after mesh
sensitivity study. lc_mm in T2 sigma-w must match final mesh size.
"""

try:
    from abaqus import mdb
    from abaqusConstants import (
        C3D8R, T3D2, HEX, ENHANCED,
        STRUCTURED, SWEEP, FREE,
        ON, OFF, STANDARD,
    )
    from mesh import ElemType
    _IN_ABAQUS = True
except ImportError:
    _IN_ABAQUS = False

# Global mesh characteristic length for initial model
LC_GLOBAL_MM = 25.0     # NEEDS_EXPERT_REVIEW — used in lc_mm for T2 sigma-w
LC_REFINED_MM = 15.0    # near supports and load point


def seed_and_mesh(model, part, global_seed=LC_GLOBAL_MM):
    """
    Apply global seed and mesh the beam part.
    Element type: C3D8R with enhanced hourglass control.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("mesh_builder must run inside Abaqus CAE kernel")

    part.seedPart(size=global_seed, deviationFactor=0.1, minSizeFactor=0.1)

    # Set element type: C3D8R (solid) with enhanced hourglass
    elem_type = ElemType(
        elemCode=C3D8R,
        elemLibrary=STANDARD,
        secondOrderAccuracy=OFF,
        hourglassControl=ENHANCED,
        distortionControl=ON,
    )
    all_cells = part.Set(name="SET_ALL_CELLS", cells=part.cells)
    part.setElementType(regions=all_cells, elemTypes=(elem_type,))

    part.generateMesh()
    return LC_GLOBAL_MM


def seed_rebar_wires(part, seed_size=LC_GLOBAL_MM):
    """
    Seed wire features (rebar lines) for meshing as T3D2 truss elements.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("mesh_builder must run inside Abaqus CAE kernel")

    truss_type = ElemType(elemCode=T3D2, elemLibrary=STANDARD)
    wire_edges = part.edges  # all wire-type edges
    part.setElementType(regions=part.Set(name="SET_WIRES", edges=wire_edges),
                        elemTypes=(truss_type,))
    part.seedEdgeBySize(edges=wire_edges, size=seed_size, deviationFactor=0.1)


def refine_near_supports_and_load(part, x_west, x_load, x_east,
                                  refined_seed=LC_REFINED_MM, margin_mm=200.0):
    """
    Apply finer seed in shear span region (between supports and load point).
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("mesh_builder must run inside Abaqus CAE kernel")

    # Collect edges in refined zones
    edges_to_refine = []
    for edge in part.edges:
        pts = edge.pointOn
        for pt in pts:
            x = pt[0]   # X coordinate (longitudinal)
            in_west_shear = (x_west - margin_mm) <= x <= (x_load + margin_mm)
            in_east_shear = (x_load - margin_mm) <= x <= (x_east + margin_mm)
            if in_west_shear or in_east_shear:
                edges_to_refine.append(edge)
                break

    if edges_to_refine:
        part.seedEdgeBySize(
            edges=edges_to_refine,
            size=refined_seed,
            deviationFactor=0.1,
        )

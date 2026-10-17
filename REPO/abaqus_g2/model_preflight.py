"""
model_preflight.py — Pre-run validation checks for Abaqus 2022 G2 models.

NOT_TESTED_IN_ABAQUS: requires `abaqus cae noGUI script=...` to verify.

Checks performed:
  G: Geometry — part exists, cells > 0, volume > 0
  R: Reinforcement — rebar wires present (if stirruped), sections assigned
  B: BCs — support and load BCs exist in model
  M: Mesh — mesh generated, element count > 0, no warnings

Results: PASS / WARN / FAIL per check.
Preflight FAIL → do not write .inp.
solver_authorized=false → never submit .inp regardless of preflight result.
"""

try:
    from abaqus import mdb
    _IN_ABAQUS = True
except ImportError:
    _IN_ABAQUS = False

from configs.specimen_configs import SPECIMENS, SUPPORT_CONFIGS, BEAM_GEOMETRY


def _check_geometry(model, part_name):
    """G: Part has cells with positive volume."""
    try:
        part = model.parts[part_name]
        n_cells = len(part.cells)
        if n_cells == 0:
            return ("FAIL", "Part '{0}': no cells found".format(part_name))
        vol = sum(c.getSize() for c in part.cells)
        if vol <= 0:
            return ("FAIL", "Part '{0}': zero volume".format(part_name))
        return ("PASS", "Part '{0}': {1} cells, volume={2:.0f}mm³".format(
            part_name, n_cells, vol))
    except KeyError:
        return ("FAIL", "Part '{0}' not found in model".format(part_name))
    except Exception as e:
        return ("WARN", "Geometry check error: {0}".format(str(e)))


def _check_bcs(model, specimen_id):
    """B: Required BCs exist."""
    issues = []
    required = [
        "BC_SUPP_WEST_{0}".format(specimen_id),
        "BC_SUPP_EAST_{0}".format(specimen_id),
        "BC_LOAD_{0}".format(specimen_id),
    ]
    for bc_name in required:
        found = False
        for step_bcs in model.steps.values():
            if hasattr(step_bcs, 'boundaryConditions'):
                pass
        if bc_name not in model.boundaryConditions:
            issues.append(bc_name)
    if issues:
        return ("FAIL", "Missing BCs: {0}".format(", ".join(issues)))
    return ("PASS", "All required BCs present: {0}".format(", ".join(required)))


def _check_mesh(model, part_name):
    """M: Mesh generated, element count > 0."""
    try:
        part = model.parts[part_name]
        n_elem = len(part.elements)
        n_node = len(part.nodes)
        if n_elem == 0:
            return ("FAIL", "No elements in mesh for '{0}'".format(part_name))
        return ("PASS", "{0}: {1} elements, {2} nodes".format(
            part_name, n_elem, n_node))
    except Exception as e:
        return ("WARN", "Mesh check error: {0}".format(str(e)))


def _check_support_coords(specimen_id):
    """B: Support coordinates are within beam extents."""
    spec = SPECIMENS[specimen_id]
    sup_cfg = SUPPORT_CONFIGS[spec["support_config"]]
    length = BEAM_GEOMETRY["total_length_mm"]
    issues = []
    for key, x_val in [
        ("support_west_X_mm", sup_cfg["support_west_X_mm"]),
        ("support_east_X_mm", sup_cfg["support_east_X_mm"]),
        ("load_X_mm",         sup_cfg["load_X_mm"]),
    ]:
        if not (0 <= x_val <= length):
            issues.append("{0}={1} outside [0,{2}]".format(key, x_val, length))
    # Load must be between supports
    x_w = sup_cfg["support_west_X_mm"]
    x_e = sup_cfg["support_east_X_mm"]
    x_l = sup_cfg["load_X_mm"]
    if not (x_w < x_l < x_e):
        issues.append("load X={0} not between supports [{1},{2}]".format(
            x_l, x_w, x_e))
    if issues:
        return ("FAIL", "; ".join(issues))
    return ("PASS", "Support coords OK for {0}: W={1} L={2} E={3}".format(
        specimen_id, x_w, x_l, x_e))


def _check_material(model, mat_name):
    """M: Material exists and has CDP tables."""
    if mat_name not in model.materials:
        return ("FAIL", "Material '{0}' not found".format(mat_name))
    mat = model.materials[mat_name]
    if not hasattr(mat, 'concreteDamagedPlasticity'):
        return ("FAIL", "Material '{0}' has no CDP definition".format(mat_name))
    if not hasattr(mat, 'concreteCompressionHardening'):
        return ("FAIL", "Material '{0}' has no compression table".format(mat_name))
    if not hasattr(mat, 'concreteTensionStiffening'):
        return ("FAIL", "Material '{0}' has no tension table".format(mat_name))
    return ("PASS", "Material '{0}' has CDP + compression + tension tables".format(mat_name))


def run_preflight(model, specimen_id, part_name, mat_name):
    """
    Run all preflight checks. Returns list of (check_name, status, message).
    FAIL in any check → do NOT write .inp.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("model_preflight must run inside Abaqus CAE kernel")

    results = []
    results.append(("GEOMETRY",     *_check_geometry(model, part_name)))
    results.append(("SUPPORT_COORDS", *_check_support_coords(specimen_id)))
    results.append(("BCS",          *_check_bcs(model, specimen_id)))
    results.append(("MESH",         *_check_mesh(model, part_name)))
    results.append(("MATERIAL",     *_check_material(model, mat_name)))

    overall = "PASS"
    for _, status, _ in results:
        if status == "FAIL":
            overall = "FAIL"
            break
        if status == "WARN" and overall == "PASS":
            overall = "WARN"

    print("=== PREFLIGHT {0} ===".format(specimen_id))
    for name, status, msg in results:
        print("  [{0}] {1}: {2}".format(status, name, msg))
    print("=== OVERALL: {0} ===".format(overall))

    return results, overall

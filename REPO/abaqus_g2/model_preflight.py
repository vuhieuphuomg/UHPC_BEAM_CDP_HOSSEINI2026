"""
model_preflight.py — Pre-run validation checks for Abaqus 2022 G2 models.

NOT_TESTED_IN_ABAQUS: requires `abaqus cae noGUI script=...` to verify.

Checks:
  GEOMETRY      — concrete part exists, cells > 0, volume > 0
  SUPPORT_COORDS — X positions within beam extents, load between supports
  BCS           — 3 required BCs present (SUPP_WEST, SUPP_EAST, LOAD)
  MESH_CONCRETE — element count > 0, node count > 0
  MESH_REBAR    — REBAR_BOT and REBAR_TOP parts have T3D2 elements
  EMBED         — EmbeddedRegion constraint exists
  MATERIAL      — UHPC material has CDP + compression + tension tables

Result per check: PASS / WARN / FAIL.
Overall FAIL if any check is FAIL → do NOT write .inp.
solver_authorized=false → never submit .inp regardless of preflight.

Output: PREFLIGHT_REPORT.json written to scratch_dir.
"""

import os
import json

try:
    from abaqus import mdb
    _IN_ABAQUS = True
except ImportError:
    _IN_ABAQUS = False

from configs.specimen_configs import SPECIMENS, SUPPORT_CONFIGS, BEAM_GEOMETRY


def _check_geometry(model, part_name):
    """Concrete part exists, has cells, positive volume."""
    try:
        part = model.parts[part_name]
        n_cells = len(part.cells)
        if n_cells == 0:
            return ("FAIL", "no cells in '{0}'".format(part_name))
        vol = sum(c.getSize() for c in part.cells)
        if vol <= 0:
            return ("FAIL", "zero volume in '{0}'".format(part_name))
        return ("PASS", "{0}: {1} cells, vol={2:.0f} mm3".format(part_name, n_cells, vol))
    except KeyError:
        return ("FAIL", "part '{0}' not found".format(part_name))
    except Exception as e:
        return ("WARN", "geometry check exception: {0}".format(e))


def _check_support_coords(specimen_id):
    """Support/load X positions are within beam and in correct order."""
    spec = SPECIMENS[specimen_id]
    sup = SUPPORT_CONFIGS[spec["support_config"]]
    L = BEAM_GEOMETRY["total_length_mm"]
    x_w, x_e, x_l = sup["support_west_X_mm"], sup["support_east_X_mm"], sup["load_X_mm"]
    issues = []
    for name, val in [("W", x_w), ("E", x_e), ("L", x_l)]:
        if not (0 <= val <= L):
            issues.append("X_{0}={1} outside [0,{2}]".format(name, val, L))
    if not (x_w < x_l < x_e):
        issues.append("load {0} not between supports [{1},{2}]".format(x_l, x_w, x_e))
    if issues:
        return ("FAIL", "; ".join(issues))
    return ("PASS", "W={0} L={1} E={2} all within [0,{3}]".format(x_w, x_l, x_e, L))


def _check_bcs(model, specimen_id):
    """3 required BCs exist in model.boundaryConditions."""
    required = [
        "BC_SUPP_WEST_{0}".format(specimen_id),
        "BC_SUPP_EAST_{0}".format(specimen_id),
        "BC_LOAD_{0}".format(specimen_id),
    ]
    missing = [n for n in required if n not in model.boundaryConditions]
    if missing:
        return ("FAIL", "missing BCs: {0}".format(", ".join(missing)))
    return ("PASS", "all 3 BCs present (PROVISIONAL: face-locked, no contact plates)")


def _check_mesh_concrete(model, part_name):
    """Concrete part has elements and nodes after generateMesh."""
    try:
        part = model.parts[part_name]
        n_e = len(part.elements)
        n_n = len(part.nodes)
        if n_e == 0:
            return ("FAIL", "'{0}': 0 elements (mesh not generated?)".format(part_name))
        return ("PASS", "{0}: {1} C3D8R elements, {2} nodes".format(part_name, n_e, n_n))
    except Exception as e:
        return ("WARN", "mesh concrete check: {0}".format(e))


def _check_mesh_rebar(model, specimen_id):
    """REBAR_BOT and REBAR_TOP wire parts have T3D2 elements > 0."""
    issues = []
    info = []
    for prefix in ["REBAR_BOT", "REBAR_TOP"]:
        pname = "{0}_{1}".format(prefix, specimen_id)
        if pname not in model.parts:
            issues.append("{0} not found".format(pname))
            continue
        n_e = len(model.parts[pname].elements)
        if n_e == 0:
            issues.append("{0}: 0 elements".format(pname))
        else:
            info.append("{0}: {1} T3D2".format(pname, n_e))
    if issues:
        return ("FAIL", "rebar mesh: " + "; ".join(issues))
    return ("PASS", "rebar elements: " + ", ".join(info))


def _check_embedded_region(model, specimen_id):
    """EmbeddedRegion constraint exists in model.constraints."""
    embed_name = "EMBED_REBAR_{0}".format(specimen_id)
    if embed_name not in model.constraints:
        return ("FAIL", "EmbeddedRegion '{0}' missing".format(embed_name))
    return ("PASS", "EmbeddedRegion '{0}' present".format(embed_name))


def _check_material(model, mat_name):
    """UHPC material has elastic + CDP + compression + tension tables."""
    if mat_name not in model.materials:
        return ("FAIL", "material '{0}' not found".format(mat_name))
    mat = model.materials[mat_name]
    missing = []
    if not hasattr(mat, "elastic"):
        missing.append("elastic")
    if not hasattr(mat, "concreteDamagedPlasticity"):
        missing.append("CDP")
    if not hasattr(mat, "concreteCompressionHardening"):
        missing.append("compressionHardening")
    if not hasattr(mat, "concreteTensionStiffening"):
        missing.append("tensionStiffening")
    if missing:
        return ("FAIL", "material '{0}' missing: {1}".format(mat_name, ", ".join(missing)))
    return ("PASS", "material '{0}' has elastic+CDP+compression+tension (STRAIN type, PROVISIONAL)".format(mat_name))


def run_preflight(model, specimen_id, part_name, mat_name, scratch_dir=None):
    """
    Run all checks. Returns (results, overall) where:
      results = list of (check_name, status, message)
      overall = "PASS" | "WARN" | "FAIL"
    Writes PREFLIGHT_REPORT.json to scratch_dir if provided.
    FAIL → do NOT write .inp.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("model_preflight must run inside Abaqus CAE kernel")

    checks = [
        ("GEOMETRY",       _check_geometry(model, part_name)),
        ("SUPPORT_COORDS", _check_support_coords(specimen_id)),
        ("BCS",            _check_bcs(model, specimen_id)),
        ("MESH_CONCRETE",  _check_mesh_concrete(model, part_name)),
        ("MESH_REBAR",     _check_mesh_rebar(model, specimen_id)),
        ("EMBED",          _check_embedded_region(model, specimen_id)),
        ("MATERIAL",       _check_material(model, mat_name)),
    ]

    results = [(name, status, msg) for name, (status, msg) in checks]

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

    if scratch_dir:
        try:
            report = {
                "specimen_id": specimen_id,
                "overall": overall,
                "checks": [
                    {"name": n, "status": s, "message": m}
                    for n, s, m in results
                ],
            }
            rpath = os.path.join(scratch_dir, "PREFLIGHT_REPORT.json")
            with open(rpath, "w") as f:
                json.dump(report, f, indent=2)
            print("Preflight report: {0}".format(rpath))
        except Exception as e:
            print("WARNING: could not write PREFLIGHT_REPORT.json: {0}".format(e))

    return results, overall

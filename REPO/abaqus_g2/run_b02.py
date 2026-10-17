"""
run_b02.py — B02 model orchestrator for Abaqus 2022 CAE.

Usage:
  abaqus cae noGUI script=abaqus_g2/run_b02.py

Specimen B02:
  batch_id=3, vf=1%, no stirrups, a/d=2.7
  Support: West=300mm, East=4700mm, Load=1407mm
  M1 role: CALIBRATION (B02, B03, B08, B12 only)

Material: C1 compression + T2 tension (STRAIN type, mesh-dependent, PROVISIONAL).
solver_authorized=false — .cae + .inp written, NOT submitted.

OPEN ITEMS before first solver run:
  1. NEEDS_EXPERT_REVIEW: CDP dilation angle psi (currently 36 deg)
  2. NEEDS_EXPERT_REVIEW: T2 tension type is STRAIN (mesh-dependent).
     For production: re-generate sigma-w table (lc_mm=25) and use TYPE=DISPLACEMENT.
     Current table is PROVISIONAL for geometry/mesh verification only.
  3. NEEDS_EXPERT_REVIEW: bottom bar bundle Z=[-54,0,+54]mm — cover not reported
  4. NEEDS_EXPERT_REVIEW: bar centroid Y=90mm — cover not reported
  5. BCs lock concrete face directly (no contact plate). PROVISIONAL geometry check.
  6. Mesh sensitivity study required before final solver run.

Build order (15 steps, no node selection before mesh):
  1. Create model
  2. Build concrete Part (YZ-plane sketch -> X-longitudinal extrusion)
  3. Partition Part at BC positions (face-based BCs work pre-mesh)
  4. Build separate rebar wire Parts (REBAR_BOT, REBAR_TOP)
  5. Create materials (UHPC CDP from G1 CSV; 4 rebar steels from Hosseini Table 3)
  6. Assign sections to Parts (NOT to assembly instances)
  7. Create assembly, instance all parts
  8. Apply support BCs using face geometry (pre-mesh, legal)
  9. Create Static step
  10. Apply load BC
  11. Set field/history output requests
  12. EmbeddedRegion constraint (rebar instance edges in concrete host)
  13. Mesh all parts (concrete C3D8R, rebar T3D2)
  14. Preflight checks (7 checks; FAIL -> no .inp)
  15. mdb.saveAs() -> .cae; writeInput() -> .inp
"""

import os
import sys
import json

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)
_REPO = os.path.dirname(_DIR)
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

try:
    from abaqus import mdb, backwardCompatibility
    from abaqusConstants import ON, OFF, CARTESIAN
    _IN_ABAQUS = True
except ImportError:
    _IN_ABAQUS = False
    print("WARNING: Not inside Abaqus CAE. Run with:")
    print("  abaqus cae noGUI script=abaqus_g2/run_b02.py")

from configs.specimen_configs import SPECIMENS, SUPPORT_CONFIGS, BATCH_PROPERTIES
from configs.specimen_configs import BOTTOM_BAR, TOP_BAR
from geometry_builder import build_beam_part, create_geometry_sets
from reinforcement_builder import build_bottom_bars, build_top_bars, build_stirrups
from support_loading_builder import partition_beam_for_bc, build_step, build_supports, build_load
from material_assignment import (
    create_uhpc_material, create_all_rebar_materials,
    assign_section_to_part, assign_rebar_section_to_part,
)
from mesh_builder import seed_and_mesh, seed_wire_part, LC_GLOBAL_MM
from model_preflight import run_preflight
from write_input import write_inp

SPECIMEN_ID = "B02"
MODEL_NAME  = "UHPC_{0}".format(SPECIMEN_ID)
CONCRETE_PART_NAME = "UHPC_T_Beam"
CONCRETE_INST_NAME = "UHPC_T_Beam-1"
COMP_MODEL = "C1"
TENS_MODEL = "T2"
STEP_NAME  = "PUSH_DOWN"
TARGET_DISP_MM = -60.0   # mm, downward; solver run not authorized

# ── SCRATCH DIRECTORY (local SSD, NOT inside Drive sync folder) ──────────────
# Output: B02.cae, B02.inp, BUILD_LOG.txt, PREFLIGHT_REPORT.json
# Change SCRATCH_ROOT if this path is unavailable.
SCRATCH_ROOT = os.path.join(
    os.environ.get("LOCALAPPDATA", "C:\\Users\\vuphu\\AppData\\Local"),
    "uhpc_g2_scratch",
)
SCRATCH_DIR = os.path.join(SCRATCH_ROOT, SPECIMEN_ID)


def _bbox_from_part(part):
    """Return bounding box string from Part vertices. Not assumed — read from model."""
    try:
        xs = [v.pointOn[0][0] for v in part.vertices]
        ys = [v.pointOn[0][1] for v in part.vertices]
        zs = [v.pointOn[0][2] for v in part.vertices]
        return "X=[{0:.0f},{1:.0f}] Y=[{2:.0f},{3:.0f}] Z=[{4:.0f},{5:.0f}]".format(
            min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))
    except Exception as e:
        return "bbox-error: {0}".format(e)


def _init_log(path):
    """Open BUILD_LOG.txt and return file handle."""
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    f = open(path, "w")
    f.write("BUILD_LOG: {0}\n".format(MODEL_NAME))
    f.write("SCRATCH_DIR: {0}\n".format(SCRATCH_DIR))
    f.write("solver_authorized: false\n\n")
    return f


def main():
    if not _IN_ABAQUS:
        raise SystemExit(
            "Must run inside Abaqus CAE:\n"
            "  abaqus cae noGUI script=abaqus_g2/run_b02.py"
        )

    if not os.path.isdir(SCRATCH_DIR):
        os.makedirs(SCRATCH_DIR)

    log_path = os.path.join(SCRATCH_DIR, "BUILD_LOG.txt")
    log = _init_log(log_path)

    def _log(msg):
        print(msg)
        log.write(msg + "\n")
        log.flush()

    spec       = SPECIMENS[SPECIMEN_ID]
    batch_id   = spec["batch_id"]
    Ec_mpa     = BATCH_PROPERTIES[batch_id]["Ec_mpa"]

    _log("=" * 60)
    _log("SPECIMEN: {0}  batch={1}  a/d={2}  stirrups={3}".format(
        SPECIMEN_ID, batch_id, spec["a_over_d"], spec["stirrup_type"]))
    _log("CDP: {0} + {1} (T2=STRAIN type, PROVISIONAL mesh-dependent)".format(
        COMP_MODEL, TENS_MODEL))
    _log("=" * 60)

    # ── 1. Create model ──────────────────────────────────────────────────────
    _log("[1] Creating model '{0}'...".format(MODEL_NAME))
    model = mdb.Model(name=MODEL_NAME)

    # ── 2. Build concrete Part ───────────────────────────────────────────────
    _log("[2] Building concrete T-beam Part (YZ-plane sketch, extrude +X)...")
    concrete_part = build_beam_part(model, part_name=CONCRETE_PART_NAME)
    create_geometry_sets(concrete_part)
    bbox = _bbox_from_part(concrete_part)
    _log("    Bounding box (from model, not assumed): " + bbox)

    # ── 3. Partition Part at BC positions ────────────────────────────────────
    _log("[3] Partitioning Part at support/load ±150mm...")
    partition_beam_for_bc(concrete_part, SPECIMEN_ID)
    _log("    Cells after partition: {0}".format(len(concrete_part.cells)))

    # ── 4. Build separate rebar wire Parts ───────────────────────────────────
    _log("[4] Building rebar wire Parts (REBAR_BOT, REBAR_TOP)...")
    rebar_bot_part = build_bottom_bars(model, SPECIMEN_ID)
    rebar_top_part = build_top_bars(model, SPECIMEN_ID)
    # B02 has no stirrups
    _log("    REBAR_BOT edges: {0}".format(len(rebar_bot_part.edges)))
    _log("    REBAR_TOP edges: {0}".format(len(rebar_top_part.edges)))

    # ── 5. Create materials ──────────────────────────────────────────────────
    _log("[5] Creating materials...")
    _log("    T2 tension: STRAIN type (mesh-dependent). PROVISIONAL for geometry check.")
    _log("    For production: use generate_sigma_w_table(lc_mm=25) TYPE=DISPLACEMENT.")
    rebar_mat_dict = create_all_rebar_materials(model)
    mat_name_uhpc = create_uhpc_material(
        model, batch_id=batch_id,
        comp_model_id=COMP_MODEL, tens_model_id=TENS_MODEL,
        Ec_mpa=Ec_mpa,
    )
    _log("    UHPC material: {0}".format(mat_name_uhpc))

    # ── 6. Assign sections to Parts (NOT instances) ──────────────────────────
    _log("[6] Assigning sections to Parts...")
    sec_uhpc = "SEC_UHPC_{0}".format(SPECIMEN_ID)
    assign_section_to_part(model, concrete_part, sec_uhpc, mat_name_uhpc)
    assign_rebar_section_to_part(
        model, rebar_bot_part,
        section_name="SEC_REBAR_BOT_{0}".format(SPECIMEN_ID),
        mat_name=rebar_mat_dict["M10_BOTTOM"],
        area_mm2=BOTTOM_BAR["bundle_area_mm2"],
    )
    assign_rebar_section_to_part(
        model, rebar_top_part,
        section_name="SEC_REBAR_TOP_{0}".format(SPECIMEN_ID),
        mat_name=rebar_mat_dict["M3_TOP"],
        area_mm2=TOP_BAR["area_mm2"],
    )

    # ── 7. Create assembly, instance all parts ───────────────────────────────
    _log("[7] Creating assembly...")
    assembly = model.rootAssembly
    assembly.DatumCsysByDefault(CARTESIAN)

    concrete_inst = assembly.Instance(
        name=CONCRETE_INST_NAME, part=concrete_part, dependent=ON)
    rebar_bot_inst_name = "REBAR_BOT_{0}-1".format(SPECIMEN_ID)
    rebar_top_inst_name = "REBAR_TOP_{0}-1".format(SPECIMEN_ID)
    assembly.Instance(name=rebar_bot_inst_name, part=rebar_bot_part, dependent=ON)
    assembly.Instance(name=rebar_top_inst_name, part=rebar_top_part, dependent=ON)

    # ── 8. Support BCs (face-based geometry, pre-mesh) ──────────────────────
    _log("[8] Applying support BCs (PROVISIONAL: face-locked, no contact plates)...")
    build_supports(model, assembly, CONCRETE_INST_NAME, SPECIMEN_ID)

    # ── 9. Static step ───────────────────────────────────────────────────────
    _log("[9] Creating Static step '{0}'...".format(STEP_NAME))
    build_step(model, step_name=STEP_NAME, initial_inc=0.001, max_inc=0.05)

    # ── 10. Load BC ──────────────────────────────────────────────────────────
    _log("[10] Applying load BC (PROVISIONAL: face-locked push-down)...")
    load_set_name = build_load(
        model, assembly, CONCRETE_INST_NAME, SPECIMEN_ID, STEP_NAME,
        target_displacement_mm=TARGET_DISP_MM,
    )

    # ── 11. Output requests ──────────────────────────────────────────────────
    _log("[11] Setting output requests...")
    model.FieldOutputRequest(
        name="F_OUTPUT", createStepName=STEP_NAME,
        variables=("S", "E", "LE", "PEEQ", "DAMAGET", "DAMAGEC", "U", "RF"),
        frequency=10,
    )
    model.HistoryOutputRequest(
        name="H_LOAD", createStepName=STEP_NAME,
        variables=("U2", "RF2"),
        region=assembly.sets[load_set_name],
        frequency=1,
    )

    # ── 12. EmbeddedRegion ───────────────────────────────────────────────────
    _log("[12] Creating EmbeddedRegion (rebar -> concrete host)...")
    rebar_edges = assembly.Set(
        name="SET_REBAR_ALL_{0}".format(SPECIMEN_ID),
        edges=(
            assembly.instances[rebar_bot_inst_name].edges +
            assembly.instances[rebar_top_inst_name].edges
        ),
    )
    concrete_cells_set = assembly.Set(
        name="SET_CONCRETE_{0}".format(SPECIMEN_ID),
        cells=assembly.instances[CONCRETE_INST_NAME].cells,
    )
    model.EmbeddedRegion(
        name="EMBED_REBAR_{0}".format(SPECIMEN_ID),
        embeddedRegion=rebar_edges,
        hostRegion=concrete_cells_set,
        weightFactorTolerance=1e-6,
    )

    # ── 13. Mesh all parts ───────────────────────────────────────────────────
    _log("[13] Meshing (concrete C3D8R, rebar T3D2, seed={0}mm)...".format(LC_GLOBAL_MM))
    seed_and_mesh(model, concrete_part, global_seed=LC_GLOBAL_MM)
    seed_wire_part(rebar_bot_part, element_size=LC_GLOBAL_MM)
    seed_wire_part(rebar_top_part, element_size=LC_GLOBAL_MM)
    _log("    Concrete: {0} elements, {1} nodes".format(
        len(concrete_part.elements), len(concrete_part.nodes)))
    _log("    REBAR_BOT: {0} T3D2 elements".format(len(rebar_bot_part.elements)))
    _log("    REBAR_TOP: {0} T3D2 elements".format(len(rebar_top_part.elements)))

    # ── 14. Preflight ────────────────────────────────────────────────────────
    _log("[14] Running preflight checks (7 checks)...")
    results, overall = run_preflight(
        model, SPECIMEN_ID, CONCRETE_PART_NAME, mat_name_uhpc,
        scratch_dir=SCRATCH_DIR,
    )
    for name, status, msg in results:
        _log("    [{0}] {1}: {2}".format(status, name, msg))
    _log("    OVERALL: {0}".format(overall))

    if overall == "FAIL":
        _log("PREFLIGHT FAIL — .cae and .inp NOT written.")
        _log("Fix issues above, then re-run.")
        log.close()
        return

    # ── 15. Save .cae and write .inp ─────────────────────────────────────────
    cae_path = os.path.join(SCRATCH_DIR, MODEL_NAME + ".cae")
    _log("[15a] Saving .cae: {0}".format(cae_path))
    mdb.saveAs(pathName=cae_path)

    _log("[15b] Writing .inp (solver_authorized=false)...")
    job_name = "{0}_{1}_{2}_B{3}".format(SPECIMEN_ID, COMP_MODEL, TENS_MODEL, batch_id)
    inp_path = write_inp(
        model_name=MODEL_NAME,
        job_name=job_name,
        output_dir=SCRATCH_DIR,
        description=(
            "UHPC T-beam B02 batch3 vf1% no-stirrups a/d=2.7 "
            "C1+T2-STRAIN-PROVISIONAL G2-PREPARATION NOT_SOLVER_AUTHORIZED"
        ),
    )

    # ── Summary ──────────────────────────────────────────────────────────────
    _log("")
    _log("=" * 60)
    _log("BUILD COMPLETE")
    _log("  CAE:   {0}".format(cae_path))
    _log("  INP:   {0}".format(inp_path))
    _log("  LOG:   {0}".format(log_path))
    _log("  Preflight JSON: {0}".format(
        os.path.join(SCRATCH_DIR, "PREFLIGHT_REPORT.json")))
    _log("  solver_authorized=false — do NOT submit")
    _log("")
    _log("OPEN ITEMS before solver run:")
    _log("  1. CDP dilation angle psi=36deg — NEEDS_EXPERT_REVIEW")
    _log("  2. T2 STRAIN -> DISPLACEMENT: re-gen sigma-w with lc_mm=25 — NEEDS_EXPERT_REVIEW")
    _log("  3. Bottom bar Z positions (+-54,0mm assumed) — NEEDS_EXPERT_REVIEW")
    _log("  4. Bar centroid Y=90mm (cover not reported) — NEEDS_EXPERT_REVIEW")
    _log("  5. Support BC: face-locked, no contact plate — PROVISIONAL")
    _log("=" * 60)

    log.close()


if __name__ == "__main__":
    main()
elif _IN_ABAQUS:
    main()

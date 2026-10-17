"""
run_b02.py — B02 model orchestrator for Abaqus 2022 CAE.

Usage (inside Abaqus):
  abaqus cae noGUI script=run_b02.py

Specimen B02:
  batch_id=3, vf=1%, no stirrups, a/d=2.7
  Support: West=300mm, East=4700mm, Load=1407mm
  Vult_reported=478kN, failure_mode=DT (diagonal tension)
  M1 role: CALIBRATION (used for material law selection)

Material: C1 compression + T2 tension, Batch 3 (G1 IMPLEMENTED models).
  CDP dilation angle=36° — NEEDS_EXPERT_REVIEW before solver run.
  T2 tension stiffening: σ–εck table (mesh-dependent, PROVISIONAL).
  Use generate_sigma_w_table(lc_mm=25.0) for production run.

NOT_TESTED_IN_ABAQUS: script structure verified; API calls require Abaqus kernel.
solver_authorized=false — .inp written but NOT submitted.

OPEN ITEMS before first solver run:
  1. NEEDS_EXPERT_REVIEW: CDP dilation angle ψ (currently 36°; typical UHPC 30-40°)
  2. NEEDS_EXPERT_REVIEW: T2 tension type — use σ-w (DISPLACEMENT) or σ-εck (STRAIN)?
     If DISPLACEMENT: re-run generate_sigma_w_table(lc_mm=25.0) and update CSV
  3. NEEDS_EXPERT_REVIEW: MMFX rebar fy not confirmed from Hosseini Table 1
  4. NEEDS_EXPERT_REVIEW: bottom bar bundle arrangement (3×2 at Z=±54,0mm)
  5. NEEDS_EXPERT_REVIEW: bar cover not reported → bar centroid Y=90mm assumed
  6. Mesh sensitivity study required after first run
  7. Engineer must select C1/T2 (or C4_ADAPTED variant) before final job matrix
"""

import os
import sys

# Allow imports from abaqus_g2/ when running as abaqus cae noGUI script=run_b02.py
_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)
# Also add parent (REPO root) for tools/cdp_builder access
_REPO = os.path.dirname(_DIR)
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

try:
    from abaqus import mdb, backwardCompatibility
    from abaqusConstants import ON, OFF
    _IN_ABAQUS = True
except ImportError:
    _IN_ABAQUS = False
    print("WARNING: Not running inside Abaqus CAE. API calls will fail.")
    print("Run with: abaqus cae noGUI script=run_b02.py")

from configs.specimen_configs import SPECIMENS, SUPPORT_CONFIGS, BATCH_PROPERTIES
from geometry_builder import build_beam_part
from reinforcement_builder import build_bottom_bars, build_top_bars, assign_rebar_sections
from support_loading_builder import build_step, build_supports, build_load
from material_assignment import (
    create_uhpc_material, create_rebar_material, assign_section_to_part
)
from mesh_builder import seed_and_mesh, seed_rebar_wires, LC_GLOBAL_MM
from model_preflight import run_preflight
from write_input import write_inp

SPECIMEN_ID = "B02"
MODEL_NAME = "UHPC_{0}".format(SPECIMEN_ID)
PART_NAME = "UHPC_T_Beam"
INSTANCE_NAME = "UHPC_T_Beam-1"
COMP_MODEL = "C1"
TENS_MODEL = "T2"
STEP_NAME = "PUSH_DOWN"
TARGET_DISP_MM = -60.0   # 60mm downward push; covers Vult zone for DT failure

# Output directory for .inp (on local SSD scratch, NOT Drive)
# IMPORTANT: do NOT run solver from Drive path (CLAUDE.md constraint)
INP_OUTPUT_DIR = os.path.join(_REPO, "abaqus_g2", "output", SPECIMEN_ID)


def main():
    if not _IN_ABAQUS:
        raise SystemExit("Must run inside Abaqus CAE: abaqus cae noGUI script=run_b02.py")

    spec = SPECIMENS[SPECIMEN_ID]
    batch_id = spec["batch_id"]
    batch_props = BATCH_PROPERTIES[batch_id]
    Ec_mpa = batch_props["Ec_mpa"]

    print("=== BUILDING MODEL: {0} ===".format(MODEL_NAME))
    print("Specimen: {0} | Batch: {1} | a/d: {2} | Stirrups: {3}".format(
        SPECIMEN_ID, batch_id, spec["a_over_d"], spec["stirrup_type"]))
    print("Compression model: {0} | Tension model: {1}".format(COMP_MODEL, TENS_MODEL))

    # 1. Create new model
    model = mdb.Model(name=MODEL_NAME)

    # 2. Build geometry
    print("Building T-beam geometry...")
    part = build_beam_part(model, part_name=PART_NAME)

    # 3. Create assembly
    print("Creating assembly instance...")
    assembly = model.rootAssembly
    assembly.DatumCsysByDefault(CARTESIAN)
    instance = assembly.Instance(
        name=INSTANCE_NAME,
        part=part,
        dependent=ON,
    )

    # 4. Build reinforcement wires
    print("Building reinforcement wires (bottom + top bars, no stirrups for B02)...")
    build_bottom_bars(model, part, SPECIMEN_ID)
    build_top_bars(model, part, SPECIMEN_ID)
    # B02 has no stirrups — skipping build_stirrups()

    # 5. Create materials
    print("Creating materials: {0}_{1}_B{2}...".format(
        COMP_MODEL, TENS_MODEL, batch_id))
    rebar_mat = create_rebar_material(model, mat_name="MMFX_REBAR")
    mat_name = create_uhpc_material(
        model, batch_id=batch_id,
        comp_model_id=COMP_MODEL, tens_model_id=TENS_MODEL,
        Ec_mpa=Ec_mpa,
    )

    # 6. Assign sections
    print("Assigning sections...")
    assign_section_to_part(model, assembly, PART_NAME, INSTANCE_NAME,
                           mat_name=mat_name,
                           section_name="SEC_UHPC_{0}".format(SPECIMEN_ID))
    assign_rebar_sections(model, SPECIMEN_ID, rebar_material_name=rebar_mat)

    # 7. Create embedded constraint for rebar in concrete
    print("Embedding rebar in concrete host...")
    wire_region = assembly.sets.get("SET_REBAR_ALL_{0}".format(SPECIMEN_ID), None)
    if wire_region is not None:
        model.EmbeddedRegion(
            name="EMBED_REBAR_{0}".format(SPECIMEN_ID),
            embeddedRegion=wire_region,
            hostRegion=instance.cells,
            weightFactorTolerance=1e-6,
        )

    # 8. Create analysis step
    print("Creating analysis step: {0}...".format(STEP_NAME))
    build_step(model, step_name=STEP_NAME, initial_inc=0.001, max_inc=0.05)

    # 9. Apply supports and load
    print("Applying BCs (supports + load)...")
    build_supports(model, assembly, INSTANCE_NAME, SPECIMEN_ID, STEP_NAME)
    build_load(model, assembly, INSTANCE_NAME, SPECIMEN_ID, STEP_NAME,
               target_displacement_mm=TARGET_DISP_MM)

    # 10. Add field/history output requests
    print("Setting output requests...")
    model.FieldOutputRequest(
        name="F_OUTPUT", createStepName=STEP_NAME,
        variables=("S", "E", "LE", "PEEQ", "DAMAGET", "DAMAGEC", "U", "RF"),
        frequency=10,
    )
    model.HistoryOutputRequest(
        name="H_LOAD", createStepName=STEP_NAME,
        variables=("U2", "RF2"),
        region=assembly.sets["SET_LOAD_{0}".format(SPECIMEN_ID)],
        frequency=1,
    )

    # 11. Mesh
    print("Meshing beam (global seed = {0}mm)...".format(LC_GLOBAL_MM))
    seed_and_mesh(model, part, global_seed=LC_GLOBAL_MM)
    seed_rebar_wires(part)

    # 12. Preflight
    print("Running preflight checks...")
    results, overall = run_preflight(model, SPECIMEN_ID, PART_NAME, mat_name)

    if overall == "FAIL":
        print("PREFLIGHT FAIL — .inp NOT written. Fix issues and re-run.")
        return

    # 13. Write .inp (DO NOT SUBMIT)
    if not os.path.isdir(INP_OUTPUT_DIR):
        os.makedirs(INP_OUTPUT_DIR)

    job_name = "{0}_{1}_{2}_B{3}".format(
        SPECIMEN_ID, COMP_MODEL, TENS_MODEL, batch_id)
    inp_path = write_inp(
        model_name=MODEL_NAME,
        job_name=job_name,
        output_dir=INP_OUTPUT_DIR,
        description=(
            "UHPC T-beam B02: batch3 vf1% no-stirrups a/d=2.7 "
            "C1+T2 CDP G2-PREPARATION NOT_SOLVER_AUTHORIZED"
        ),
    )
    print("=== DONE ===")
    print("Model: {0}".format(MODEL_NAME))
    print("INP: {0}".format(inp_path))
    print("solver_authorized=false — do NOT submit without engineer approval")
    print("OPEN ITEMS before solver run:")
    print("  1. Confirm CDP dilation angle ψ (currently 36°) — NEEDS_EXPERT_REVIEW")
    print("  2. Confirm T2 tension type: STRAIN (σ-εck) or DISPLACEMENT (σ-w)")
    print("  3. Confirm MMFX rebar fy from Hosseini Table 1 — NEEDS_EXPERT_REVIEW")
    print("  4. Confirm bottom bar bundle arrangement — NEEDS_EXPERT_REVIEW")


if __name__ == "__main__":
    main()
elif _IN_ABAQUS:
    # When run via abaqus cae noGUI script=run_b02.py, the module is executed directly
    main()

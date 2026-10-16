# Claude Code — UHPC BEAM CDP HOSSEINI2026 / V5

## First action (mandatory)
- Open `../README_START_HERE_V5.md`, `../00_CONTROL/PROJECT_STATE_V5.json`, `../00_CONTROL/GATES_V5.json`, `../00_CONTROL/ENGINEERING_OPEN_ITEMS_V5.md` and `../00_CONTROL/RUN_REGISTRY_MASTER_V5.csv` (header + only rows relevant to current stage).
- Run `python tools/fe_control.py validate`, then `python -m unittest discover -s tests -v`; do not launch Abaqus.
- Start **G0_SOURCE_AUDIT only**. User must approve solver submission and scientific gate releases. Do not auto-approve gates because code tests pass.

## Responsibilities and boundaries
- Claude Code: implement and test bounded code changes on branch `claude/feature`, produce evidence/diffs. Antigravity: independently review via notes/patches; no assumed cross-agent API. Orchestrator decides execution from machine-verifiable gates, not agent self-declaration.
- Abaqus/CAE 2022 typically uses Python 2.7. Verify actual installation. Keep `abaqus2022/` legacy compatible, `tools/` Python 3 only. Do not run `python3` modules from Abaqus CAE kernel.
- Maintain a single official master `.cae`. Never overwrite master or completed .inp/.odb. Work on a local SSD scratch; never solver-run in Drive folders.
- **NEVER invent source geometry, steel data, material curves, dt/dc, sigma-w, fracture energy, supports, or signs.** Stop with NEEDS_EXPERT_REVIEW. Keep raw inputs untouched.
- Work through build -> consistency input -> datacheck -> solver -> postprocess -> science review as separate gates. Do not suppress Abaqus checks to get a green log.
- Do not read eight holdout outcomes to choose CDP laws. No hiding non-matching failure cases. No uncontrolled retries or silent change of viscosity, mesh, contacts or strengths.
- All changes classify A=code/API, B=topology/selections, C=engineering parameters, D=solver controls. Report modified files and gate evidence.

## State and safety
- V5 canonical registry: `../00_CONTROL/RUN_REGISTRY_MASTER_V5.csv`; V3 remains historical, never modify it to reconcile gates.
- V5 gates: `../00_CONTROL/GATES_V5.json` (HOLD by default).
- `../00_CONTROL/PROJECT_STATE_V5.json` has `solver_authorized=false`. Neither Claude nor VS Code tasks should flip it automatically.
- `src`/`abaqus2022` routines can be implemented only with source evidence; testing under normal Python is NOT proof of Abaqus API execution.

## Current task
Validate Figure 1 (B01–B12), note M#3 versus M#4 conflict, B11 special support, exact shear force statics, and 3 batch CDP consistency. Produce G0 audit and reviewed coordinates **without submitting FE jobs**. Return blockers, evidence, next step.

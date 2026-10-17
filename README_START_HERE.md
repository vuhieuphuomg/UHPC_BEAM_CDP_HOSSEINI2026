# UHPC BEAM CDP — unified research/FE plan (V3)

**This is a planning and provenance package, not a completed Abaqus model.** No Drive folders were created by this package; no job was executed; all 62 jobs are NOT RUN or HOLD. The .cae, complete material damage curves, and Abaqus builder must be implemented after the source and model gates pass.

- Destination Drive parent: https://drive.google.com/drive/folders/1l7XapSULCCwx4CoZ2iK72O24Wr6jnTZ6
- Proposed child: `UHPC_BEAM_CDP_HOSSEINI2026`
- Start with `09_DOCUMENTATION/STEPS_DETAILED_VI.md` and `09_DOCUMENTATION/WINDOWS_ABAQUS_RUNBOOK.md`.
- Master registry: `00_CONTROL/RUN_REGISTRY_MASTER_V3.csv` (18 material + 44 beam).
- Previous original matrices preserved under `00_CONTROL/` (do not silently change the 44 ID definitions).
- Experiment workbook preserved under `02_EXPERIMENT/01_DIGITIZED/`.
- Source article in original parent folder is referenced rather than duplicated.
- GATE_0 remains HOLD pending source figure/rebar/support audit. `T_BEST_LOCKED` and `C_BEST_LOCKED` are NOT executable model IDs and must never be passed to the builder unresolved.

For `.odb` storage, monitor estimated per-job size and total Drive quota. Never solve in synced folders; scratch locally and archive atomically.


## V4 preparation
Drive root folder: https://drive.google.com/drive/folders/1Rb4jsh5d1gaVAJFoKxZxnUp3ENLr03Pm
Workspace: REPO/; start with `python REPO/orchestrator/fe_control.py validate` in this bundle root.
SAFETY: code is an orchestration scaffold, NOT a tested Abaqus builder. SOURCE/MATERIAL GATES remain blocked. No Abaqus solver has run.

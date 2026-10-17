# ABQ UHPC BEAM/CDP agent contract

Read these small files only at startup: `00_CONTROL/PROJECT_CONFIG.json`, `00_CONTROL/GATES.json`, `00_CONTROL/BLOCKERS.md`, `00_CONTROL/RUN_REGISTRY_MASTER_V3.csv` (filter to requested stage). Read experimental batch and source tables only when relevant. Do not recursively load all ODB/PDF/CAE at startup.

Never create solver jobs while `auto_run_enabled=false` or without an explicit user command authorizing a stage. Fail on unresolved T_BEST_LOCKED/C_BEST_LOCKED placeholders, invalid CDP tables, missing region sets, or clashes with existing run IDs.

Preserve all older files and source evidence. Stage outputs on local SSD; archive by exact run_id with SHA-256. New scientific physical input changes require explicit CHANGELOG A/B/C/D entry, new config version and rerun scope. Status labels distinguish STATIC_CHECK, CAE_BUILD, DATACHECK, SOLVER_COMPLETED, POSTPROCESSED, ENGINEERING_VALIDATED and ARCHIVED.

M1: independently check 3 batches x 4 compression + 3 batches x 2 tension; these are material NUMERICAL CHECKS, not genuine full-curve experimental fits without actual curves. Select laws on B02 B03 B08 B12 only. Complete mesh/sensitivity BEFORE the 8 holdout specimens. NEVER use B01 B04 B05 B06 B07 B09 B10 B11 to tune/freeze material.

User's priority is actual Abaqus simulation and provenance; do not write manuscripts unless specifically requested.

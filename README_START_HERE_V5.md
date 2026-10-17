# UHPC BEAM CDP / HOSSEINI 2026 — RELEASE V5 STANDARDIZED

**Status: PREPARATION_ONLY, STATICALLY_TESTED; NO ABAQUS BUILD, NO SOLVER RUN.** The authoritative parent Drive folder is https://drive.google.com/drive/folders/1l7XapSULCCwx4CoZ2iK72O24Wr6jnTZ6 ; project subfolder is https://drive.google.com/drive/folders/1Rb4jsh5d1gaVAJFoKxZxnUp3ENLr03Pm . Legacy `/CDP` and original Hosseini PDF remain untouched.

## Start on Windows in VS Code
1. Extract the full V5 ZIP into `C:\\Abaqus\\UHPC_BEAM_CDP\\` (the project root should directly contain `REPO`, `00_CONTROL`, `01_SOURCES`... ). Avoid extracting into a nested `...\\..._V5\\` unless you adapt paths.
2. Open **only** the `REPO` directory as VS Code workspace: `code C:\\Abaqus\\UHPC_BEAM_CDP\\REPO`.
3. Confirm Python 3 is installed; in the VS Code terminal run: `python tools\\fe_control.py validate`, `python tools\\fe_control.py status`, and `python -m unittest discover -s tests -v`.
4. Launch Claude Code in the same VS Code workspace (CLI `claude` in integrated terminal or official extension); paste prompt at `../09_DOCUMENTATION/CLAUDE_CODE_MASTER_PROMPT_V5.md` or prompt copy file. Keep solver permission off.
5. Use local SSD for model build/run, not a Drive-synced path; configure `REPO/config/runtime.local.json` copied from `runtime.local.example.json` only after verifying executable/license and path permissions.

## Source-of-truth
- **V5 registry**: `00_CONTROL/RUN_REGISTRY_MASTER_V5.csv`, 18 coupons + 44 beam recipes; stage execution controlled by `00_CONTROL/GATES_V5.json` and `00_CONTROL/PROJECT_STATE_V5.json`.
- Historical **V3 registry**, **V4 ZIP**, and B01-B12 experimental values retained; V5 repairs invalid metadata self-reference and explicit gate names without editing experimental results.
- `03_MATERIALS/00_LITERATURE_MODELS/fig2*.csv` from V4 are **QUARANTINED PENDING MANUAL SOURCE QA**; not approved for Abaqus input.
- **No `.cae` master is supplied**. Code stubs are not permission to fill missing geometry, constitutive damage or contact values.

## Next stage
G0 = audit Figure 1 dimensions, support and loading points, B11 special support, top-bar M#3/M#4 discrepancy, shear force convention, and Batch2 inelastic-strain issue. Provide referenced evidence and a `NEEDS_EXPERT_REVIEW` checklist. Do not run coupon/dam solver yet.

## Release rules
- `REPO/` contains Python3-only read-only tools. Abaqus scripts must be authored under `REPO/abaqus2022/`, Python2.7-compatible and validated against installed version.
- All jobs have owner IDs, a gate dependency, and a future archival path. These are **planned recipes**, not actual computed results.
- Only archive closed solver artifacts after checksum/QA; keep raw experiments separate from digitized and proposed constitutive data.

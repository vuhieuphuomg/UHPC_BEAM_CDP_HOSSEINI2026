# Registry migration V3 -> V5 (non-destructive)
- V3 retained unchanged. The V3 `source_run_id` column points to each job's own `run_id` for all 44 beam cases, which is not a valid dependency/reuse provenance. V5 records the V3 value under `legacy_source_run_id_v3` and leaves `source_run_id` empty until an actual verified source job exists.
- V3 has inconsistent gate labels `GATE_1`, `GATE_2`, etc. V5 uses explicit `required_gates`, aligned with `GATES_V5.json` and chronological freeze.
- No source paper, geometry, CDP law, numerical result, or experiment altered. All jobs still blocked; this is a **workflow metadata correction**, not validation.
- Registry scientific phases/order and unique 44 beam / 18 coupon IDs preserved.

- V3 left `batch_id` blank on all beam jobs. V5 back-fills from Hosseini Table 1 via `02_EXPERIMENT/02_AUDITED_LOCKED/EXPERIMENT_TARGETS_REPORTED_V5.csv`, while retaining blank legacy value in `legacy_batch_id_v3`. This is metadata traceability, not a physical-model validation.

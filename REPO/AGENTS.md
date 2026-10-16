# Shared Agent Operating Contract (V5)
- One git repository. Claude Code implements; Antigravity reviews if available. Separate worktrees/branches during concurrent work, never edit same .cae/.inp/.odb or registry simultaneously.
- Exchange review through `control/REVIEW_QUEUE.json`, `control/REVIEWS/`, Git commit IDs and SHA-256. Do not assume an automatic Antigravity API.
- Python 3 code under `tools/` (Windows orchestration). Abaqus 2022 Python 2.7-compatible code must be isolated under `abaqus2022/` and tested on the real installation.
- The authoritative experimental PDF is Hosseini et al. 2026 in the parent Drive folder. Fakeh et al. 2025 is constitutive literature, not experimental data for the tested batch.
- No simultaneous solver jobs until resource profiling; no automatic unapproved job; no silent material/geometry/solver modifications. Preserve baseline and ODB provenance.
- Review all claims as REPORTED / DERIVED / ADOPTED / NOT_REPORTED / NEEDS_EXPERT_REVIEW.
- After any edit, run tests and record affected run IDs, stage and engineering change type; failing gates block the next step.

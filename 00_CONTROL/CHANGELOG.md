# Project changelog

- PLAN V3: Created folder schema and consolidated existing 44 beam jobs with 18 material coupon jobs. No solver was run. No Drive folders were created yet.

---

## C-001 — 2026-10-17 — Batch 2 CDP peak inelastic strain FE approximation

**Classification:** C — engineering parameter (FE input approximation, Batch 2 only)  
**Approved by:** Project engineer (vuphuong.xdhn@gmail.com), 2026-10-17  
**Stage:** G0_SOURCE_AUDIT → recorded as G0 closure condition

**Context:**  
Batch 2 UHPC (2% Vf): f'c=153.2 MPa, Ec=47.3 GPa, εcp=0.0032 (Table 2, Hosseini 2026).  
Nominal inelastic strain at peak = εcp − f'c/Ec = 0.0032 − 0.003239 = −0.000039.  
Abaqus CDP requires the first compression inelastic-strain table entry ≥ 0. Value is inadmissible as-is.

**Decision — FE input only:**
```
eps_in,peak (FE) = max(0, εcp − f'c/Ec) = max(0, −0.000039) = 0
```
Deviation = 1.2% of total peak strain; within experimental scatter (εcp SD ≈ 15.6%).

**Experimental data — NOT modified:**  
f'c = 153.2 MPa · Ec = 47.3 GPa · εcp = 0.0032 remain as REPORTED in all source tables.

**Scope and constraints:**  
- Applies ONLY to CDP compression table peak entry for Batch 2.  
- Does NOT validate any ascending branch model (e.g. Graybeal–Fakeh C1). Model selection and full curve verification is a G1 task.  
- At G1: build full ascending branch, verify ALL eps_in ≥ 0 and non-decreasing across all table rows. If C1 produces inconsistency, flag BLOCKED and propose adjustment with evidence.  
- All G1 CDP table entries must be labelled: REPORTED (raw measurement), ADOPTED (model fit), or APPROXIMATED (this eps_in=0 case).

**Reference:** `00_CONTROL/G0_REVIEW_REQUEST_V5.md` BLOCKER-4 conditional approval.

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

---

## C-002 — 2026-10-17 — Fiber dimensions ASSUMED for C1 post-peak and λf calculation

**Classification:** C — engineering parameter (ASSUMED, not from source)  
**Stage:** G1_MATERIAL_TABLE_VALID — recorded as HOLD condition  

**Context:**  
C1 Graybeal–Fakeh post-peak slope M = 7061.5 × λf^(−0.411) (Fakeh 2025 Eq.9/Table 3) requires  
fiber reinforcement index λf = vf × (l/df). Fiber dimensions (l = length, df = diameter) are  
NOT reported in Hosseini 2026 Table 2 or any confirmed source for these UHPC batches.

**Decision:**  
Use standard UHPC straight steel fiber dimensions: l=13.0 mm, df=0.2 mm (ASSUMED).  
These values are consistent with the majority of specimens in Fakeh 2025 Table 1 calibration database.

λf values (ASSUMED):  
- Batch 1 (vf=2%): λf = 0.02 × 65 = 1.30 → M ≈ 6337 MPa/strain  
- Batch 2 (vf=2%): λf = 1.30 → M ≈ 6337 MPa/strain  
- Batch 3 (vf=1%): λf = 0.65 → M ≈ 8428 MPa/strain  

**Scope:**  
- C1 post-peak rows are tagged ADOPTED (depend on ASSUMED fiber dims).  
- C1 ascending branch is INDEPENDENT of fiber dims (uses only Ec, fc, ac, bc).  
- T1 Tian model λf-based prediction (fte, ft, εte, εt0) is NOT used; Hosseini  
  measured values used instead. T1 hardening table is INDEPENDENT of fiber dims.  
- Must be revised if fiber specifications are confirmed from Hosseini source.

**Required action before G1=PASS:**  
Obtain fiber dimensions from Hosseini 2026 supplementary data or equipment records.  
If confirmed = 0.2mm × 13mm → C-002 VALIDATED. If different → recalculate M and retag.

---

## C-003 — 2026-10-17 — C3 Wang excluded from FE; C4_YAN_EC_ADAPTED developed as new IMPLEMENTED candidate

**Classification:** C — engineering parameter (model selection and adaptation decision)  
**Approved by:** Project engineer (vuphuong.xdhn@gmail.com), 2026-10-17  
**Stage:** G1_MATERIAL_TABLE_VALID — C4_ADAPTED IMPLEMENTED; G1 still HOLD

### C3 Wang — Exclusion from FE main matrix

**Decision:** C3 Wang excluded from Abaqus FE run matrix. Retained as THEORETICAL REFERENCE ONLY.

**Reason:** Wang (2016) parabolic ascending formula has initial slope = 2×f_peak/ε0 >> Ec_reported (where ε0 is from Wang Eq.7). This causes εin < 0 for the majority of the ascending branch in all three batches (B1:96.6%, B2:93.9%, B3:100%). The incompatibility is structural — it arises because Wang's own ε0 formula does not reproduce the experimentally measured Ec. Correcting it while retaining Wang's formula would require a different ascending formula constituting a new, distinct model. No clipping or parameter forcing was applied.

**What is retained:** C3 class (STATUS=BLOCKED) remains in code for raw σ–ε diagnostic comparison. Diagnostic plots at `03_MATERIALS/plots/B{n}_C3_raw_curve.png`. C3 will NOT appear in Abaqus material tables or the FE run matrix.

### C4_YAN_EC_ADAPTED — Engineering adaptation

**Decision:** Set `eps_c0_model = alpha_a × fc / Ec` (not the reported εcp). This makes the initial tangent = Ec exactly, by construction.

**Rationale:** The Yan (2010) rational formula for the ascending branch is:  
`σ = fc × (αa×η − η²) / [1+(αa−2)×η]`  
Its initial tangent is `αa × fc / εc0`. Setting `εc0_model = αa × fc / Ec` makes this tangent = Ec.  
The resulting inelastic strain is provably non-negative:  
`εin(η) = (fc/Ec) × η² × (αa−1)² / (1+(αa−2)×η) ≥ 0 ∀ η∈[0,1]`  
No clipping required. This is an ADAPTED model (not raw Yan 2010).

**Source:** Fakeh (2025) Table 3 [SECONDARY source]. Yan (2010) original paper not in repository.

**Two variants implemented:**

| Model | αa | αd | B1 eps_c0 dev | B2 eps_c0 dev | B3 eps_c0 dev |
|---|---|---|---|---|---|
| C4_ADAPTED_LB | 1.100 | 0.193 | +4.4% | +11.4% | +0.8% |
| C4_ADAPTED_UB | 1.138 | 0.312 | +8.1% | +15.2% | +4.3% |

`dev = (eps_c0_model − ecp_reported) / ecp_reported × 100%`  
Peak strain deviation is largest for Batch 2 (k=0.988 < 1.0) because reported εcp is very close to elastic recovery.

**What is NOT changed:** fc and Ec remain as experimentally reported for all three batches. Raw experimental measurements in BATCHES dict are untouched.

**QA results:** All 6 tables (3 batches × 2 variants) PASS CDP QA: first εin=0, all εin≥0, strictly monotone, all σ>0. 111 unit tests ALL PASS.

**Four variants implemented (2×2 survey, 2026-10-17):**

| Model | αa | αd | B1 dev | B2 dev | B3 dev | Notes |
|---|---|---|---|---|---|---|
| C4_ADAPTED_LB    | 1.100 | 0.193 | +4.4% | +11.3% | +0.8% | αa LB + αd LB |
| C4_ADAPTED_LA_HD | 1.100 | 0.312 | +4.4% | +11.3% | +0.8% | αa LB + αd UB |
| C4_ADAPTED_HA_LD | 1.138 | 0.193 | +8.0% | +15.2% | +4.3% | αa UB + αd LB |
| C4_ADAPTED_UB    | 1.138 | 0.312 | +8.0% | +15.2% | +4.3% | αa UB + αd UB |

Peak deviation depends only on αa (ascending). αd only affects descending ductility.
eps_pl column added to all C4_ADAPTED tables (= eps_in at G1; dc=0, no damage table yet).

**Scope and constraints:**
- All 4 variants ADAPTED: tag must appear in all output tables and plots.
- Alpha coefficients are parameter ranges from secondary source — no unique Hosseini calibration without Yan (2010) original paper.
- B2 peak strain deviation: αa=1.1 variants +11.3%, αa=1.138 variants +15.2%. Must be noted in FE matrix entries.
- Do NOT select one αa/αd pair solely because it matches experimental data (engineer decision required).
- Do NOT use for holdout batch comparison without explicit approval.
- FE matrix update is a separate step: engineer to review all 4 variants and decide which enter the run matrix.

---

## C-004 — 2026-10-17 — T2 fracture energy estimate; T1 softening parameter classified

**Classification:** A — code (new method); C — engineering parameter classification  
**Stage:** G1_MATERIAL_TABLE_VALID — documentation only; no new model implemented; G1 still HOLD

### T2 Zhao tension — fracture energy estimate

`fracture_energy_lambda_clc()` method added to T2ZhaoTension. Computes GFI using Fakeh (2025) λclc as localization length (not FE mesh lc). This is an ESTIMATE for engineering reference only.

Derivation: GFI = λclc × ft × εt0 / 0.4 × ((εtu/εt0)^0.4 − 1)

| Batch | ft_loc (MPa) | λclc (mm) | wtu (mm) | wto (mm) | GFI (N/mm) |
|---|---|---|---|---|---|
| B1 | 10.0 | 71.0 | 5.19 | 0.355 | 23.7 |
| B2 | 9.3  | 69.5 | 5.08 | 0.348 | 21.6 |
| B3 | 7.5  | 65.8 | 2.60 | 0.178 |  8.9 |

**Important:** T2 generate_table() output (σ–εck) is MESH-DEPENDENT. Do NOT use as final Abaqus-ready input without σ–w conversion. GFI above uses Fakeh's calibrated λclc as a stand-in for lc — not a direct fracture toughness measurement.

### T1 Tian tension — missing parameter classified

Softening formula (from Fakeh 2025 Table 4, SECONDARY): σ(ε) = ft × (1 − 0.15 × (ε−εt0)/(εu−εt0))

Missing: **εu** — total strain at σ = 0.85×ft on Tian descending branch. This is NOT in Hosseini (2026) Table 2. The Tian (2023) original paper (not in repo) contains the εu prediction formula (expected to be a function of fc and λf). Until Tian (2023) is obtained, T1 softening remains BLOCKED.

Note: The formula `1 − 0.15×(...)` represents a 15% linear drop from ft at εt0 to 0.85×ft at εu. Fakeh then extends further to 0.2×ft — this extension formula requires the same εu plus lc (mesh characteristic length).

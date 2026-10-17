# G1 Material Table Report

**Generated:** 2026-10-17  
**Gate:** G1_MATERIAL_TABLE_VALID — HOLD (pending source papers for C1-C4, T1-T2)  
**solver_authorized:** false  

---

## Summary

- **BLOCKED:** 6
- **DEGENERATE:** 1
- **IMPLEMENTED:** 18
- **IMPLEMENTED_REFERENCE:** 5

## Compression tables

| Batch | Model | Status | CSV | QA | Notes |
|-------|-------|--------|-----|----|-------|
| 1 | REF_POPOVICS | IMPLEMENTED_REFERENCE | `03_MATERIALS\tables\B1_REF_POPOVICS_compression.csv` | PASS | Post-peak branch (15 pts) is ADOPTED (C1: Fakeh Eq.9 M=7061.5×λf^-0.411 with ASSUMED fiber dims l=13mm df=0.2mm; REF_POPOVICS: linear descent placeholder). |
| 1 | C1 | IMPLEMENTED | `03_MATERIALS\tables\B1_C1_compression.csv` | PASS | Post-peak branch (15 pts) is ADOPTED (C1: Fakeh Eq.9 M=7061.5×λf^-0.411 with ASSUMED fiber dims l=13mm df=0.2mm; REF_POPOVICS: linear descent placeholder). |
| 1 | C2 | IMPLEMENTED | `03_MATERIALS\tables\B1_C2_compression.csv` | PASS | — |
| 1 | C3 | BLOCKED | — | PASS | BLOCKED: Ascending parabolic model (initial slope = 2×f_peak/ε0 >> Ec). εin = ε − σ/Ec < 0 for ~94–100% of ascending branch in all 3 batches (Wang Eq.7 ε0; B1:~96.6%, B2:~93.9%, B3:100%). Expert engineering decision required before generating CDP table. A rewritten ascending branch is a different hybrid law — use new model ID.; εin analysis: α_Wang=1.0331; η_cross=0.9669; εin<0 on 96.7% of ascending; εin_peak=1.10e-04; ε0_Wang=0.00343; ε20=0.00735 |
| 1 | C4 | BLOCKED | — | PASS | BLOCKED: Ascending rational formula: initial tangent αa×fc/εc0 > Ec for all batches (αa ∈ [1.1,1.138]; k=Ec×εcp/fc ≈ 0.988–1.091). εin < 0 for ~49–100% of ascending branch (batch/αa-dependent). αa, αd are parameter ranges only from secondary source (Fakeh Table 3); no unique calibration for Hosseini batches without Yan (2010) original paper.; εin<0 on ascending: αa=1.1: 89.6%; αa=1.138: 91.9% (k=Ec×εcp/fc=1.0537) |
| 1 | C4_ADAPTED_LB | IMPLEMENTED | `03_MATERIALS\tables\B1_C4_ADAPTED_LB_compression.csv` | PASS | ADAPTED eps_c0: 0.003654 vs ecp_rep=0.00350 (+4.4%); k=1.0537; eps_in_peak=3.32e-04; αa=1.1 αd=0.193 [SECONDARY source] |
| 1 | C4_ADAPTED_UB | IMPLEMENTED | `03_MATERIALS\tables\B1_C4_ADAPTED_UB_compression.csv` | PASS | ADAPTED eps_c0: 0.003780 vs ecp_rep=0.00350 (+8.0%); k=1.0537; eps_in_peak=4.58e-04; αa=1.138 αd=0.312 [SECONDARY source] |
| 2 | REF_POPOVICS | DEGENERATE | — | PASS | DEGENERATE: alpha = Ec*ecp/fc = 0.9880 <= 1.0; Popovics model invalid for Batch 2. Use C1-C4 (REVIEW_REQUIRED) instead. |
| 2 | C1 | IMPLEMENTED | `03_MATERIALS\tables\B2_C1_compression.csv` | PASS | Post-peak branch (15 pts) is ADOPTED (C1: Fakeh Eq.9 M=7061.5×λf^-0.411 with ASSUMED fiber dims l=13mm df=0.2mm; REF_POPOVICS: linear descent placeholder).; CHANGELOG C-001: eps_in,peak clipped from -3.9e-5 → 0 (FE approximation, 1.2% deviation, within scatter). |
| 2 | C2 | IMPLEMENTED | `03_MATERIALS\tables\B2_C2_compression.csv` | PASS | CHANGELOG C-001: eps_in,peak clipped from -3.9e-5 → 0 (FE approximation, 1.2% deviation, within scatter). |
| 2 | C3 | BLOCKED | — | PASS | BLOCKED: Ascending parabolic model (initial slope = 2×f_peak/ε0 >> Ec). εin = ε − σ/Ec < 0 for ~94–100% of ascending branch in all 3 batches (Wang Eq.7 ε0; B1:~96.6%, B2:~93.9%, B3:100%). Expert engineering decision required before generating CDP table. A rewritten ascending branch is a different hybrid law — use new model ID.; εin analysis: α_Wang=1.0607; η_cross=0.9393; εin<0 on 93.9% of ascending; εin_peak=1.97e-04; ε0_Wang=0.00344; ε20=0.00731 |
| 2 | C4 | BLOCKED | — | PASS | BLOCKED: Ascending rational formula: initial tangent αa×fc/εc0 > Ec for all batches (αa ∈ [1.1,1.138]; k=Ec×εcp/fc ≈ 0.988–1.091). εin < 0 for ~49–100% of ascending branch (batch/αa-dependent). αa, αd are parameter ranges only from secondary source (Fakeh Table 3); no unique calibration for Hosseini batches without Yan (2010) original paper.; εin<0 on ascending: αa=1.1: 100.0%; αa=1.138: 100.0% (k=Ec×εcp/fc=0.9880) |
| 2 | C4_ADAPTED_LB | IMPLEMENTED | `03_MATERIALS\tables\B2_C4_ADAPTED_LB_compression.csv` | PASS | CHANGELOG C-001: eps_in,peak clipped from -3.9e-5 → 0 (FE approximation, 1.2% deviation, within scatter).; ADAPTED eps_c0: 0.003563 vs ecp_rep=0.00320 (+11.3%); k=0.9880; eps_in_peak=3.24e-04; αa=1.1 αd=0.193 [SECONDARY source] |
| 2 | C4_ADAPTED_UB | IMPLEMENTED | `03_MATERIALS\tables\B2_C4_ADAPTED_UB_compression.csv` | PASS | CHANGELOG C-001: eps_in,peak clipped from -3.9e-5 → 0 (FE approximation, 1.2% deviation, within scatter).; ADAPTED eps_c0: 0.003686 vs ecp_rep=0.00320 (+15.2%); k=0.9880; eps_in_peak=4.47e-04; αa=1.138 αd=0.312 [SECONDARY source] |
| 3 | REF_POPOVICS | IMPLEMENTED_REFERENCE | `03_MATERIALS\tables\B3_REF_POPOVICS_compression.csv` | PASS | Post-peak branch (15 pts) is ADOPTED (C1: Fakeh Eq.9 M=7061.5×λf^-0.411 with ASSUMED fiber dims l=13mm df=0.2mm; REF_POPOVICS: linear descent placeholder). |
| 3 | C1 | IMPLEMENTED | `03_MATERIALS\tables\B3_C1_compression.csv` | PASS | Post-peak branch (15 pts) is ADOPTED (C1: Fakeh Eq.9 M=7061.5×λf^-0.411 with ASSUMED fiber dims l=13mm df=0.2mm; REF_POPOVICS: linear descent placeholder). |
| 3 | C2 | IMPLEMENTED | `03_MATERIALS\tables\B3_C2_compression.csv` | PASS | — |
| 3 | C3 | BLOCKED | — | PASS | BLOCKED: Ascending parabolic model (initial slope = 2×f_peak/ε0 >> Ec). εin = ε − σ/Ec < 0 for ~94–100% of ascending branch in all 3 batches (Wang Eq.7 ε0; B1:~96.6%, B2:~93.9%, B3:100%). Expert engineering decision required before generating CDP table. A rewritten ascending branch is a different hybrid law — use new model ID.; εin analysis: α_Wang=0.9713; η_cross=1.0287; εin<0 on 100.0% of ascending; εin_peak=-1.05e-04; ε0_Wang=0.00356; ε20=0.00804 |
| 3 | C4 | BLOCKED | — | PASS | BLOCKED: Ascending rational formula: initial tangent αa×fc/εc0 > Ec for all batches (αa ∈ [1.1,1.138]; k=Ec×εcp/fc ≈ 0.988–1.091). εin < 0 for ~49–100% of ascending branch (batch/αa-dependent). αa, αd are parameter ranges only from secondary source (Fakeh Table 3); no unique calibration for Hosseini batches without Yan (2010) original paper.; εin<0 on ascending: αa=1.1: 48.6%; αa=1.138: 78.7% (k=Ec×εcp/fc=1.0913) |
| 3 | C4_ADAPTED_LB | IMPLEMENTED | `03_MATERIALS\tables\B3_C4_ADAPTED_LB_compression.csv` | PASS | ADAPTED eps_c0: 0.004032 vs ecp_rep=0.00400 (+0.8%); k=1.0913; eps_in_peak=3.67e-04; αa=1.1 αd=0.193 [SECONDARY source] |
| 3 | C4_ADAPTED_UB | IMPLEMENTED | `03_MATERIALS\tables\B3_C4_ADAPTED_UB_compression.csv` | PASS | ADAPTED eps_c0: 0.004171 vs ecp_rep=0.00400 (+4.3%); k=1.0913; eps_in_peak=5.06e-04; αa=1.138 αd=0.312 [SECONDARY source] |

## Tension tables

| Batch | Model | Status | CSV | QA | Notes |
|-------|-------|--------|-----|----|-------|
| 1 | REF_BILINEAR | IMPLEMENTED_REFERENCE | `03_MATERIALS\tables\B1_REF_BILINEAR_tension.csv` | PASS | REVIEW_REQUIRED: post-localization softening (σ–w) not available. Gauge length GL=700mm converts avg tensile strain to displacement but does NOT give localized crack opening width. σ–w requires localization length lc (mesh-dependent) or experimental crack opening data. Do NOT use w = et_loc × GL as default conversion. Fakeh (2025) Eq.8: λclc = 2.078×ft + 50.21 [mm]; wtu = εtu×λclc; wto = εt0×lc (lc unknown at G1). |
| 1 | T1 | IMPLEMENTED | `03_MATERIALS\tables\B1_T1_tension.csv` | PASS | BLOCKED_MISSING_PARAM: Tian post-peak σ(ε) = ft×(1−0.15×(ε−εt0)/(εu−εt0)) requires εu (strain at 0.85×ft on descending). εu not in Hosseini (2026) Table 2; Tian (2023) paper not in 01_SOURCES/02_SECONDARY_REFERENCE. Fakeh σ–w extension (to 0.2×ft) also needs lc (mesh-size, unknown at G1). Do NOT use w = et_loc × GL_gauge (gauge length ≠ localization length). Fakeh (2025) Eq.8: λclc = 2.078×ft + 50.21 [mm]; wtu = εtu×λclc; wto = εt0×lc (lc unknown). |
| 1 | T2 | IMPLEMENTED | `03_MATERIALS\tables\B1_T2_tension.csv` | PASS | IMPLEMENTED (σ–εck, mesh-dependent): Zhao power law σ=ft×(εt0/ε)^0.6, terminal at 0.2×ft (εtu≈0.0731). MESH DEPENDENCY WARNING: post-peak σ–εck is mesh-size dependent. Fakeh (2025) σ–w: λclc=2.078×10.0+50.21=71.0mm; wtu=εtu×λclc≈5.2mm; wto=εt0×lc (lc unknown at G1). Do NOT use w=et_loc×GL (gauge length ≠ localization length). |
| 2 | REF_BILINEAR | IMPLEMENTED_REFERENCE | `03_MATERIALS\tables\B2_REF_BILINEAR_tension.csv` | PASS | REVIEW_REQUIRED: post-localization softening (σ–w) not available. Gauge length GL=700mm converts avg tensile strain to displacement but does NOT give localized crack opening width. σ–w requires localization length lc (mesh-dependent) or experimental crack opening data. Do NOT use w = et_loc × GL as default conversion. Fakeh (2025) Eq.8: λclc = 2.078×ft + 50.21 [mm]; wtu = εtu×λclc; wto = εt0×lc (lc unknown at G1). |
| 2 | T1 | IMPLEMENTED | `03_MATERIALS\tables\B2_T1_tension.csv` | PASS | BLOCKED_MISSING_PARAM: Tian post-peak σ(ε) = ft×(1−0.15×(ε−εt0)/(εu−εt0)) requires εu (strain at 0.85×ft on descending). εu not in Hosseini (2026) Table 2; Tian (2023) paper not in 01_SOURCES/02_SECONDARY_REFERENCE. Fakeh σ–w extension (to 0.2×ft) also needs lc (mesh-size, unknown at G1). Do NOT use w = et_loc × GL_gauge (gauge length ≠ localization length). Fakeh (2025) Eq.8: λclc = 2.078×ft + 50.21 [mm]; wtu = εtu×λclc; wto = εt0×lc (lc unknown). |
| 2 | T2 | IMPLEMENTED | `03_MATERIALS\tables\B2_T2_tension.csv` | PASS | IMPLEMENTED (σ–εck, mesh-dependent): Zhao power law σ=ft×(εt0/ε)^0.6, terminal at 0.2×ft (εtu≈0.0731). MESH DEPENDENCY WARNING: post-peak σ–εck is mesh-size dependent. Fakeh (2025) σ–w: λclc=2.078×9.3+50.21=69.5mm; wtu=εtu×λclc≈5.1mm; wto=εt0×lc (lc unknown at G1). Do NOT use w=et_loc×GL (gauge length ≠ localization length). |
| 3 | REF_BILINEAR | IMPLEMENTED_REFERENCE | `03_MATERIALS\tables\B3_REF_BILINEAR_tension.csv` | PASS | REVIEW_REQUIRED: post-localization softening (σ–w) not available. Gauge length GL=500mm converts avg tensile strain to displacement but does NOT give localized crack opening width. σ–w requires localization length lc (mesh-dependent) or experimental crack opening data. Do NOT use w = et_loc × GL as default conversion. Fakeh (2025) Eq.8: λclc = 2.078×ft + 50.21 [mm]; wtu = εtu×λclc; wto = εt0×lc (lc unknown at G1). |
| 3 | T1 | IMPLEMENTED | `03_MATERIALS\tables\B3_T1_tension.csv` | PASS | BLOCKED_MISSING_PARAM: Tian post-peak σ(ε) = ft×(1−0.15×(ε−εt0)/(εu−εt0)) requires εu (strain at 0.85×ft on descending). εu not in Hosseini (2026) Table 2; Tian (2023) paper not in 01_SOURCES/02_SECONDARY_REFERENCE. Fakeh σ–w extension (to 0.2×ft) also needs lc (mesh-size, unknown at G1). Do NOT use w = et_loc × GL_gauge (gauge length ≠ localization length). Fakeh (2025) Eq.8: λclc = 2.078×ft + 50.21 [mm]; wtu = εtu×λclc; wto = εt0×lc (lc unknown). |
| 3 | T2 | IMPLEMENTED | `03_MATERIALS\tables\B3_T2_tension.csv` | PASS | IMPLEMENTED (σ–εck, mesh-dependent): Zhao power law σ=ft×(εt0/ε)^0.6, terminal at 0.2×ft (εtu≈0.0395). MESH DEPENDENCY WARNING: post-peak σ–εck is mesh-size dependent. Fakeh (2025) σ–w: λclc=2.078×7.5+50.21=65.8mm; wtu=εtu×λclc≈2.6mm; wto=εt0×lc (lc unknown at G1). Do NOT use w=et_loc×GL (gauge length ≠ localization length). |

---

## Blockers

### BLOCKED models (source equations available; raw σ–ε plots generated; CDP table blocked)

| Model | Source | Blocker summary | εin<0 on ascending | Resolution |
|-------|--------|-----------------|---------------------|------------|
| C3 | Wang (2016) Adv Mech Eng 8(2) — PRIMARY ✓ | Initial slope 2×fp/ε0 >> Ec (Wang Eq.7 ε0). ε20 from Eq.10-11 resolved. | B1:~96.6%, B2:~93.9%, B3:100% | Expert decision on ascending branch hybrid law |
| C4 | Yan (2010) via Fakeh (2025) Table 3 — SECONDARY | αa∈[1.1,1.138] > k≈0.988–1.091 for all batches. αa/αd are ranges only. | αa=1.1: B1:89.6%, B2:100%, B3:48.9%; αa=1.138: B1:91.9%, B2:100%, B3:78.8% | Yan (2010) original paper + engineering decision |

### BLOCKED softening (hardening tables generated; post-peak unavailable)

| Model | Blocker | Resolution required |
|-------|---------|---------------------|
| T1 | εu (ultimate strain at 0.85×ft) not in Hosseini 2026; Tian (2023) paper not in sources | Tian (2023) paper |

### Mesh-dependent softening (implemented but mesh-dependent)

| Model | Note |
|-------|------|
| T2 | Zhao σ–εck post-peak implemented; mesh-dependent. Fakeh σ–w conversion available when lc is set. |

**Batch 2 Popovics degeneracy:** alpha = Ec·εcp/f'c = 47300×0.0032/153.2 = 0.988 < 1.
C1 and C2 implemented for Batch 2. CHANGELOG C-001: peak eps_in clip approved.

**Fiber dimensions ASSUMED:** l=13mm, df=0.2mm (not in Hosseini 2026).
C1 post-peak slope M and T1 λf-based formulas use ASSUMED fiber dimensions.
Confirm fiber specifications before using C1 post-peak for structural analysis.

### C4_YAN_EC_ADAPTED — peak strain deviation from reported ecp

eps_c0_model = αa × fc / Ec (ADAPTED; initial tangent = Ec exactly by construction).  
Deviation from reported ecp: ratio = αa / k  where k = Ec × ecp / fc.

| Batch | fc (MPa) | Ec (MPa) | ecp (rep.) | k | αa=1.100: eps_c0 | dev% | αa=1.138: eps_c0 | dev% |
|-------|---------|---------|-----------|---|----------------|------|----------------|------|
| B1 | 152.8 | 46000 | 0.0035 | 1.054 | 0.003652 | +4.3% | 0.003782 | +8.1% |
| B2 | 153.2 | 47300 | 0.0032 | 0.988 | 0.003565 | +11.4% | 0.003687 | +15.2% |
| B3 | 166.4 | 45400 | 0.0040 | 1.091 | 0.004028 | +0.7% | 0.004172 | +4.3% |

**C3 Wang — excluded from Abaqus FE matrix (theoretical reference only).**  
Engineering decision 2026-10-17: C3 Wang not compatible with Ec_reported for Abaqus CDP.
Raw σ–ε curves retained for comparison. Requires expert decision before FE inclusion.

---

## G1 gate conditions

G1=PASS requires ALL of:
1. C3/C4 BLOCKED resolved (expert decision on ascending εin + source papers)
2. T1 softening resolved (Tian 2023 paper + εu confirmed)
3. All tables that generate must QA PASS (currently: C1,C2,T1,T2 = 12 tables)
4. Softening decision for T1/T2 documented (σ–w vs σ–εck)
5. Fiber dimensions confirmed or ASSUMED flag escalated
6. This report updated with PASS verdict by project engineer

**G1 gate is currently HOLD.**

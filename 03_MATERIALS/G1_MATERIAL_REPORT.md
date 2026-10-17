# G1 Material Table Report

**Generated:** 2026-10-17  
**Gate:** G1_MATERIAL_TABLE_VALID — HOLD (pending source papers for C1-C4, T1-T2)  
**solver_authorized:** false  

---

## Summary

- **BLOCKED:** 6
- **DEGENERATE:** 1
- **IMPLEMENTED:** 12
- **IMPLEMENTED_REFERENCE:** 5

## Compression tables

| Batch | Model | Status | CSV | QA | Notes |
|-------|-------|--------|-----|----|-------|
| 1 | REF_POPOVICS | IMPLEMENTED_REFERENCE | `03_MATERIALS\tables\B1_REF_POPOVICS_compression.csv` | PASS | Post-peak branch (15 pts) is ADOPTED (C1: Fakeh Eq.9 M=7061.5×λf^-0.411 with ASSUMED fiber dims l=13mm df=0.2mm; REF_POPOVICS: linear descent placeholder). |
| 1 | C1 | IMPLEMENTED | `03_MATERIALS\tables\B1_C1_compression.csv` | PASS | Post-peak branch (15 pts) is ADOPTED (C1: Fakeh Eq.9 M=7061.5×λf^-0.411 with ASSUMED fiber dims l=13mm df=0.2mm; REF_POPOVICS: linear descent placeholder). |
| 1 | C2 | IMPLEMENTED | `03_MATERIALS\tables\B1_C2_compression.csv` | PASS | — |
| 1 | C3 | BLOCKED | — | PASS | BLOCKED: Ascending parabolic model (initial slope = 2f'c/εc0 >> Ec) gives negative εin for >50% of ascending branch in all 3 batches. Additionally, parameter ε20 (descending endpoint) not defined in Fakeh (2025) Table 3 — requires Wang (2016) original paper. |
| 1 | C4 | BLOCKED | — | PASS | BLOCKED: Yan ascending αa=1.1–1.138 > alpha≈0.988–1.091 for all batches. εin < 0 for 81–92% of the ascending branch. Additionally αa and αd given as ranges only; Yan (2010) paper not in sources. |
| 2 | REF_POPOVICS | DEGENERATE | — | PASS | DEGENERATE: alpha = Ec*ecp/fc = 0.9880 <= 1.0; Popovics model invalid for Batch 2. Use C1-C4 (REVIEW_REQUIRED) instead. |
| 2 | C1 | IMPLEMENTED | `03_MATERIALS\tables\B2_C1_compression.csv` | PASS | Post-peak branch (15 pts) is ADOPTED (C1: Fakeh Eq.9 M=7061.5×λf^-0.411 with ASSUMED fiber dims l=13mm df=0.2mm; REF_POPOVICS: linear descent placeholder).; CHANGELOG C-001: eps_in,peak clipped from -3.9e-5 → 0 (FE approximation, 1.2% deviation, within scatter). |
| 2 | C2 | IMPLEMENTED | `03_MATERIALS\tables\B2_C2_compression.csv` | PASS | CHANGELOG C-001: eps_in,peak clipped from -3.9e-5 → 0 (FE approximation, 1.2% deviation, within scatter). |
| 2 | C3 | BLOCKED | — | PASS | BLOCKED: Ascending parabolic model (initial slope = 2f'c/εc0 >> Ec) gives negative εin for >50% of ascending branch in all 3 batches. Additionally, parameter ε20 (descending endpoint) not defined in Fakeh (2025) Table 3 — requires Wang (2016) original paper. |
| 2 | C4 | BLOCKED | — | PASS | BLOCKED: Yan ascending αa=1.1–1.138 > alpha≈0.988–1.091 for all batches. εin < 0 for 81–92% of the ascending branch. Additionally αa and αd given as ranges only; Yan (2010) paper not in sources. |
| 3 | REF_POPOVICS | IMPLEMENTED_REFERENCE | `03_MATERIALS\tables\B3_REF_POPOVICS_compression.csv` | PASS | Post-peak branch (15 pts) is ADOPTED (C1: Fakeh Eq.9 M=7061.5×λf^-0.411 with ASSUMED fiber dims l=13mm df=0.2mm; REF_POPOVICS: linear descent placeholder). |
| 3 | C1 | IMPLEMENTED | `03_MATERIALS\tables\B3_C1_compression.csv` | PASS | Post-peak branch (15 pts) is ADOPTED (C1: Fakeh Eq.9 M=7061.5×λf^-0.411 with ASSUMED fiber dims l=13mm df=0.2mm; REF_POPOVICS: linear descent placeholder). |
| 3 | C2 | IMPLEMENTED | `03_MATERIALS\tables\B3_C2_compression.csv` | PASS | — |
| 3 | C3 | BLOCKED | — | PASS | BLOCKED: Ascending parabolic model (initial slope = 2f'c/εc0 >> Ec) gives negative εin for >50% of ascending branch in all 3 batches. Additionally, parameter ε20 (descending endpoint) not defined in Fakeh (2025) Table 3 — requires Wang (2016) original paper. |
| 3 | C4 | BLOCKED | — | PASS | BLOCKED: Yan ascending αa=1.1–1.138 > alpha≈0.988–1.091 for all batches. εin < 0 for 81–92% of the ascending branch. Additionally αa and αd given as ranges only; Yan (2010) paper not in sources. |

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

### BLOCKED models (equations available; technical/data issue prevents valid table)

| Model | Blocker | Resolution required |
|-------|---------|---------------------|
| C3 | Ascending parabolic: initial slope 2f'c/εc0 >> Ec → εin < 0 for >50% of ascending (all batches). ε20 unknown. | Expert engineering decision + Wang (2016) paper |
| C4 | αa=1.1–1.138 > alpha≈0.988–1.091 → εin < 0 for 81–92% of ascending. αa/αd ranges only. | Expert engineering decision + Yan (2010) paper |

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

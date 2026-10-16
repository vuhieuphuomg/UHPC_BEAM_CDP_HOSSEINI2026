# G1 Material Table Report

**Generated:** 2026-10-17  
**Gate:** G1_MATERIAL_TABLE_VALID — HOLD (pending source papers for C1-C4, T1-T2)  
**solver_authorized:** false  

---

## Summary

- **DEGENERATE:** 1
- **IMPLEMENTED_REFERENCE:** 5
- **REVIEW_REQUIRED:** 18

## Compression tables

| Batch | Model | Status | CSV | QA | Notes |
|-------|-------|--------|-----|----|-------|
| 1 | REF_POPOVICS | IMPLEMENTED_REFERENCE | `03_MATERIALS\tables\B1_REF_POPOVICS_compression.csv` | PASS | Post-peak branch (15 pts) is ADOPTED (linear descent placeholder — not from source paper). Replace at G1 when C1 source equations are available. |
| 1 | C1 | REVIEW_REQUIRED | — | PASS | REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE |
| 1 | C2 | REVIEW_REQUIRED | — | PASS | REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE |
| 1 | C3 | REVIEW_REQUIRED | — | PASS | REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE |
| 1 | C4 | REVIEW_REQUIRED | — | PASS | REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE |
| 2 | REF_POPOVICS | DEGENERATE | — | PASS | DEGENERATE: alpha = Ec*ecp/fc = 0.9880 <= 1.0; Popovics model invalid for Batch 2. Use C1-C4 (REVIEW_REQUIRED) instead. |
| 2 | C1 | REVIEW_REQUIRED | — | PASS | REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE |
| 2 | C2 | REVIEW_REQUIRED | — | PASS | REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE |
| 2 | C3 | REVIEW_REQUIRED | — | PASS | REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE |
| 2 | C4 | REVIEW_REQUIRED | — | PASS | REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE |
| 3 | REF_POPOVICS | IMPLEMENTED_REFERENCE | `03_MATERIALS\tables\B3_REF_POPOVICS_compression.csv` | PASS | Post-peak branch (15 pts) is ADOPTED (linear descent placeholder — not from source paper). Replace at G1 when C1 source equations are available. |
| 3 | C1 | REVIEW_REQUIRED | — | PASS | REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE |
| 3 | C2 | REVIEW_REQUIRED | — | PASS | REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE |
| 3 | C3 | REVIEW_REQUIRED | — | PASS | REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE |
| 3 | C4 | REVIEW_REQUIRED | — | PASS | REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE |

## Tension tables

| Batch | Model | Status | CSV | QA | Notes |
|-------|-------|--------|-----|----|-------|
| 1 | REF_BILINEAR | IMPLEMENTED_REFERENCE | `03_MATERIALS\tables\B1_REF_BILINEAR_tension.csv` | PASS | REVIEW_REQUIRED: post-localization softening (σ-w) not in paper. Batch GL=700mm; crack opening w = et_loc × GL = 3.5mm at localization. Provide Gf or σ-w curve to complete softening branch. |
| 1 | T1 | REVIEW_REQUIRED | — | PASS | REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE |
| 1 | T2 | REVIEW_REQUIRED | — | PASS | REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE |
| 2 | REF_BILINEAR | IMPLEMENTED_REFERENCE | `03_MATERIALS\tables\B2_REF_BILINEAR_tension.csv` | PASS | REVIEW_REQUIRED: post-localization softening (σ-w) not in paper. Batch GL=700mm; crack opening w = et_loc × GL = 3.5mm at localization. Provide Gf or σ-w curve to complete softening branch. |
| 2 | T1 | REVIEW_REQUIRED | — | PASS | REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE |
| 2 | T2 | REVIEW_REQUIRED | — | PASS | REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE |
| 3 | REF_BILINEAR | IMPLEMENTED_REFERENCE | `03_MATERIALS\tables\B3_REF_BILINEAR_tension.csv` | PASS | REVIEW_REQUIRED: post-localization softening (σ-w) not in paper. Batch GL=500mm; crack opening w = et_loc × GL = 1.4mm at localization. Provide Gf or σ-w curve to complete softening branch. |
| 3 | T1 | REVIEW_REQUIRED | — | PASS | REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE |
| 3 | T2 | REVIEW_REQUIRED | — | PASS | REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE |

---

## Blockers / REVIEW_REQUIRED items

The following source papers are required to build G1-compliant tables.
Add PDFs to `01_SOURCES/02_SECONDARY_REFERENCE/` and implement equations.

| Model | Paper | Required for |
|-------|-------|-------------|
| C1 | Graybeal (FHWA) + Fakeh et al. (2025) | Compression Batch 1,2,3 |
| C2 | Zhao et al. (2013) | Compression Batch 1,2,3 |
| C3 | Wang et al. (2016) | Compression Batch 1,2,3 |
| C4 | Yan (2010) | Compression Batch 1,2,3 |
| T1 | Tian et al. (2023) + Fakeh et al. (2025) | Tension Batch 1,2,3 |
| T2 | Zhao et al. (2013) | Tension Batch 1,2,3 |

**Batch 2 Popovics degeneracy:** alpha = Ec·εcp/f'c = 47300×0.0032/153.2 = 0.988 < 1.
C1-C4 (nonlinear ascending) required for Batch 2 compression.
CHANGELOG C-001: peak eps_in clipped 0 (FE approximation) — does NOT validate C1 curve.

**Softening:** post-localization σ-w data not in Hosseini 2026.
Tension tables contain hardening branch only. Softening REVIEW_REQUIRED.

---

## G1 gate conditions

G1=PASS requires ALL of:
1. Source papers for C1-C4, T1-T2 loaded and equations verified
2. All 18 tables (3 batches × 6 models) generate with QA PASS
3. All eps_in ≥ 0, non-decreasing (Batch 2 C1 must be checked explicitly)
4. Softening branch (or explicit decision to use no-softening) documented
5. This report updated with PASS verdict by project engineer

**G1 gate is currently HOLD.**

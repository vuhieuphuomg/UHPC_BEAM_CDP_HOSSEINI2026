# G0 SOURCE AUDIT — HOSSEINI ET AL. (2026)
**Project:** UHPC_BEAM_CDP_HOSSEINI2026 V5  
**Source:** Hosseini S.M., Quan Z., Shao Y. "Enhancing shear performance in UHPC beams through strategic fiber and stirrup integration." *Engineering Structures* 348 (2026) 121810. DOI: 10.1016/j.engstruct.2025.121810  
**Audited:** 2026-10-17 by Claude Code (session G0)  
**Status:** PARTIAL — Figure 1 visual (images) not accessible via text extraction; geometry/support/rebar positions NOT_REPORTED from text alone.

---

## 1. OVERALL BEAM GEOMETRY (Cross-section and length)

| Item | Value | Tag | Evidence |
|------|-------|-----|----------|
| Total beam length | 5000 mm | REPORTED | Section 2.1, p. 3 |
| Web width | 180 mm | REPORTED | Section 2.1, p. 3 |
| Overall height | 500 mm | REPORTED | Section 2.1, p. 3 |
| Flange width | 400 mm | REPORTED | Section 2.1, p. 3 |
| Flange thickness | 100 mm | REPORTED | Section 2.1, p. 3 |
| Effective depth d | 410 mm (all specimens) | REPORTED | Table 1 footnote, p. 3 |
| Shear span a/d=1.7 | a = 1.7 × 410 = **697 mm** | DERIVED | Table 1 note + geometry |
| Shear span a/d=2.7 | a = 2.7 × 410 = **1107 mm** | DERIVED | Table 1 note + geometry |

**NOT_REPORTED (NEEDS_EXPERT_REVIEW — Figure 1 visual inspection required):**
- Exact support center coordinates (distance from beam ends)
- Clear span between supports
- Load plate dimensions and exact position
- Support plate dimensions

---

## 2. LONGITUDINAL REINFORCEMENT

| Item | Value | Tag | Evidence |
|------|-------|-----|----------|
| Bottom bars | 6 bundled MMFX Grade 4100 **M#10** (32.3 mm dia) | REPORTED | Section 2.1, p. 3; Table 3, p. 6 |
| Bottom fy | 690 MPa | REPORTED | Table 3, p. 6 |
| Bottom fu | 1160 MPa | REPORTED | Table 3, p. 6 |
| Bottom Es | 200 GPa | REPORTED | Table 3, p. 6 |
| Top bars (text) | 2 MMFX Grade 4100 **M#4** (12.7 mm dia) | REPORTED (text) | Section 2.1, p. 3; Table 3, p. 6 |
| Top bars (Figure 1) | Possibly **M#3** (9.5 mm dia) — UNCONFIRMED | NOT_REPORTED | Figure 1, p. 5 (image, not text-extractable) |
| Top M#4 fy | 684 MPa | REPORTED | Table 3, p. 6 |
| Top M#4 fu | 1142 MPa | REPORTED | Table 3, p. 6 |
| Top M#4 Es | 196 GPa | REPORTED | Table 3, p. 6 |
| M#3 fy | 684 MPa (**assumed = M#4**, no test data) | REPORTED with caveat | Table 3 note, p. 6 |
| M#3 diameter | 9.5 mm | REPORTED | Table 3, p. 6 |

**CONFLICT — NEEDS_EXPERT_REVIEW:**  
Section 2.1 text (p. 3) says top bars are **M#4** (12.7 mm dia). BLOCKERS.md and ENGINEERING_OPEN_ITEMS_V5.md flag that Figure 1 **may show M#3**. Visual inspection of Figure 1 (PDF page 5, image only) required to resolve. Table 3 note confirms M#3 test data was unavailable and M#4 properties were assumed.

**NOT_REPORTED (NEEDS_EXPERT_REVIEW):**
- Bar center coordinates (concrete cover, bundle arrangement for 6-M#10 at bottom)
- Distance from bottom fiber to centroid of 6-bundle group (to verify d = 410 mm)

---

## 3. TRANSVERSE REINFORCEMENT (STIRRUPS)

| Item | Value | Tag | Evidence |
|------|-------|-----|----------|
| NSS stirrups | 10M Grade 500 (11.3 mm dia), fy=463 MPa, fu=600 MPa, Es=208 GPa | REPORTED | Table 3, p. 6 |
| HSS stirrups | MMFX Grade 4100, fsy=684 MPa (M#3 assumed) | REPORTED | Table 1, Table 3, p. 6 |
| Stirrup spacing | d/2 (maximum ACI 318 limit) = **205 mm** (nominal) | DERIVED | Section 3.3.2, p. 12: "stirrups spaced at maximum permitted limit (d/2)" |
| Stirrup size (HSS) | M#3 (9.5mm dia) likely for stirrups (smaller member bar) | PROBABLE | Table 3 note says M#3 used, no tests done |
| Stirrup size (NSS) | 10M (11.3mm dia) | REPORTED | Table 3, p. 6 |

**NOT_REPORTED (NEEDS_EXPERT_REVIEW):**
- Exact stirrup spacing in tested zone vs untested zone
- Stirrup layout detail from Figure 1 (visual)
- 5 vertical cages in untested span (size and spacing)

---

## 4. TEST MATRIX — BATCH ASSIGNMENTS (Table 1)

Complete specimen-to-batch mapping verified from Table 1 (p. 3):

| Specimen ID | B# | Vf | ρsv | Stirrup type | a/d | Batch |
|-------------|----|----|-----|-------------|-----|-------|
| Vf1-ρsv0%-1.7 | B01 | 1% | 0% | NONE | 1.7 | **#3** |
| Vf1-ρsv0%-2.7 | B02 | 1% | 0% | NONE | 2.7 | **#3** |
| Vf2-ρsv0%-1.7 | B03 | 2% | 0% | NONE | 1.7 | **#2** |
| Vf2-ρsv0%-2.7 | B04 | 2% | 0% | NONE | 2.7 | **#2** |
| Vf1-ρsv0.6%N-1.7 | B05 | 1% | 0.6% | NSS | 1.7 | **#3** |
| Vf1-ρsv0.6%N-2.7 | B06 | 1% | 0.6% | NSS | 2.7 | **#3** |
| Vf2-ρsv0.6%N-1.7 | B07 | 2% | 0.6% | NSS | 1.7 | **#1** |
| Vf2-ρsv0.6%N-2.7 | B08 | 2% | 0.6% | NSS | 2.7 | **#1** |
| Vf1-ρsv0.7%H-1.7 | B09 | 1% | 0.7% | HSS | 1.7 | **#3** |
| Vf1-ρsv0.7%H-2.7 | B10 | 1% | 0.7% | HSS | 2.7 | **#3** |
| Vf1-ρsv0.4%H-2.7 | B11 | 1% | 0.4% | HSS | 2.7 | **#3** |
| Vf1-ρsv0.5%H-2.7 | B12 | 1% | 0.5% | HSS | 2.7 | **#3** |

Tag: REPORTED (Table 1, p. 3). **Batch assignments in EXPERIMENT_TARGETS_REPORTED_V5.csv are consistent with Table 1.**

---

## 5. UHPC MATERIAL PROPERTIES (Table 2, p. 4)

| Batch | Vf | f'c (MPa) | Ec (GPa) | εcp (%) | ft,cr (MPa) | εt,cr (%) | ft,loc (MPa) | εt,loc (%) | ft,cr,inv (MPa) | fFu,inv (MPa) |
|-------|-----|-----------|---------|---------|-------------|----------|--------------|----------|----------------|--------------|
| 1 | 2% | 152.8±9.3 | 46.0±0.5 | 0.35±0.06 | 9.0±0.8 | 0.16±0.04 | 10.0±0.8 | 0.50±0.04 | 8.8±1.2 | 12.0±1.2 |
| 2 | 2% | 153.2±9.6 | 47.3±2.1 | 0.32±0.05 | 8.8±1.2 | 0.15±0.03 | 9.3±1.2 | 0.50±0.01 | 9.0±0.8 | 10.8±0.8 |
| 3 | 1% | 166.4±4.4 | 45.4±1.1 | 0.40±0.04 | 6.0±1.0 | 0.10±0.04 | 7.5±1.0 | 0.27±0.02 | 5.3±2.0 | 7.8±0.4 |

Tag: REPORTED (Table 2, p. 4)

**Note from paper:** Prismatic tensile specimens — Batch 1 & 2 used 50×50×700 mm (gauge length different from Batch 3 which used 50×50×500 mm). Direct comparison of εt requires gauge-length normalization. Tag: REPORTED caveat.

### Batch 2 CDP Inelastic Strain BLOCKER:
- εcp_Batch2 = 0.0032 (mean)
- Elastic strain at peak = f'c / Ec = 153.2 / 47300 = **0.003239** (MPa/MPa)
- Nominal inelastic strain at peak = εcp − fc/Ec = 0.0032 − 0.003239 = **−0.000039 (NEGATIVE)**
- **This is physically inadmissible in CDP.** Must NOT be auto-clipped. BLOCKER — see ENGINEERING_OPEN_ITEMS_V5.md #4.

### Batch 1 check:
- εcp_Batch1 = 0.0035; fc/Ec = 152.8/46000 = 0.003322; inelastic = 0.0035−0.003322 = **+0.000178** (positive, OK)

### Batch 3 check:
- εcp_Batch3 = 0.0040; fc/Ec = 166.4/45400 = 0.003666; inelastic = 0.0040−0.003666 = **+0.000334** (positive, OK)

---

## 6. STEEL REBAR PROPERTIES (Table 3, p. 6)

| Bar | Grade | Dia (mm) | fy (MPa) | fu (MPa) | Es (GPa) | Notes |
|-----|-------|---------|---------|---------|---------|-------|
| 10M | Grade 500 (NSS) | 11.3 | 463 | 600 | 208 | Stirrups (NSS beams) |
| M#3 | MMFX Grade 4100 (HSS) | 9.5 | 684* | 1142* | 196* | Stirrups (HSS beams); *assumed = M#4; no test data |
| M#4 | MMFX Grade 4100 | 12.7 | 684 | 1142 | 196 | Top bars (text) or stirrups |
| M#10 | MMFX Grade 4100 | 32.3 | 690 | 1160 | 200 | Bottom longitudinal bars |

Tag: REPORTED (Table 3, p. 6)

**Yield method:** 0.2% offset per ASTM A370. HSS does NOT have a defined yield plateau — constitutive curve beyond fy is strain-hardening. Full postyield curve NOT PROVIDED in paper. Tag: NOT_REPORTED for postyield hardening.

---

## 7. SHEAR FORCE CONVENTION AND STATICS

| Item | Value | Tag |
|------|-------|-----|
| Loading type | 3-point (monotonic quasi-static, 0.1 mm/s) | REPORTED (p. 3) |
| Vult reported | Maximum recorded shear capacity (kN) | REPORTED (Table 4 header, p. 10) |
| Vult = shear in shear span | Yes — Vult equals reaction at near support | DERIVED (3-point statics) |
| P_applied to Vult ratio | P × (L_span − a) / L_span = Vult → P = Vult × L_span / (L_span − a) | DERIVED |
| L_span (between supports) | NOT_REPORTED — needs Figure 1 | NOT_REPORTED |
| Support positions | NOT_REPORTED — needs Figure 1 | NOT_REPORTED |

**Note:** For FE modeling, the exact position of supports and load relative to beam ends must come from Figure 1 (visual). The text gives total length = 5000 mm and shear span = a, but the clear span L_span between supports is NOT stated in text.

---

## 8. B11 SPECIAL SUPPORT CONDITION (Vf1-ρsv0.4%H-2.7)

| Item | Value | Tag |
|------|-------|-----|
| Special support stated | Yes — "modified support arrangement" | REPORTED (Fig. 1 caption, p. 5; Table 4 note, p. 10) |
| Effect on stiffness | Stiffness not comparable to other a/d=2.7 specimens | REPORTED (Fig. 7 note, p. 10) |
| Exact support topology | NOT_REPORTED — in Figure 1(c) image only | NOT_REPORTED |
| Vult comparability | Vult still reported but stiffness results affected | REPORTED |

**NEEDS_EXPERT_REVIEW:** Figure 1(c) shows the B11 modified support arrangement. Must be reviewed visually to define correct FE boundary conditions. Do NOT assume roller+pin same as other specimens.

---

## 9. EXPERIMENTAL RESULTS SUMMARY (Table 4, p. 10)

All 12 Vult values confirmed from Table 4. Mapping to B01–B12 as per Section 4 above verified.

| B# | Vult (kN) | δult (mm) | θave (°) | FM | εc,ult (με) | B11 note |
|----|-----------|----------|---------|-----|------------|---------|
| B01 | 884 | 7.9 | 38 | DC+SC | -902 | — |
| B02 | 478 | 12.7 | 29 | DT | -1091 | — |
| B03 | 1241 | 14.6 | 44 | DC+SC | -1023 | — |
| B04 | 862 | 29.6 | 30 | DT+DC+SC | -1551 | — |
| B05 | 1358 | 14.1 | 34 | DC+SC | -2082 | — |
| B06 | 888 | 30.0 | 28 | DT+DC+SC | -2491 | — |
| B07 | 1534 | 18.9 | 37 | DC+SC | -2140 | — |
| B08 | 1092 | 38.9 | 29 | DT+DC+SC | -4203 | — |
| B09 | 1600 | 15.8 | 44 | DC+SC | -3595 | — |
| B10 | 1156 | 35.9 | 45 | DC+FL | -4348 | — |
| B11 | 1125 | 23.1 | 30 | DC+FL | -3149 | SPECIAL SUPPORT |
| B12 | 1134 | 38.3 | 37 | DC+FL | -3445 | — |

Tag: REPORTED (Table 4, p. 10)

---

## 10. ITEMS REQUIRING EXPERT REVIEW (SUMMARY)

| # | Item | Priority |
|---|------|---------|
| 1 | Figure 1 visual: support coordinates, load position, span | CRITICAL |
| 2 | Figure 1 visual: top bar M#3 vs M#4 confirmation | CRITICAL |
| 3 | Figure 1(c): B11 modified support exact topology | CRITICAL |
| 4 | Batch 2 negative inelastic strain — CDP reconstruction | BLOCKER |
| 5 | Bar centroid for 6-bundle M#10 to verify d=410 mm | HIGH |
| 6 | Full postyield curves for MMFX M#10, M#4, M#3 | HIGH |
| 7 | Tensile gauge length normalization Batch 1/2 vs 3 | MEDIUM |
| 8 | Stirrup exact spacing in FE model zone | MEDIUM |

**Do NOT set G0 = PASS until items 1, 2, 3, 4 are resolved with expert review.**

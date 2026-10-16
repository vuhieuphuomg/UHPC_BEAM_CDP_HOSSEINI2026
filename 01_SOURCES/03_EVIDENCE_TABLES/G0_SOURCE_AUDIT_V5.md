# G0 SOURCE AUDIT — HOSSEINI ET AL. (2026)
**Project:** UHPC_BEAM_CDP_HOSSEINI2026 V5  
**Source:** Hosseini S.M., Quan Z., Shao Y. "Enhancing shear performance in UHPC beams through strategic fiber and stirrup integration." *Engineering Structures* 348 (2026) 121810. DOI: 10.1016/j.engstruct.2025.121810  
**Audited:** 2026-10-17 by Claude Code (session G0)  
**Status:** PARTIAL — BLOCKER-1/2/3 resolved 2026-10-17 from Figure 1 visual read; BLOCKER-4 (Batch 2 CDP negative inelastic strain) awaits expert decision before G0=PASS.

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

**CONFIRMED FROM FIGURE 1 (2026-10-17, PDF page 5 rendered as image):**

| Configuration | West support (from W end) | East support (from W end) | Load point (from W end) | Clear span L | Shear span a | Verification |
|---|---|---|---|---|---|---|
| a/d=2.7 (B02,B04,B06,B08,B10,B12) | 300 mm | 4700 mm | 1407 mm | 4400 mm | 1407−300=**1107 mm** | a/d=1107/410=**2.70 ✓** |
| a/d=1.7 (B01,B03,B05,B07,B09) | 1613 mm | 4700 mm | 4003 mm | 3087 mm | 4700−4003=**697 mm** | a/d=697/410=**1.70 ✓** |
| B11 (Vf1-ρsv0.4%H-2.7, special) | 1613 mm | 4700 mm | 3387 mm | 3087 mm | 4700−3387=**1313 mm** | a/d_eff=1313/410=**3.20** |

Load plate width: 300 mm. Support plate width: 300 mm.  
Tag: REPORTED (Figure 1(a)(b)(c), p. 5). Source: PDF rendered 2026-10-17.

---

## 2. LONGITUDINAL REINFORCEMENT

| Item | Value | Tag | Evidence |
|------|-------|-----|----------|
| Bottom bars | 6 bundled MMFX Grade 4100 **M#10** (32.3 mm dia) | REPORTED | Section 2.1, p. 3; Table 3, p. 6 |
| Bottom fy | 690 MPa | REPORTED | Table 3, p. 6 |
| Bottom fu | 1160 MPa | REPORTED | Table 3, p. 6 |
| Bottom Es | 200 GPa | REPORTED | Table 3, p. 6 |
| Top bars (text) | 2 MMFX Grade 4100 **M#4** (12.7 mm dia) — **TEXT ERROR** | REPORTED (text, error) | Section 2.1, p. 3 |
| Top bars (Figure 1) | 2 MMFX Grade 4100 **M#3** (9.5 mm dia) — **CONFIRMED** | REPORTED (Figure 1) | Figure 1 A-A cross-section, p. 5, rendered 2026-10-17 |
| Top M#4 fy | 684 MPa | REPORTED | Table 3, p. 6 |
| Top M#4 fu | 1142 MPa | REPORTED | Table 3, p. 6 |
| Top M#4 Es | 196 GPa | REPORTED | Table 3, p. 6 |
| M#3 fy | 684 MPa (**assumed = M#4**, no test data) | REPORTED with caveat | Table 3 note, p. 6 |
| M#3 diameter | 9.5 mm | REPORTED | Table 3, p. 6 |

**RESOLVED (2026-10-17):**  
Figure 1 A-A section explicitly labels top bars as **M#3 (Ø10)** — i.e., M#3 at nominal 9.5 mm. The paper text (Section 2.1, p. 3) stating "M#4" is an error. Figure 1 is the primary geometric drawing and is authoritative. Use M#3 (9.5 mm dia, As=2×70.9=141.8 mm²) for top bars. Table 3 note already confirms M#3 test data was unavailable and M#4 properties were assumed — those properties remain applicable.

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
| Stirrup spacing (exact, ρ=0.4% HSS) | **200 mm** | REPORTED | Figure 1 elevation, p. 5 |
| Stirrup spacing (exact, ρ=0.5% HSS) | **150 mm** | REPORTED | Figure 1 elevation, p. 5 |
| Stirrup spacing (exact, ρ=0.6% NSS) | **200 mm** | REPORTED | Figure 1 elevation, p. 5 |
| Stirrup spacing (exact, ρ=0.7% HSS) | **200 mm** | REPORTED | Figure 1 elevation, p. 5 |
| Stirrup size (HSS) | M#3 (9.5mm dia) likely for stirrups (smaller member bar) | PROBABLE | Table 3 note says M#3 used, no tests done |
| Stirrup size (NSS) | 10M (11.3mm dia) | REPORTED | Table 3, p. 6 |

**Remaining NOT_REPORTED:**
- Stirrup layout in untested zone (outside shear span) — 5 vertical cages
- Hook details, first stirrup from support face

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
| L_span a/d=2.7 | **4400 mm** (4700−300) | DERIVED (Figure 1) |
| L_span a/d=1.7 | **3087 mm** (4700−1613) | DERIVED (Figure 1) |
| West support a/d=2.7 | 300 mm from West beam end | REPORTED (Figure 1(a)) |
| East support (all configs) | 4700 mm from West beam end | REPORTED (Figure 1) |
| West support a/d=1.7 | 1613 mm from West beam end | REPORTED (Figure 1(b)) |
| Load point a/d=2.7 | 1407 mm from West end (near support = West, a=1107mm) | DERIVED (300+1107) |
| Load point a/d=1.7 | 4003 mm from West end (near support = East, a=697mm) | DERIVED (4700−697) |
| Vult statics a/d=2.7 | P×(4400−1107)/4400 = P×0.7484 | DERIVED |
| Vult statics a/d=1.7 | P×(3087−697)/3087 = P×0.7742 | DERIVED |

**CONFIRMED 2026-10-17:** Figure 1 read as image confirms support layout. Two distinct span configurations exist — the a/d=2.7 beams use a longer span (4400 mm) than the a/d=1.7 beams (3087 mm), not just a repositioned load.

---

## 8. B11 SPECIAL SUPPORT CONDITION (Vf1-ρsv0.4%H-2.7)

| Item | Value | Tag |
|------|-------|-----|
| Special support stated | Yes — "modified support arrangement" | REPORTED (Fig. 1 caption, p. 5; Table 4 note, p. 10) |
| Effect on stiffness | Stiffness not comparable to other a/d=2.7 specimens | REPORTED (Fig. 7 note, p. 10) |
| West support position | 1613 mm from West beam end | REPORTED (Figure 1(c)) |
| Load position | 3387 mm from West beam end | REPORTED (Figure 1(c)) |
| East support position | 4700 mm from West beam end | REPORTED (Figure 1(c)) |
| Effective shear span a_eff | 4700−3387 = **1313 mm** (load→East support) | DERIVED |
| a/d_eff | 1313/410 = **3.20** (not 2.7 as specimen name implies) | DERIVED |
| L_span B11 | 4700−1613 = 3087 mm (same as a/d=1.7 config) | DERIVED |
| Vult comparability | Vult still reported but stiffness results affected | REPORTED |

**CONFIRMED 2026-10-17:** Figure 1(c) read as image. B11 uses the same West support position as the a/d=1.7 configuration (1613mm) but load is placed for a longer shear span → a_eff=1313mm. This means B11 has a true a/d_eff=3.20, making it a distinct configuration. FE model must use these exact support coordinates.

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

| # | Item | Priority | Status |
|---|------|---------|--------|
| 1 | Figure 1 visual: support coordinates, load position, span | CRITICAL | **RESOLVED 2026-10-17** — coords confirmed; see Section 1 |
| 2 | Figure 1 visual: top bar M#3 vs M#4 confirmation | CRITICAL | **RESOLVED 2026-10-17** — M#3 confirmed from Figure 1 A-A |
| 3 | Figure 1(c): B11 modified support exact topology | CRITICAL | **RESOLVED 2026-10-17** — a_eff=1313mm, a/d_eff=3.20 |
| 4 | Batch 2 negative inelastic strain — CDP reconstruction | BLOCKER | **OPEN — expert decision required** |
| 5 | Bar centroid for 6-bundle M#10 to verify d=410 mm | HIGH | OPEN |
| 6 | Full postyield curves for MMFX M#10, M#4, M#3 | HIGH | OPEN |
| 7 | Tensile gauge length normalization Batch 1/2 vs 3 | MEDIUM | OPEN |
| 8 | Stirrup exact spacing in FE model zone | MEDIUM | **RESOLVED 2026-10-17** — spacings confirmed from Figure 1 |

**Do NOT set G0 = PASS until item 4 is resolved with expert review.**

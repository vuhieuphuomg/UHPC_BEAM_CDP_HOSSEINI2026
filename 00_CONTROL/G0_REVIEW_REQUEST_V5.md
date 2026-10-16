# G0 REVIEW REQUEST — Unresolved Physical Inputs
**Date:** 2026-10-17  
**Stage:** G0_SOURCE_AUDIT  
**Prepared by:** Claude Code (automated audit), session G0  
**Requires:** Human expert review before G0 can be set to PASS

---

## CRITICAL BLOCKERS (must resolve before any FE build)

### BLOCKER-1: Figure 1 Geometry (Support positions, load point, span)
**Issue:** PDF page 5 contains Figure 1 (image only). Text extraction yields only the figure caption. The following are NOT derivable from text:
- Distance from beam end to near support center
- Distance from beam end to far support center
- Clear span between supports
- Load plate center position
- Load plate dimensions
- Support plate dimensions

**Why critical:** Without these, the statics (Vult = R_near = P × (L_span − a) / L_span) cannot be verified, and FE boundary conditions cannot be set.

**What is known from text:**
- Total beam length = 5000 mm (Section 2.1)
- d = 410 mm (Table 1 note)
- Shear span a = 697 mm (a/d=1.7) or 1107 mm (a/d=2.7)

**Action required:** Open PDF page 5, measure Figure 1(a) and 1(b) to extract span and support dimensions.

---

### BLOCKER-2: Top Bar Size — M#3 vs M#4
**Issue:** Section 2.1 text (p. 3) states "two MMFX Grade 4100 **M#4** bars at the top." BLOCKERS.md and ENGINEERING_OPEN_ITEMS flag that Figure 1 **may show M#3**. Both M#3 (9.5 mm dia) and M#4 (12.7 mm dia) are MMFX Grade 4100 with same assumed fy=684 MPa (Table 3), but different cross-sectional areas and therefore different compression reinforcement contribution.

**Implication for FE:**
- M#4: As = 2 × π × 12.7²/4 = 2 × 126.7 mm² = 253.4 mm²
- M#3: As = 2 × π × 9.5²/4 = 2 × 70.9 mm² = 141.8 mm²
- Difference = 79% less area if M#3; affects compression zone behavior

**Action required:** Visual inspection of Figure 1 to confirm top bar label.

---

### BLOCKER-3: B11 Modified Support Topology
**Issue:** Figure 1(c) shows the modified support for specimen Vf1-ρsv0.4%H-2.7 (B11). Text confirms it exists but provides no dimensional data. FE model requires a separate support configuration for B11; using the standard support topology would be physically incorrect.

**Action required:** Measure Figure 1(c) to extract support centerline positions and any additional bearing constraints.

---

### BLOCKER-4: Batch 2 Negative Inelastic Strain at Peak Compression
**Calculation:**
- f'c = 153.2 MPa, Ec = 47.3 GPa = 47300 MPa
- εcp (mean) = 0.0032
- Elastic strain at peak = f'c / Ec = 153.2 / 47300 = 0.003239
- **Nominal inelastic strain at peak = 0.0032 − 0.003239 = −0.000039 (NEGATIVE)**

**Why this is a blocker:** Abaqus CDP requires the first data point of the compression damage/inelastic table to have zero or positive inelastic strain. A negative value is inadmissible and must NOT be silently clipped to zero.

**Options (for expert judgment only — do not auto-select):**
1. Use Ec from a compatible point on the loading curve (secant modulus at lower stress level)
2. Adopt a slightly lower εcp within the reported standard deviation range (0.32% ± 0.05% → try 0.37%)
3. Use only the mean ± SD range to bracket admissible solutions
4. Accept that the peak is a singular data point and use a bilinear/polynomial fit through reported mean ± 1σ

**Action required:** Expert decision on physically justified reconstruction for Batch 2 CDP compression table. Document rationale in CHANGELOG with A/B/C/D classification.

---

## HIGH PRIORITY (needed before G2 model build)

### REVIEW-5: Bar Center Coordinates (cover verification)
**Issue:** The effective depth d=410 mm is reported in Table 1 but the distance from the bottom fiber to the centroid of the 6-bundle M#10 group is NOT explicitly given. For FE, the exact y-coordinate of each rebar layer is needed.
- If d=410 mm and total height=500 mm, then bottom bar centroid = 500 − 410 = 90 mm from bottom fiber
- This seems large for typical cover (~40-50 mm), possibly due to 6 bars in a bundled group with 2+ rows
- Figure 1 should show the bar positions explicitly

**Action required:** Verify from Figure 1 the actual cover and bundle arrangement.

---

### REVIEW-6: HSS Postyield Constitutive Curve
**Issue:** Table 3 reports fy=684 MPa and fu=1142 MPa for MMFX Grade 4100. The full stress-strain curve (postyield hardening) is NOT provided in the paper. MMFX (ASTM A1035) does not have a yield plateau; it has a continuously rising curve.

**Why critical:** In HSS stirrup specimens, the stirrups likely exceed fy at failure. Without the full hardening curve, the model cannot capture the correct stirrup contribution beyond yield.

**Action required:** Obtain published MMFX Grade 4100 stress-strain curve from ASTM A1035 or manufacturer data. If unavailable, label as ADOPTED with documented uncertainty.

---

## MEDIUM PRIORITY

### REVIEW-7: Tensile Specimen Gauge Length Normalization
**Issue:** Table 2 note states: "The gauge length used for Batch IDs 1 and 2 was different from the gauge length used for Batch ID 3." Batch 1 & 2 used 50×50×700 mm prisms; Batch 3 used 50×50×500 mm. The εt,loc and related strains are gauge-length dependent.

**Implication:** Localization strain εt,loc cannot be compared directly between batches. If using σ-w (crack opening) instead of σ-ε, gauge length must be factored in.

**Action required:** Confirm gauge lengths used for strain reporting in Table 2, and document normalization method for CDP tensile input.

---

### REVIEW-8: Stirrup Spacing in FE Test Zone
**Issue:** Text states stirrups are spaced at d/2 = 205 mm (maximum ACI 318 limit). However, the exact layout (first stirrup from support, hook details, distribution in shear span) is in Figure 1 and not available from text extraction.

**Action required:** Read Figure 1(b) to get the stirrup layout in the FE model zone.

---

## WHAT IS CONFIRMED AND READY (no further expert review needed)

| Item | Status |
|------|--------|
| B01-B12 Vult, δult, FM, θave (Table 4) | CONFIRMED |
| Batch ID assignment for all 12 specimens (Table 1) | CONFIRMED |
| UHPC mean properties Batch 1, 2, 3 (Table 2) | CONFIRMED |
| Batch 2 negative inelastic strain is a real problem | CONFIRMED |
| Steel fy, fu, Es for NSS, M#4, M#10 (Table 3) | CONFIRMED |
| d = 410 mm for all specimens (Table 1 note) | CONFIRMED |
| B11 has special support (text and figure caption) | CONFIRMED |
| Shear spans: 697 mm (1.7) and 1107 mm (2.7) | CONFIRMED DERIVED |
| NSS stirrup spacing nominal = d/2 = 205 mm | CONFIRMED DERIVED |
| Overall cross-section dimensions | CONFIRMED |

---

## NEXT ACTION
**Specific action:** Open the Hosseini PDF (01_SOURCES/01_ORIGINAL_REFERENCE/1-s2.0-S0141029625022011-main.pdf) on PDF page 5 and visually read Figure 1 to extract: (a) support center coordinates, (b) load point position, (c) top bar designation (M#3 or M#4), (d) B11 modified support topology from Figure 1(c), (e) bar cover and bundle arrangement. Record findings in this file.

**No FE build, no solver, no gate release until the above blockers are resolved.**

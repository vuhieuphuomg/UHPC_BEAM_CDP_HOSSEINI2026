# G0 REVIEW REQUEST — Unresolved Physical Inputs
**Date:** 2026-10-17  
**Stage:** G0_SOURCE_AUDIT  
**Prepared by:** Claude Code (automated audit), session G0  
**Requires:** Human expert review before G0 can be set to PASS

---

## CRITICAL BLOCKERS (must resolve before any FE build)

### ~~BLOCKER-1: Figure 1 Geometry~~ — **RESOLVED 2026-10-17**
**Resolution:** PDF page 5 rendered as image via PyMuPDF; Figure 1(a)(b) read visually.

| Configuration | West support | East support | Load position | Clear span | Shear span a |
|---|---|---|---|---|---|
| a/d=2.7 | 300 mm from W | 4700 mm from W | 1407 mm from W | 4400 mm | 1107 mm (near=West) |
| a/d=1.7 | 1613 mm from W | 4700 mm from W | 4003 mm from W | 3087 mm | 697 mm (near=East) |

Load plate and support plate width: 300 mm each.  
**Key finding:** Two DIFFERENT span configurations — not just repositioned load. a/d=2.7 uses L=4400mm; a/d=1.7 uses L=3087mm.  
Source: Figure 1(a)(b), p. 5, rendered 2026-10-17.

---

### ~~BLOCKER-2: Top Bar Size~~ — **RESOLVED 2026-10-17**
**Resolution:** Figure 1 A-A cross-section explicitly labels top bars as **M#3 (Ø10)** (9.5 mm dia). The text (Section 2.1, p. 3) stating "M#4" is a typographic error in the paper. Figure 1 is authoritative.

**Confirmed values:**
- Top bars: 2 × M#3, diameter = 9.5 mm, As = 2 × 70.9 = **141.8 mm²**
- Steel: fy=684 MPa, fu=1142 MPa, Es=196 GPa (Table 3; M#3 test unavailable, M#4 values adopted)

Source: Figure 1 A-A section, p. 5, rendered 2026-10-17.

---

### ~~BLOCKER-3: B11 Modified Support Topology~~ — **RESOLVED 2026-10-17**
**Resolution:** Figure 1(c) read as image.

| Item | Value | Derivation |
|---|---|---|
| West support | 1613 mm from W beam end | Figure 1(c) |
| Load position | 3387 mm from W beam end | Figure 1(c) |
| East support | 4700 mm from W beam end | Figure 1(c) |
| Effective shear span a_eff | **1313 mm** | 4700−3387 |
| a/d_eff | **3.20** | 1313/410 |
| Clear span L | 3087 mm | 4700−1613 |

B11 true a/d_eff=3.20 — not 2.7 as the specimen name implies. FE model must use these coordinates.  
Source: Figure 1(c), p. 5, rendered 2026-10-17.

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

---

### **EXPERT DECISION — 2026-10-17 (CONDITIONAL APPROVAL)** — Tag: ADOPTED

**Decision:**  
Approximate the very small negative inelastic strain at peak to zero as FE input:

```
eps_in,peak (FE) = max(0,  εcp − f'c/Ec)
                 = max(0,  0.0032 − 153.2/47300)
                 = max(0,  −0.000039)
                 = 0
```

**Justification:**  
Absolute deviation = 0.000039. Relative to total peak strain: |0.000039 / 0.0032| = **1.2%** — less than the experimental scatter on εcp (SD=0.05%, relative SD ≈ 15.6%). The approximation is a FE input boundary condition, not a modification of the measured data.

**Raw experimental data — UNCHANGED:**  
f'c = 153.2 MPa · Ec = 47.3 GPa · εcp = 0.0032 (all mean values, Table 2)

**Separation of experimental data vs FE parameters:**  
| Parameter | Experimental (REPORTED) | FE input (ADOPTED/APPROXIMATED) |
|---|---|---|
| εcp | 0.0032 | 0.0032 (unchanged) |
| f'c | 153.2 MPa | 153.2 MPa (unchanged) |
| Ec | 47.3 GPa | 47.3 GPa (unchanged) |
| eps_in at peak | N/A (not a direct measurement) | 0 (max(0, −0.000039)) |

**Conditions on this approval (must be respected at G1):**  
1. This zero-clip applies ONLY to the CDP compression table peak entry for Batch 2. All other data points are unchanged.  
2. This approval does NOT automatically validate the Graybeal–Fakeh C1 ascending branch shape. At G1, the full curve equation must be derived, and all eps_in and eps_pl values verified to be ≥ 0 and non-decreasing.  
3. If forcing eps_in,peak = 0 creates inconsistency in the C1 ascending branch (e.g. intermediate points have eps_in > 0 before peak), flag as BLOCKED at G1 and propose a physically justified curve adjustment — do not silently clip additional points.  
4. All CHANGELOG entries at G1 must distinguish experimental data (REPORTED) from curve-model parameters (ADOPTED) from FE approximations (APPROXIMATED).

**Classified:** Type C (FE input approximation — Batch 2 CDP peak only)  
**Approved by:** Project engineer, 2026-10-17  
**Recorded by:** Claude Code (Sonnet 4.6)

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
| Support coordinates a/d=2.7: West=300mm, East=4700mm, Load=1407mm | CONFIRMED (Figure 1(a)) |
| Support coordinates a/d=1.7: West=1613mm, East=4700mm, Load=4003mm | CONFIRMED (Figure 1(b)) |
| B11 support: West=1613mm, Load=3387mm, East=4700mm, a_eff=1313mm | CONFIRMED (Figure 1(c)) |
| Top bars: 2×M#3 (Ø9.5mm) confirmed from Figure 1 A-A | CONFIRMED (Figure 1) |
| Stirrup spacings: 200mm (ρ=0.4%/0.6%/0.7%), 150mm (ρ=0.5%) | CONFIRMED (Figure 1) |

---

## NEXT ACTION
**All blockers have expert decisions recorded. G0=PASS pending engineer gate approval.**

BLOCKER-4 decision: ADOPTED (Graybeal–Fakeh C1 model, see above).  
**Engineer must set G0=PASS manually in `00_CONTROL/GATES_V5.json`** — Claude Code does not modify gate files.

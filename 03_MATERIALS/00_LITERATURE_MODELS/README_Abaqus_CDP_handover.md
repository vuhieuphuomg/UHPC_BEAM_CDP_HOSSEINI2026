# HOSSEINI 2026 — ABAQUS CDP HANDOVER, 16 October 2026

**Evidence status: material and structure DATA EXTRACTED; nonlinear CDP constitutive law NOT YET VERIFIED.**

Source: Hosseini, Quan, Shao, *Enhancing shear performance in UHPC beams through strategic fiber and stirrup integration*, Engineering Structures 348 (2026) 121810, DOI https://doi.org/10.1016/j.engstruct.2025.121810. Drive PDF: https://drive.google.com/file/d/1TUkaMsIZJr7iJ6plnbLnr89tA95ONGga/view.

This package contains an 8-sheet Excel evidence workbook, 4 representative digitized Fig. 2 curves (300 total plotted points), 12 beam-test targets from Table 4, geometry/rebar from Fig. 1 and Table 3, a strict Abaqus CDP material-loader template and an uncertainty register. The digitization is approximate vector-art reconstruction, **not author-provided raw data**. The plotting origin is fixed at (0,0) as a graphical anchor. The 2% fiber curve is **not identified as Batch 1 or 2**.

## Structural evidence

- All 12 T beams: length 5000 mm, 180 mm web width, 500 mm height, 400 mm flange width, 100 mm flange thickness, effective depth d=410 mm. Test speed 0.1 mm/s. Steel fibers 13 mm × 0.2 mm, minimum tensile strength 2500 MPa (paper Section 2, Fig. 1, Tables 1-3).
- **Do not model this as symmetric 3PB.** Nominal load-support center coordinates (x in mm from West end), read from the dimensioned Fig. 1: default a/d2.7 West=300, load=1613, East=4700; default a/d1.7 West=1613, load=3797, East=4700. Special 0.4% HSS a/d2.7 West=1613, load=3387, East=4700. These are figure-based nominal locations, pending contact pad geometry verification.
- Support-reaction fraction of applied vertical P at the critical short shear span (assuming ideal simply supported statics): 3087/4400 for regular a/d2.7, 2184/3087 for regular a/d1.7, 1774/3087 for the special a/d2.7. Therefore **Vult in Table 4 is shear force; do not compare it blindly with the Abaqus load RP reaction P**.
- 6 bottom MMFX Grade 4100 M#10 bars (nominal Ø32.3 mm), 2 upper longitudinal bars: **conflict** in paper: Fig. 1 labels M#3 nominal Ø10, Section 2.1 says M#4. Verify with authors before locking rebar area. Stirrup selection shown Fig.1: NSS 10M s200; HSS M#3 s200 for 0.4%, M#3 s150 for 0.5%, M#4 s200 for 0.7%.

## Material evidence

- Excel 01_BATCH_MATERIAL stores 3 batches with reported means and standard deviations (Table 2). Batch1/Batch2 both 2% but are different casting batches. Table3 contains MMFX 4100 and Grade500 steel E, fy, fu; full post-yield curves are **not** published. For MMFX #3, Table3 explicitly uses #4 properties by substitution.
- Fig. 2(a) gives material small-beam 100×100×400 mm **LOAD versus NET DEFLECTION**. This is *not* tensile stress–crack opening.
- Fig. 2(b) gives representative **DIRECT TENSILE STRESS versus measured strain**, including apparent post-localization decrease, but lacks independent crack-opening, localization length and the full data file. Batch 1/2 direct-tension samples were 50×50×700 mm; Batch 3 samples 50×50×500 mm; gauge definitions differ (Table 2 note). Do not simply convert test strain into Abaqus local cracking strain or σ-w.
- CDP missing: separately evidenced compressive post-peak curve, tension σ-w/GFI, compression/tension damage functions, dilation/flow calibration, precise Poisson ratio, fiber orientation characterization, complete rebar hardening.
- Mechanical consistency caveat: with the published MEAN values, Batch 2 peak compressive inelastic strain ε_cp − fc/Ec ≈ **−3.89×10⁻⁵**, which cannot be directly entered as a nonnegative CDP inelastic-strain value. This is likely due to averaging/rounding different specimens; **do not silently change fc, E or strain** to hide the discrepancy. Resolve with a consistent source-derived curve and document any independent constitutive fit.

## Abaqus 2022 handoff

1. Copy `CDP_CONFIRMATION_REQUIRED_TEMPLATE.json` into a working version e.g. `CDP_CONFIRMED.json`.
2. Populate all explicit `nu`, `CDP` parameters, full `compression_hardening_sigma_epsin` table, and one `tension_GFI_ft_Gf_Nmm` pair for **each** batch. These must be source-supported or individually marked as analyst assumptions. Do not set Gf based on the old Fang test without a justified transfer model.
3. Optional damage curves are *not* automatically generated. If added, validate the Abaqus plastic-strain transformations and monotonicity (the loader only has basic syntactic/sequence checks; this is not a complete numerical constitutive audit).
4. The script `abaqus_material_loader.py` has `load_confirmed_config(path)` for preflight under plain Python, and `apply_materials(mdb.models['Model-1'],path)` for Abaqus CAE. It refuses incomplete templates and refuses to overwrite a material of the same name. It **does not build geometry, submit jobs or claim Abaqus runtime testing**.
5. First reproduce the two no-stirrup a/d2.7 specimens, Batch 3 1% diagonal tension and Batch 2 2% mixed failure. Next the 1.7 specimens (compression-strut failure). Then add NSS/HSS stirrups with independent steel hardening and constraints verified.
6. Output at each experimental comparison: critical support reaction V (not just applied P), load-vs-deflection curve, peak V and Δ, shear cracking/DAMAGET pattern, compression-band localization, tensile fiber bridging limits, steel stress/PEEQ, local support/pad crush. Require mesh sensitivity and physical failure-mode agreement before declaring VALIDATED.

## Important consistency checks

1. Text vs Fig1: top steel M#4 versus Fig1 M#3 (major geometry input discrepancy).
2. Table4 heading `Anal./Exp.` appears reversed: e.g., 884 / 504 = 1.75, meaning tabulated ratio is Exp./Anal. instead. Not used as FE validation evidence.
3. Several 1%-vs-2% shear effects are confounded with different casting batches; do not attribute all load differences to fiber dosage alone without qualification.
4. Figure 7 contains 12 plotted shear–deflection traces; Table 4 supplies exact peak pairs. Figure 7 has not been converted into author-quality raw numerical time histories here.
5. Source states `All data and models used appear in the manuscript` under Data Availability; no underlying numerical tensile/bending raw CSV is linked in the paper as reviewed.

**Release gate:** `READY_FOR_GEOMETRY_AND_ELASTIC_PREFLIGHT`, `HOLD_FOR_NONLINEAR_CDP`, `NO_ABAQUS_JOB_RUN`.

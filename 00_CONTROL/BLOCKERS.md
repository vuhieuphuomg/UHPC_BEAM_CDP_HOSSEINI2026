# SOURCE / PHYSICS BLOCKERS (do not auto-guess)

1. ~~B01-B12 geometry and dimensions from Hosseini Figure 1 must be inspected manually; top longitudinal reinforcement shows M#3 vs M#4 conflict between figure and description.~~ **RESOLVED 2026-10-17**: Top bars confirmed M#3 (Ø9.5mm) from Figure 1 A-A; paper text (M#4) is in error. Support coords confirmed for all configs.
2. ~~B11 (Vf1-HSS0.4-ad2.7) has nonstandard support layout and must have its own config.~~ **RESOLVED 2026-10-17**: B11 West=1613mm, Load=3387mm, East=4700mm → a_eff=1313mm, a/d_eff=3.20. Use separate config.
3. ~~Obtain loading point and both support center coordinates and consistent shear force vs total applied load conversion.~~ **RESOLVED 2026-10-17**: a/d=2.7 West=300mm East=4700mm Load=1407mm L=4400mm; a/d=1.7 West=1613mm East=4700mm Load=4003mm L=3087mm.
4. Batch2: average eps_c_peak = 0.0032, fc/E = 0.0032389 -> negative nominal inelastic strain at peak. **ADOPTED 2026-10-17**: Use Graybeal-Fakeh C1 nonlinear ascending branch; raw measurements kept unchanged; CDP table built at G1. See G0_REVIEW_REQUEST_V5.md BLOCKER-4 expert decision. **C1 IMPLEMENTED 2026-10-17 — G1**: C1 ascending εin = ε×αb ≥ 0 always; peak QA PASS for all 3 batches including Batch 2.
11. **[G1] C3 Wang compression — EXCLUDED from FE main matrix (2026-10-17)**:  
    Wang (2016) parabolic ascending has initial slope 2×fp/ε0 >> Ec_reported; εin < 0 for ascending branch: B1:~96.6%, B2:~93.9%, B3:100%.  
    **Engineering decision 2026-10-17:** C3 excluded from Abaqus FE run matrix. Reason: CDP incompatibility with experimental Ec is systematic and affects all three batches; correcting it would require a different ascending formula, constituting a new model. No clipping or parameter forcing applied.  
    Retained as THEORETICAL REFERENCE ONLY. Raw σ–ε diagnostic plots at `03_MATERIALS/plots/B{n}_C3_raw_curve.png`. STATUS=BLOCKED (CDP table never generated). See CHANGELOG C-003.
12. **[G1] C4 Yan (original) — CDP BLOCKED (raw σ–ε reference only)**:  
    Source: Fakeh (2025) Table 3 SECONDARY (Yan 2010 original not in repo). αa∈[1.1,1.138]; k: B1=1.054, B2=0.988, B3=1.091.  
    εin<0 on ascending with reported ecp: αa=1.1: B1:89.6%, B2:100%, B3:48.9%; αa=1.138: B1:91.9%, B2:100%, B3:78.8%.  
    Raw σ–ε plots at `03_MATERIALS/plots/B{n}_C4_raw_curve.png`. STATUS=BLOCKED (CDP table never generated).  
    → **SUPERSEDED** for FE use by C4_YAN_EC_ADAPTED (see Blocker 15).
15. **[G1] C4_YAN_EC_ADAPTED — IMPLEMENTED 2026-10-17 (CHANGELOG C-003)**:  
    Engineering decision: set eps_c0_model = αa×fc/Ec (not reported ecp). Initial tangent = Ec exactly. Algebraic proof: εin(η) = (fc/Ec)×η²×(αa−1)²/(1+(αa−2)×η) ≥ 0 for all η∈[0,1], αa∈[1.100,1.138].  
    Two variants generated:  
    — C4_ADAPTED_LB: αa=1.100, αd=0.193 — peak dev: B1:+4.4%, B2:+11.4%, B3:+0.8%  
    — C4_ADAPTED_UB: αa=1.138, αd=0.312 — peak dev: B1:+8.1%, B2:+15.2%, B3:+4.3%  
    QA: εin≥0 all rows, strict monotone, first εin=0, all σ>0 — PASS for B1/B2/B3 both variants (111 unit tests PASS).  
    CSV tables + plots at `03_MATERIALS/tables/B{n}_C4_ADAPTED_{LB|UB}_compression.{csv|png}`.  
    Source: Fakeh (2025) Table 3 [SECONDARY]; Yan (2010) original not in repo. Tag: ADAPTED.  
    Remaining open items: (a) αa/αd are parameter ranges only — no unique Hosseini calibration; (b) Yan (2010) original paper needed for full provenance; (c) peak strain deviation B2 LB +11.4% must be noted in FE matrix.
13. **[G1] T1 Tian tension softening — BLOCKED 2026-10-17**: Formula documented from Fakeh (2025) Table 4 (secondary): σ(ε) = ft×(1−0.15×(ε−εt0)/(εu−εt0)). Missing: εu (strain at 0.85×ft). εu not in Hosseini 2026 Table 2; Tian (2023) original paper NOT in 01_SOURCES/02_SECONDARY_REFERENCE. T1 hardening table (bilinear, same as REF_BILINEAR) IMPLEMENTED for all 3 batches. σ–w conversion also needs lc (mesh size, unknown at G1).
14. **[G1] Fiber dimensions ASSUMED for C1 post-peak — 2026-10-17**: l=13mm, df=0.2mm assumed (standard UHPC steel fiber from Fakeh 2025 Table 1). Not confirmed in Hosseini 2026. CHANGELOG C-002. Must be confirmed before using C1 post-peak for structural analysis.
16. **[G1] T2 Zhao tension — σ–εck MESH-DEPENDENT (2026-10-17)**: T2 generate_table() produces σ–εck table using power law σ=ft×(εt0/ε)^0.6. This table is MESH-DEPENDENT (strain localization in tension). Do NOT use as final Abaqus-ready input without σ–w conversion. Fracture energy estimate (via Fakeh λclc, not mesh lc): B1:23.7 N/mm, B2:21.6 N/mm, B3:8.9 N/mm; wtu: B1:5.2mm, B2:5.1mm, B3:2.6mm. These are ESTIMATES using Fakeh Eq.8 λclc as localization length — not direct GF measurements. Production σ–w table requires lc from FE mesh (set at G2).
5. Full compression descending branches and batch-specific direct-tension full localization are not provided in Hosseini; external constitutive law is a MODEL ASSUMPTION, not directly measured.
6. Tensile sigma-w and finite Gf/w_cutoff are necessary; a 0.2 ft residual plateau without a prescribed stopping displacement can imply unbounded work.
7. Damages dc, dt require physically defensible law and monotone plastic strain verification; 'elastic only' cannot be reported as CDP damage calibration.
8. Steel #3/#4 top and detailed NSS/HSS hardening curves must be resolved for mode transitions; if not, label uncertainty or HOLD.
9. Older ROOT/CDP has unrelated legacy studies: DO NOT move, delete, overwrite, or import them as baseline automatically.
10. Files archived in Drive must be copied only after Abaqus exits and lock files are gone; do not run through Google Drive mounted/streaming paths.

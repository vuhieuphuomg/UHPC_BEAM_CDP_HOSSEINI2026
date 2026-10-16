# SOURCE / PHYSICS BLOCKERS (do not auto-guess)

1. ~~B01-B12 geometry and dimensions from Hosseini Figure 1 must be inspected manually; top longitudinal reinforcement shows M#3 vs M#4 conflict between figure and description.~~ **RESOLVED 2026-10-17**: Top bars confirmed M#3 (Ø9.5mm) from Figure 1 A-A; paper text (M#4) is in error. Support coords confirmed for all configs.
2. ~~B11 (Vf1-HSS0.4-ad2.7) has nonstandard support layout and must have its own config.~~ **RESOLVED 2026-10-17**: B11 West=1613mm, Load=3387mm, East=4700mm → a_eff=1313mm, a/d_eff=3.20. Use separate config.
3. ~~Obtain loading point and both support center coordinates and consistent shear force vs total applied load conversion.~~ **RESOLVED 2026-10-17**: a/d=2.7 West=300mm East=4700mm Load=1407mm L=4400mm; a/d=1.7 West=1613mm East=4700mm Load=4003mm L=3087mm.
4. Batch2: average eps_c_peak = 0.0032, fc/E = 0.0032389 -> negative nominal inelastic strain at peak. **ADOPTED 2026-10-17**: Use Graybeal-Fakeh C1 nonlinear ascending branch; raw measurements kept unchanged; CDP table built at G1. See G0_REVIEW_REQUEST_V5.md BLOCKER-4 expert decision.
5. Full compression descending branches and batch-specific direct-tension full localization are not provided in Hosseini; external constitutive law is a MODEL ASSUMPTION, not directly measured.
6. Tensile sigma-w and finite Gf/w_cutoff are necessary; a 0.2 ft residual plateau without a prescribed stopping displacement can imply unbounded work.
7. Damages dc, dt require physically defensible law and monotone plastic strain verification; 'elastic only' cannot be reported as CDP damage calibration.
8. Steel #3/#4 top and detailed NSS/HSS hardening curves must be resolved for mode transitions; if not, label uncertainty or HOLD.
9. Older ROOT/CDP has unrelated legacy studies: DO NOT move, delete, overwrite, or import them as baseline automatically.
10. Files archived in Drive must be copied only after Abaqus exits and lock files are gone; do not run through Google Drive mounted/streaming paths.

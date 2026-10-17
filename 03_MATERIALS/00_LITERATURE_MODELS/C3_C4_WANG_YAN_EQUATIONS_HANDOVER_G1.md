# G1 TECHNICAL HANDOVER — C3 WANG (2016) & C4 YAN (via FAKEH 2025)

**Project:** UHPC_BEAM_CDP_HOSSEINI2026  
**Prepared:** 2026-10-17  
**Decision status:** Equations EXTRACTED; **NOT ABAQUS CDP APPROVED**; G1 remains HOLD.

## 1. SOURCE AUDIT

- **Wang et al. (2016)**: `wang-et-al-2016-modeling-seismic-performance-of-high-strength-steel-ultra-high-performance-concrete-piers-with-modified.pdf` (user uploaded), *Advances in Mechanical Engineering* 8(2), DOI `10.1177/1687814016633411`. Full original, verified visually at **PDF pp.3–4**, Eqs. **(3)–(11)**. Model comes from modified Kent–Park for unconfined and confined UHPC used in OpenSees fiber elements, *not* originally Abaqus CDP.
- **Yan (2010)**: the uploaded `Experimental_Study_on_the_Strength_and_Deformation.pdf` is **NOT the Yan paper**. It is **Wei Xia et al. (2021)**, *Experimental Study on the Strength and Deformation Characteristics of Concrete under True Triaxial Compression after Sulfate Attack*, DOI `10.1155/2021/5548313`. **Do not cite or use this document as evidence for C4.**
- **Yan mathematical expression — SECONDARY SOURCE**: Fakeh et al. (2025), *Recommended concrete damage plasticity parameters and constitutive models for UHPC in ABAQUS*, *Engineering Structures* 333, 120154, **Table 3**, DOI `10.1016/j.engstruct.2025.120154`; Drive PDF `https://drive.google.com/file/d/1-10u8bd1djHkbNAvYnfPRy_p2xiEYfA0/view`. Paper attributes C4 to `Yan, G., Experimental Study on Strength and Deformation of Reactive Powder Concrete Under Triaxial Compression, Yantai, China, pp.383-386 (2010)`. **Do not claim C4 is independently confirmed against Yan original.**

## 2. C3 — WANG 2016 UNCONFINED UHPC; original Eq. (3)

Define `eta = eps/eps0`, where compression stress `sigma`, peak `f_peak`, peak strain `eps0`, residual ratio `lambda_rs`, residual strain onset `eps20`.

```text
sigma(eps) = f_peak * [2*eta - eta**2]                                     0 <= eps <= eps0
sigma(eps) = f_peak * [1 - (1-lambda_rs)*(eps-eps0)/(eps20-eps0)]          eps0 < eps < eps20
sigma(eps) = lambda_rs * f_peak                                            eps >= eps20
```

- Wang original Eq. (4): `f_peak = lambda_sh * sigma_B`, recommended `lambda_sh = 0.85` (cylinder-to-in-pier shape factor). In original model, Eq. (9) modifies: `f_peak = k_E * lambda_sh * sigma_B`, with `k_E = 0.85` suggested. If `f_peak` is instead set equal to Hosseini's measured `fc`, **tag as ADAPTED**, not original Wang's conversion.
- Original Eq. (5): `eps0_microstrain = 1950 + 14.6*f_peak`.
- Original Eq. (6): `eps0_microstrain = 763 * f_peak**(1/4)`.
- Original Eq. (7), author's compromise:

```text
eps0_microstrain = 0.5 * [1950 + 14.6*f_peak + 763*f_peak**0.25]
eps0_dimensionless = eps0_microstrain * 1e-6
```

  `f_peak` in MPa; Eq. (7) reports strain in **microstrain**, converted explicitly for Abaqus dimensional strain.
- Original Eq. (8), **equivalent/average slope**, `E_equiv = 1.5*f_peak/eps0`. This is **not the initial tangent**; Eq. (3) gives `E_initial = 2*f_peak/eps0`.
- Original residual recommendation `lambda_rs=0.30`, see p.4, just before Eq. (10).
- Original Eqs. (10) and (11) specify `eps20`.

```text
eps20_microstrain = ((0.65-lambda_rs)*f_peak)/0.0103 + 0.65*f_peak/E_MPa_per_microstrain
eps20_dimensionless = ((0.65-lambda_rs)*f_peak)/10300 + 0.65*f_peak/E_MPa
```

  The `10300` term is the unit-converted representation of the printed `0.0103` in Eq. (11) when using stress and modulus in MPa and strain dimensionless. Validate numerically against the p.4 Fig.4 scale before coding. `eps20` must exceed `eps0`. For the three Hosseini batches, `f_peak=fc_reported`, `E=Ec_reported`, `lambda_rs=.3` gives **illustrative adapted** eps20 values B1 ~0.00735136, B2 ~0.00731111, B3 ~0.00803675.

**CDP compatibility warning:** With `eps0=eps_peak_reported`, initial slope `2*fc/eps0` exceeds `Ec_reported`, resulting in `eps_in=eps-sigma/Ec < 0` over much of ascending branch. The source's `E_equiv=1.5*fc/eps0` does not resolve the initial tangent mismatch. Preserve the original envelope for comparison; do not mass-clip negative eps_in or silently change Ec. Separate a possible `C3_WANG_DESC_ONLY_HYBRID` as a newly *ADAPTED* engineering variant if approved, not as the authentic full C3.

## 3. C4 — YAN 2010, as REPRODUCED IN FAKEH 2025 TABLE 3

Define `eta = eps/eps_c0`, with peak `fc` and `eps_c0`.

```text
sigma_ascending(eps) = fc * (alpha_a*eta - eta**2) / [1 + (alpha_a-2)*eta]
                         for 0 <= eta <= 1
sigma_descending(eps) = fc * (alpha_d*eta) / [1 + (alpha_d-2)*eta + eta**2]
                         for eta >= 1
```

**Ranges exactly as secondary source lists them:** `alpha_a in [1.1,1.138]`; `alpha_d in [0.193,0.312]`. Neither coefficient is uniquely fixed for Hosseini B1/B2/B3 by Fakeh Table 3; no arbitrary midpoint should be reported as measured or original Yan value.

Consistency checks from formulas (derived, not claims made by Yan): `sigma_a(eta=1)=fc`, `sigma_d(eta=1)=fc`, both branch slopes vanish at peak. **Initial tangent** `E_initial=alpha_a*fc/eps_c0`. Abaqus with reported `Ec` requires `E_initial <= Ec` to keep `eps_in=eps-sigma/Ec >= 0` close to zero strain, which is not satisfied for all batches using the published alpha_a range and the reported peak strains.

Hosseini `k=Ec*eps_peak/fc`: B1=1.0536649, B2=0.9879896, B3=1.0913462, while `alpha_a >=1.1`. Therefore **all three** violate initial tangent compatibility; Batch 2 additionally has reported peak `eps_in < 0` itself. Do not force C4 original envelope into the CDP table with clipping. Keep `C4=SOURCE_FORMULA_VERIFIED_SECONDARY / CDP_BLOCKED` until an explicitly distinguished physically compatible adaptation is approved.

**Check of original CODE summary:** statements 'negative eps_in for 81–92% of ascending for all batches' are not universally correct across alpha range. For `alpha_a=1.1` with reported peak strains, negative eps_in occurs approximately over first 89.6% (B1), 100% (B2), and 48.6% (B3) of the ascending strain interval (from algebra, ignoring near-zero floating noise). Verify any percentage before reusing in G1 report.

## 4. G1 IMPLEMENTATION/QA RULES

1. Preserve `REPORTED` experimental `fc, Ec, eps_peak`. Tag source law, any chosen parameter or normalization as `SECONDARY`, `DERIVED`, or `ADAPTED` as appropriate.
2. Generate full **RAW STRESS–TOTAL STRAIN** candidate curves for C3/C4 to demonstrate equations and compare graphically. Do **not** label these as Abaqus-ready.
3. Independently form `eps_in = eps_total - sigma/Ec_reported`. Report minimum, intervals with negative values, peak mismatch, and branch continuity. No silent epsilon monotonicity epsilon-padding, clipping, or changing E.
4. If native constitutive source is incompatible with Abaqus CDP given reported Ec, retain blocker. A rewritten branch is a **different hybrid law**, requiring formal engineering approval and a new model ID; do not call it C3 or C4 original.
5. Raw Wang residual stress plateau to infinite strain is unsuitable as an unqualified finite-energy CDP input. Use an explicit approved truncation strategy and verify compression damage and plastic strain compatibility. Yan descending branch also requires a chosen finite endpoint if truncated.
6. Keep `G1=HOLD`, `solver_authorized=false`. No FE jobs or registry rewrites until engineering decision.

## 5. SOURCE TRACE

- Wang PDF p.3: Eq.(3) piecewise, Eq.(4) shape factor, Eq.(5)-(7) peak strain, Eq.(8) equivalent modulus, Eq.(9) correction.
- Wang PDF p.4: Fig.4, Eq.(10)-(11) residual onset, proposed lambda_rs=0.30.
- Fakeh (2025), Table 3 (PDF ~p.10): Yan ascending/descending rational formulas and alpha ranges, provenance SECONDARY.
- Xia et al. (2021), first page: proves that the other uploaded 'Experimental Study' PDF is unrelated to Yan 2010.

**Recommendation:** No extra Yan PDF is strictly necessary to examine the Yan formula as reproduced by Fakeh, but without original Yan do not claim primary-source verification or unique calibration of alpha_a/alpha_d. The Wang paper supplied is sufficient to resolve original missing-eps20 blocker, while CDP compatibility remains a separate blocker.

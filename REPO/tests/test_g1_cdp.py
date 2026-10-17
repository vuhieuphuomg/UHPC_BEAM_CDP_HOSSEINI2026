"""
G1 CDP material table unit tests.

Run from REPO/ directory:
  python -m pytest tests/test_g1_cdp.py -v
or:
  python -m unittest tests.test_g1_cdp -v
"""
import sys
import os
import math
import unittest

_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_tools_dir = os.path.join(_repo_root, "tools")
if _tools_dir not in sys.path:
    sys.path.insert(0, _tools_dir)

from cdp_builder.batch_data import (
    BATCHES, alpha_compression, eps_in_peak, lambda_f, M_graybeal_descent,
)
from cdp_builder.models import (
    PopovicsCompression, BilinearTensionHardening,
    C1GraybealFakehCompression, C2ZhaoCompression,
    C3WangCompression, C4YanCompression,
    C4YanEcAdaptedCompression, C4YanEcAdaptedLB, C4YanEcAdaptedLAHD, C4YanEcAdaptedHALD, C4YanEcAdaptedUB,
    T1TianFakehTension, T2ZhaoTension,
    ModelStatus, ModelNotAvailableError,
    COMPRESSION_MODELS, TENSION_MODELS,
)
from cdp_builder.tables.qa import qa_compression, qa_tension


class TestAlphaCompression(unittest.TestCase):
    def test_batch1_not_degenerate(self):
        alpha, is_degen = alpha_compression(1)
        self.assertFalse(is_degen, f"Batch 1 should not be degenerate; alpha={alpha:.4f}")
        self.assertGreater(alpha, 1.0)

    def test_batch2_degenerate(self):
        alpha, is_degen = alpha_compression(2)
        self.assertTrue(is_degen, f"Batch 2 should be degenerate; alpha={alpha:.4f}")
        self.assertAlmostEqual(alpha, 0.988, delta=0.01)

    def test_batch3_not_degenerate(self):
        alpha, is_degen = alpha_compression(3)
        self.assertFalse(is_degen, f"Batch 3 should not be degenerate; alpha={alpha:.4f}")
        self.assertGreater(alpha, 1.0)


class TestFiberData(unittest.TestCase):
    def test_lambda_f_batch1(self):
        lf = lambda_f(1)
        # vf=2%, l=13, df=0.2 → λf = 0.02 × 65 = 1.3
        self.assertAlmostEqual(lf, 1.3, places=5)

    def test_lambda_f_batch3(self):
        lf = lambda_f(3)
        # vf=1%, l=13, df=0.2 → λf = 0.01 × 65 = 0.65
        self.assertAlmostEqual(lf, 0.65, places=5)

    def test_M_graybeal_batch1(self):
        M = M_graybeal_descent(1)
        # M = 7061.5 × 1.3^(-0.411) ≈ 6337 MPa
        self.assertGreater(M, 5000)
        self.assertLess(M, 9000)

    def test_M_graybeal_batch3_greater_than_batch1(self):
        # Batch 3 has lower λf → higher M (steeper descent)
        self.assertGreater(M_graybeal_descent(3), M_graybeal_descent(1))


class TestPopovicsCompression(unittest.TestCase):
    def _make(self, batch_id):
        return PopovicsCompression(BATCHES[batch_id])

    def test_batch2_raises_degenerate(self):
        m = self._make(2)
        with self.assertRaises(ModelNotAvailableError):
            m.generate_table()

    def test_batch1_table_generated(self):
        rows = self._make(1).generate_table()
        self.assertGreater(len(rows), 10)

    def test_batch3_table_generated(self):
        rows = self._make(3).generate_table()
        self.assertGreater(len(rows), 10)

    def test_first_row_eps_in_zero(self):
        for batch_id in (1, 3):
            rows = self._make(batch_id).generate_table()
            self.assertAlmostEqual(
                rows[0]["inelastic_strain"], 0.0, places=8,
                msg=f"Batch {batch_id}: first eps_in must be 0",
            )

    def test_first_row_stress_positive(self):
        for batch_id in (1, 3):
            rows = self._make(batch_id).generate_table()
            self.assertGreater(rows[0]["stress_mpa"], 0)

    def test_monotone_inelastic_strain(self):
        for batch_id in (1, 3):
            rows = self._make(batch_id).generate_table()
            for i in range(1, len(rows)):
                self.assertGreater(
                    rows[i]["inelastic_strain"],
                    rows[i - 1]["inelastic_strain"],
                    msg=f"Batch {batch_id}: eps_in not strictly increasing at row {i}",
                )

    def test_all_stresses_positive(self):
        for batch_id in (1, 3):
            rows = self._make(batch_id).generate_table()
            for i, r in enumerate(rows):
                self.assertGreater(r["stress_mpa"], 0, msg=f"Batch {batch_id} row {i}: stress <= 0")

    def test_peak_stress_near_fc(self):
        for batch_id in (1, 3):
            rows = self._make(batch_id).generate_table()
            fc = BATCHES[batch_id]["fc_mpa"]
            stresses = [r["stress_mpa"] for r in rows]
            self.assertAlmostEqual(max(stresses), fc, delta=0.1,
                                   msg=f"Batch {batch_id}: peak stress should be ~fc={fc}")

    def test_qa_passes_batch1(self):
        rows = self._make(1).generate_table()
        errors = qa_compression(rows, BATCHES[1]["Ec_mpa"])
        self.assertEqual(errors, [], msg=f"QA errors: {errors}")

    def test_qa_passes_batch3(self):
        rows = self._make(3).generate_table()
        errors = qa_compression(rows, BATCHES[3]["Ec_mpa"])
        self.assertEqual(errors, [], msg=f"QA errors: {errors}")

    def test_status_is_implemented_reference(self):
        m = self._make(1)
        self.assertEqual(m.STATUS, ModelStatus.IMPLEMENTED_REFERENCE)


class TestC1GraybealFakeh(unittest.TestCase):
    def _make(self, batch_id):
        return C1GraybealFakehCompression(BATCHES[batch_id])

    def test_all_batches_generate(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            self.assertGreater(len(rows), 5, msg=f"Batch {batch_id}: too few rows")

    def test_first_row_eps_in_zero(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            self.assertAlmostEqual(
                rows[0]["inelastic_strain"], 0.0, places=8,
                msg=f"C1 Batch {batch_id}: first eps_in must be 0",
            )

    def test_all_eps_in_nonnegative(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            for i, r in enumerate(rows):
                self.assertGreaterEqual(
                    r["inelastic_strain"], 0.0,
                    msg=f"C1 Batch {batch_id} row {i}: eps_in = {r['inelastic_strain']:.6e} < 0",
                )

    def test_monotone_inelastic_strain(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            for i in range(1, len(rows)):
                self.assertGreater(
                    rows[i]["inelastic_strain"],
                    rows[i - 1]["inelastic_strain"],
                    msg=f"C1 Batch {batch_id}: eps_in not strictly increasing at row {i}",
                )

    def test_all_stresses_positive(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            for i, r in enumerate(rows):
                self.assertGreater(r["stress_mpa"], 0, msg=f"C1 Batch {batch_id} row {i}")

    def test_peak_stress_within_10pct_of_fc(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            fc = BATCHES[batch_id]["fc_mpa"]
            sigma_peak = max(r["stress_mpa"] for r in rows)
            dev_pct = abs(sigma_peak - fc) / fc * 100
            self.assertLess(dev_pct, 10.0,
                            msg=f"C1 Batch {batch_id}: peak {sigma_peak:.1f} MPa vs fc {fc:.1f} MPa, dev={dev_pct:.1f}%")

    def test_qa_passes_all_batches(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            errors = qa_compression(rows, BATCHES[batch_id]["Ec_mpa"])
            self.assertEqual(errors, [], msg=f"C1 Batch {batch_id} QA errors: {errors}")

    def test_post_peak_rows_tagged_adopted(self):
        rows = self._make(1).generate_table()
        desc_rows = [r for r in rows if r["tag"] == "ADOPTED"]
        self.assertGreater(len(desc_rows), 0, "C1 should have ADOPTED post-peak rows")

    def test_status_is_implemented(self):
        self.assertEqual(C1GraybealFakehCompression.STATUS, ModelStatus.IMPLEMENTED)

    def test_batch2_all_eps_in_nonnegative(self):
        # Critical test: Batch 2 alpha < 1 but Graybeal εin=ε×αb ≥ 0 always
        rows = self._make(2).generate_table()
        for i, r in enumerate(rows):
            self.assertGreaterEqual(r["inelastic_strain"], 0.0,
                                    msg=f"C1 Batch 2 row {i}: negative eps_in")


class TestC2Zhao(unittest.TestCase):
    def _make(self, batch_id):
        return C2ZhaoCompression(BATCHES[batch_id])

    def test_all_batches_generate(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            self.assertGreater(len(rows), 2, msg=f"C2 Batch {batch_id}: too few rows")

    def test_first_row_eps_in_zero(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            self.assertAlmostEqual(rows[0]["inelastic_strain"], 0.0, places=8,
                                   msg=f"C2 Batch {batch_id}: first eps_in must be 0")

    def test_first_row_stress_is_fc(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            fc = BATCHES[batch_id]["fc_mpa"]
            self.assertAlmostEqual(rows[0]["stress_mpa"], fc, places=3,
                                   msg=f"C2 Batch {batch_id}: first row should be fc")

    def test_descending_stress_decreases(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            stresses = [r["stress_mpa"] for r in rows]
            # After first row (peak), stress must decrease
            for i in range(2, len(stresses)):
                self.assertLess(stresses[i], stresses[i - 1],
                                msg=f"C2 Batch {batch_id}: stress not decreasing at row {i}")

    def test_monotone_inelastic_strain(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            for i in range(1, len(rows)):
                self.assertGreater(
                    rows[i]["inelastic_strain"], rows[i - 1]["inelastic_strain"],
                    msg=f"C2 Batch {batch_id}: eps_in not strictly increasing at row {i}",
                )

    def test_all_eps_in_nonnegative(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            for i, r in enumerate(rows):
                self.assertGreaterEqual(r["inelastic_strain"], 0.0,
                                        msg=f"C2 Batch {batch_id} row {i}: negative eps_in")

    def test_qa_passes_all_batches(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            errors = qa_compression(rows, BATCHES[batch_id]["Ec_mpa"])
            self.assertEqual(errors, [], msg=f"C2 Batch {batch_id} QA errors: {errors}")

    def test_status_is_implemented(self):
        self.assertEqual(C2ZhaoCompression.STATUS, ModelStatus.IMPLEMENTED)


class TestC3C4Blocked(unittest.TestCase):
    """CDP table generation BLOCKED; raw curve methods must work."""

    # ── Status and CDP-table blocking ──────────────────────────────────────────

    def test_c3_status_is_blocked(self):
        self.assertEqual(C3WangCompression.STATUS, ModelStatus.BLOCKED)

    def test_c4_status_is_blocked(self):
        self.assertEqual(C4YanCompression.STATUS, ModelStatus.BLOCKED)

    def test_c3_raises_on_generate(self):
        for batch_id in (1, 2, 3):
            inst = C3WangCompression(BATCHES[batch_id])
            with self.assertRaises(ModelNotAvailableError,
                                   msg=f"C3 Batch {batch_id} should raise"):
                inst.generate_table()

    def test_c4_raises_on_generate(self):
        for batch_id in (1, 2, 3):
            inst = C4YanCompression(BATCHES[batch_id])
            with self.assertRaises(ModelNotAvailableError,
                                   msg=f"C4 Batch {batch_id} should raise"):
                inst.generate_table()

    # ── C3 Wang source equations ───────────────────────────────────────────────

    def test_c3_eps0_wang_formula(self):
        """Wang Eq.(7) ε0 should differ from reported ecp (different formula)."""
        for batch_id, expected_eps0_approx in [(1, 0.00343), (2, 0.00344), (3, 0.00356)]:
            inst = C3WangCompression(BATCHES[batch_id])
            eps0 = inst._eps0_wang()
            self.assertAlmostEqual(eps0, expected_eps0_approx, delta=0.00005,
                                   msg=f"C3 Batch {batch_id}: ε0_Wang={eps0:.5f}")

    def test_c3_eps20_exceeds_eps0(self):
        """ε20 > ε0 required for descending branch to be valid."""
        for batch_id in (1, 2, 3):
            inst = C3WangCompression(BATCHES[batch_id])
            self.assertGreater(inst._eps20_wang(), inst._eps0_wang(),
                               msg=f"C3 Batch {batch_id}: ε20 must exceed ε0")

    def test_c3_eps20_values_approx(self):
        """Wang Eq.(10)-(11) ε20 values. Handover file: B1≈0.00735, B2≈0.00731, B3≈0.00804."""
        expected = {1: 0.00735, 2: 0.00731, 3: 0.00804}
        for batch_id, exp in expected.items():
            inst = C3WangCompression(BATCHES[batch_id])
            eps20 = inst._eps20_wang()
            self.assertAlmostEqual(eps20, exp, delta=0.0001,
                                   msg=f"C3 Batch {batch_id}: ε20={eps20:.5f}, expected≈{exp}")

    def test_c3_sigma_at_peak(self):
        """σ(ε0) = f_peak (= fc_reported for ADAPTED variant)."""
        for batch_id in (1, 2, 3):
            inst = C3WangCompression(BATCHES[batch_id])
            sigma_peak = inst.sigma(inst._eps0_wang())
            fc = BATCHES[batch_id]["fc_mpa"]
            self.assertAlmostEqual(sigma_peak, fc, places=3,
                                   msg=f"C3 Batch {batch_id}: σ(ε0)={sigma_peak:.2f} ≠ fc={fc}")

    def test_c3_sigma_residual(self):
        """σ(ε >> ε20) = λrs × f_peak = 0.30 × fc."""
        for batch_id in (1, 2, 3):
            inst = C3WangCompression(BATCHES[batch_id])
            sigma_res = inst.sigma(inst._eps20_wang() * 2.0)
            fc = BATCHES[batch_id]["fc_mpa"]
            self.assertAlmostEqual(sigma_res, 0.30 * fc, places=3,
                                   msg=f"C3 Batch {batch_id}: residual σ={sigma_res:.2f}")

    def test_c3_raw_curve_structure(self):
        """raw_sigma_eps_curve returns non-empty list with required keys."""
        for batch_id in (1, 2, 3):
            pts = C3WangCompression(BATCHES[batch_id]).raw_sigma_eps_curve()
            self.assertGreater(len(pts), 10, msg=f"C3 Batch {batch_id}: too few points")
            required = {"eps_total", "sigma_mpa", "eta", "eps_in", "branch", "tag"}
            for k in required:
                self.assertIn(k, pts[0], msg=f"Missing key: {k}")

    def test_c3_eps_in_analysis_b1(self):
        """B1: α_Wang>1 → η_cross<1; ~96.6% of ascending has εin<0."""
        an = C3WangCompression(BATCHES[1]).eps_in_analysis()
        self.assertGreater(an["alpha_wang"], 1.0, "B1 alpha_wang should be > 1")
        self.assertGreater(an["pct_ascending_negative"], 90.0,
                           f"B1: {an['pct_ascending_negative']:.1f}% expected >90%")
        self.assertLess(an["eta_crossover"], 1.0, "B1 crossover within ascending range")

    def test_c3_eps_in_analysis_b2(self):
        """B2: α_Wang>1 → ~93.9% negative."""
        an = C3WangCompression(BATCHES[2]).eps_in_analysis()
        self.assertGreater(an["alpha_wang"], 1.0)
        self.assertGreater(an["pct_ascending_negative"], 88.0,
                           f"B2: {an['pct_ascending_negative']:.1f}%")

    def test_c3_eps_in_analysis_b3_all_negative(self):
        """B3: α_Wang<1 → η_cross>1 → entire ascending has εin<0 (100%)."""
        an = C3WangCompression(BATCHES[3]).eps_in_analysis()
        self.assertAlmostEqual(an["pct_ascending_negative"], 100.0, delta=0.5,
                               msg=f"B3: {an['pct_ascending_negative']:.1f}% expected=100%")
        self.assertGreater(an["eta_crossover"], 1.0, "B3: crossover beyond ascending range")

    # ── C4 Yan source equations ────────────────────────────────────────────────

    def test_c4_ascending_peak_equals_fc(self):
        """σ_ascending(εc0) = fc for both αa bounds."""
        for batch_id in (1, 2, 3):
            inst = C4YanCompression(BATCHES[batch_id])
            fc = BATCHES[batch_id]["fc_mpa"]
            ecp = BATCHES[batch_id]["ecp"]
            for aa in inst.ALPHA_A_RANGE:
                sigma = inst.sigma_ascending(ecp, aa)
                self.assertAlmostEqual(sigma, fc, places=3,
                                       msg=f"C4 Batch {batch_id} αa={aa}: σ(εc0)={sigma:.2f}")

    def test_c4_descending_peak_equals_fc(self):
        """σ_descending(εc0) = fc for both αd bounds."""
        for batch_id in (1, 2, 3):
            inst = C4YanCompression(BATCHES[batch_id])
            fc = BATCHES[batch_id]["fc_mpa"]
            ecp = BATCHES[batch_id]["ecp"]
            for ad in inst.ALPHA_D_RANGE:
                sigma = inst.sigma_descending(ecp, ad)
                self.assertAlmostEqual(sigma, fc, places=3,
                                       msg=f"C4 Batch {batch_id} αd={ad}: σ(εc0)={sigma:.2f}")

    def test_c4_descending_decays(self):
        """Descending branch σ decreases after η=1."""
        for batch_id in (1, 2, 3):
            inst = C4YanCompression(BATCHES[batch_id])
            ecp = BATCHES[batch_id]["ecp"]
            for ad in inst.ALPHA_D_RANGE:
                s1 = inst.sigma_descending(ecp * 1.5, ad)
                s2 = inst.sigma_descending(ecp * 3.0, ad)
                self.assertGreater(s1, s2,
                                   msg=f"C4 Batch {batch_id} αd={ad}: descending must decay")

    def test_c4_raw_curve_structure(self):
        """raw_sigma_eps_curve returns well-formed list."""
        for batch_id in (1, 2, 3):
            inst = C4YanCompression(BATCHES[batch_id])
            pts = inst.raw_sigma_eps_curve(alpha_a=1.1, alpha_d=0.193)
            self.assertGreater(len(pts), 10)
            required = {"eps_total", "sigma_mpa", "eta", "eps_in", "branch", "tag"}
            for k in required:
                self.assertIn(k, pts[0])

    def test_c4_eps_in_analysis_b1_alpha_11(self):
        """B1 with αa=1.1: η_cross≈0.895 → ~89.6% negative."""
        an = C4YanCompression(BATCHES[1]).eps_in_analysis([1.1])
        pct = an[1.1]["pct_ascending_negative"]
        self.assertAlmostEqual(pct, 89.6, delta=1.0,
                               msg=f"B1 αa=1.1: {pct:.1f}% expected≈89.6%")

    def test_c4_eps_in_analysis_b2_alpha_11_all_negative(self):
        """B2 with αa=1.1: k<αa and η_cross>1 → entire ascending negative."""
        an = C4YanCompression(BATCHES[2]).eps_in_analysis([1.1])
        pct = an[1.1]["pct_ascending_negative"]
        self.assertAlmostEqual(pct, 100.0, delta=1.0,
                               msg=f"B2 αa=1.1: {pct:.1f}% expected=100%")

    def test_c4_eps_in_analysis_b3_alpha_11(self):
        """B3 with αa=1.1: k≈1.091; η_cross≈0.489 → ~48.9% negative."""
        an = C4YanCompression(BATCHES[3]).eps_in_analysis([1.1])
        pct = an[1.1]["pct_ascending_negative"]
        self.assertAlmostEqual(pct, 48.9, delta=2.0,
                               msg=f"B3 αa=1.1: {pct:.1f}% expected≈48.9%")

    def test_c4_initial_tangent_exceeds_ec(self):
        """Initial tangent αa×fc/εc0 > Ec for all batches and αa bounds."""
        for batch_id in (1, 2, 3):
            b = BATCHES[batch_id]
            Ec = b["Ec_mpa"]
            inst = C4YanCompression(b)
            for aa in inst.ALPHA_A_RANGE:
                tangent = aa * b["fc_mpa"] / b["ecp"]
                self.assertGreater(tangent, Ec,
                                   msg=f"C4 Batch {batch_id} αa={aa}: tangent={tangent:.0f} must > Ec={Ec}")


class TestBilinearTension(unittest.TestCase):
    def _make(self, batch_id):
        return BilinearTensionHardening(BATCHES[batch_id])

    def test_all_batches_generate(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            self.assertGreater(len(rows), 2, msg=f"Batch {batch_id}: too few rows")

    def test_first_cracking_strain_zero(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            self.assertAlmostEqual(rows[0]["cracking_strain"], 0.0, places=8,
                                   msg=f"Batch {batch_id}: first cracking_strain must be 0")

    def test_first_stress_is_ft_cr(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            ft_cr = BATCHES[batch_id]["ft_cr_mpa"]
            self.assertAlmostEqual(rows[0]["stress_mpa"], ft_cr, places=3)

    def test_monotone_cracking_strain(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            for i in range(1, len(rows)):
                self.assertGreater(rows[i]["cracking_strain"], rows[i - 1]["cracking_strain"],
                                   msg=f"Batch {batch_id}: cracking_strain not strictly increasing at row {i}")

    def test_peak_stress_is_ft_loc(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            ft_loc = BATCHES[batch_id]["ft_loc_mpa"]
            self.assertAlmostEqual(rows[-1]["stress_mpa"], ft_loc, places=3)

    def test_qa_passes_all_batches(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            errors = qa_tension(rows, BATCHES[batch_id]["Ec_mpa"])
            self.assertEqual(errors, [], msg=f"Batch {batch_id} QA errors: {errors}")

    def test_softening_status_review_required(self):
        for batch_id in (1, 2, 3):
            m = self._make(batch_id)
            self.assertIn("REVIEW_REQUIRED", m.softening_status)

    def test_softening_status_no_gauge_length_conversion(self):
        # Must NOT contain the erroneous "w = et_loc × GL" default conversion claim
        for batch_id in (1, 2, 3):
            m = self._make(batch_id)
            s = m.softening_status
            # Should warn against using GL directly as localization length
            self.assertIn("NOT", s)


class TestT1TianFakeh(unittest.TestCase):
    def _make(self, batch_id):
        return T1TianFakehTension(BATCHES[batch_id])

    def test_all_batches_generate(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            self.assertGreater(len(rows), 2)

    def test_first_cracking_strain_zero(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            self.assertAlmostEqual(rows[0]["cracking_strain"], 0.0, places=8)

    def test_first_stress_is_ft_cr(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            ft_cr = BATCHES[batch_id]["ft_cr_mpa"]
            self.assertAlmostEqual(rows[0]["stress_mpa"], ft_cr, places=3)

    def test_last_stress_is_ft_loc(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            ft_loc = BATCHES[batch_id]["ft_loc_mpa"]
            self.assertAlmostEqual(rows[-1]["stress_mpa"], ft_loc, places=3)

    def test_monotone_cracking_strain(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            for i in range(1, len(rows)):
                self.assertGreater(rows[i]["cracking_strain"], rows[i - 1]["cracking_strain"])

    def test_qa_passes_all_batches(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            errors = qa_tension(rows, BATCHES[batch_id]["Ec_mpa"])
            self.assertEqual(errors, [], msg=f"T1 Batch {batch_id} QA errors: {errors}")

    def test_softening_status_blocked_missing_param(self):
        for batch_id in (1, 2, 3):
            m = self._make(batch_id)
            self.assertIn("BLOCKED", m.softening_status)

    def test_softening_status_no_gauge_length_default(self):
        for batch_id in (1, 2, 3):
            m = self._make(batch_id)
            s = m.softening_status
            self.assertNotIn("w = et_loc × GL_gauge", s.replace("Do NOT use w = et_loc × GL_gauge", ""))
            self.assertIn("εu", s)

    def test_softening_status_documents_formula_source(self):
        for batch_id in (1, 2, 3):
            s = self._make(batch_id).softening_status
            # Formula must be attributed to Fakeh Table 4
            self.assertIn("Fakeh", s)
            # Must state Tian (2023) is missing from repo
            self.assertIn("Tian", s)

    def test_status_is_implemented(self):
        self.assertEqual(T1TianFakehTension.STATUS, ModelStatus.IMPLEMENTED)


class TestT2ZhaoTension(unittest.TestCase):
    def _make(self, batch_id):
        return T2ZhaoTension(BATCHES[batch_id])

    def test_all_batches_generate(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            self.assertGreater(len(rows), 5, msg=f"T2 Batch {batch_id}: too few rows")

    def test_first_cracking_strain_zero(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            self.assertAlmostEqual(rows[0]["cracking_strain"], 0.0, places=8)

    def test_first_stress_is_ft_cr(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            ft_cr = BATCHES[batch_id]["ft_cr_mpa"]
            self.assertAlmostEqual(rows[0]["stress_mpa"], ft_cr, places=3)

    def test_monotone_cracking_strain(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            for i in range(1, len(rows)):
                self.assertGreater(rows[i]["cracking_strain"], rows[i - 1]["cracking_strain"],
                                   msg=f"T2 Batch {batch_id}: cracking_strain not strictly increasing at row {i}")

    def test_all_stresses_positive(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            for i, r in enumerate(rows):
                self.assertGreater(r["stress_mpa"], 0, msg=f"T2 Batch {batch_id} row {i}")

    def test_post_peak_stress_decreases(self):
        # After the peak row (ft_loc), stress decreases (power law softening)
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            ft_loc = BATCHES[batch_id]["ft_loc_mpa"]
            # Find the index of the peak row (last row with stress == ft_loc)
            peak_idx = max(
                (i for i, r in enumerate(rows) if abs(r["stress_mpa"] - ft_loc) < 0.01),
                default=None,
            )
            self.assertIsNotNone(peak_idx, msg=f"T2 Batch {batch_id}: no peak row found")
            post_peak = rows[peak_idx + 1:]
            self.assertGreater(len(post_peak), 0, msg=f"T2 Batch {batch_id}: no post-peak rows")
            post_stresses = [r["stress_mpa"] for r in post_peak]
            for i in range(1, len(post_stresses)):
                self.assertLessEqual(post_stresses[i], post_stresses[i - 1],
                                     msg=f"T2 Batch {batch_id}: post-peak stress not decreasing at row {i}")

    def test_terminal_stress_near_02ft(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            ft_loc = BATCHES[batch_id]["ft_loc_mpa"]
            last_sigma = rows[-1]["stress_mpa"]
            # Terminal should be near 0.2×ft_loc (within some tolerance due to discrete sampling)
            self.assertLessEqual(last_sigma, ft_loc * 0.25,
                                 msg=f"T2 Batch {batch_id}: terminal stress {last_sigma:.2f} too high")
            self.assertGreater(last_sigma, ft_loc * 0.15,
                               msg=f"T2 Batch {batch_id}: terminal stress {last_sigma:.2f} too low")

    def test_qa_passes_all_batches(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            errors = qa_tension(rows, BATCHES[batch_id]["Ec_mpa"])
            self.assertEqual(errors, [], msg=f"T2 Batch {batch_id} QA errors: {errors}")

    def test_softening_status_mentions_mesh_dependency(self):
        for batch_id in (1, 2, 3):
            m = self._make(batch_id)
            s = m.softening_status
            self.assertIn("mesh", s.lower())
            self.assertIn("λclc", s)

    def test_sigma_w_params(self):
        # λclc and wtu should be computable
        for batch_id in (1, 2, 3):
            m = self._make(batch_id)
            params = m.sigma_w_params()
            self.assertIn("lambda_clc_mm", params)
            self.assertGreater(params["lambda_clc_mm"], 50)  # λclc > 50.21 mm always
            self.assertGreater(params["wtu_mm"], 0)

    def test_status_is_implemented(self):
        self.assertEqual(T2ZhaoTension.STATUS, ModelStatus.IMPLEMENTED)

    def test_fracture_energy_positive(self):
        for batch_id in (1, 2, 3):
            result = T2ZhaoTension(BATCHES[batch_id]).fracture_energy_lambda_clc()
            self.assertGreater(result["GFI_nmm"], 0.0,
                               msg=f"B{batch_id}: GFI must be positive")
            self.assertGreater(result["wtu_mm"], result["wto_mm"],
                               msg=f"B{batch_id}: wtu must exceed wto")
            self.assertGreater(result["lambda_clc_mm"], 50.0,  # λclc > 50.21 always
                               msg=f"B{batch_id}: λclc too small")

    def test_fracture_energy_tag_not_mesh(self):
        # GFI estimate must be flagged as estimate (not final Abaqus-ready)
        result = T2ZhaoTension(BATCHES[1]).fracture_energy_lambda_clc()
        self.assertIn("ESTIMATE", result["tag"])
        self.assertIn("λclc", result["tag"])


class TestQAFunctions(unittest.TestCase):
    def test_qa_compression_catches_nonzero_first_eps_in(self):
        rows = [{"stress_mpa": 50.0, "inelastic_strain": 0.001}]
        errors = qa_compression(rows, 46000)
        self.assertTrue(any("first" in e.lower() or "zero" in e.lower() for e in errors),
                        msg=f"Expected first-row error, got: {errors}")

    def test_qa_compression_catches_decreasing(self):
        rows = [
            {"stress_mpa": 50.0, "inelastic_strain": 0.0},
            {"stress_mpa": 80.0, "inelastic_strain": 0.001},
            {"stress_mpa": 90.0, "inelastic_strain": 0.0005},
        ]
        errors = qa_compression(rows, 46000)
        self.assertTrue(len(errors) > 0, "Should detect decreasing inelastic_strain")

    def test_qa_tension_catches_nonzero_first_cracking(self):
        rows = [{"stress_mpa": 9.0, "cracking_strain": 0.001}]
        errors = qa_tension(rows, 46000)
        self.assertTrue(len(errors) > 0)

    def test_qa_tension_catches_decreasing(self):
        rows = [
            {"stress_mpa": 9.0, "cracking_strain": 0.0},
            {"stress_mpa": 10.0, "cracking_strain": 0.002},
            {"stress_mpa": 10.5, "cracking_strain": 0.001},
        ]
        errors = qa_tension(rows, 46000)
        self.assertTrue(len(errors) > 0)


class TestC4YanEcAdapted(unittest.TestCase):
    """Tests for C4_YAN_EC_ADAPTED (eps_c0 = alpha_a × fc / Ec)."""

    def _make(self, batch_id, alpha_a=1.1, alpha_d=0.193):
        return C4YanEcAdaptedCompression(BATCHES[batch_id], alpha_a=alpha_a, alpha_d=alpha_d)

    def _make_lb(self, batch_id):
        return C4YanEcAdaptedLB(BATCHES[batch_id])

    def _make_ub(self, batch_id):
        return C4YanEcAdaptedUB(BATCHES[batch_id])

    # ── Status ──────────────────────────────────────────────────────────────
    def test_lb_status_implemented(self):
        self.assertEqual(C4YanEcAdaptedLB.STATUS, ModelStatus.IMPLEMENTED)

    def test_ub_status_implemented(self):
        self.assertEqual(C4YanEcAdaptedUB.STATUS, ModelStatus.IMPLEMENTED)

    # ── eps_c0 formula ───────────────────────────────────────────────────────
    def test_eps_c0_model_formula_all_batches(self):
        for batch_id in (1, 2, 3):
            for alpha_a in (1.100, 1.138):
                m = self._make(batch_id, alpha_a=alpha_a)
                fc = BATCHES[batch_id]["fc_mpa"]
                Ec = BATCHES[batch_id]["Ec_mpa"]
                expected = alpha_a * fc / Ec
                self.assertAlmostEqual(m._eps_c0_model(), expected, places=10,
                                       msg=f"B{batch_id} alpha_a={alpha_a}")

    # ── Ascending first-row eps_in = 0 (Abaqus CDP requirement) ─────────────
    def test_first_eps_in_zero_all_batches(self):
        for batch_id in (1, 2, 3):
            rows = self._make_lb(batch_id).generate_table()
            self.assertAlmostEqual(rows[0]["inelastic_strain"], 0.0, places=8,
                                   msg=f"B{batch_id} LB: first eps_in must be 0")

    def test_first_eps_in_zero_ub_all_batches(self):
        for batch_id in (1, 2, 3):
            rows = self._make_ub(batch_id).generate_table()
            self.assertAlmostEqual(rows[0]["inelastic_strain"], 0.0, places=8,
                                   msg=f"B{batch_id} UB: first eps_in must be 0")

    # ── eps_in ≥ 0 throughout (algebraic proof) ──────────────────────────────
    def test_all_eps_in_nonnegative_lb(self):
        for batch_id in (1, 2, 3):
            rows = self._make_lb(batch_id).generate_table()
            for i, r in enumerate(rows):
                self.assertGreaterEqual(r["inelastic_strain"], 0.0,
                                        msg=f"B{batch_id} LB row {i}: eps_in={r['inelastic_strain']:.2e} < 0")

    def test_all_eps_in_nonnegative_ub(self):
        for batch_id in (1, 2, 3):
            rows = self._make_ub(batch_id).generate_table()
            for i, r in enumerate(rows):
                self.assertGreaterEqual(r["inelastic_strain"], 0.0,
                                        msg=f"B{batch_id} UB row {i}: eps_in={r['inelastic_strain']:.2e} < 0")

    # ── eps_in strictly monotone ──────────────────────────────────────────────
    def test_monotone_eps_in_lb(self):
        for batch_id in (1, 2, 3):
            rows = self._make_lb(batch_id).generate_table()
            for i in range(1, len(rows)):
                self.assertGreater(rows[i]["inelastic_strain"], rows[i - 1]["inelastic_strain"],
                                   msg=f"B{batch_id} LB row {i}: eps_in not strictly increasing")

    def test_monotone_eps_in_ub(self):
        for batch_id in (1, 2, 3):
            rows = self._make_ub(batch_id).generate_table()
            for i in range(1, len(rows)):
                self.assertGreater(rows[i]["inelastic_strain"], rows[i - 1]["inelastic_strain"],
                                   msg=f"B{batch_id} UB row {i}: eps_in not strictly increasing")

    # ── Peak stress = fc (ascending top row) ─────────────────────────────────
    def test_peak_stress_equals_fc_lb(self):
        for batch_id in (1, 2, 3):
            rows = self._make_lb(batch_id).generate_table()
            fc = BATCHES[batch_id]["fc_mpa"]
            # The last ascending row (row 25 of 25) should be sigma=fc
            last_asc = rows[24]  # 0-indexed; ascending is rows 0..24 (n_asc=25)
            self.assertAlmostEqual(last_asc["stress_mpa"], fc, delta=0.01,
                                   msg=f"B{batch_id} LB: peak row sigma={last_asc['stress_mpa']:.3f} vs fc={fc}")

    # ── All stresses positive ─────────────────────────────────────────────────
    def test_all_stresses_positive_lb(self):
        for batch_id in (1, 2, 3):
            rows = self._make_lb(batch_id).generate_table()
            for i, r in enumerate(rows):
                self.assertGreater(r["stress_mpa"], 0.0,
                                   msg=f"B{batch_id} LB row {i}: sigma={r['stress_mpa']:.4f} ≤ 0")

    # ── Peak strain deviation ────────────────────────────────────────────────
    def test_peak_strain_deviation_b1_lb(self):
        dev = self._make_lb(1).peak_strain_deviation()
        # B1: k=1.054, alpha_a=1.1 → dev = (1.1/1.054 - 1)*100 ≈ +4.4%
        self.assertAlmostEqual(dev["dev_pct"], 4.4, delta=0.3,
                               msg=f"B1 LB peak dev={dev['dev_pct']:.2f}%")
        self.assertGreater(dev["eps_in_at_peak"], 0.0)

    def test_peak_strain_deviation_b2_lb(self):
        dev = self._make_lb(2).peak_strain_deviation()
        # B2: k=0.988, alpha_a=1.1 → dev = (1.1/0.988 - 1)*100 ≈ +11.4%
        self.assertAlmostEqual(dev["dev_pct"], 11.4, delta=0.5,
                               msg=f"B2 LB peak dev={dev['dev_pct']:.2f}% (largest deviation)")
        self.assertGreater(dev["eps_in_at_peak"], 0.0)

    def test_peak_strain_deviation_b3_lb(self):
        dev = self._make_lb(3).peak_strain_deviation()
        # B3: k=1.091, alpha_a=1.1 → dev ≈ +0.8%
        self.assertAlmostEqual(dev["dev_pct"], 0.8, delta=0.4,
                               msg=f"B3 LB peak dev={dev['dev_pct']:.2f}%")

    def test_peak_strain_deviation_b2_ub(self):
        dev = self._make_ub(2).peak_strain_deviation()
        # B2: k=0.988, alpha_a=1.138 → dev ≈ +15.2%
        self.assertAlmostEqual(dev["dev_pct"], 15.2, delta=0.5,
                               msg=f"B2 UB peak dev={dev['dev_pct']:.2f}%")

    # ── QA passes (Abaqus CDP table validity) ────────────────────────────────
    def test_qa_passes_all_batches_lb(self):
        for batch_id in (1, 2, 3):
            rows = self._make_lb(batch_id).generate_table()
            errors = qa_compression(rows, BATCHES[batch_id]["Ec_mpa"])
            self.assertEqual(errors, [],
                             msg=f"B{batch_id} LB QA errors: {errors}")

    def test_qa_passes_all_batches_ub(self):
        for batch_id in (1, 2, 3):
            rows = self._make_ub(batch_id).generate_table()
            errors = qa_compression(rows, BATCHES[batch_id]["Ec_mpa"])
            self.assertEqual(errors, [],
                             msg=f"B{batch_id} UB QA errors: {errors}")

    # ── eps_pl column present and equals eps_in (dc=0 at G1) ─────────────────
    def test_eps_pl_column_present_and_equals_eps_in(self):
        for batch_id in (1, 2, 3):
            rows = self._make_lb(batch_id).generate_table()
            for i, r in enumerate(rows):
                self.assertIn("eps_pl", r, msg=f"B{batch_id} LB row {i}: eps_pl column missing")
                self.assertAlmostEqual(r["eps_pl"], r["inelastic_strain"], places=9,
                                       msg=f"B{batch_id} LB row {i}: eps_pl != eps_in (dc=0)")

    # ── Descending endpoint: terminal sigma ≈ 5% fc ──────────────────────────
    def test_descending_endpoint_terminal_stress(self):
        for batch_id in (1, 2, 3):
            for make_fn in (self._make_lb, self._make_ub):
                rows = make_fn(batch_id).generate_table()
                fc = BATCHES[batch_id]["fc_mpa"]
                sigma_last = rows[-1]["stress_mpa"]
                self.assertAlmostEqual(sigma_last / fc, 0.05, delta=0.005,
                                       msg=f"B{batch_id}: terminal sigma={sigma_last:.2f} not near 0.05×fc={0.05*fc:.2f}")


class TestC4YanEcAdaptedCrossVariants(unittest.TestCase):
    """Tests for C4_ADAPTED_LA_HD (αa=1.100,αd=0.312) and C4_ADAPTED_HA_LD (αa=1.138,αd=0.193)."""

    def _make_lahd(self, batch_id):
        return C4YanEcAdaptedLAHD(BATCHES[batch_id])

    def _make_hald(self, batch_id):
        return C4YanEcAdaptedHALD(BATCHES[batch_id])

    def test_status_implemented(self):
        self.assertEqual(C4YanEcAdaptedLAHD.STATUS, ModelStatus.IMPLEMENTED)
        self.assertEqual(C4YanEcAdaptedHALD.STATUS, ModelStatus.IMPLEMENTED)

    def test_all_eps_in_nonneg_lahd(self):
        for batch_id in (1, 2, 3):
            rows = self._make_lahd(batch_id).generate_table()
            for i, r in enumerate(rows):
                self.assertGreaterEqual(r["inelastic_strain"], 0.0,
                                        msg=f"B{batch_id} LA_HD row {i}: eps_in<0")

    def test_all_eps_in_nonneg_hald(self):
        for batch_id in (1, 2, 3):
            rows = self._make_hald(batch_id).generate_table()
            for i, r in enumerate(rows):
                self.assertGreaterEqual(r["inelastic_strain"], 0.0,
                                        msg=f"B{batch_id} HA_LD row {i}: eps_in<0")

    def test_monotone_lahd(self):
        for batch_id in (1, 2, 3):
            rows = self._make_lahd(batch_id).generate_table()
            for i in range(1, len(rows)):
                self.assertGreater(rows[i]["inelastic_strain"], rows[i - 1]["inelastic_strain"],
                                   msg=f"B{batch_id} LA_HD row {i}: eps_in not strictly increasing")

    def test_monotone_hald(self):
        for batch_id in (1, 2, 3):
            rows = self._make_hald(batch_id).generate_table()
            for i in range(1, len(rows)):
                self.assertGreater(rows[i]["inelastic_strain"], rows[i - 1]["inelastic_strain"],
                                   msg=f"B{batch_id} HA_LD row {i}: eps_in not strictly increasing")

    def test_qa_passes_lahd(self):
        for batch_id in (1, 2, 3):
            rows = self._make_lahd(batch_id).generate_table()
            errors = qa_compression(rows, BATCHES[batch_id]["Ec_mpa"])
            self.assertEqual(errors, [], msg=f"B{batch_id} LA_HD QA: {errors}")

    def test_qa_passes_hald(self):
        for batch_id in (1, 2, 3):
            rows = self._make_hald(batch_id).generate_table()
            errors = qa_compression(rows, BATCHES[batch_id]["Ec_mpa"])
            self.assertEqual(errors, [], msg=f"B{batch_id} HA_LD QA: {errors}")

    def test_peak_strain_identical_ascending_only(self):
        # eps_c0 depends only on alpha_a, not alpha_d — LAHD and LB must share same peak strain
        for batch_id in (1, 2, 3):
            dev_lb = C4YanEcAdaptedLB(BATCHES[batch_id]).peak_strain_deviation()
            dev_lahd = self._make_lahd(batch_id).peak_strain_deviation()
            self.assertAlmostEqual(dev_lb["eps_c0_model"], dev_lahd["eps_c0_model"], places=9,
                                   msg=f"B{batch_id}: LAHD and LB have different eps_c0 (same alpha_a=1.100)")

    def test_descending_endpoint_positive_lahd(self):
        # Terminal row must have sigma > 0 for all batches
        for batch_id in (1, 2, 3):
            rows = self._make_lahd(batch_id).generate_table()
            self.assertGreater(rows[-1]["stress_mpa"], 0.0,
                               msg=f"B{batch_id} LA_HD: terminal stress ≤ 0")

    def test_descending_endpoint_positive_hald(self):
        for batch_id in (1, 2, 3):
            rows = self._make_hald(batch_id).generate_table()
            self.assertGreater(rows[-1]["stress_mpa"], 0.0,
                               msg=f"B{batch_id} HA_LD: terminal stress ≤ 0")


class TestModelRegistryConsistency(unittest.TestCase):
    def test_compression_models_dict_has_all_keys(self):
        for key in ("REF_POPOVICS", "C1", "C2", "C3", "C4",
                    "C4_ADAPTED_LB", "C4_ADAPTED_LA_HD", "C4_ADAPTED_HA_LD", "C4_ADAPTED_UB"):
            self.assertIn(key, COMPRESSION_MODELS)

    def test_tension_models_dict_has_all_keys(self):
        for key in ("REF_BILINEAR", "T1", "T2"):
            self.assertIn(key, TENSION_MODELS)

    def test_c1_c2_status_implemented(self):
        for key in ("C1", "C2"):
            cls = COMPRESSION_MODELS[key]
            self.assertEqual(cls.STATUS, ModelStatus.IMPLEMENTED,
                             msg=f"{key} should be IMPLEMENTED")

    def test_c3_c4_status_blocked(self):
        for key in ("C3", "C4"):
            cls = COMPRESSION_MODELS[key]
            self.assertEqual(cls.STATUS, ModelStatus.BLOCKED,
                             msg=f"{key} should be BLOCKED")

    def test_t1_t2_status_implemented(self):
        for key in ("T1", "T2"):
            cls = TENSION_MODELS[key]
            self.assertEqual(cls.STATUS, ModelStatus.IMPLEMENTED,
                             msg=f"{key} should be IMPLEMENTED")


if __name__ == "__main__":
    unittest.main(verbosity=2)

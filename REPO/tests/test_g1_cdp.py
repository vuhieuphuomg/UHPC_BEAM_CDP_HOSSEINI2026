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
    def test_c3_status_is_blocked(self):
        cls = COMPRESSION_MODELS["C3"]
        self.assertEqual(cls.STATUS, ModelStatus.BLOCKED)

    def test_c4_status_is_blocked(self):
        cls = COMPRESSION_MODELS["C4"]
        self.assertEqual(cls.STATUS, ModelStatus.BLOCKED)

    def test_c3_raises_on_generate(self):
        cls = COMPRESSION_MODELS["C3"]
        inst = cls(BATCHES[1])
        with self.assertRaises(ModelNotAvailableError):
            inst.generate_table()

    def test_c4_raises_on_generate(self):
        cls = COMPRESSION_MODELS["C4"]
        inst = cls(BATCHES[1])
        with self.assertRaises(ModelNotAvailableError):
            inst.generate_table()

    def test_c3_blocked_reason_mentions_ascending(self):
        cls = COMPRESSION_MODELS["C3"]
        self.assertIn("ascending", cls.BLOCKED_REASON.lower())

    def test_c4_blocked_reason_mentions_alpha_a(self):
        cls = COMPRESSION_MODELS["C4"]
        self.assertIn("alpha", cls.BLOCKED_REASON.lower())


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
            # Must warn against GL default conversion
            s = m.softening_status
            self.assertNotIn("w = et_loc × GL_gauge", s.replace("Do NOT use w = et_loc × GL_gauge", ""))
            # Should reference εu as the missing parameter
            self.assertIn("εu", s)

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


class TestModelRegistryConsistency(unittest.TestCase):
    def test_compression_models_dict_has_all_keys(self):
        for key in ("REF_POPOVICS", "C1", "C2", "C3", "C4"):
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

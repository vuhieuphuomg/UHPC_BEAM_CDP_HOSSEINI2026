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

# Add REPO/tools to path
_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_tools_dir = os.path.join(_repo_root, "tools")
if _tools_dir not in sys.path:
    sys.path.insert(0, _tools_dir)

from cdp_builder.batch_data import BATCHES, alpha_compression, eps_in_peak
from cdp_builder.models import (
    PopovicsCompression, BilinearTensionHardening,
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
            self.assertAlmostEqual(
                rows[0]["cracking_strain"], 0.0, places=8,
                msg=f"Batch {batch_id}: first cracking_strain must be 0",
            )

    def test_first_stress_is_ft_cr(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            ft_cr = BATCHES[batch_id]["ft_cr_mpa"]
            self.assertAlmostEqual(rows[0]["stress_mpa"], ft_cr, places=3,
                                   msg=f"Batch {batch_id}: first stress should be ft_cr")

    def test_monotone_cracking_strain(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            for i in range(1, len(rows)):
                self.assertGreater(
                    rows[i]["cracking_strain"],
                    rows[i - 1]["cracking_strain"],
                    msg=f"Batch {batch_id}: cracking_strain not strictly increasing at row {i}",
                )

    def test_peak_stress_is_ft_loc(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            ft_loc = BATCHES[batch_id]["ft_loc_mpa"]
            self.assertAlmostEqual(
                rows[-1]["stress_mpa"], ft_loc, places=3,
                msg=f"Batch {batch_id}: last row stress should be ft_loc",
            )

    def test_qa_passes_all_batches(self):
        for batch_id in (1, 2, 3):
            rows = self._make(batch_id).generate_table()
            errors = qa_tension(rows, BATCHES[batch_id]["Ec_mpa"])
            self.assertEqual(errors, [], msg=f"Batch {batch_id} QA errors: {errors}")

    def test_softening_status_review_required(self):
        for batch_id in (1, 2, 3):
            m = self._make(batch_id)
            self.assertIn("REVIEW_REQUIRED", m.softening_status)


class TestReviewRequiredStubs(unittest.TestCase):
    def test_compression_stubs_raise(self):
        for model_id in ("C1", "C2", "C3", "C4"):
            cls = COMPRESSION_MODELS[model_id]
            inst = cls(BATCHES[1])
            with self.assertRaises(ModelNotAvailableError,
                                   msg=f"{model_id} should raise ModelNotAvailableError"):
                inst.generate_table()

    def test_tension_stubs_raise(self):
        for model_id in ("T1", "T2"):
            cls = TENSION_MODELS[model_id]
            inst = cls(BATCHES[1])
            with self.assertRaises(ModelNotAvailableError,
                                   msg=f"{model_id} should raise ModelNotAvailableError"):
                inst.generate_table()

    def test_stub_status_is_review_required(self):
        for model_id in ("C1", "C2", "C3", "C4"):
            cls = COMPRESSION_MODELS[model_id]
            self.assertEqual(cls.STATUS, ModelStatus.REVIEW_REQUIRED)
        for model_id in ("T1", "T2"):
            cls = TENSION_MODELS[model_id]
            self.assertEqual(cls.STATUS, ModelStatus.REVIEW_REQUIRED)


class TestQAFunctions(unittest.TestCase):
    """Direct QA function tests with crafted inputs."""

    def test_qa_compression_catches_nonzero_first_eps_in(self):
        rows = [{"stress_mpa": 50.0, "inelastic_strain": 0.001}]
        errors = qa_compression(rows, 46000)
        self.assertTrue(any("first" in e.lower() or "zero" in e.lower() for e in errors),
                        msg=f"Expected first-row error, got: {errors}")

    def test_qa_compression_catches_decreasing(self):
        rows = [
            {"stress_mpa": 50.0, "inelastic_strain": 0.0},
            {"stress_mpa": 80.0, "inelastic_strain": 0.001},
            {"stress_mpa": 90.0, "inelastic_strain": 0.0005},  # decreasing
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
            {"stress_mpa": 10.5, "cracking_strain": 0.001},  # decreasing
        ]
        errors = qa_tension(rows, 46000)
        self.assertTrue(len(errors) > 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

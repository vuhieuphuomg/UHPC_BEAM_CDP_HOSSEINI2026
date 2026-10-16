import csv
import json
import unittest
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'REPO'/'tools'))
from fe_control import load,audit
from cdp_table_qa import validate

class ProjectContract(unittest.TestCase):
    def test_registry_exact(self):
        rows,gates,state=load()
        self.assertEqual(audit(rows,gates,state)['problems'],[])
        self.assertEqual(len(rows),62)
        self.assertEqual(sum(x['kind']=='FULL_BEAM' for x in rows),44)
    def test_holdout_sealed(self):
        rows,gates,state=load()
        holdout=[x for x in rows if x['phase']=='P3_HOLDOUT']
        self.assertEqual(len(holdout),8)
        self.assertTrue(all('FROZEN_MODEL' in x['required_gates'] for x in holdout))
        self.assertTrue(all('HOLD'==gates['special_prerequisites']['FROZEN_MODEL']['status'] for x in holdout))
    def test_no_self_reference(self):
        rows,gates,state=load()
        self.assertTrue(all(x['source_run_id']!=x['run_id'] for x in rows))
    def test_cdp_negative_inelastic_rejected(self):
        self.assertTrue(validate([{'stress_mpa':'153.2','inelastic_strain':str(0.0032-153.2/47300),'damage':'0'}],47300))
    def test_cdp_valid_example(self):
        self.assertEqual(validate([{'stress_mpa':'10','inelastic_strain':'0','damage':'0'},{'stress_mpa':'20','inelastic_strain':'0.0001','damage':'0'}],45000),[])
    def test_cdp_decreasing_plastic_rejected(self):
        rows=[{'stress_mpa':'20','inelastic_strain':'0','damage':'0'}, {'stress_mpa':'15','inelastic_strain':'0.0001','damage':'0.3'}]
        self.assertTrue(validate(rows,45000))
    def test_cdp_first_inelastic_zero(self):
        self.assertTrue(validate([{'stress_mpa':'10','inelastic_strain':'0.0001','damage':'0'}],45000))
    def test_no_live_solver_permission(self):
        rows,gates,state=load()
        self.assertFalse(state['solver_authorized'])
        self.assertFalse(state['automatic_submit_enabled'])

if __name__=='__main__':unittest.main()

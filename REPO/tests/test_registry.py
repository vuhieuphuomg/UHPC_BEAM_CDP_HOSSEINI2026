import csv,unittest
from pathlib import Path
class RegistryTests(unittest.TestCase):
 def test_manifest(self):
  p=Path(__file__).resolve().parents[2]/'00_CONTROL'/'RUN_REGISTRY_MASTER_V3.csv'
  with p.open(encoding='utf-8-sig',newline='') as f:r=list(csv.DictReader(f))
  self.assertEqual(len(r),62)
  self.assertEqual(len(set(x['run_id'] for x in r)),62)
  self.assertEqual(sum(x['kind']=='MATERIAL_COUPON' for x in r),18)
  self.assertEqual(sum(x['kind']!='MATERIAL_COUPON' for x in r),44)
if __name__=='__main__':unittest.main()

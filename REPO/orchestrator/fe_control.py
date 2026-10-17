#!/usr/bin/env python3
"""Fail-closed orchestration skeleton. Run with Python 3 OUTSIDE Abaqus.
Do not claim this builds a model. Real builder must be independently verified.
"""
import argparse,csv,json,hashlib,os,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]
REG=BASE/'00_CONTROL'/'RUN_REGISTRY_MASTER_V3.csv'
CFG=BASE/'REPO'/'config'/'runtime.json'
BLOCK=BASE/'00_CONTROL'/'BLOCKERS.md'
def read():
    with REG.open(encoding='utf-8-sig',newline='') as fh: rows=list(csv.DictReader(fh))
    return rows,json.loads(CFG.read_text(encoding='utf-8'))
def validate(rows):
    ids=[r.get('run_id','') for r in rows]
    assert len(rows)==62, 'Expected 62 planned rows, got '+str(len(rows))
    assert len(set(ids))==len(ids), 'Duplicate run ID'
    assert all(x and x.strip()==x for x in ids), 'Invalid ID'
    assert sum(r['kind']=='MATERIAL_COUPON' for r in rows)==18
    assert sum(r['kind']!='MATERIAL_COUPON' for r in rows)==44
    assert all(r.get('status') not in ['COMPLETED','VALIDATED'] for r in rows),'Unverified success entry'
    return {'total':len(rows),'material':18,'beam':44,'unique':len(set(ids))}
def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['status','validate','next','dry-run','archive-check']);p.add_argument('--run-id');a=p.parse_args()
    rows,cfg=read();stats=validate(rows)
    if a.action=='validate':print(json.dumps(stats,indent=2));return
    if a.action=='status':
        print(json.dumps({'registry':stats,'solver_authorized':cfg['solver_authorized'],'abaqus_version_verified':cfg['abaqus_version_verified'],'material_gate_passed':cfg['material_gate_passed'],'built_model_gate_passed':cfg['built_model_gate_passed'],'blockers':str(BLOCK)},indent=2));return
    if a.action=='next':
        pending=[r for r in rows if r['status'] not in ['DONE','VALIDATED']]
        print(json.dumps([{'run_id':r['run_id'],'status':r['status'],'gate':r['gate']} for r in pending[:5]],indent=2));return
    if a.action=='archive-check':
        print('ARCHIVE DISABLED. Verify complete ODB, result hashes and Drive write API first.');return
    if a.action=='dry-run':
        r=next((r for r in rows if r['run_id']==a.run_id),rows[0] if rows else None)
        print('DRY_RUN only:',json.dumps(r,indent=2,ensure_ascii=False))
        blockers=[k for k in ['solver_authorized','abaqus_version_verified','material_gate_passed','built_model_gate_passed'] if not cfg.get(k)]
        if blockers:print('BLOCKED:',','.join(blockers))
        print('No Abaqus subprocess executed; no configuration mutated.')
if __name__=='__main__':main()

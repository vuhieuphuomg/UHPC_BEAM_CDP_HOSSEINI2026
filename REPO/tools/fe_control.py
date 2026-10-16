#!/usr/bin/env python3
"""Read-only project controller: NO ABAQUS submission, no status mutation."""
import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / '00_CONTROL' / 'RUN_REGISTRY_MASTER_V5.csv'
GATES = ROOT / '00_CONTROL' / 'GATES_V5.json'
STATE = ROOT / '00_CONTROL' / 'PROJECT_STATE_V5.json'
KNOWN = ('P0_MATERIAL', 'P1_TENSION', 'P2_COMPRESSION',
         'P4_MESH', 'P5_CDP_SENSITIVITY', 'P3_HOLDOUT', 'P6_HSS_CONDITIONAL')
PROHIBITED = ('COMPLETED', 'VALIDATED', 'DONE', 'PASS', 'SOLVER_OK')

def load():
    with REGISTRY.open('r', encoding='utf-8-sig', newline='') as fh:
        rows = list(csv.DictReader(fh))
    return rows, json.loads(GATES.read_text(encoding='utf-8')), json.loads(STATE.read_text(encoding='utf-8'))

def gate_state(gates, name):
    for section in ('scientific_gates', 'special_prerequisites'):
        if name in gates.get(section, {}):
            return gates[section][name]['status']
    raise ValueError('Unknown required gate: ' + name)

def audit(rows, gates, state):
    problems = []
    ids = [r['run_id'] for r in rows]
    kind = Counter(r['kind'] for r in rows)
    phase = Counter(r['phase'] for r in rows)
    if len(rows) != 62 or len(set(ids)) != 62 or not all(ids):
        problems.append('Expected exactly 62 unique, nonempty IDs')
    if kind != {'MATERIAL_COUPON': 18, 'FULL_BEAM': 44}:
        problems.append('Expected 18 coupons and 44 full-beam jobs: ' + str(dict(kind)))
    expected = {'P0_MATERIAL':18,'P1_TENSION':8,'P2_COMPRESSION':12,
                'P4_MESH':6,'P5_CDP_SENSITIVITY':8,'P3_HOLDOUT':8,
                'P6_HSS_CONDITIONAL':2}
    if dict(phase) != expected:
        problems.append('Phase count mismatch: ' + str(dict(phase)))
    for r in rows:
        if r['source_run_id'] == r['run_id']:
            problems.append(r['run_id'] + ': self-reference forbidden')
        if r['status'] in PROHIBITED or r['execution_permission'] != 'HOLD_NOT_AUTHORIZED':
            problems.append(r['run_id'] + ': unexpected success/permission')
        if r['qa_status'] != 'NOT_RUN':
            problems.append(r['run_id'] + ': QA unexpectedly marked done')
        for g in r['required_gates'].split(';'):
            try:gate_state(gates,g)
            except ValueError as e:problems.append(r['run_id'] + ': ' + str(e))
        if r['phase'] not in KNOWN:
            problems.append(r['run_id']+': unknown phase')
    if state.get('solver_authorized') or state.get('automatic_submit_enabled'):
        problems.append('Solver must remain disabled in preparation release')
    if gates.get('release_status') != 'PREPARATION_ONLY':
        problems.append('V5 release must remain preparation-only')
    return {'total':len(rows),'coupons':kind['MATERIAL_COUPON'],
            'beams':kind['FULL_BEAM'],'phases':dict(phase),'problems':problems}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('action',choices=['validate','status','next','preview'])
    ap.add_argument('--run-id',default=None)
    args=ap.parse_args()
    rows,gates,state=load()
    summary=audit(rows,gates,state)
    if args.action=='validate':
        print(json.dumps(summary,indent=2,ensure_ascii=False))
        return 1 if summary['problems'] else 0
    if summary['problems']:
        print('REGISTRY INVALID; stop.\n'+json.dumps(summary,indent=2),file=sys.stderr)
        return 2
    if args.action=='status':
        print(json.dumps({'active_stage':state['active_stage'],
           'next_action':state['next_action'],'solver_authorized':False,
           'master_cae_verified':state['master_cae_verified'],
           'gate_status':{k:v['status'] for k,v in gates['scientific_gates'].items()},
           'registry':{'total':62,'coupons':18,'beams':44}},indent=2,ensure_ascii=False))
    elif args.action=='next':
        print(json.dumps({'next_action':state['next_action'],
          'pending_stage':state['active_stage'], 'suggested_work':'G0 source audit only',
          'ready_solver_jobs':0},indent=2))
    elif args.action=='preview':
        if not args.run_id:
            ap.error('--run-id required for preview')
        r=next((x for x in rows if x['run_id']==args.run_id),None)
        if r is None:
            ap.error('Unknown run ID')
        missing=[g for g in r['required_gates'].split(';') if gate_state(gates,g)!='PASS']
        print(json.dumps({'run_id':r['run_id'],'phase':r['phase'],
          'specimen_id':r['specimen_id'],'required_gates':r['required_gates'],
          'blocked_by':missing,'solver_authorized':False,
          'submit_attempted':False,'candidate':r},indent=2,ensure_ascii=False))
    return 0

if __name__=='__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Syntactic/consistency gate for Abaqus CDP compression tables (does NOT validate physics)."""
import argparse
import csv
import json
import math
import sys


def validate(rows, E):
    errors=[]
    if E<=0 or not math.isfinite(E):
        return ['E must be finite and positive']
    prior=-float('inf')
    prior_pl=-float('inf')
    prior_damage=0.0
    for i,r in enumerate(rows,2):
        try:
            sigma=float(r['stress_mpa'])
            eps_in=float(r['inelastic_strain'])
        except (KeyError,ValueError) as exc:
            errors.append('line {} invalid stress/inelastic: {}'.format(i,exc))
            continue
        if not (math.isfinite(sigma) and math.isfinite(eps_in)):
            errors.append('line {} nonfinite'.format(i));continue
        if i==2 and abs(eps_in)>1e-9:
            errors.append('line {} first inelastic strain must be zero for Abaqus compression hardening'.format(i))
        if sigma<=0 or eps_in<0 or eps_in<=prior:
            errors.append('line {} invalid ordering/negative strain/stress'.format(i))
        prior=eps_in
        if 'damage' in r and r['damage'] not in ('',None):
            try:d=float(r['damage'])
            except ValueError:
                errors.append('line {} invalid damage'.format(i));continue
            if not (0<=d<1):
                errors.append('line {} damage must be [0,1)'.format(i))
                continue
            eps_pl=eps_in-(d/(1.0-d))*sigma/E
            if d+1e-12<prior_damage:
                errors.append('line {} damage decreases'.format(i))
            if eps_pl<(-1e-10) or eps_pl+1e-10<prior_pl:
                errors.append('line {} implied plastic strain negative or decreases'.format(i))
            prior_damage=d
            prior_pl=eps_pl
    return errors


def main():
    p=argparse.ArgumentParser()
    p.add_argument('csv_file')
    p.add_argument('--elastic-mpa',type=float,required=True)
    a=p.parse_args()
    with open(a.csv_file,encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    errors=validate(rows,a.elastic_mpa)
    print(json.dumps({'table':a.csv_file,'rows':len(rows),'errors':errors},indent=2))
    return 0 if rows and not errors else 1

if __name__=='__main__':sys.exit(main())

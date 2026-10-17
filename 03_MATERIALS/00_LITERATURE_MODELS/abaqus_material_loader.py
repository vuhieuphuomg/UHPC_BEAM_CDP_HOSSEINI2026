# -*- coding: utf-8 -*-
"""Abaqus 2022 CAE material-only handoff. Does NOT create geometry/jobs or run.

Safe usage from an existing Abaqus CAE kernel script:
    from abaqus_material_loader import apply_materials
    apply_materials(mdb.models['Model-1'], 'CDP_CONFIRMED.json')

All unmeasured CDP parameters require explicit analyst confirmation. No defaults.
"""
import json

def _fail(message):
    raise ValueError('CDP_EVIDENCE_GATE: ' + message)

def _rows(rows, label, expected=None):
    if not rows or (expected is not None and len(rows)!=expected):
        _fail(label + ' requires nonempty fully confirmed numeric rows')
    for i, r in enumerate(rows):
        if not isinstance(r,(list,tuple)) or len(r)!=2 or None in r:
            _fail(label + ' bad row ' + str(i))
        if r[0] < 0 or r[1] < 0:
            _fail(label + ' negative value at ' + str(i))
    return tuple(tuple(float(z) for z in row) for row in rows)

def load_confirmed_config(path):
    with open(path, 'r') as f:
        cfg=json.load(f)
    for a in cfg.get('materials',[]):
        if not isinstance(a.get('E_MPa'),(int,float)) or a['E_MPa']<=0:
            _fail('E_MPa missing for '+str(a.get('name')))
        if a.get('nu') is None or not (0 <= a['nu'] < .5):
            _fail('nu not explicitly confirmed for '+a['name'])
        c=a.get('CDP') or {}
        keys=('psi_deg','eccentricity','fb0_over_fc0','Kc','viscosity')
        if any(c.get(k) is None for k in keys):
            _fail('CDP parameters incomplete for '+a['name'])
        if not (0<=c['psi_deg']<90 and c['eccentricity']>0 and c['fb0_over_fc0']>=1 and .5<c['Kc']<=1 and c['viscosity']>=0):
            _fail('CDP domain invalid for '+a['name'])
        hard=_rows(a.get('compression_hardening_sigma_epsin'),a['name']+' compression')
        if len(hard)<2 or abs(hard[0][1])>1e-10:
            _fail('Compression curve must start at eps_in=0 and have >=2 points')
        for a0,b0 in zip(hard[:-1],hard[1:]):
            if b0[1]<=a0[1]:_fail('Compression inelastic strain must increase strictly')
        gfi=_rows(a.get('tension_GFI_ft_Gf_Nmm'),a['name']+' tension GFI',expected=1)
        if gfi[0][0]<=0 or gfi[0][1]<=0:_fail('GFI ft and fracture energy must be positive')
        for name in ('compression_damage_dc_epsin','tension_damage_dt_epsck'):
            damage=a.get(name) or []
            if damage:
                rr=_rows(damage,a['name']+' '+name)
                if any(not (0<=d<1) for d,e in rr):_fail(name+' damage out of range')
                if any(rr[i+1][1] <= rr[i][1] for i in range(len(rr)-1)):_fail(name+' strain must increase')
                if any(rr[i+1][0] < rr[i][0] for i in range(len(rr)-1)):_fail(name+' damage must not decrease')
        if a.get('evidence','').startswith('PAPER TABLE 2 elastic anchor only'):
            _fail('Template is unconfirmed; replace evidence with an explicit analyst-approved source/assumption ID')
    if not cfg.get('materials'):_fail('No materials')
    return cfg

def apply_materials(model, confirmed_config_path):
    # Validate FIRST, before modifying existing Abaqus model.
    cfg=load_confirmed_config(confirmed_config_path)
    from abaqusConstants import GFI
    for r in cfg['materials']:
        if r['name'] in model.materials.keys():
            _fail('Duplicate material: '+r['name']+'; do not overwrite baseline')
    for r in cfg['materials']:
        mat=model.Material(name=r['name'])
        mat.Elastic(table=((float(r['E_MPa']),float(r['nu'])),))
        c=r['CDP']
        mat.ConcreteDamagedPlasticity(table=((float(c['psi_deg']),float(c['eccentricity']),float(c['fb0_over_fc0']),float(c['Kc']),float(c['viscosity'])),))
        mat.concreteDamagedPlasticity.ConcreteCompressionHardening(table=_rows(r['compression_hardening_sigma_epsin'],'compression'))
        mat.concreteDamagedPlasticity.ConcreteTensionStiffening(table=_rows(r['tension_GFI_ft_Gf_Nmm'],'tension'),type=GFI)
        if r.get('compression_damage_dc_epsin'):
            mat.concreteDamagedPlasticity.ConcreteCompressionDamage(table=_rows(r['compression_damage_dc_epsin'],'compression damage'))
        if r.get('tension_damage_dt_epsck'):
            mat.concreteDamagedPlasticity.ConcreteTensionDamage(table=_rows(r['tension_damage_dt_epsck'],'tension damage'))
    return [r['name'] for r in cfg['materials']]

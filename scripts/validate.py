"""Offline structural and provenance checks; not a substitute for source review."""
import json
import pathlib
import re
import sys
from collections import Counter
from urllib.parse import urlparse
from fssai import eligible, district
from directory import load_directory
ROOT=pathlib.Path(__file__).resolve().parents[1]

def validate(data):
    errors=[];ids=set();licences=set()
    for p in data['establishments']:
        key=p.get('id',''); prefix=f'{key}: '
        if not key or key in ids: errors.append(prefix+'missing/duplicate ID')
        ids.add(key)
        for f in ('name','address','district','category','status','note'):
            if not isinstance(p.get(f),str) or not p[f].strip(): errors.append(prefix+'missing '+f)
        if p.get('status') not in ('positive','historical','suspension','unknown'): errors.append(prefix+'unknown status')
        if p.get('current_licence_status','unknown')!='unknown': errors.append(prefix+'current status requires separate official verification policy')
        if not isinstance(p.get('events'),list) or not p['events']: errors.append(prefix+'missing events'); continue
        for e in p['events']:
            for f in ('date','title','description','source'):
                if not isinstance(e.get(f),str) or not e[f]: errors.append(prefix+'missing event '+f)
            u=urlparse(e.get('source',''))
            if u.scheme!='https' or not u.hostname or u.username or u.password: errors.append(prefix+'invalid source URL')
        if key.startswith('fssai-'):
            lic=p.get('licence_number','')
            if not re.fullmatch(r'\d{14}',lic) or lic in licences or key!='fssai-'+lic: errors.append(prefix+'invalid/duplicate licence')
            licences.add(lic)
            for e in p['events']:
                if e.get('type')=='hygiene_rating' and (e.get('source_type')!='official_register' or not e.get('checked_at')): errors.append(prefix+'missing provenance')
    return errors

def main():
    d=load_directory(); errors=validate(d)
    snapshot=json.loads((ROOT/'data/sources/fssai-2026-10-12.json').read_text())
    expected={(r['licence'],r['source']):r for r in snapshot['rows'] if eligible(r)}
    actual={}
    for p in d['establishments']:
        if not p['id'].startswith('fssai-'): continue
        for e in p['events']:
            k=(p['licence_number'],e['source']);r=expected.get(k);actual[k]=e
            if not r or any(e.get(f)!=r[s] for f,s in [('points','points'),('published_rating','rating'),('register_valid_from','valid_from'),('register_valid_upto','valid_upto')]): errors.append(p['id']+': snapshot mismatch')
            elif p['district']!=district(r['jurisdiction']): errors.append(p['id']+': district mismatch')
    if set(actual)!=set(expected): errors.append('Imported event coverage differs from reviewed snapshot')
    if errors: print('\n'.join(errors)); return 1
    print(f"Validated {len(d['establishments'])} records, {len(expected)} official register events, and unique outlet identifiers.")
    return 0
if __name__=='__main__': sys.exit(main())

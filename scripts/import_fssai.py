"""Reproduce reviewed imports from a local snapshot, never from a live daily fetch.
Run: python scripts/import_fssai.py --snapshot data/sources/fssai-2026-10-12.json --apply
Without --apply, previews counts only. Existing outlet history/status is preserved.
"""
import argparse
import datetime as dt
import json
import pathlib
from fssai import eligible, district
from directory import load_directory, save_directory
ROOT = pathlib.Path(__file__).resolve().parents[1]

def merge(data, snapshot):
    existing = {p['id']: p for p in data['establishments']}
    licences = {p.get('licence_number'): p for p in data['establishments'] if p.get('licence_number')}
    added = events = 0
    for row in snapshot['rows']:
        if not eligible(row): continue
        licence = row['licence']; key = 'fssai-' + licence
        p = licences.get(licence) or existing.get(key)
        if p is None:
            p = {'id':key, 'name':row['name'], 'address':'Street address not supplied in the source register',
                 'city':'', 'district':district(row['jurisdiction']), 'category':row['category'],
                 'status':'positive', 'licence_number':licence, 'source_jurisdiction':row['jurisdiction'],
                 'location_precision':'regulatory jurisdiction only', 'current_licence_status':'unknown',
                 'record_reviewed_at':snapshot['retrieved_at'][:10],
                 'note':'Historical FSSAI Hygiene Rating Scheme record. Register date is shown; '
                        'current certificate validity, licensing and hygiene are unverified. '
                        'The licence number identifies this record; it must not be applied to other branches. '
                        'Street address and city are not supplied by this register.', 'events':[]}
            data['establishments'].append(p); existing[key] = p; licences[licence] = p; added += 1
        if any(e.get('source') == row['source'] for e in p['events']): continue
        date = dt.datetime.strptime(row['valid_from'], '%d-%m-%Y').date().isoformat()
        p['events'].append({'date':date, 'date_precision':'register valid-from date',
            'type':'hygiene_rating', 'title':'Historical FSSAI hygiene rating recorded',
            'description':f"FSSAI register: {row['points']} points; published percentage/rating {row['rating']}. "
                          'This is a dated scheme record, not proof of present-day clearance.',
            'source':row['source'], 'source_type':'official_register',
            'register_source':snapshot['url'], 'source_snapshot':'data/sources/fssai-2026-10-12.json',
            'checked_at':snapshot['retrieved_at'][:10], 'register_valid_from':row['valid_from'],
            'register_valid_upto':row['valid_upto'], 'points':row['points'], 'published_rating':row['rating']})
        events += 1
    return added, events

def main():
    a=argparse.ArgumentParser(); a.add_argument('--snapshot',required=True,type=pathlib.Path); a.add_argument('--apply',action='store_true'); args=a.parse_args()
    path=ROOT/'data/establishments.json'; data=load_directory(path); snapshot=json.loads(args.snapshot.read_text())
    result=merge(data,snapshot); print(f'New licence records: {result[0]}; new events: {result[1]}')
    if args.apply: save_directory(data,path)
if __name__=='__main__': main()

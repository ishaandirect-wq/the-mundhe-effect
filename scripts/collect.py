"""Free daily discovery of potential Maharashtra food-safety reports.

This script NEVER publishes accusations or changes establishment status.
It merely appends article leads to the review queue for manual verification.
Requires Python 3.11+ standard library only.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import pathlib
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEST = ROOT / 'data' / 'review_candidates.json'
QUERIES = [
    'Maharashtra FDA food licence suspended restaurant when:7d',
    'Maharashtra FDA restaurant inspection licence restored when:7d',
    'Maharashtra food safety cloud kitchen action when:7d',
    'महाराष्ट्र अन्न औषध प्रशासन हॉटेल परवाना निलंबित when:7d',
    'महाराष्ट्र अन्न औषध प्रशासन अन्न भेसळ तपासणी when:7d',
]

def fetch_rss(query: str) -> list[dict]:
    url = 'https://news.google.com/rss/search?' + urllib.parse.urlencode({
        'q': query, 'hl': 'en-IN', 'gl': 'IN', 'ceid': 'IN:en'
    })
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; the-mundhe-effect-public-interest/0.1)'})
    with urllib.request.urlopen(request, timeout=25) as response:
        data = response.read(2_000_000)
    root = ET.fromstring(data)
    results = []
    for item in root.findall('./channel/item'):
        link = item.findtext('link', '').strip()
        title = item.findtext('title', '').strip()
        if not title or not link:
            continue
        source = item.find('source')
        results.append({
            'id': hashlib.sha256((title + '|' + link).encode()).hexdigest()[:20],
            'title': title,
            'url': link,
            'publisher': source.text if source is not None else '',
            'published': item.findtext('pubDate', ''),
            'discovered': dt.datetime.now(dt.timezone.utc).date().isoformat(),
            'review_status': 'pending',
            'note': 'Lead only. Not verified; do not publish this as an inspection outcome.',
        })
    return results

def main():
    existing = json.loads(DEST.read_text(encoding='utf-8')) if DEST.exists() else {'candidates': []}
    by_id = {entry['id']: entry for entry in existing['candidates']}
    failures = []
    added = 0
    for q in QUERIES:
        try:
            for entry in fetch_rss(q):
                if entry['id'] not in by_id:
                    by_id[entry['id']] = entry
                    added += 1
        except Exception as exc:
            failures.append(f'{q}: {exc}')
    existing['candidates'] = sorted(by_id.values(), key=lambda x: x.get('discovered', ''), reverse=True)[:500]
    existing['last_checked'] = dt.datetime.now(dt.timezone.utc).isoformat()
    existing['warnings'] = failures
    DEST.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Discovered {added} new leads. {len(failures)} source failures.')
    if len(failures) == len(QUERIES):
        raise SystemExit('Every RSS query failed: review collector configuration')

if __name__ == '__main__':
    main()

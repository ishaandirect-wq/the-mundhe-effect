"""Free, bounded discovery. No automatic publication of regulatory conclusions.
New news leads store links and metadata only, never unverified headline allegations.
Existing review decisions and all legacy candidates are retained.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
import pathlib
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from fssai import parse_register, SOURCE

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEST = ROOT / 'data/review_candidates.json'
MONITOR = ROOT / 'data/source_monitor.json'
DISTRICTS = ['Ahilyanagar Ahmednagar','Akola','Amravati','Beed','Bhandara','Buldhana',
 'Chandrapur','Chhatrapati Sambhajinagar Aurangabad','Dharashiv Osmanabad','Dhule',
 'Gadchiroli','Gondia','Hingoli','Jalgaon','Jalna','Kolhapur','Latur','Mumbai City',
 'Mumbai Suburban','Nagpur','Nanded','Nandurbar','Nashik','Palghar','Parbhani','Pune',
 'Raigad','Ratnagiri','Sangli','Satara','Sindhudurg','Solapur','Thane','Wardha','Washim','Yavatmal']
QUERIES = [f'{d} FDA food restaurant licence suspended restored inspection when:7d' for d in DISTRICTS] + [
 'महाराष्ट्र अन्न औषध प्रशासन हॉटेल परवाना निलंबित when:7d',
 'महाराष्ट्र अन्न औषध प्रशासन परवाना निलंबन रद्द when:30d',
 'Maharashtra FDA restaurant licence reinstated reopened stay suspension when:30d',
 'Maharashtra FSSAI hygiene rating audit when:7d']
OFFICIAL = [SOURCE, 'https://fda.maharashtra.gov.in/category/press-release/',
            'https://fda.maharashtra.gov.in/notice-category/announcements-general/']

class Links(HTMLParser):
    """Read the FDA content region, excluding menus, shares, clocks and footer."""
    VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self):
        super().__init__(); self.urls=set(); self.depth=0; self.found=False; self.text=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if attrs.get('id')=='row-content' and not self.depth:
            self.depth=1; self.found=True
        elif self.depth and tag not in self.VOID: self.depth+=1
        if self.depth and tag=='a' and attrs.get('href'): self.urls.add(attrs['href'])
    def handle_endtag(self,tag):
        if self.depth and tag not in self.VOID: self.depth-=1
    def handle_data(self,data):
        if self.depth: self.text.append(data)

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()

def read_json(path, default):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else default

def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    os.replace(temp, path)

def download(url, limit=8_000_000):
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'TheMundheEffect/0.3 public-record research'})
            with urllib.request.urlopen(req,timeout=12) as response:
                data=response.read(limit+1)
                if len(data)>limit: raise ValueError('Source exceeds size limit')
                if urllib.parse.urlparse(response.url).scheme != 'https': raise ValueError('Insecure redirect')
                return data
        except (OSError, ValueError):
            if attempt==2: raise
            time.sleep(attempt+1)

def fetch_rss(query):
    url='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':query,'hl':'en-IN','gl':'IN','ceid':'IN:en'})
    root=ET.fromstring(download(url,2_000_000))
    if root.tag!='rss' or root.find('channel') is None: raise ValueError('Unexpected RSS layout')
    results=[]
    for item in root.findall('./channel/item'):
        link=item.findtext('link','').strip(); title=item.findtext('title','').strip()
        if not title or urllib.parse.urlparse(link).scheme!='https': continue
        source=item.find('source')
        results.append({'id':hashlib.sha256(link.encode()).hexdigest()[:20],
            'title':'Unreviewed source link', 'url':link,
            'publisher':source.text if source is not None else '',
            'published':item.findtext('pubDate',''), 'discovered':now()[:10],
            'review_status':'pending', 'note':'Discovery only; no inspection outcome verified.'})
    return results

def fingerprint(url, raw):
    if url == SOURCE:
        rows=parse_register(raw.decode('utf-8'))
        return hashlib.sha256(json.dumps(sorted(rows,key=lambda r:r['audit_id']),sort_keys=True).encode()).hexdigest(),len(rows)
    parser=Links(); parser.feed(raw.decode('utf-8'))
    if not parser.found: raise ValueError('FDA content region missing; possible source layout change')
    urls=sorted({urllib.parse.urljoin(url,u).split('#')[0] for u in parser.urls
                 if urllib.parse.urlparse(urllib.parse.urljoin(url,u)).scheme=='https'
                 and urllib.parse.urlparse(urllib.parse.urljoin(url,u)).hostname in
                    {'fda.maharashtra.gov.in','cdnbbsr.s3waas.gov.in'}
                 and not u.startswith('#')})
    text=' '.join(' '.join(parser.text).split())
    if not text: raise ValueError('FDA content region empty')
    return hashlib.sha256(json.dumps([text,urls],ensure_ascii=False).encode()).hexdigest(),len(urls)

def run(dest=DEST, monitor_path=MONITOR, queries=None, official=None):
    queries=QUERIES if queries is None else queries; official=OFFICIAL if official is None else official
    existing=read_json(dest,{'candidates':[]}); entries=existing['candidates']
    ids={e['id'] for e in entries}; urls={e['url'] for e in entries}; added=0; failures=[]; rss_ok=0
    for q in queries:
        try:
            for entry in fetch_rss(q):
                if entry['id'] not in ids and entry['url'] not in urls:
                    entries.append(entry); ids.add(entry['id']); urls.add(entry['url']); added+=1
            rss_ok+=1
        except Exception as exc:
            failures.append({'source':'RSS', 'query':q, 'error_type':type(exc).__name__})
    state=read_json(monitor_path,{'sources':{}}); official_ok=0
    for url in official:
        old=state['sources'].get(url,{})
        try:
            digest,count=fingerprint(url,download(url)); official_ok+=1
            changed=old.get('sha256')!=digest
            state['sources'][url]={**old,'sha256':digest,'item_count':count,'last_success':now(),
                'last_attempt':now(),'error_type':None,
                'last_changed':now() if changed else old.get('last_changed'),
                'review_required':changed or old.get('review_required',False)}
        except Exception as exc:
            state['sources'][url]={**old,'last_attempt':now(),'error_type':type(exc).__name__}
            failures.append({'source':url,'error_type':type(exc).__name__})
    # All RSS failures leave the queue byte-for-byte intact. Official health remains visible.
    if rss_ok:
        existing.update(last_checked=now(),warnings=[f for f in failures if f['source']=='RSS'])
        existing['candidates']=entries; atomic_json(dest,existing)
    if official: atomic_json(monitor_path,state)
    report={'checked_at':now(),'rss_successes':rss_ok,'rss_total':len(queries),
            'official_successes':official_ok,'official_total':len(official),'new_links':added,'failures':failures}
    atomic_json(ROOT/'work/scan-report.json',report)
    summary=os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary,'a') as out:
            out.write(f"## Food-safety source scan\n\nRSS: {rss_ok}/{len(queries)}; official pages: {official_ok}/{len(official)}; new source links: {added}.\n\nDirectory records were not modified. Detailed health is in data/source_monitor.json.\n")
    print(json.dumps(report,ensure_ascii=False))
    return 1 if failures else 0

if __name__=='__main__': raise SystemExit(run())

import copy
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
import collect
from fssai import parse_register,eligible
from import_fssai import merge
from validate import validate
from directory import load_directory
ROOT=pathlib.Path(__file__).resolve().parents[1]

class Safeguards(unittest.TestCase):
    def setUp(self):
        self.snapshot=json.loads((ROOT/'data/sources/fssai-2026-10-12.json').read_text())
    def test_all_directory_parts_are_loaded(self):
        data=load_directory()
        self.assertEqual(len(data['establishments']),692)
        self.assertEqual(len({p['id'] for p in data['establishments']}),692)
    def test_missing_directory_part_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path=pathlib.Path(td)/'data/establishments.json';path.parent.mkdir()
            path.write_text(json.dumps({'establishments':[], 'additional_data':['data/establishments/fssai-01.json']}))
            with self.assertRaises(FileNotFoundError):load_directory(path)
    def test_import_is_idempotent_and_preserves_history(self):
        data={'establishments':[]};merge(data,self.snapshot)
        p=data['establishments'][0];p['status']='historical';p['events'].insert(0,{'source':'https://example.org/order','description':'retained'})
        before=copy.deepcopy(data);self.assertEqual(merge(data,self.snapshot),(0,0));self.assertEqual(data,before)
    def test_rejects_changed_or_empty_table(self):
        for html in ('<html>Access denied</html>','<table><tr><th>Changed</th></tr></table>'):
            with self.assertRaises(ValueError):parse_register(html)
    def test_score_and_identity_gates(self):
        row=next(r for r in self.snapshot['rows'] if eligible(r))
        for changes in ({'licence':'bad'},{'points':'1/112'},{'rating':'79 - 5'},{'valid_from':'bad'},{'rating':'100 - 2'}):
            self.assertFalse(eligible({**row,**changes}))
    def test_official_hash_ignores_outside_content_noise(self):
        # FDA HTML noise must not create false document changes.
        a=b'<div id="row-content"><a href="/document/a/">One</a></div><span>12:00</span>'
        b=b'<span>13:00</span><div id="row-content"><a href="/document/a/">One</a></div>'
        self.assertEqual(collect.fingerprint(collect.OFFICIAL[1],a),collect.fingerprint(collect.OFFICIAL[1],b))
    def test_unsafe_source_rejected(self):
        d={'establishments':[{'id':'x','name':'x','address':'x','district':'x','category':'x','status':'historical','note':'x','events':[{'date':'2026-01-01','title':'x','description':'x','source':'javascript:alert(1)'}]}]}
        self.assertTrue(validate(d))
    def test_news_headlines_are_not_published(self):
        raw=b'<rss><channel><item><title>UNVERIFIED ALLEGATION</title><link>https://news.google.com/a</link><source>Publisher</source></item></channel></rss>'
        with patch.object(collect,'download',return_value=raw): rows=collect.fetch_rss('test')
        self.assertNotIn('UNVERIFIED',json.dumps(rows));self.assertEqual(rows[0]['title'],'Unreviewed source link')
    def test_all_failures_preserve_queue(self):
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/'queue.json';p.write_text('{"candidates": []}\n');before=p.read_bytes()
            with patch.object(collect,'fetch_rss',side_effect=OSError),patch.object(collect,'atomic_json') as write:
                self.assertEqual(collect.run(p,pathlib.Path(td)/'health.json',['test'],[]),1)
            self.assertEqual(p.read_bytes(),before)
    def test_duplicates_retain_review_decisions(self):
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/'queue.json';original={'id':'legacy-id','url':'https://example.org/a','review_status':'dismissed','title':'Legacy'}
            p.write_text(json.dumps({'candidates':[original]}))
            with patch.object(collect,'fetch_rss',return_value=[{**original,'id':'new-hash','review_status':'pending'}]),patch.object(collect,'ROOT',pathlib.Path(td)):
                self.assertEqual(collect.run(p,pathlib.Path(td)/'health.json',['test'],[]),0)
            self.assertEqual(json.loads(p.read_text())['candidates'],[original])
    def test_partial_failure_saves_success_without_hiding_failure(self):
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/'q.json';row={'id':'1','url':'https://example.org/a','review_status':'pending'}
            with patch.object(collect,'fetch_rss',side_effect=[[row],OSError()]),patch.object(collect,'ROOT',pathlib.Path(td)):
                result=collect.run(p,pathlib.Path(td)/'health.json',['ok','fail'],[])
            self.assertEqual(result,1);self.assertEqual(json.loads(p.read_text())['candidates'],[row])
    def test_official_failure_retains_last_good_state(self):
        with tempfile.TemporaryDirectory() as td:
            m=pathlib.Path(td)/'health.json';old={'sha256':'last-good','last_success':'yesterday'};m.write_text(json.dumps({'sources':{'https://example.org':old}}))
            with patch.object(collect,'download',side_effect=OSError),patch.object(collect,'ROOT',pathlib.Path(td)):
                self.assertEqual(collect.run(pathlib.Path(td)/'q.json',m,[],['https://example.org']),1)
            entry=json.loads(m.read_text())['sources']['https://example.org'];self.assertEqual(entry['sha256'],'last-good');self.assertEqual(entry['last_success'],'yesterday')
if __name__=='__main__':unittest.main()

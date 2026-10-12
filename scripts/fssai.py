"""Parse the public FSSAI register. Network discovery never applies these records."""
from html.parser import HTMLParser
from html import unescape
import datetime as dt
import re

SOURCE = 'https://hygiene.fssai.gov.in/adminAuditListFbo.php'
HEADERS = ['Organization License No.', 'Organization Name', 'State', 'District',
           'KOB Type', 'Valid From', 'Valid upto', 'Points Obtained/ Total Points',
           '%Obtained-Rating', 'Action']

class Table(HTMLParser):
    def __init__(self):
        super().__init__(); self.rows = []; self.cells = None; self.cell = None; self.links = []
    def handle_starttag(self, tag, attrs):
        if tag == 'tr': self.cells = []; self.links = []
        elif tag in ('td', 'th') and self.cells is not None: self.cell = []
        elif tag == 'br' and self.cell is not None: self.cell.append(' ')
        elif tag == 'a' and self.cells is not None:
            self.links.extend(v for k, v in attrs if k == 'href')
    def handle_data(self, data):
        if self.cell is not None: self.cell.append(data)
    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None:
            # The register contains double-escaped entities.
            self.cells.append(' '.join(unescape(''.join(self.cell)).split())); self.cell = None
        elif tag == 'tr' and self.cells is not None:
            self.rows.append((self.cells, self.links)); self.cells = None; self.cell = None

def parse_register(content):
    table = Table(); table.feed(content)
    if not any(c == HEADERS for c, _ in table.rows):
        raise ValueError('FSSAI column layout changed; refusing import')
    rows = []
    for c, links in table.rows:
        if len(c) != 10 or c[2] != 'Maharashtra': continue
        match = next((re.fullmatch(r'auditDetails.php\?mid=(\d+)', u) for u in links
                      if re.fullmatch(r'auditDetails.php\?mid=(\d+)', u)), None)
        if not match: raise ValueError('Maharashtra row has no audit identifier')
        rows.append(dict(zip(['licence','name','state','jurisdiction','category',
                              'valid_from','valid_upto','points','rating','action'], c),
                         audit_id=match[1], source='https://hygiene.fssai.gov.in/'+match[0]))
    if not rows: raise ValueError('No Maharashtra rows; refusing empty source')
    return rows

def eligible(row):
    """Conservative favourable subset; omitted rows are not accusations."""
    if not re.fullmatch(r'\d{14}', row['licence']) or not row['name']: return False
    try: dt.datetime.strptime(row['valid_from'], '%d-%m-%Y')
    except ValueError: return False
    points = re.fullmatch(r'(\d+)/(\d+)', row['points'])
    rating = re.fullmatch(r'(\d+)\s*-\s*(\d+)', row['rating'])
    if not points or not rating: return False
    obtained, total = map(int, points.groups()); percent, stars = map(int, rating.groups())
    return (total > 0 and 0 <= obtained <= total and 80 <= percent <= 100
            and stars == 5 and abs(100*obtained/total-percent) <= 1)

def district(j):
    if j.startswith('Pune'): return 'Pune'
    if j.startswith('Nagpur'): return 'Nagpur'
    if j.startswith('Nashik'): return 'Nashik'
    if j.startswith('Ahmadnagar'): return 'Ahilyanagar'
    if j.startswith(('Palghar', 'Vasai')): return 'Palghar'
    if '(Thane Zone-' in j: return 'Thane'
    return {'Greater Mumbai':'Mumbai (district unspecified)', 'Mumbai':'Mumbai (district unspecified)',
            'Mumbai (Suburban)':'Mumbai Suburban', 'Aurangabad':'Chhatrapati Sambhajinagar',
            'Osmanabad':'Dharashiv', 'Buldana':'Buldhana', 'Gondiya':'Gondia',
            'Sangli Municipal Corporation':'Sangli'}.get(j, j)

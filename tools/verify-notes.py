#!/usr/bin/env python3
"""Check new Notes articles before they go into a PR.

Run from the repo root, naming the slugs you added:

    python3 tools/verify-notes.py airport-font baseball-jersey-font

Strict checks run on the named articles: length, head tags, JSON-LD, headings,
hero colour, and the six places every post has to be wired into. Site-wide
checks always run: XML well-formedness, JSON-LD on every page, internal links,
and title/description uniqueness. Older posts predate some limits, so they are
only held to the site-wide checks.

Exit status is 0 when nothing FAILs. WARN lines are for a human to read.
"""
import email.utils, glob, html, json, os, re, sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

SITE = 'https://www.vigilfont.com'
BODY_WORDS = (1300, 1700)
LEAD_WORDS = (40, 60)
TITLE_MAX = 60
DESC_MAX = 155
FAQ_COUNT = (3, 4)
MIN_CONTRAST = 4.5
GRAPH_TYPES = {'Article', 'WebPage', 'BreadcrumbList', 'FAQPage', 'Person'}

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)

fails, warns = [], []
def fail(msg): fails.append(msg); print('FAIL ', msg)
def warn(msg): warns.append(msg); print('WARN ', msg)
def ok(msg): print('ok   ', msg)

def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()

def words(fragment):
    text = re.sub(r'<(script|style)\b.*?</\1>', ' ', fragment, flags=re.S)
    return len(html.unescape(re.sub(r'<[^>]+>', ' ', text)).split())

class Page(HTMLParser):
    """Collects what the checks need without regexing across <script> bodies."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.headings, self.meta, self.linkrels = [], [], {}, []
        self.title, self._in_title = '', False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for attr in ('href', 'src'):
            if a.get(attr):
                self.links.append(a[attr])
        if re.fullmatch(r'h[1-6]', tag):
            self.headings.append(int(tag[1]))
        if tag == 'meta':
            key = a.get('name') or a.get('property')
            if key:
                self.meta[key] = a.get('content', '')
        if tag == 'link':
            self.linkrels.append(a)
        if tag == 'title':
            self._in_title = True
    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False
    def handle_data(self, data):
        if self._in_title:
            self.title += data

def parse(path):
    p = Page()
    p.feed(read(path))
    p.title = p.title.strip()
    return p

def jsonld_blocks(s):
    return re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)

def resolves(url):
    """Vercel cleanUrls: /notes/x serves notes/x.html; /notes serves notes/index.html."""
    path = url.split('#')[0].split('?')[0].lstrip('/')
    if path == '':
        return True
    return any(os.path.isfile(c) for c in (path, path + '.html', os.path.join(path, 'index.html')))

def luminance(hex_):
    hex_ = hex_.lstrip('#')
    if len(hex_) == 3:
        hex_ = ''.join(c * 2 for c in hex_)
    chans = [int(hex_[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in chans]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]

def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)

def hex_of(colour):
    named = {'#fff': '#FFFFFF', '#000': '#000000', 'white': '#FFFFFF', 'black': '#000000'}
    colour = colour.strip()
    return named.get(colour.lower(), colour)

pages = sorted(glob.glob('*.html') + glob.glob('notes/*.html'))
notes = sorted(p for p in glob.glob('notes/*.html') if not p.endswith('index.html'))

# ---------------------------------------------------------------- per-article

def check_article(slug):
    path = f'notes/{slug}.html'
    if not os.path.isfile(path):
        fail(f'{path} does not exist')
        return
    s = read(path)
    p = parse(path)
    url = f'{SITE}/notes/{slug}'

    m = re.search(r'<div class="prose">(.*?)</div>\s*</article>', s, re.S)
    if not m:
        fail(f'{slug}: no <div class="prose"> … </article> body found')
    else:
        n = words(m.group(1))
        (ok if BODY_WORDS[0] <= n <= BODY_WORDS[1] else fail)(f'{slug}: body {n} words (want {BODY_WORDS[0]}–{BODY_WORDS[1]})')
    lead = re.search(r'<p class="lead">(.*?)</p>', s, re.S)
    if not lead:
        fail(f'{slug}: no <p class="lead">')
    else:
        n = words(lead.group(1))
        (ok if LEAD_WORDS[0] <= n <= LEAD_WORDS[1] else fail)(f'{slug}: lead {n} words (want {LEAD_WORDS[0]}–{LEAD_WORDS[1]})')

    (ok if len(p.title) <= TITLE_MAX else fail)(f'{slug}: <title> {len(p.title)} chars (max {TITLE_MAX})')
    desc = p.meta.get('description', '')
    if not desc:
        fail(f'{slug}: no meta description')
    else:
        (ok if len(desc) <= DESC_MAX else fail)(f'{slug}: description {len(desc)} chars (max {DESC_MAX})')

    canon = [l.get('href') for l in p.linkrels if l.get('rel') == 'canonical']
    if canon != [url]:
        fail(f'{slug}: canonical is {canon}, want [{url}]')
    for key in ('og:title', 'og:description', 'og:url', 'og:image', 'twitter:card',
                'twitter:title', 'twitter:description', 'article:published_time'):
        if not p.meta.get(key):
            fail(f'{slug}: missing <meta> {key}')
    if not any(l.get('rel') == 'alternate' and l.get('href') == '/feed.xml' for l in p.linkrels):
        fail(f'{slug}: missing RSS rel=alternate')
    preloads = [l.get('href', '') for l in p.linkrels if l.get('rel') == 'preload' and l.get('as') == 'font']
    if len(preloads) != 2:
        fail(f'{slug}: {len(preloads)} font preloads, want 2')
    if not any(l.get('rel') == 'stylesheet' and l.get('href') == '/notes.css' for l in p.linkrels):
        fail(f'{slug}: stylesheet is not href="/notes.css"')
    relative = [u for u in p.links if not re.match(r'^(/|#|https?:|mailto:|tel:|data:)', u)]
    if relative:
        fail(f'{slug}: relative URLs resolve under /notes/ and 404: {relative[:5]}')

    types, faqs = set(), 0
    for block in jsonld_blocks(s):
        try:
            data = json.loads(block)
        except ValueError as e:
            fail(f'{slug}: JSON-LD does not parse: {e}')
            continue
        for node in data.get('@graph', [data]):
            types.add(node.get('@type'))
            if node.get('@type') == 'FAQPage':
                faqs = len(node.get('mainEntity', []))
            if node.get('@type') == 'Person' and node.get('@id') != f'{SITE}/#keno':
                fail(f'{slug}: Person @id is {node.get("@id")}, want {SITE}/#keno')
            if node.get('@type') == 'Article' and node.get('@id') != f'{url}#article':
                fail(f'{slug}: Article @id is {node.get("@id")}, want {url}#article')
    missing = GRAPH_TYPES - types
    if missing:
        fail(f'{slug}: JSON-LD @graph missing {sorted(missing)}')
    else:
        ok(f'{slug}: JSON-LD has {sorted(GRAPH_TYPES)}')
    if not FAQ_COUNT[0] <= faqs <= FAQ_COUNT[1]:
        fail(f'{slug}: FAQPage has {faqs} questions (want {FAQ_COUNT[0]}–{FAQ_COUNT[1]})')

    h = p.headings
    if h.count(1) != 1:
        fail(f'{slug}: {h.count(1)} <h1> elements')
    skips = [(a, b) for a, b in zip(h, h[1:]) if b > a + 1]
    if skips:
        fail(f'{slug}: heading level skips {skips}')
    else:
        ok(f'{slug}: one h1, no heading skips')

    hero = re.search(r'--hero:(#[0-9A-Fa-f]{3,6});--hero-ink:([^;"]+)', s)
    if not hero:
        fail(f'{slug}: no --hero / --hero-ink pair on .post-hero')
    else:
        bg, ink = hero.group(1).upper(), hex_of(hero.group(2))
        c = contrast(bg, ink) if re.fullmatch(r'#[0-9A-Fa-f]{3,6}', ink) else 0
        (ok if c >= MIN_CONTRAST else fail)(f'{slug}: hero {bg} / ink {ink} contrast {c:.1f}:1 (min {MIN_CONTRAST})')
        others = [o for o in notes if o != path and f'--hero:{bg}' in read(o).upper()]
        if others:
            fail(f'{slug}: hero {bg} already used by {others}')

    prose = m.group(1) if m else ''
    prose = re.sub(r'<(blockquote|q)\b.*?</\1>', ' ', prose, flags=re.S)
    prose = re.sub(r'“[^”]*”', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', prose)))
    first = []
    for hit in re.finditer(r"\b(I|I'm|I've|I'd|me|my|mine|we|our|us)\b", prose):
        before = prose[max(0, hit.start() - 20):hit.start()]
        if hit.group() == 'I' and re.search(r'\b(1|l|the)\W*$|\b(1|l)\b', before):
            continue  # the letter I, as in "a 1, l and I you can tell apart"
        first.append(prose[max(0, hit.start() - 30):hit.end() + 20].replace('\n', ' ').strip())
    for ctx in first:
        warn(f'{slug}: first person outside quotes — Notes are third-person: "…{ctx}…"')

    # The six places. No build step, so a post missing from any of them is orphaned.
    idx = read('notes/index.html')
    if f'href="/notes/{slug}"' not in idx:
        fail(f'{slug}: not listed in notes/index.html')
    if f'"{url}#article"' not in idx:
        fail(f'{slug}: no blogPost @id in notes/index.html JSON-LD')
    home = re.search(r'<section id="notes">(.*?)</section>', read('index.html'), re.S)
    if not home or f'href="/notes/{slug}"' not in home.group(1):
        fail(f'{slug}: not listed in index.html <section id="notes">')
    if f'<loc>{url}</loc>' not in read('sitemap.xml'):
        fail(f'{slug}: no <loc> in sitemap.xml')
    notes_section = read('llms.txt').split('## Notes', 1)
    if len(notes_section) < 2 or f'({url})' not in notes_section[1].split('\n## ', 1)[0]:
        fail(f'{slug}: no bullet under "## Notes" in llms.txt')
    if f'<link>{url}</link>' not in read('feed.xml'):
        fail(f'{slug}: no <item> in feed.xml')
    if url not in read('llms-full.txt'):
        fail(f'{slug}: missing from llms-full.txt — run python3 tools/build-llms-full.py')
    ok(f'{slug}: wiring checked (notes/index, index, sitemap, llms.txt, feed, llms-full)')

# ---------------------------------------------------------------- site-wide

def check_site():
    for f in ('feed.xml', 'sitemap.xml'):
        try:
            ET.parse(f)
            ok(f'{f} is well-formed XML')
        except ET.ParseError as e:
            fail(f'{f} is not well-formed: {e}')

    try:
        channel = ET.parse('feed.xml').getroot().find('channel')
        dates = []
        for item in channel.findall('item'):
            raw = item.findtext('pubDate', '')
            d = email.utils.parsedate_to_datetime(raw)
            dates.append(d)
            if raw[:3] != d.strftime('%a'):
                fail(f'feed.xml: pubDate "{raw}" has the wrong weekday (should be {d.strftime("%a")})')
        built = email.utils.parsedate_to_datetime(channel.findtext('lastBuildDate', ''))
        if dates and built < max(dates):
            fail(f'feed.xml: lastBuildDate {built:%Y-%m-%d} is older than the newest item {max(dates):%Y-%m-%d}')
        # feed.xml lists every note except the blog index
        missing = [n for n in notes if f'<link>{SITE}/{n[:-5]}</link>' not in read('feed.xml')]
        if missing:
            warn(f'feed.xml has no <item> for {missing}')
    except (ET.ParseError, AttributeError, TypeError, ValueError) as e:
        fail(f'feed.xml dates could not be read: {e}')

    bad_json = 0
    for f in pages:
        for block in jsonld_blocks(read(f)):
            try:
                json.loads(block)
            except ValueError as e:
                bad_json += 1
                fail(f'{f}: JSON-LD does not parse: {e}')
    if not bad_json:
        ok(f'JSON-LD parses on all {len(pages)} pages')

    broken = set()
    for f in pages:
        for u in parse(f).links:
            if u.startswith(SITE):
                u = u[len(SITE):] or '/'
            if u.startswith('/') and not u.startswith('//') and not resolves(u):
                broken.add((f, u))
    for f, u in sorted(broken):
        fail(f'{f}: internal link {u} does not resolve')
    if not broken:
        ok(f'every internal href/src on {len(pages)} pages resolves')

    seen_t, seen_d = {}, {}
    for f in pages:
        p = parse(f)
        if p.meta.get('robots', '').startswith('noindex') or f in ('404.html', 'og-serif.html'):
            continue
        for key, seen in ((p.title, seen_t), (p.meta.get('description', ''), seen_d)):
            if key:
                seen.setdefault(key, []).append(f)
    dupes = [v for v in list(seen_t.values()) + list(seen_d.values()) if len(v) > 1]
    for v in dupes:
        fail(f'duplicate title or description across {v}')
    if not dupes:
        ok('titles and descriptions unique across indexable pages')

# ----------------------------------------------------------------------------

slugs = [a.removeprefix('notes/').removesuffix('.html') for a in sys.argv[1:]]
if not slugs:
    print(__doc__.strip().split('\n\n')[1])
    print('\nNo slugs given: running site-wide checks only.\n')
for slug in slugs:
    check_article(slug)
check_site()

print(f'\n{len(fails)} FAIL, {len(warns)} WARN')
sys.exit(1 if fails else 0)

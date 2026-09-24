#!/usr/bin/env python3
"""Read-only scan of 00.Inbox. Text is MASKED before it is saved or shown (ID/account numbers, MRZ, IBANs, passwords). For every file: fingerprint, pages, pixel size, DPI, sharpness,
image hash, extracted text (text layer or OCR in the languages listed in 99.System/vault.json),
and duplicate candidates from the catalog. Writes 99.System/.work/inbox_scan.json and prints a short summary. Never moves anything.
Usage: python3 inbox_scan.py [--inbox PATH]"""
import os, sys, json, hashlib, subprocess, re, zipfile, csv, tempfile, shutil, difflib, html
from PIL import Image
import numpy as np, cv2
Image.MAX_IMAGE_PIXELS = None
SYS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT = os.path.dirname(SYS)
INBOX = sys.argv[sys.argv.index('--inbox')+1] if '--inbox' in sys.argv else os.path.join(VAULT, '00.Inbox')
os.environ['OMP_THREAD_LIMIT'] = '1'
DEFAULT_LANGS = ['eng', 'por', 'rus', 'heb']   # English, Portuguese, Russian, Hebrew
def _langs():
    # OCR languages come from 99.System/vault.json; trained data from 99.System/tessdata if present, else the system's.
    try: want = json.load(open(os.path.join(SYS, 'vault.json'))).get('ocr_languages') or DEFAULT_LANGS
    except Exception: want = DEFAULT_LANGS
    td = os.path.join(SYS, 'tessdata')
    local = [l for l in want if os.path.exists(os.path.join(td, l + '.traineddata'))]
    if local:
        os.environ['TESSDATA_PREFIX'] = td; return '+'.join(local)
    try: sysl = set(subprocess.run(['tesseract', '--list-langs'], capture_output=True, timeout=20).stdout.decode().split())
    except Exception: sysl = set()
    return '+'.join(l for l in want if l in sysl) or 'eng'
LANGS = _langs()

def run(cmd, t=90):
    try: return subprocess.run(cmd, capture_output=True, timeout=t).stdout.decode('utf-8', 'replace')
    except Exception: return ''
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()
def metrics(im):
    g = np.array(im.convert('L')); s = 1000/max(g.shape)
    if s < 1: g = cv2.resize(g, (int(g.shape[1]*s), int(g.shape[0]*s)), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(np.array(im.convert('RGB').resize((200, 200))), cv2.COLOR_RGB2HSV)
    d = np.array(im.convert('L').resize((9, 8), Image.LANCZOS), dtype=int)
    bits = ''.join('1' if x else '0' for x in (d[:, 1:] > d[:, :-1]).flatten())
    return dict(sharpness=round(float(cv2.Laplacian(g, cv2.CV_64F).var()), 1),
                colourfulness=round(float(hsv[..., 1].mean()), 1), dhash='%016x' % int(bits, 2))

# ---- privacy masking: nothing below leaves the Mac unmasked ----
SECRET_WORDS = r'(password|passwd|passcode|senha|palavra[- ]?passe|contraseña|clave|passwort|kennwort|mot de passe|пароль|סיסמה|pin|puk|cvv|código de acesso|access code|секретн)'
def mask(text):
    """Hide ID/account numbers, MRZ lines, IBANs and credential values; keep dates, amounts and words."""
    lines = []
    for ln in text.splitlines():
        if ln.count('<') >= 5: lines.append('[machine-readable zone hidden]'); continue
        ln = re.sub(r'(?i)(\b' + SECRET_WORDS + r'\w*\s*(?:\([^)]{0,20}\))?\s*[:=\-]?\s*)(\S+)', lambda m: m.group(1) + '[hidden]', ln)
        ln = re.sub(r'\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]){11,30}\b', '[IBAN hidden]', ln)
        def num(m):
            return '[number hidden]' if sum(c.isdigit() for c in m.group(0)) >= 7 else m.group(0)
        ln = re.sub(r'(?<![\d.,/:\-])\d(?:[\d ]*\d)?(?![\d.,/:\-])', num, ln)
        ln = re.sub(r'(?<![\d.,/:])\d+(?:-\d+)+(?![\d.,/:])', lambda m: m.group(0) if re.fullmatch(r'\d{4}-\d{2}(-\d{2})?|\d{2}-\d{2}-\d{4}', m.group(0)) else num(m), ln)
        ln = re.sub(r'\b(?=[A-Z0-9]*\d)(?=[A-Z0-9]*[A-Z])[A-Z0-9]{8,}\b', '[code hidden]', ln)
        ln = re.sub(r'\d{7,}', '[number hidden]', ln)   # any 7+ digit run, whatever surrounds it
        lines.append(ln)
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(lines))

NO_OCR = '--no-ocr' in sys.argv
def ocr(p): return '' if NO_OCR else run(['tesseract', p, 'stdout', '-l', LANGS, '--psm', '3'])
def scan(p):
    ext = p.rsplit('.', 1)[-1].lower() if '.' in p else ''
    r = dict(path=os.path.relpath(p, VAULT) if p.startswith(VAULT) else p, name=os.path.basename(p),
             ext=ext, size=os.path.getsize(p), sha256=sha(p)); text = ''
    try:
        if ext == 'pdf':
            info = run(['pdfinfo', p])
            if 'Incorrect password' in info or 'Encrypted:       yes' in info: r['locked'] = True
            m = re.search(r'Pages:\s+(\d+)', info); r['pages'] = int(m.group(1)) if m else None
            m = re.search(r'Page size:\s+([\d.]+) x ([\d.]+)', info); pin = [float(m.group(1))/72, float(m.group(2))/72] if m else None
            imgs = [l.split() for l in run(['pdfimages', '-list', '-f', '1', '-l', '1', p]).splitlines()[2:] if len(l.split()) > 13]
            if imgs:
                b = max(imgs, key=lambda x: int(x[3])*int(x[4])); r['pixel_size'] = f'{b[3]}x{b[4]}'
                r['effective_dpi'] = round(max(int(b[3]), int(b[4]))/max(pin)) if pin else int(float(b[12]))
            tl = run(['pdftotext', '-l', '3', '-layout', p, '-'])
            td = tempfile.mkdtemp(); run(['pdftoppm', '-f', '1', '-l', '2', '-r', '200', '-png', p, td+'/pg'])
            pgs = sorted(os.listdir(td))
            if pgs: r.update(metrics(Image.open(os.path.join(td, pgs[0]))))
            if len(tl.strip()) >= 40: text, r['text_source'] = tl, 'text-layer'
            else: text, r['text_source'] = '\n--- next page ---\n'.join(ocr(os.path.join(td, g)) for g in pgs), 'ocr'
            shutil.rmtree(td, ignore_errors=True)
        elif ext in ('jpg', 'jpeg', 'png', 'bmp', 'tif', 'tiff', 'gif', 'heic', 'heif'):
            src = p
            if ext in ('heic', 'heif'):
                td = tempfile.mkdtemp(); src = td+'/x.jpg'; run(['convert', p, src])
            im = Image.open(src); r['pixel_size'] = f'{im.size[0]}x{im.size[1]}'; r['pages'] = 1
            r.update(metrics(im)); text, r['text_source'] = ocr(src), 'ocr'
        elif ext in ('xlsx', 'xlsm'):
            import openpyxl; wb = openpyxl.load_workbook(p, data_only=True, read_only=True)
            for ws in wb.worksheets[:2]:
                for row in ws.iter_rows(max_row=60, values_only=True):
                    v = [str(c) for c in row if c is not None]
                    if v: text += ' | '.join(v)+'\n'
            r['text_source'] = 'xlsx'
        elif ext in ('doc', 'docx', 'rtf', 'odt'): text, r['text_source'] = run(['soffice', '--headless', '--cat', p]), 'soffice'
        elif ext == 'zip':
            with zipfile.ZipFile(p) as z: text = '\n'.join(i.filename for i in z.infolist() if '__MACOSX' not in i.filename)
            r['text_source'] = 'zip-listing'
        elif ext in ('txt', 'md', 'html', 'htm', 'csv', 'eml'):
            text = open(p, errors='replace').read()
            if ext in ('html', 'htm'):
                text = re.sub(r'(?is)<(script|style|svg|noscript)\b.*?</\1>', ' ', text)
                text = html.unescape(re.sub(r'<[^>]+>', ' ', text))
                text = re.sub(r'[ \t]+', ' ', text)
            r['text_source'] = 'plain'
    except Exception as e: r['error'] = str(e)[:200]
    if r.get('text_source') != 'ocr': r.pop('effective_dpi', None)  # DPI only means something for scans
    r['text_chars'] = len(text.strip())
    r['has_secrets'] = bool(re.search(r'\b(?:pin|puk|cvv)\b|\b' + SECRET_WORDS.replace('|pin|puk|cvv', ''), text, re.I))
    r['text'] = mask(text)[:2500]   # masked and shortened: enough to identify a document
    return r

cat = list(csv.DictReader(open(os.path.join(SYS, 'catalog.csv'))))
live = [c for c in cat if c.get('status') == 'filed']
def ham(a, b): return bin(int(a, 16) ^ int(b, 16)).count('1')
files = sorted(os.path.join(d, f) for d, _, fs in os.walk(INBOX) for f in fs if not f.startswith('.'))
out = []
for p in files:
    r = scan(p); cands = []
    for c in cat:
        if c['sha256'] == r['sha256']: cands.append(dict(path=c['path'], kind='exact', status=c['status']))
    if r.get('dhash'):
        for c in live:
            if c.get('dhash') and ham(c['dhash'], r['dhash']) <= 6 and all(x['path'] != c['path'] for x in cands):
                cands.append(dict(path=c['path'], kind='similar-image', distance=ham(c['dhash'], r['dhash'])))
    r['duplicate_candidates'] = cands
    out.append(r)
# duplicates within the inbox itself
for i, a in enumerate(out):
    for b in out[i+1:]:
        if a['sha256'] == b['sha256']: a['duplicate_candidates'].append(dict(path=b['path'], kind='exact-in-inbox'))
os.makedirs(os.path.join(SYS, '.work'), exist_ok=True)
json.dump(out, open(os.path.join(SYS, '.work', 'inbox_scan.json'), 'w'), ensure_ascii=False, indent=1)
print(f'{len(out)} file(s) scanned in {INBOX}; details in 99.System/.work/inbox_scan.json')
for r in out:
    flag = (' LOCKED' if r.get('locked') else '') + (' CONTAINS-SECRETS' if r.get('has_secrets') else '')
    d = '; '.join(f"{c['kind']}: {c['path']}" for c in r['duplicate_candidates'])
    print(f"- {r['name']} | {r.get('pages','-')}p {r.get('pixel_size','-')} dpi={r.get('effective_dpi','-')} sharp={r.get('sharpness','-')} | text {r['text_chars']} chars ({r.get('text_source','-')}){flag}" + (f" | DUP? {d}" if d else ''))

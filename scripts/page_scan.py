#!/usr/bin/env python3
"""Masked per-page OCR of one PDF, for splitting multi-document scans. Read-only.
Usage: python3 page_scan.py <pdf> <first> <last>  -> writes ~/vault-pages/pages_<name>_<first>-<last>.json (outside the vault)"""
import os, sys, json, subprocess, tempfile, shutil, re
HERE=os.path.dirname(os.path.abspath(__file__)); SYS=os.path.dirname(HERE)
src=open(os.path.join(HERE,'inbox_scan.py')).read(); ns={}
exec(src[src.index('import os'):src.index('def ocr(p)')].replace("SYS = os.path","SYS=r'"+SYS+"'#").replace("VAULT = os.path","VAULT='.'#").replace("INBOX = sys","INBOX='.'#"),ns)
pdf,a,b=sys.argv[1],int(sys.argv[2]),int(sys.argv[3])
os.makedirs(os.path.expanduser('~/vault-pages'),exist_ok=True); out=os.path.join(os.path.expanduser('~/vault-pages'),'pages_'+os.path.basename(pdf)+f'_{a}-{b}.json')
res=json.load(open(out)) if os.path.exists(out) else {}
td=tempfile.mkdtemp()
for p in range(a,b+1):
    if str(p) in res: continue
    subprocess.run(['pdftoppm','-f',str(p),'-l',str(p),'-r','150','-png',pdf,td+'/pg'],capture_output=True)
    f=sorted(os.listdir(td))[-1]; im=os.path.join(td,f)
    t=subprocess.run(['tesseract',im,'stdout','-l',ns['LANGS'],'--psm','3'],capture_output=True).stdout.decode('utf-8','replace')
    from PIL import Image; m=ns['metrics'](Image.open(im))
    res[str(p)]=dict(text=ns['mask'](t)[:600],dhash=m['dhash'],sharp=m['sharpness'],secrets=bool(re.search(ns['SECRET_WORDS'],t,re.I)))
    os.remove(im); json.dump(res,open(out,'w'),ensure_ascii=False)
shutil.rmtree(td,ignore_errors=True); print(os.path.basename(pdf),a,b,'done',len(res))

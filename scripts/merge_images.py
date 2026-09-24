#!/usr/bin/env python3
"""Combine images (or single-page PDFs' images) into ONE PDF without recompressing (img2pdf).
iPhone photos: only the primary frame is used (HDR gain maps are dropped). Never overwrites.
Usage: python3 merge_images.py <out.pdf> <img1> [img2 ...] --batch <name>   (paths relative to the vault)"""
import sys, os, struct, hashlib, datetime, img2pdf
from PIL import Image
VAULT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); os.chdir(VAULT)
a=sys.argv[1:]; batch=a[a.index('--batch')+1]; a=a[:a.index('--batch')]; out,imgs=a[0],a[1:]
if os.path.exists(out): sys.exit(f'refusing: {out} exists')
def primary(p):
    b=open(p,'rb').read()
    try: offs=getattr(Image.open(p),'_MpoImageFile__mpoffsets',None)
    except Exception: offs=None
    if offs and len(offs)>1: b=b[:offs[1]]
    if b[:2]!=b'\xff\xd8': return b
    o=bytearray(b[:2]); i=2
    while i<len(b):
        m=b[i+1]
        if m==0xDA: o+=b[i:]; break
        L=struct.unpack('>H',b[i+2:i+4])[0]; seg=b[i:i+2+L]
        if not (m==0xE2 and seg[4:8]==b'MPF\x00'): o+=seg
        i+=2+L
    return bytes(o)
data=img2pdf.convert([primary(p) for p in imgs])
os.makedirs(os.path.dirname(out) or '.',exist_ok=True); open(out,'wb').write(data)
h=hashlib.sha256(data).hexdigest(); ts=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
open('99.System/move-log.csv','a').write(f'{ts},{batch},create,"","{out}",{h},"lossless combined PDF of {" + ".join(os.path.basename(p) for p in imgs)}"\n')
print(out,len(data)//1024,'KB',h[:12])

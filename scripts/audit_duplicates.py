#!/usr/bin/env python3
"""Read-only audit: for every group in 90.Review/Duplicates compare the kept library file with each copy
by ORIGINAL resolution (native pixels of the embedded images, not a rendering), and by effective pixels
on the document itself (native pixels x share of the page the document occupies)."""
import os, subprocess, csv, tempfile, json
from PIL import Image
import numpy as np
Image.MAX_IMAGE_PIXELS=None
V=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def run(c): return subprocess.run(c,capture_output=True).stdout.decode('utf-8','replace')
def _run(v,thr):
    idx=np.where(v>thr)[0]
    if len(idx)==0: return 0,len(v)
    # largest contiguous block of "content" rows/cols (gaps up to 3% tolerated)
    best=(idx[0],idx[0]); start=idx[0]; prev=idx[0]; gap=max(2,int(len(v)*0.03))
    for i in idx[1:]:
        if i-prev>gap: start=i
        prev=i
        if prev-start>best[1]-best[0]: best=(start,prev)
    return best[0],best[1]+1
def fill(im):
    w=400; g=np.array(im.convert('RGB').resize((w,max(1,int(w*im.size[1]/im.size[0])))),dtype=int)
    bg=np.median(np.concatenate([g[:3].reshape(-1,3),g[-3:].reshape(-1,3),g[:,:3].reshape(-1,3),g[:,-3:].reshape(-1,3)]),axis=0)
    m=(np.abs(g-bg).sum(axis=2)>60)
    # drop thin scanner shadows at the very edges
    m[:4]=m[-4:]=False; m[:,:4]=m[:,-4:]=False
    if m.sum()<100: return 1.0
    y0,y1=_run(m.mean(axis=1),0.04); x0,x1=_run(m.mean(axis=0),0.04)
    return round(min(1.0,((x1-x0)*(y1-y0))/(m.shape[0]*m.shape[1])),2)
def info(p):
    ext=p.rsplit('.',1)[-1].lower(); pages=[]
    if ext=='pdf':
        if 'Incorrect password' in run(['pdfinfo',p]) : return dict(locked=True)
        lst=[l.split() for l in run(['pdfimages','-list',p]).splitlines()[2:] if len(l.split())>13]
        byp={}
        for l in lst:
            pg=int(l[0]); px=int(l[3])*int(l[4])
            if px>byp.get(pg,(0,))[0]: byp[pg]=(px,int(l[3]),int(l[4]),l[12])
        td=tempfile.mkdtemp(); run(['pdftoppm','-r','40','-png',p,td+'/r'])
        rs=sorted(os.listdir(td))
        n=int(run(['pdfinfo',p]).split('Pages:')[1].split()[0]) if 'Pages:' in run(['pdfinfo',p]) else len(rs)
        for i in range(1,n+1):
            f=fill(Image.open(f'{td}/{rs[i-1]}')) if i-1<len(rs) else 1
            b=byp.get(i)
            pages.append(dict(px=f'{b[1]}x{b[2]}' if b else 'vector/text', mp=round(b[0]/1e6,2) if b else None, ppi=b[3] if b else '-', fill=round(f,2), eff=round(b[0]*f/1e6,2) if b else None))
    else:
        im=Image.open(p); f=fill(im)
        pages.append(dict(px=f'{im.size[0]}x{im.size[1]}',mp=round(im.size[0]*im.size[1]/1e6,2),ppi='-',fill=round(f,2),eff=round(im.size[0]*im.size[1]*f/1e6,2)))
    return dict(pages=pages,kb=os.path.getsize(p)//1024)
cat={r['path']:r for r in csv.DictReader(open(f'{V}/99.System/catalog.csv'))}
filed={os.path.splitext(os.path.basename(k))[0]:k for k,r in cat.items() if r['status']=='filed' and os.path.exists(f'{V}/{k}')}
out=[]
D=f'{V}/90.Review/Duplicates'
for g in sorted(os.listdir(D)):
    gp=f'{D}/{g}'
    if not os.path.isdir(gp): continue
    keep=filed.get(g) or filed.get(g+'_p01')
    copies=[f for f in sorted(os.listdir(gp)) if not f.endswith('.md') and not f.startswith('.')]
    rec=dict(group=g,keep=keep,keep_info=info(f'{V}/{keep}') if keep else None,copies=[])
    for c in copies:
        h=run(['shasum','-a','256',f'{gp}/{c}']).split()[0] if keep else ''
        rec['copies'].append(dict(name=c,info=info(f'{gp}/{c}')))
    out.append(rec)
json.dump(out,open(f'{V}/99.System/.work/audit.json','w'),indent=1,ensure_ascii=False)
def s(i):
    if not i: return 'MISSING'
    if i.get('locked'): return 'locked PDF'
    return f"{len(i['pages'])}p " + '; '.join(f"{p['px']} ({p['mp']}MP, doc {int(p['fill']*100)}% -> {p['eff']}MP)" for p in i['pages'][:3]) + (' ...' if len(i['pages'])>3 else '')
for r in out:
    print(f"\n## {r['group']}\n  KEPT  {r['keep']}: {s(r['keep_info'])}")
    for c in r['copies']: print(f"  COPY  {c['name']}: {s(c['info'])}")

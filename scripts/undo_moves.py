# Reverse one batch from 99.System/move-log.csv. Dry run by default; --apply to execute.
import csv,os,sys,subprocess,hashlib
V=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); batch=sys.argv[1]; apply='--apply' in sys.argv
rows=[r for r in csv.DictReader(open(f'{V}/99.System/move-log.csv')) if r['batch']==batch and r['action'] in ('move','rename')]
ok=0; rows_done=[]
for r in reversed(rows):
    src=f"{V}/{r['new_path']}"; dst=f"{V}/{r['old_path']}"
    if not os.path.exists(src): print('MISSING',r['new_path']); continue
    if os.path.exists(dst): print('BLOCKED (target exists)',r['old_path']); continue
    if r['sha256'] and os.path.isfile(src) and hashlib.sha256(open(src,'rb').read()).hexdigest()!=r['sha256']: print('CHANGED since move',r['new_path']); continue
    if apply:
        os.makedirs(os.path.dirname(dst),exist_ok=True); subprocess.run(['mv','-n',src,dst],check=True)
    ok+=1; rows_done.append(r)
if apply and ok:
    cp=f'{V}/99.System/catalog.csv'; crow=list(csv.reader(open(cp))); H=crow[0]; I={k:i for i,k in enumerate(H)}
    back={r['new_path']:r['old_path'] for r in rows_done}
    folders={n:o for n,o in back.items() if os.path.isdir(f'{V}/{o}')}   # folder renames: fix paths under them
    for r in crow[1:]:
        if r[I['path']] in back and r[I['path']] not in folders: r[I['path']]=back[r[I['path']]]; r[I['status']]='undone ('+batch+')'
        for f in ('path','proposed_path'):
            for n,o in folders.items():
                if f in I and (r[I[f]]+'/').startswith(n+'/'): r[I[f]]=o+r[I[f]][len(n):]
    vj=f'{V}/99.System/vault.json'
    if folders and os.path.exists(vj):   # keep vault.json in step with renamed folders (add_person.py)
        import json; cfg=json.load(open(vj))
        for k in ('family_folder','relatives_folder'):
            if cfg.get(k) in folders: cfg[k]=folders[cfg[k]]
        created=[r['new_path'] for r in csv.DictReader(open(f'{V}/99.System/move-log.csv')) if r['batch']==batch and r['action']=='create']
        for c in created:
            cfg['people']=[p for p in cfg.get('people',[]) if p.get('folder')!=c]
            if os.path.isdir(f'{V}/{c}') and not os.listdir(f'{V}/{c}'):
                d=f'{V}/90.Review/Empty-folders/{c}'; os.makedirs(os.path.dirname(d),exist_ok=True); subprocess.run(['mv','-n',f'{V}/{c}',d])
                print('moved empty folder',c,'to 90.Review/Empty-folders (NAMING.md still lists its code; edit by hand)')
        open(vj,'w').write(json.dumps(cfg,indent=2,ensure_ascii=False)+'\n')
    csv.writer(open(cp,'w',newline='')).writerows(crow)
    with open(f'{V}/99.System/move-log.csv','a') as lg:
        for r in rows_done: lg.write(f'{__import__("datetime").datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")},undo-{batch},move,"{r["new_path"]}","{r["old_path"]}",{r["sha256"]},"undo"\n')
print(('restored' if apply else 'would restore'),ok,'of',len(rows),'files in batch',batch)

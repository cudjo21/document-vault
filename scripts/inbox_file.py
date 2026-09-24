#!/usr/bin/env python3
"""File an APPROVED inbox plan. Dry run by default; --apply to execute.
Plan = JSON list, one entry per inbox file:
  {"src": "00.Inbox/x.pdf",
   "action": "file" | "duplicate" | "unclear" | "move",   # move = existing vault file or original bundle -> dest (status via "status")
   "dest": "01.Alex/01.IDs/AS_passport-GBR_exp2030-06.pdf",          # for "file"
   "keep": "01.Alex/01.IDs/AS_passport-GBR_exp2030-06.pdf",          # for "duplicate": the copy that stays
   "replace_keeper": false,   # duplicate only: true = the NEW file is better; it takes the name and the old keeper goes to Review
   "reason": "one line", 
   "catalog": {person, category, doc_kind, doc_date, expiry_date, original_title, summary, issuer, country,
               language, related, sensitive, confidence, notes}}
Rules enforced: never delete, never overwrite, file unchanged since scan, every move logged in
99.System/move-log.csv, catalog.csv updated. Usage: python3 inbox_file.py plan.json <batch-name> [--apply]"""
import os, sys, json, csv, hashlib, subprocess, datetime
SYS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); VAULT = os.path.dirname(SYS)
plan = json.load(open(sys.argv[1])); BATCH = sys.argv[2]; APPLY = '--apply' in sys.argv
scan = {r['path']: r for r in json.load(open(os.path.join(SYS, '.work', 'inbox_scan.json')))}
V = lambda p: os.path.join(VAULT, p)
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
def base(p): return os.path.splitext(os.path.basename(p))[0]
steps, problems = [], []
for e in plan:
    s = e['src']
    if e['action'] == 'move':   # move an existing library file or an original bundle (not a newly scanned inbox file)
        if not os.path.exists(V(s)): problems.append(f'missing: {s}'); continue
        steps.append((s, e['dest'], e)); continue
    S = scan.get(s)
    if not S: problems.append(f'not in scan: {s}'); continue
    if not os.path.exists(V(s)): problems.append(f'missing: {s}'); continue
    if sha(V(s)) != S['sha256']: problems.append(f'changed since scan: {s}')
    if e['action'] == 'file':
        steps.append((s, e['dest'], e))
    elif e['action'] == 'unclear':
        steps.append((s, f"90.Review/Unclear/{os.path.basename(s)}", e))
    elif e['action'] == 'duplicate':
        k = e['keep']; g = f"90.Review/Duplicates/{base(k)}"
        if not os.path.exists(V(k)) and k not in {x.get('dest') for x in plan if x['action']=='file'}: problems.append(f'keeper missing: {k}')
        if e.get('replace_keeper'):
            steps.append((k, f"{g}/{os.path.basename(k)}", dict(e, _old_keeper=True)))
            steps.append((s, k, e))
        else:
            steps.append((s, f"{g}/{os.path.basename(s)}", e))
    else: problems.append(f'unknown action for {s}')
dests = [d for _, d, _ in steps]
if len(dests) != len(set(dests)): problems.append('two moves share one destination')
moved_away = {src for src, _, _ in steps}
for src, d, _ in steps:
    if os.path.exists(V(d)) and d not in moved_away: problems.append(f'destination exists: {d}')
print(f'{len(plan)} plan entries -> {len(steps)} moves, {len(problems)} problems')
for src, d, _ in steps: print(f'  {src}  ->  {d}')
for p in problems: print('  PROBLEM:', p)
if problems: sys.exit(1)
if not APPLY: print('dry run only; add --apply'); sys.exit(0)
ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
log = open(os.path.join(SYS, 'move-log.csv'), 'a')
cat_p = os.path.join(SYS, 'catalog.csv'); rows = list(csv.reader(open(cat_p))); H = rows[0]; I = {k: i for i, k in enumerate(H)}
groups = {}
for src, d, e in steps:
    h = sha(V(src)); os.makedirs(os.path.dirname(V(d)), exist_ok=True)
    subprocess.run(['mv', '-n', V(src), V(d)], check=True)
    assert os.path.exists(V(d)) and not os.path.exists(V(src)), f'move failed: {src}'
    log.write(f'{ts},{BATCH},move,"{src}","{d}",{h},"{e.get("reason","").replace(chr(34),chr(39))}"\n'); log.flush()
    if e['action'] == 'move':
        hit = False
        for r in rows[1:]:
            if r[I['path']] == src: r[I['path']] = d; r[I['status']] = e.get('status', 'in-review'); hit = True
        if not hit:
            r = [''] * len(H); r[I['path']] = d; r[I['sha256']] = h; r[I['original_name']] = os.path.basename(src)
            r[I['status']] = e.get('status', 'in-review'); r[I['summary']] = e.get('reason', ''); rows.append(r)
        if '/Duplicates/' in d: groups.setdefault(os.path.dirname(d), []).append((os.path.basename(d), e.get('reason', '')))
        continue
    if e.get('_old_keeper'):
        for r in rows[1:]:
            if r[I['path']] == src: r[I['path']] = d; r[I['status']] = 'in-review-replaced'
        groups.setdefault(os.path.dirname(d), []).append((os.path.basename(d), 'previous copy, replaced by a better scan'))
        continue
    S = scan[src]; r = [''] * len(H); c = e.get('catalog', {})
    for k, v in c.items():
        if k in I: r[I[k]] = str(v)
    r[I['path']] = d; r[I['proposed_path']] = d; r[I['sha256']] = h; r[I['original_name']] = os.path.basename(src)
    r[I['pages']] = str(S.get('pages') or ''); r[I['pixel_size']] = S.get('pixel_size', ''); r[I['effective_dpi']] = str(S.get('effective_dpi', ''))
    if 'dhash' in I: r[I['dhash']] = S.get('dhash', '')
    r[I['status']] = {'file': 'filed', 'unclear': 'unclear', 'duplicate': 'filed' if d == e.get('keep') else 'in-review-duplicate'}[e['action']]
    if e['action'] == 'duplicate' and d != e.get('keep'):
        r[I['related']] = f"duplicate of {e['keep']}"
        groups.setdefault(os.path.dirname(d), []).append((os.path.basename(d), e.get('reason', '')))
    rows.append(r)
log.close(); csv.writer(open(cat_p, 'w', newline='')).writerows(rows)
for g, items in groups.items():
    cm = V(g + '/comparison.md')
    with open(cm, 'a') as f:
        if os.path.getsize(cm) == 0 if os.path.exists(cm) else True:
            f.write(f"# {os.path.basename(g)}\n\nThe best copy stays in the library under this name. Copies below were moved here for review. Nothing was deleted.\n\n")
        f.write(f"\n## Added {ts[:10]} (batch {BATCH})\n\n")
        for n, why in items: f.write(f"- **{n}**: {why}\n")
print(f'done: {len(steps)} moves logged as batch {BATCH}; undo with: python3 99.System/Scripts/undo_moves.py {BATCH} --apply')

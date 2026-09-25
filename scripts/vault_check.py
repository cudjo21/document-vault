#!/usr/bin/env python3
"""Read-only health check of a Document Vault. Never moves or changes anything.
Usage: python3 vault_check.py [--months N]     (default N = 6)
Reports:
  1. documents expired or expiring within N months (from catalog expiry_date)
  2. library files not in the catalog
  3. catalog rows marked filed whose file is missing (or only an iCloud placeholder)
  4. names that break the naming convention
  5. tidy suggestions: 5+ files of one topic or series directly in one folder (--tidy-min N)
  6. expired documents outside an Archive folder: replaced by a newer one (archive) or not (ask)
  7. empty folders, stray files at the top level, files waiting in the inbox or in Review
Output is metadata only (paths, kinds, dates): no document content."""
import os, sys, csv, re, datetime, json

SYS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); VAULT = os.path.dirname(SYS)
MONTHS = int(sys.argv[sys.argv.index("--months") + 1]) if "--months" in sys.argv else 6
TIDY_MIN = int(sys.argv[sys.argv.index("--tidy-min") + 1]) if "--tidy-min" in sys.argv else 5
SKIP_TOP = {"00.Inbox", "80.Packs", "90.Review", "99.System"}   # packs are deliberate copies
IGNORE = {".DS_Store", "Icon\r", "desktop.ini", "Thumbs.db"}
NAME_RE = re.compile(r"^[A-Z]{2,4}(-(MOM|DAD|REL))?_(\d{4}-\d{2}-\d{2}_)?[a-z0-9]+(-[a-zA-Z0-9]+)*(_exp\d{4}-\d{2})?\.[a-z0-9]+$")

def rel(p): return os.path.relpath(p, VAULT)
def add_months(d, n):
    y, m = divmod(d.month - 1 + n, 12); return datetime.date(d.year + y, m + 1, min(d.day, 28))
def parse(s):
    for f in ("%Y-%m-%d", "%Y-%m"):
        try: return datetime.datetime.strptime(s.strip(), f).date()
        except Exception: pass
    return None

def main():
    rows = list(csv.DictReader(open(os.path.join(SYS, "catalog.csv"), encoding="utf-8")))
    filed = [r for r in rows if r.get("status", "").startswith("filed")]
    today = datetime.date.today(); horizon = add_months(today, MONTHS)

    print(f"== Expired or expiring by {horizon} ==")
    exp = []
    for r in filed:
        d = parse(r.get("expiry_date", "") or "")
        if d and d <= horizon: exp.append((d, r))
    for d, r in sorted(exp, key=lambda x: x[0]):
        state = "EXPIRED " if d < today else "expires "
        print(f"  {state}{d}  {r['path']}")
    if not exp: print("  none")

    lib = set()
    for top in sorted(os.listdir(VAULT)):
        tp = os.path.join(VAULT, top)
        if top in SKIP_TOP or top.startswith("."): continue
        if os.path.isfile(tp):
            continue
        for dp, dn, fn in os.walk(tp):
            dn[:] = [d for d in dn if not d.startswith(".")]
            for f in fn:
                if f in IGNORE: continue
                lib.add(rel(os.path.join(dp, f)))
    cat_paths = {r["path"] for r in filed}

    print("== Library files not in the catalog ==")
    placeholders = {p for p in lib if os.path.basename(p).startswith(".") and p.endswith(".icloud")}
    real = {p for p in lib - placeholders if not os.path.basename(p).startswith(".")}
    extra = sorted(real - cat_paths)
    for p in extra: print("  " + p)
    if not extra: print("  none")

    print("== Catalog says filed, file missing ==")
    miss = []
    for p in sorted(cat_paths):
        if os.path.exists(os.path.join(VAULT, p)): continue
        ph = os.path.join(os.path.dirname(p), "." + os.path.basename(p) + ".icloud")
        miss.append(p + ("   (in iCloud, not downloaded)" if ph in placeholders else ""))
    for p in miss: print("  " + p)
    if not miss: print("  none")

    print("== Names that break the convention ==")
    badn = [p for p in sorted(real) if not NAME_RE.match(os.path.basename(p))]
    for p in badn: print("  " + p)
    if not badn: print("  none")

    print(f"== Tidy suggestions ({TIDY_MIN}+ files of one topic in a folder) ==")
    try: cfg = json.load(open(os.path.join(SYS, "vault.json"), encoding="utf-8"))
    except Exception: cfg = {}
    flat = {cfg.get("relatives_folder")} - {None}           # relatives stay flat by design
    by_dir = {}
    for p in real:
        d, f = os.path.split(p)
        parts = d.split(os.sep)
        if parts[0] in flat or len(parts) != 2: continue          # only category folders; one level of subfolders at most
        if parts[1].endswith(".IDs"): continue                     # IDs stay together by kind (passports, cards)
        if re.match(r"^[A-Z-]+_\d{4}-\d{2}-\d{2}_", f): continue   # dated medical exams stay in date order
        stem = re.sub(r"^[A-Z]{2,4}(-[A-Z]+)?_", "", os.path.splitext(f)[0])
        key = stem.split("-")[0][:6]
        by_dir.setdefault((d, key), []).append(f)
    tidy = [(d, k, fs) for (d, k), fs in by_dir.items() if len(fs) >= TIDY_MIN]
    for d, k, fs in sorted(tidy):
        print(f"  {d}/  {len(fs)} files starting '{k}...': " + ", ".join(sorted(fs)[:4]) + (" ..." if len(fs) > 4 else ""))
    if not tidy: print("  none")

    print("== Expired, outside an Archive folder ==")
    def who(r): return r.get("person") or os.path.basename(r["path"]).split("_")[0]
    def kind(r): return r.get("doc_kind") or re.sub(r"^[A-Z]{2,4}(-[A-Z]+)?_", "", os.path.basename(r["path"])).split("-")[0]
    shown = False
    for d, r in sorted(exp, key=lambda x: x[0]):
        if d >= today or "Archive" in r["path"].split("/"): continue
        newer = [o for o in filed if o is not r and who(o) == who(r) and kind(o) == kind(r)
                 and (o.get("country") or "") == (r.get("country") or "")
                 and (parse(o.get("expiry_date", "") or "") or datetime.date.max) > d
                 and (parse(o.get("expiry_date", "") or "") or datetime.date.max) >= today]
        arch = os.path.join(os.path.dirname(r["path"]), "Archive") + "/"
        if newer: print(f"  replaced   {r['path']}  -> {arch}  (newer: {os.path.basename(newer[0]['path'])})")
        else:     print(f"  ASK        {r['path']}  (expired {d}, no replacement in the vault: renew, or archive to {arch}?)")
        shown = True
    if not shown: print("  none")

    print("== Other ==")
    stray = [f for f in os.listdir(VAULT) if os.path.isfile(os.path.join(VAULT, f)) and f not in IGNORE and not f.startswith(".")]
    if stray: print("  files at the top level: " + ", ".join(sorted(stray)))
    empty = []
    for dp, dn, fn in os.walk(VAULT):
        if "/." in dp or rel(dp).startswith("99.System"): continue
        if not [x for x in fn if x not in IGNORE] and not [d for d in dn if not d.startswith(".")] and dp != VAULT:
            if os.sep in rel(dp) and not rel(dp).startswith(("90.Review", "80.Packs")):   # top-level person folders may be empty
                empty.append(rel(dp))
    if empty: print("  empty folders: " + ", ".join(sorted(empty)))
    def count(d):
        n = 0
        for dp, dn, fn in os.walk(os.path.join(VAULT, d)):
            n += len([f for f in fn if f not in IGNORE and not f.startswith(".")])
        return n
    print(f"  inbox: {count('00.Inbox')} file(s) waiting")
    pk = os.path.join(VAULT, "80.Packs")
    if os.path.isdir(pk):
        for d in sorted(os.listdir(pk)):
            if os.path.isdir(os.path.join(pk, d)):
                age = (datetime.date.today() - datetime.date.fromtimestamp(os.path.getmtime(os.path.join(pk, d)))).days
                print(f"  pack: 80.Packs/{d} ({count(os.path.join('80.Packs', d))} file(s), {age} days old; move to 90.Review when done)")
    rv = os.path.join(VAULT, "90.Review")
    if os.path.isdir(rv):
        for d in sorted(os.listdir(rv)):
            if os.path.isdir(os.path.join(rv, d)):
                n = count(os.path.join("90.Review", d))
                if n: print(f"  90.Review/{d}: {n} file(s)")
    print(f"  catalog: {len(filed)} filed documents, {len(rows)} rows")

if __name__ == "__main__":
    main()

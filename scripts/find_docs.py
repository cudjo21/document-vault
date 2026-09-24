#!/usr/bin/env python3
"""Search the Document Vault catalog. Read-only; prints metadata only (never document content).
Usage: python3 find_docs.py [words ...] [--person CODE] [--kind KIND] [--category CAT]
                            [--country ISO3] [--expiring MONTHS] [--all] [--limit N]
Words match (case-insensitive, all must match) against path, doc_kind, original_title, summary,
issuer, country, original_name and notes. --all includes rows that are not filed (Review etc.)."""
import os, sys, csv, datetime

SYS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); VAULT = os.path.dirname(SYS)
FIELDS = ["path", "doc_kind", "original_title", "summary", "issuer", "country", "original_name", "notes", "category", "person"]

def opt(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name); v = sys.argv[i + 1]; del sys.argv[i:i + 2]; return v
    return default

def main():
    person, kind, cat, country = opt("--person"), opt("--kind"), opt("--category"), opt("--country")
    expiring = opt("--expiring"); limit = int(opt("--limit", "40"))
    show_all = "--all" in sys.argv
    words = [w.lower() for w in sys.argv[1:] if not w.startswith("--")]
    rows = list(csv.DictReader(open(os.path.join(SYS, "catalog.csv"), encoding="utf-8")))
    today = datetime.date.today()
    horizon = None
    if expiring:
        m = int(expiring); y, mm = divmod(today.month - 1 + m, 12); horizon = datetime.date(today.year + y, mm + 1, 1)
    hits = []
    for r in rows:
        if not show_all and not r.get("status", "").startswith("filed"): continue
        if person and not (r.get("person", "").upper() == person.upper() or os.path.basename(r["path"]).upper().startswith(person.upper() + "_")): continue
        if kind and kind.lower() not in (r.get("doc_kind", "") + " " + r["path"]).lower(): continue
        if cat and cat.lower() not in (r.get("category", "") + " " + r["path"]).lower(): continue
        if country and country.upper() not in (r.get("country", "").upper() + " " + r["path"]): continue
        if horizon:
            e = (r.get("expiry_date") or "")[:10]
            try: d = datetime.datetime.strptime(e if len(e) == 10 else e + "-01", "%Y-%m-%d").date()
            except Exception: continue
            if d > horizon: continue
        hay = " ".join((r.get(f) or "") for f in FIELDS).lower()
        if all(w in hay for w in words): hits.append(r)
    hits.sort(key=lambda r: r["path"])
    for r in hits[:limit]:
        extra = []
        if r.get("expiry_date"): extra.append("expires " + r["expiry_date"])
        if r.get("doc_date"): extra.append("dated " + r["doc_date"])
        if not r.get("status", "").startswith("filed"): extra.append("status " + r.get("status", ""))
        exists = "" if os.path.exists(os.path.join(VAULT, r["path"])) else "  [FILE MISSING]"
        print(f"{r['path']}{exists}\n    {(r.get('summary') or '')[:140]}" + (f"\n    {'; '.join(extra)}" if extra else ""))
    print(f"-- {len(hits)} match(es)" + (f", showing {limit}" if len(hits) > limit else ""))

if __name__ == "__main__":
    main()

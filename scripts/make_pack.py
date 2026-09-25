#!/usr/bin/env python3
"""Build a document pack (visa, residence renewal, mortgage...) from an approved plan.
COPIES library files into 80.Packs/<pack name>/, numbered in the order of the requested list,
one subfolder per person. The library is never changed. Dry run by default; --apply to execute.

Usage: python3 make_pack.py <plan.json> [--apply]

plan.json:
{
  "name": "2026-10 USA visa",                 # folder name under 80.Packs/
  "purpose": "US tourist visa, consulate Madrid",
  "travel_date": "2026-11-20",                # optional; enables validity checks
  "min_validity_months": 6,                   # optional; passports etc. valid this long after travel_date
  "combine": "none" | "person" | "family",    # optional combined PDF(s), lossless
  "items": [
    {"n": 1, "label": "Valid passport", "person": "AS",
     "src": "01.Alex/01.IDs/AS_passport-GBR_exp2030-06.pdf", "check_validity": true},
    {"n": 3, "label": "Bank statements, last 3 months", "person": "AS",
     "src": "01.Alex/03.Finance/AS_bank-statement-2026-08.pdf", "max_age_months": 3},
    {"n": 2, "label": "Marriage certificate", "person": "FAM", "src": "05.Family/04.Legal/FAM_marriage-certificate-ESP.pdf"},
    {"n": 4, "label": "Photo 5x5 cm", "person": "AS", "missing": true, "todo": "take a photo at a photo booth"}
  ]
}
Several items may share one n (one per person). Several files for one item: repeat the item.
Writes checklist.md in the pack, logs every copy in 99.System/move-log.csv (action "copy").
Never overwrites; refuses if the pack folder already exists."""
import os, sys, json, csv, hashlib, shutil, datetime, subprocess, tempfile, re

SYS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); VAULT = os.path.dirname(SYS)
V = lambda p: os.path.join(VAULT, p)

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def parse_date(s):
    s = (s or "").strip()
    for fmt, n in (("%Y-%m-%d", 10), ("%Y-%m", 7)):
        try: return datetime.datetime.strptime(s[:n], fmt).date()
        except Exception: pass
    return None

def add_months(d, m):
    y, mm = divmod(d.month - 1 + m, 12); return datetime.date(d.year + y, mm + 1, min(d.day, 28))

def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    plan = json.load(open(sys.argv[1], encoding="utf-8")); apply = "--apply" in sys.argv
    name = plan["name"].strip()
    if not name or "/" in name or name.startswith("."): sys.exit("bad pack name")
    pack = os.path.join("80.Packs", name)
    if os.path.exists(V(pack)): sys.exit(f"pack already exists: {pack} (choose another name; nothing is overwritten)")
    cfg = json.load(open(os.path.join(SYS, "vault.json"), encoding="utf-8"))
    folders = {p["code"]: p["folder"] for p in cfg["people"]}
    folders["FAM"] = "00.Family"
    cat = {r["path"]: r for r in csv.DictReader(open(os.path.join(SYS, "catalog.csv"), encoding="utf-8"))}
    travel = parse_date(plan.get("travel_date")); minv = int(plan.get("min_validity_months", 6))
    today = datetime.date.today()

    rows, copies, problems = [], [], []
    for it in sorted(plan["items"], key=lambda x: (x["n"], x.get("person", ""))):
        who = it.get("person", "FAM")
        sub = folders.get(who) or folders.get(who.split("-")[0])
        if not sub: problems.append(f"unknown person code {who}"); continue
        status, note = "OK", it.get("note", "")
        if it.get("missing"):
            rows.append((it["n"], it["label"], who, "MISSING", "", it.get("todo", ""))); continue
        src = it["src"]
        if not os.path.isfile(V(src)): problems.append(f"file not found: {src}"); continue
        c = cat.get(src, {})
        exp = parse_date(c.get("expiry_date"))
        if exp and exp < today: status, note = "EXPIRED", (note + f" expired {exp}").strip()
        elif exp and travel and it.get("check_validity", True) and exp < add_months(travel, minv):
            status, note = "CHECK", (note + f" expires {exp}, less than {minv} months after travel").strip()
        if it.get("max_age_months"):
            d = parse_date(c.get("doc_date"))
            if not d: status, note = "CHECK", (note + " date unknown; check it is recent enough").strip()
            elif d < add_months(today, -int(it["max_age_months"])):
                status, note = "CHECK", (note + f" dated {d}, older than {it['max_age_months']} months").strip()
        dest = os.path.join(pack, sub, f"{it['n']:02d}_{os.path.basename(src)}")
        if dest in [d for _, d in copies]: problems.append(f"same file twice for one person: {dest}"); continue
        copies.append((src, dest)); rows.append((it["n"], it["label"], who, status, dest, note))

    print(f"Pack {pack}: {len(copies)} file(s) to copy, {sum(1 for r in rows if r[3]=='MISSING')} missing, "
          f"{sum(1 for r in rows if r[3] in ('CHECK','EXPIRED'))} to check, {len(problems)} problem(s)")
    for n, label, who, st, dest, note in rows:
        print(f"  {n:02d} {who:<7} {st:<8} {label[:40]:<40} {os.path.basename(dest)} {('- ' + note) if note else ''}")
    for p in problems: print("  PROBLEM:", p)
    if problems: sys.exit(1)
    if not apply: print("dry run only; add --apply"); return

    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"); batch = "pack-" + re.sub(r"[^A-Za-z0-9-]+", "-", name).strip("-")
    log = open(os.path.join(SYS, "move-log.csv"), "a")
    for src, dest in copies:
        os.makedirs(os.path.dirname(V(dest)), exist_ok=True)
        if os.path.exists(V(dest)): sys.exit(f"refusing to overwrite {dest}")
        shutil.copy2(V(src), V(dest))
        h = sha(V(src))
        assert sha(V(dest)) == h, f"copy mismatch: {dest}"
        log.write(f'{ts},{batch},copy,"{src}","{dest}",{h},"document pack {name}"\n')
    log.flush()

    combined = []
    mode = plan.get("combine", "none")
    if mode in ("person", "family"):
        groups = {}
        for src, dest in copies:
            key = "ALL" if mode == "family" else os.path.dirname(dest)
            groups.setdefault(key, []).append(dest)
        for key, files in groups.items():
            out = os.path.join(pack, f"{name}_all-documents.pdf") if key == "ALL" else \
                  os.path.join(key, os.path.basename(key).split(".", 1)[-1] + "_all-documents.pdf")
            tmp = tempfile.mkdtemp(); parts, skipped = [], []
            for f in files:
                ext = f.rsplit(".", 1)[-1].lower()
                if ext == "pdf": parts.append(V(f))
                elif ext in ("jpg", "jpeg", "png", "tif", "tiff"):
                    import img2pdf
                    p = os.path.join(tmp, f"{len(parts):03d}.pdf"); open(p, "wb").write(img2pdf.convert(V(f))); parts.append(p)
                else: skipped.append(os.path.basename(f))
            if len(parts) < 2: shutil.rmtree(tmp, ignore_errors=True); continue   # one file needs no combined copy
            if os.path.exists(V(out)): sys.exit(f"refusing to overwrite {out}")
            subprocess.run(["pdfunite", *parts, V(out)], check=True)
            shutil.rmtree(tmp, ignore_errors=True)
            log.write(f'{ts},{batch},create,"","{out}",{sha(V(out))},"combined PDF of the pack, list order"\n')
            combined.append((out, skipped))
    log.close()

    L = [f"# {name}", ""]
    if plan.get("purpose"): L.append(f"Purpose: {plan['purpose']}  ")
    if travel: L.append(f"Travel / appointment date: {travel}  ")
    L += [f"Made: {ts[:10]}. These are COPIES; the originals stay in the vault. When you are done, move this folder to 90.Review and delete it there.", "",
          "| # | Item | Who | Status | File | Notes |", "|---|---|---|---|---|---|"]
    for n, label, who, st, dest, note in rows:
        L.append(f"| {n} | {label} | {who} | {st} | {os.path.relpath(dest, pack) if dest else ''} | {note} |")
    todo = [r for r in rows if r[3] in ("MISSING", "CHECK", "EXPIRED")]
    if todo:
        L += ["", "## To do", ""] + [f"- [ ] {r[1]} ({r[2]}): {r[3].lower()}{' - ' + r[5] if r[5] else ''}" for r in todo]
    if combined:
        L += ["", "## Combined PDFs (list order)", ""] + [f"- {os.path.relpath(out, pack)}" + (f" (not included: {', '.join(skipped)})" if skipped else "") for out, skipped in combined]
    open(V(os.path.join(pack, "checklist.md")), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"done: {len(copies)} copies in {pack}/, checklist.md written" + (f", {len(combined)} combined PDF(s)" if combined else ""))
    print(f"logged as batch {batch}")

if __name__ == "__main__":
    main()

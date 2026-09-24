#!/usr/bin/env python3
"""Create a new, empty Document Vault from a small JSON config. Never overwrites anything.

Usage: python3 create_vault.py <vault-folder> <config.json> [--apply]
Dry run by default: prints what would be created.

config.json:
{
  "family_name": "Smith",
  "people": [
    {"name": "Alex",  "code": "AS"},
    {"name": "Maria", "code": "MS"},
    {"name": "Sam",   "code": "SAM"}
  ],
  "relatives": true,
  "ocr_languages": ["eng", "por", "rus", "heb"],   # optional; this is the default
  "scripts_from": "/path/to/plugin/scripts"      # folder holding the vault scripts to copy in
}
"""
import os, sys, json, shutil, datetime, re

CATALOG_HEADER = ("path,person,category,doc_kind,doc_date,expiry_date,original_title,summary,issuer,"
                  "country,language,pages,pixel_size,effective_dpi,sha256,original_name,related,sensitive,"
                  "confidence,notes,status,proposed_path,dhash")
MOVELOG_HEADER = "timestamp,batch,action,old_path,new_path,sha256,reason"
DEFAULT_LANGS = ["eng", "por", "rus", "heb"]   # English, Portuguese, Russian, Hebrew
VAULT_SCRIPTS = ["inbox_scan.py", "inbox_file.py", "undo_moves.py", "merge_images.py", "page_scan.py",
                 "audit_duplicates.py", "vault_check.py", "find_docs.py", "check_tools.py", "add_person.py"]

def main():
    if len(sys.argv) < 3: sys.exit(__doc__)
    vault, cfg_path = sys.argv[1], sys.argv[2]; apply = "--apply" in sys.argv
    cfg = json.load(open(cfg_path))
    people = cfg.get("people") or []
    if not people: sys.exit("config has no people")
    codes = [p["code"] for p in people]
    for c in codes:
        if not re.fullmatch(r"[A-Z]{2,4}", c): sys.exit(f"person code must be 2-4 capital letters: {c}")
    if len(set(codes)) != len(codes) or "FAM" in codes: sys.exit("person codes must be unique and not FAM")
    if os.path.exists(os.path.join(vault, "99.System", "catalog.csv")): sys.exit("a vault already exists here; nothing done")

    dirs = ["00.Inbox"]
    for i, p in enumerate(people, 1):
        dirs.append(f"{i:02d}.{p['name']}")
    fam_n = len(people) + 1
    dirs.append(f"{fam_n:02d}.Family")
    if cfg.get("relatives", True): dirs.append(f"{fam_n + 1:02d}.Relatives")
    dirs += ["90.Review/Duplicates", "90.Review/Unclear", "90.Review/Split-originals", "90.Review/Not-needed",
             "99.System/Scripts", "99.System/tessdata", "99.System/.work"]

    print(("Creating" if apply else "Would create") + f" vault in {vault}:")
    for d in dirs: print("  " + d + "/")
    print("  99.System/NAMING.md, catalog.csv, move-log.csv, vault.json, Scripts/*")
    if not apply: print("dry run only; add --apply"); return

    for d in dirs: os.makedirs(os.path.join(vault, d), exist_ok=True)
    S = os.path.join(vault, "99.System")
    def write_new(name, text):
        p = os.path.join(S, name)
        if not os.path.exists(p): open(p, "w").write(text)
    write_new("catalog.csv", CATALOG_HEADER + "\n")
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    write_new("move-log.csv", MOVELOG_HEADER + "\n" + f'{ts},setup,create,"","99.System",,"vault created"\n')
    vcfg = {"family_name": cfg.get("family_name", ""), "created": ts[:10],
            "people": [{"name": p["name"], "code": p["code"], "folder": f"{i:02d}.{p['name']}"} for i, p in enumerate(people, 1)],
            "family_folder": f"{fam_n:02d}.Family",
            "relatives_folder": f"{fam_n + 1:02d}.Relatives" if cfg.get("relatives", True) else None,
            "ocr_languages": cfg.get("ocr_languages") or DEFAULT_LANGS}
    write_new("vault.json", json.dumps(vcfg, indent=2, ensure_ascii=False) + "\n")
    here = os.path.dirname(os.path.abspath(__file__))
    tmpl = next((t for t in [os.path.join(here, "NAMING.template.md"), os.path.join(here, "..", "templates", "NAMING.md")]
                 if os.path.exists(t)), None)
    if not tmpl: sys.exit("NAMING template not found next to this script (NAMING.template.md)")
    naming = open(tmpl).read()
    people_lines = "\n".join(f"  - {p['code']} ({p['name']})" for p in people)
    naming = naming.replace("{{PEOPLE}}", people_lines).replace("{{DATE}}", ts[:10])
    write_new("NAMING.md", naming)
    src = cfg.get("scripts_from") or os.path.dirname(os.path.abspath(__file__))
    for f in VAULT_SCRIPTS:
        s, d = os.path.join(src, f), os.path.join(S, "Scripts", f)
        if os.path.exists(s) and not os.path.exists(d): shutil.copy2(s, d)
    print("done")

if __name__ == "__main__":
    main()

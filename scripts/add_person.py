#!/usr/bin/env python3
"""Add a person to an existing Document Vault. Dry run by default; --apply to execute.
Usage: python3 add_person.py <Name> <CODE> [--apply]

The new person gets the next number after the existing people (e.g. 05.Leo). The Family and
Relatives folders move up one number (05.Family -> 06.Family) so people stay before Family.
Folder renames are logged in move-log.csv (batch add-person-<CODE>), catalog paths are updated,
vault.json and NAMING.md learn the new code. Never overwrites; undo with undo_moves.py."""
import os, sys, json, csv, re, datetime, subprocess

SYS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); VAULT = os.path.dirname(SYS)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]; apply = "--apply" in sys.argv
    if len(args) != 2: sys.exit(__doc__)
    name, code = args[0], args[1].upper()
    if not re.fullmatch(r"[A-Za-z][A-Za-z-]*", name): sys.exit("name: ASCII letters only (drop accents)")
    if not re.fullmatch(r"[A-Z]{2,4}", code) or code == "FAM": sys.exit("code must be 2-4 capital letters and not FAM")
    vp = os.path.join(SYS, "vault.json"); cfg = json.load(open(vp))
    people = cfg["people"]
    if code in [p["code"] for p in people]: sys.exit(f"code {code} is already used")
    if name.lower() in [p["name"].lower() for p in people]: sys.exit(f"{name} is already in the vault")

    n = len(people) + 1
    new_folder = f"{n:02d}.{name}"
    renames = []   # (old, new), highest number first so nothing collides
    shift = [k for k in ("relatives_folder", "family_folder") if cfg.get(k)]
    for k in shift:
        old = cfg[k]; num, rest = old.split(".", 1)
        renames.append((k, old, f"{int(num) + 1:02d}.{rest}"))
    for _, old, new in renames:
        if not os.path.isdir(os.path.join(VAULT, old)): sys.exit(f"folder missing: {old}")
    targets = [new for _, _, new in renames] + [new_folder]
    olds = {old for _, old, _ in renames}
    for t in targets:
        if os.path.exists(os.path.join(VAULT, t)) and t not in olds: sys.exit(f"already exists: {t}")

    print(("Adding" if apply else "Would add") + f" {name} ({code}) as {new_folder}/")
    for _, old, new in renames: print(f"  rename {old}/ -> {new}/")
    if not apply: print("dry run only; add --apply"); return

    batch = f"add-person-{code}"; ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    cat_p = os.path.join(SYS, "catalog.csv"); rows = list(csv.reader(open(cat_p, encoding="utf-8")))
    H = rows[0]; I = {k: i for i, k in enumerate(H)}
    with open(os.path.join(SYS, "move-log.csv"), "a") as log:
        for k, old, new in renames:
            subprocess.run(["mv", "-n", os.path.join(VAULT, old), os.path.join(VAULT, new)], check=True)
            assert os.path.isdir(os.path.join(VAULT, new)) and not os.path.exists(os.path.join(VAULT, old))
            log.write(f'{ts},{batch},rename,"{old}","{new}",,"make room for {name}"\n'); log.flush()
            for r in rows[1:]:
                for f in ("path", "proposed_path"):
                    if f in I and (r[I[f]] + "/").startswith(old + "/"): r[I[f]] = new + r[I[f]][len(old):]
            cfg[k] = new
        os.makedirs(os.path.join(VAULT, new_folder))
        log.write(f'{ts},{batch},create,"","{new_folder}",,"new person {name} ({code})"\n')
    csv.writer(open(cat_p, "w", newline="", encoding="utf-8")).writerows(rows)
    people.append({"name": name, "code": code, "folder": new_folder})
    open(vp, "w").write(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")
    np_ = os.path.join(SYS, "NAMING.md")
    if os.path.exists(np_):
        s = open(np_).read(); last = people[-2]
        line = f"  - {last['code']} ({last['name']})\n"
        if line in s: s = s.replace(line, line + f"  - {code} ({name})\n", 1); open(np_, "w").write(s)
        else: print("note: add the new code to NAMING.md by hand")
    print(f"done: batch {batch}; undo with: python3 99.System/Scripts/undo_moves.py {batch} --apply")

if __name__ == "__main__":
    main()

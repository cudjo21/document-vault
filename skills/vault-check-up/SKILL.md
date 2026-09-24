---
name: vault-check-up
description: Runs a health check of the Document Vault - expiring passports and permits, files missing from the catalog, broken names, leftovers in Review. Use when the user asks "check my vault", "what documents are expiring", "vault check-up", "is my vault in order" or wants a periodic review.
---

# Vault check-up

A read-only review first; fixes only after the user agrees. First read `../../guide/vault-basics.md` (relative to this skill's folder).

## Steps

1. **Find the vault** and make sure its scripts match the plugin's (update per the basics guide; `vault_check.py` may be new).
2. **Run** `python3 99.System/Scripts/vault_check.py` (add `--months 12` if the user wants a longer horizon; default 6). Output is metadata only.
3. **Report** in short sections, skipping empty ones:
   - **Expired or expiring**: group by person, soonest first, plain dates ("Alex's UK passport expires June 2027"). Remind that many countries require 6 months of passport validity for travel. Expired documents are kept (they are history); only mention them if a renewed one is missing from the vault.
   - **Not in the catalog**: files someone dropped straight into the library. Offer to process them like inbox files (move them to `00.Inbox` with a small `move` plan, then run the inbox skill) or to catalog them in place.
   - **Missing files**: catalog rows whose file is gone. Cloud placeholders mean "not downloaded" (ask the user to download). Otherwise ask whether they deleted them; if yes, set `status=deleted-by-user` and add a `delete` line to the move log.
   - **Names off-convention**: propose new names per NAMING.md in a table.
   - **Review**: counts in `90.Review/*`. Remind the user these wait for their manual decision; offer `audit_duplicates.py` to confirm each kept copy is the best one. Never delete them.
   - **Other**: empty subfolders, stray top-level files, files waiting in the inbox.
4. **Fix only with approval.** Renames and moves go through a plan file and `inbox_file.py` (action `move`, dry run, then `--apply`, batch name `checkup-YYYY-MM-DD`), so they are logged and can be undone. Empty folders move to `90.Review/Empty-folders/` rather than being removed.
5. **Offer a routine**: if the user would like, set up a scheduled task (e.g. monthly) that runs this check-up and reports expiring documents.

Never print document contents; this skill works from the catalog and file names only.

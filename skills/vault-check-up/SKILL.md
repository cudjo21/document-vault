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
   - **Expired or expiring**: group by person, soonest first, plain dates ("Alex's UK passport expires June 2027"). Remind that many countries require 6 months of passport validity for travel. Expired documents are kept (they are history: forms ask for previous passports and numbers).
   - **Expired, outside an Archive folder**: `replaced` lines have a newer document of the same kind and country; propose moving the old one to `Archive/` inside the same category folder (e.g. `01.IDs/Archive/`). `ASK` lines have no replacement in the vault: ask whether the person is renewing it (keep it where it is and remind later) or it should be archived. Never send expired documents to `90.Review` (that means "safe to delete") or to `99.Misc`.
   - **Tidy suggestions**: 5 or more files of one topic or series directly in one folder. Propose one subfolder per group with a clear name (e.g. `06.Education/Language-Course/`, `03.Finance/Invoices/`, `05.Work/SARs/`), one level deep only. Judge each group: suggest it for series (payslips, invoices, statements) and topics (a course, an assessment, a property, a legal case); do not split core document kinds such as passports in `01.IDs`, and leave dated medical exams in date order. Files keep their names.
   - **Not in the catalog**: files someone dropped straight into the library. Offer to process them like inbox files (move them to `00.Inbox` with a small `move` plan, then run the inbox skill) or to catalog them in place.
   - **Missing files**: catalog rows whose file is gone. Cloud placeholders mean "not downloaded" (ask the user to download). Otherwise ask whether they deleted them; if yes, set `status=deleted-by-user` and add a `delete` line to the move log.
   - **Names off-convention**: propose new names per NAMING.md in a table.
   - **Review**: counts in `90.Review/*`. Remind the user these wait for their manual decision; offer `audit_duplicates.py` to confirm each kept copy is the best one. Never delete them.
   - **Other**: empty subfolders, stray top-level files, files waiting in the inbox.
4. **Fix only with approval.** Renames and moves go through a plan file and `inbox_file.py` (action `move`, dry run, then `--apply`, batch name `checkup-YYYY-MM-DD`), so they are logged and can be undone. For archive and tidy moves of library documents, set `"status": "filed"` in each plan entry so they stay in the library. Empty folders move to `90.Review/Empty-folders/` rather than being removed.
5. **Offer a routine**: if the user would like, set up a scheduled task (e.g. monthly) that runs this check-up and reports expiring documents.

Never print document contents; this skill works from the catalog and file names only.

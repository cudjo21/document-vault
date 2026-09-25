---
name: prepare-pack
description: Prepares a document pack for an application (visa, residence permit renewal, citizenship, mortgage, school, new job) by matching a pasted list of required documents to the Document Vault and copying them, numbered in list order, per person. Use for "I'm applying for a visa, here's the list", "prepare the documents for our renewal", "make a pack for the consulate".
---

# Prepare a document pack

Turn a list of required documents into a ready folder of copies, in the order the list asks for, per applicant, with a checklist of what is missing. First read `../../guide/vault-basics.md` (relative to this skill's folder): ground rules, privacy, finding the vault, installing scripts.

A pack is **copies only**. The library is never changed. Packs live in `80.Packs/<pack name>/`, which the check-up ignores for duplicates.

## 1. Gather the request

From the user's message take: the pasted list, who is applying, and the purpose (country, type of application). If the list or the applicants are missing, ask for them in plain text (the list must be pasted, so no question tool for it). Then read `99.System/vault.json` to map names to codes and folders.

Ask the rest in one AskUserQuestion round, only what is still unknown (up to four questions):

- **Date:** the travel or appointment date (options such as "within a month", "in 1 to 3 months", "no date yet"; ask for the exact date in free text if they pick a period and validity matters). Used to check passport validity.
- **Combined PDF:** "Besides separate files, should I also make combined PDFs in the list order?" Options: **Separate files only** / **One combined PDF per person** (recommended for online portals) / **One PDF for the whole family**. Say that combining is lossless and that web pages (.html) and **password-protected PDFs can't be included**: those stay as separate files next to the combined PDF. If you already know that some matched files are locked (e.g. payslips), name them in the question.
- **Pack name**, if not obvious: propose `YYYY-MM <country> <purpose>`, e.g. `2026-10 USA visa`.

## 2. Match every item to the vault

Split the list into numbered items, keeping the user's order and numbering. For each item and each applicant, search the catalog (`python3 99.System/Scripts/find_docs.py <words> --person <CODE>`, with English synonyms: "travel document" = passport, "proof of address" = lease/utility bill, "proof of income" = payslips/tax return...). Family-wide items (marriage certificate, lease) use person `FAM`.

**Several candidates for one item: never pick silently.** Most common with passports and IDs:

- **Different countries** (e.g. a British and a Spanish passport): ask which one this application needs. Recommend the passport the person will travel or apply with, or the one of the relevant nationality; mention that some forms ask for all nationalities, and in that case include all.
- **Two of the same country** (e.g. old and new, or a regular and an internal passport): recommend the current, valid one; include the older one only if the list asks for previous passports or visa history.
- **Residence permits, visas, certificates with translations:** same approach (current one; translation next to the original if the destination country needs it).

Ask these in one AskUserQuestion round, one question per person and document type, options naming the actual files (e.g. "UK passport, expires Jun 2030", "Spanish passport, expires Jan 2027", "Both"). If there are more than four such questions, ask the most important first and the rest in a second round.

Items that cannot be in the vault (photos, filled-in forms, fees, appointment letters) and items not found become **missing** with a short to-do.

## 3. Check and show the plan

For each matched file, flag:

- **Expired** documents (never include silently; ask if the user really wants them).
- **Validity**: passports and permits that expire less than 6 months after the travel date (or the rule the list states).
- **Recency**: statements or certificates older than the list allows ("last 3 months") using the catalog date; if the date is unknown, flag it to check.
- **Translation**: the document's language differs from what the destination expects and the list asks for translations.
- **Password-protected PDFs** (check with `pdfinfo`: "Incorrect password" means locked): they are copied into the pack as they are, but can't go into a combined PDF. Say so in the note. If the application needs one single file (many online portals do), tell the user the only way is an unlocked copy: they open the file with its password (e.g. in Preview on a Mac) and export it as a new PDF without a password, then drop it into the Inbox. Never ask for or handle the password yourself, and remind them that an unlocked copy is readable by anyone who gets it.

Show one table: # | item | who | file | status (OK / check / expired / missing) | note. Keep it short; no document contents, no ID numbers. Wait for the user's go and apply their edits.

## 4. Build the pack

Write the plan to `99.System/.work/pack.json` in the format at the top of `99.System/Scripts/make_pack.py` (`name`, `purpose`, `travel_date`, `min_validity_months`, `combine`: none/person/family, `items` with `n`, `label`, `person`, `src` or `missing` + `todo`, optional `max_age_months`, `check_validity`). Dry run:

```
python3 99.System/Scripts/make_pack.py 99.System/.work/pack.json
```

Compare the dry run with the approved table, fix any PROBLEM lines, then run with `--apply`. The script copies (never moves), numbers files in list order (`01_...`, `02_...`) inside one folder per person (`00.Family` for family items), verifies each copy, logs it, builds the combined PDFs if asked, and writes `checklist.md` into the pack.

## 5. Report

In a few lines: where the pack is (folder name), how many files per person, what is missing or needs checking (the to-do list), and that the combined PDFs are there if made. Remind that these are copies: when the application is done, say "archive the pack": run `python3 99.System/Scripts/make_pack.py --archive "<pack name>"` (dry run), then with `--apply`. It moves the whole pack to `90.Review/Packs/`, logs it and can be undone; the user deletes it from there. Never delete a pack.

## Rules

- Copies only; the library, catalog paths and file names stay unchanged.
- Never overwrite: a pack name that exists stops the script; pick a new name.
- Privacy as always: work from the catalog and file names; if a detail must be read from inside a document, use the masked scans described in the basics guide.
- If a document is found in `90.Review` only (e.g. a better copy was never filed), say so and ask before using it.

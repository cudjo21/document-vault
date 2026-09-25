---
name: process-inbox
description: Files new documents from the Document Vault inbox - reads each one (masked), proposes a name and folder, handles duplicates and front/back scans, and moves them after approval. Also adds a new family member to the vault. Use when the user says "process my inbox", "file my new documents", "I added scans to the vault", "I shared photos from my phone", "add Leo to the vault" or similar.
---

# Process the Document Vault inbox

Turn the files in `00.Inbox` into correctly named, correctly filed documents, with the user approving every batch. First read `../../guide/vault-basics.md` (relative to this skill's folder): ground rules, privacy, layout, finding the vault, installing scripts.

## Scripts (in `<vault>/99.System/Scripts/`)

- `inbox_scan.py`: read-only masked scan of the inbox (`--inbox PATH` for another folder, `--no-ocr` for a quick pass). Writes `99.System/.work/inbox_scan.json`: masked text, pages, pixel size, DPI, `has_secrets`, duplicate candidates.
- `page_scan.py <pdf> <first> <last>`: masked per-page OCR for multi-document scans (writes to `~/vault-pages/`, outside the vault). Run page ranges in parallel to stay within shell time limits.
- `merge_images.py <out.pdf> <img1> <img2> ... --batch <name>`: lossless combined PDF (front + back), logged.
- `audit_duplicates.py`: read-only comparison of Review duplicate groups against their kept copies.
- `inbox_file.py <plan.json> <batch> [--apply]`: files an approved plan; dry run by default.
- `undo_moves.py <batch> [--apply]`: reverses a batch; dry run by default.
- `add_person.py <Name> <CODE> [--apply]`: adds a person to the vault (next number; Family and Relatives move up one, logged, undoable).

## Steps

1. **Find the vault**, check its scripts match the plugin's (update per the basics guide), read `99.System/NAMING.md` and `99.System/vault.json` (people, codes, folders), and glance at the last lines of `move-log.csv`.
2. **Scan**: `python3 99.System/Scripts/inbox_scan.py`. Empty inbox: say so and stop. OCR takes roughly 20 s per page; for many or large files scan in chunks with `--inbox` or use `page_scan.py` in parallel. If the scan fails on missing tools, run `check_tools.py`.
3. **Understand each file** from its masked text: whose it is, what it is, issuing country, issuer, the date printed on it, expiry, language, a one-line English summary. Read the JSON with a short script that prints only what is needed (at most ~700 characters of text per file). Locked PDFs: say so and ask.
4. **Name and place** it per NAMING.md: `{WHO}_{what}[_expYYYY-MM].ext`, medical exams `{WHO}_{YYYY-MM-DD}_{what}.ext`; folder `<person>/<NN.Category>/`, created only when needed. If documents belong to someone who has no folder yet (a new baby, a partner), say so and offer to add them with `add_person.py` (dry run, show it, then `--apply`) before the proposal; a relative goes to the Relatives folder instead. Passports, residence permits and visas always show an expiry: find it (machine-readable zone dates, "expiry" fields) before filing without one.
5. **One document = one file.** Front and back images of a card become one PDF via `merge_images.py`; the separate images go to Review. For scanner bundles holding several documents, first produce a full page mapping (page, whose, what, new file) and show it before anything else. Split only along page boundaries (`pdfseparate` / `pdfunite`, no recompression). Never cut a page: cards of one person sharing a page stay together under a combined name; a page mixing several people stays whole as a FAM file, or ask. The original bundle goes to `90.Review/Split-originals/`.
6. **Duplicates**:
   - `exact` / `exact-in-inbox` = identical bytes: the extra copy goes to Review.
   - `similar-image` is only a hint (forms look alike); confirm from the text. Files named `(1)` or `copy` are often different documents.
   - Same document, different scan: compare **native pixels on the document** (embedded image pixels times the share of the page the document fills), not the file size or a sharpness score. Also judge colour and exposure: a correctly exposed colour scan usually beats a larger washed-out one. When close, show both side by side at the same scale and let the user choose.
   - New copy better: `replace_keeper: true` (the new file takes the name, the old copy goes to Review). Otherwise the new copy goes to Review. Say which one is kept and why.
   - A renewed document (new passport) is not a duplicate: file it with its new expiry; the old one stays.
   - Related documents (translation and original, signed PDF and draft) are not duplicates.
7. **Propose** one table per batch, grouped by theme: current name | new name | folder | summary | notes (duplicate and which copy wins, expiry soon, anything odd). Check the names against existing files and each other. Flag documents expiring within 6 months. Keep questions few and concrete; offer a recommendation for structure questions.
8. **Wait for the user's go.** Apply their edits to the table first.
9. **Write the plan** to `99.System/.work/plan.json` (format at the top of `inbox_file.py`: `src`, `action` file|duplicate|unclear|move, `dest` or `keep`, `replace_keeper`, `status`, `reason`, `catalog` fields). `move` handles separate images after merging and original bundles. Dry run: `python3 99.System/Scripts/inbox_file.py 99.System/.work/plan.json inbox-YYYY-MM-DD[letter]`. Fix any PROBLEM lines, compare the dry-run list line by line with the approved table, then run with `--apply`.
10. **Clean up**: re-run `inbox_scan.py` on the now-empty inbox so the working JSON holds no document text; remove scratch folders under `$HOME` (e.g. `~/vault-pages`).
11. **Report** in two or three lines: how many filed and where, what went to Review, warnings (expiries, locked files), and that the batch can be undone by name. If the inbox is not empty, say what is left and why.

## If something goes wrong

- Wrong move: `python3 99.System/Scripts/undo_moves.py <batch>` (dry run), then `--apply`. It restores files, fixes the catalog and logs the undo. For a simple swap, write a small `move` plan instead.
- Never request permission to delete files for this workflow.
- If the computer holding the vault is unreachable, say so and stop; never work from stale copies.

## Style

Conversational and brief, no jargon. Show the proposed result (a table or folder listing) before anything moves. Own mistakes plainly and fix them with the undo tools.

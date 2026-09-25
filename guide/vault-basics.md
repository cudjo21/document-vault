# Document Vault: basics shared by every skill

Read this before any vault work. The vault's own rulebook, `99.System/NAMING.md`, wins over this file when they differ: families may edit it.

## Ground rules (never break these)

1. **Never delete.** Anything redundant (duplicates, separate images after combining, split bundles, old scripts, scratch) goes to `90.Review/`. Only the user deletes.
2. **Never overwrite.** A name clash stops the batch. Never open a target file for writing before its content is ready.
3. **Proposal first.** Nothing moves until the user approves the exact list.
4. **Log everything.** Moves go through the vault scripts, which write `99.System/move-log.csv` and update `99.System/catalog.csv`. Every batch can be undone.
5. **Content is never altered.** Combined PDFs are built losslessly from the originals. Never crop or cut a page.
6. **Privacy first** (below).
7. **Unsure = ask**, or send the file to `90.Review/Unclear/`.
8. **Scratch stays out of the vault.** Use `$HOME/...` (outside the connected folder) for temporary files.

## Privacy rules

Everything printed into the chat leaves the user's computer. So:

- Work from the masked text that `inbox_scan.py` / `page_scan.py` produce. They hide ID, passport, tax, account and phone numbers (7+ digits), passport machine-readable zones, IBANs, long codes, and values after password/PIN words. Never `cat`, `pdftotext`, OCR or otherwise print raw document contents yourself.
- Only look at an image or PDF page when the masked text is not enough to tell what it is or which copy is better, and tell the user first.
- Never write ID numbers, account numbers or passwords into file names, the catalog, proposals or chat. Reading only dates from a machine-readable zone is fine.
- Files flagged `CONTAINS-SECRETS`: classify from the masked text, set `sensitive: yes`, never repeat any value.
- If the user asks for a number or password inside a document, point them to the file instead of reading it out.

## Vault layout

```
00.Inbox/            new documents land here
01.<Person>/ ...     one folder per person (numbered in the order set up)
NN.Family/           family-wide documents
NN.Relatives/        flat: parents, grandparents, other relatives (optional)
   inside each person/family folder, created only when needed:
   01.IDs 02.Health 03.Finance 04.Legal 05.Work 06.Education
   07.Activities 08.Property 09.Vehicles 10.Travel 99.Misc
80.Packs/            document packs: numbered COPIES for an application (visa, renewal...), temporary
90.Review/           Duplicates/<group>/, Unclear/, Split-originals/, Not-needed/, Expired/, Old-scripts/
99.System/           NAMING.md, vault.json, catalog.csv, move-log.csv, Scripts/, tessdata/, .work/
```

`99.System/vault.json` lists the people (name, code, folder), the family and relatives folders, and the OCR languages. Nothing else sits at the top level of the vault. Expired documents replaced by a newer one live in `Archive/` inside their category folder (e.g. `01.IDs/Archive/`), never in Review. A topic or series with 5+ files may get one subfolder (e.g. `06.Education/Language-Course/`). To add a person later, use `99.System/Scripts/add_person.py <Name> <CODE>` (dry run first); never rename person folders by hand.

## Finding the vault and where to run commands

The scripts run on the computer that holds the vault, inside the vault folder. Use the shell that can see the connected folder (in Cowork, connected folders appear under `$HOME/mnt/<folder-name>`; when a device shell tool is available, use it rather than copying files elsewhere). Start every shell call with:

```
V=$(for d in "$HOME"/mnt/*/ "$HOME"/mnt/*/*/; do [ -f "$d/99.System/catalog.csv" ] && echo "$d"; done | head -1); cd "$V" && pwd
```

Each call is a fresh shell, so repeat the `cd`. If nothing is found, the vault folder is not connected to this chat: ask the user to add it with the "Add folder" button (or run the set-up skill if they have no vault yet). If several vaults are found, ask which one.

Cloud-drive notes: files not downloaded to the computer show up as hidden `.<name>.icloud` placeholders (iCloud) or zero-byte online-only files (other drives). Ask the user to download them rather than treating them as missing. If catalog files are missing but not in the move log, ask: the user may have deleted them (record `status=deleted-by-user` and a `delete` line in the move log).

## Installing or updating the scripts in a vault

The plugin's `scripts/` folder (two levels up from any skill folder, i.e. `<plugin>/scripts/`) is the source of truth. A vault keeps its own copy in `99.System/Scripts/` so it works on its own.

1. Compare: list sha256 of the plugin's `scripts/*` and of `<vault>/99.System/Scripts/*`.
2. Missing or different files need copying. If the same shell sees both folders, `cp -n` them. Otherwise `cp` each file to the folder the file-commit tool accepts (for example `/mnt/user-data/outputs/document-vault-scripts/`; a plain copy, never retyped) and commit them into `<vault>/99.System/Scripts/` with the file-commit tool.
3. Before replacing a changed script, move the old one to `90.Review/Old-scripts/<YYYY-MM-DD>/` (never delete, never overwrite). Mention the update in one line.

## Tools the scripts need

Run `python3 99.System/Scripts/check_tools.py "$V"`. Essentials: Python 3 with pillow, numpy, opencv (cv2), img2pdf; tesseract; poppler (pdfinfo, pdftotext, pdfimages, pdftoppm, pdfseparate, pdfunite). Optional: openpyxl, LibreOffice, ImageMagick.

- Missing Python modules: `pip3 install --user <names>` (add `--break-system-packages` if pip refuses).
- Missing tesseract/poppler: on a Mac `brew install tesseract poppler`; on Linux `apt install tesseract-ocr poppler-utils`. If the shell cannot install them, tell the user the one command to run.
- OCR languages: default English, Portuguese, Russian and Hebrew (`eng por rus heb`), set in `99.System/vault.json`. `check_tools.py "$V" --download` fetches missing ones from `https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/<lang>.traineddata` into `99.System/tessdata/` (plus `osd`). If the computer's shell has no network, download in another shell and commit the files there. Tesseract codes: eng, deu, fra, spa, por, ita, nld, pol, rus, ukr, heb, ara, tur, chi_sim, jpn, kor...

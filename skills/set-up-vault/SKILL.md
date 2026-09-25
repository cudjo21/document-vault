---
name: set-up-vault
description: Creates a new family Document Vault in an empty folder - people, folder structure, naming rules, catalog and scripts. Use when the user says "set up a document vault", "create my document vault", "organize my family documents from scratch" or has no vault yet.
---

# Set up a Document Vault

Create a new, empty vault the family will fill through the inbox. First read `../../guide/vault-basics.md` (relative to this skill's folder) for the ground rules, layout and how to run commands.

## 1. Ask the few things that shape the vault

Treat the user as new to the vault. Ask from scratch: do not prefill names, codes or folders from memory, earlier chats or other vaults you can see, and do not mention an existing vault unless the user picks its folder.

**First message (plain text, no question tool):** in three or four sentences say what the vault is (one folder, one sub-folder per person, an Inbox Claude files from after the user approves, nothing ever deleted), then ask: *"Who should have their own folder? First names, adults first, then children. Example: Alex, Maria, Sam."* Names need free text, so do not use the question tool for this.

**Then one AskUserQuestion round with three questions:**

- **Relatives?** "Also keep documents of parents, grandparents or other relatives?" Yes, one shared Relatives folder (recommended) / No.
- **Languages?** "Which languages are your documents in? (so scans can be read)" English, Portuguese, Russian and Hebrew (the default) / English only / Default plus another language (they name it). Map to tesseract codes (Spanish spa, German deu, French fra, Italian ita, Ukrainian ukr, Arabic ara...). Always keep English.
- **Where?** "Where should the vault live?" A new folder in a cloud drive: iCloud Drive, Google Drive, Dropbox or OneDrive (recommended: backed up, on your phone, shareable with a partner) / A folder on this computer only. In the option text, say how: create an empty folder named `DocumentVault` there and add it to this chat with the "Add folder" button.

Then propose the person codes in one line, from initials (2 to 4 capital letters, unique, never `FAM`; a single first name can use its first three letters, e.g. Sam = SAM), and say they appear at the start of every file name. Accept changes, then continue once the empty folder is connected. If it isn't connected yet, wait for it.

## 2. Check the target folder

- Find the connected folder the user chose. If it already contains `99.System/catalog.csv`, a vault exists: stop and offer the vault check-up instead.
- If the folder already holds documents, do not reorganize them in place. Tell the user they will go through the inbox later, and create the vault in a new empty subfolder (e.g. `DocumentVault`) or ask them for an empty folder.

## 3. Install the scripts

Copy every file from the plugin's `scripts/` folder into `<vault>/99.System/Scripts/` (see "Installing or updating the scripts" in the basics guide). `NAMING.template.md` goes along with them.

## 4. Create the vault

Write the config outside the vault, e.g. `$HOME/vault-setup.json`:

```json
{"family_name": "Smith",
 "people": [{"name": "Alex", "code": "AS"}, {"name": "Maria", "code": "MS"}, {"name": "Sam", "code": "SAM"}],
 "relatives": true,
 "ocr_languages": ["eng", "por", "rus", "heb"]}
```

Folder names use the first name as typed, ASCII letters only (drop accents). Then:

```
cd "<vault>" && python3 99.System/Scripts/create_vault.py . "$HOME/vault-setup.json"          # dry run
```

Show the user the resulting folder tree in a code block. After a yes, run again with `--apply`. It never overwrites and refuses if a vault already exists.

## 5. Make the tools work

Run `python3 99.System/Scripts/check_tools.py . --download` (fetches the OCR language files into `99.System/tessdata/`) and install missing modules as the basics guide describes. Tell the user plainly about anything they must install themselves (one command). Re-run until it says ALL ESSENTIALS PRESENT.

## 6. Hand over

Tell the user, in a few lines:

- The vault is ready; `99.System/NAMING.md` holds the rules and can be edited.
- To add documents: drop them into `00.Inbox` (scans, phone photos, PDFs, any language) and say "process my inbox". Every batch is shown as a proposal before anything moves, and can be undone.
- For existing piles of documents: **copy** (not move) them into the inbox in batches of 20 to 40, so the originals stay safe until the vault is trusted.
- Nothing is ever deleted: extra copies and unclear files land in `90.Review` for them to check.
- If the vault lives in a cloud drive, they can share the folder with their partner; the partner connects the same folder in their own Claude to use it.
- Suggest a periodic "vault check-up" for expiring documents.
- iPhone users can save straight from the Share button: offer the shortcut https://www.icloud.com/shortcuts/83377abbb92149ab889a9f1d1e554f1b (tap Add Shortcut, then check once that both Save File steps point to this vault's `00.Inbox`, and pick it if not). Android: share to the cloud drive's `00.Inbox` folder.

Finally remove the scratch config `$HOME/vault-setup.json` (it is outside the vault).

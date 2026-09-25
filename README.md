# Document Vault

A Claude plugin that turns a messy pile of family paperwork into one tidy folder where every document has a clear name and a clear place. You drop new files into an Inbox; Claude reads each one, works out whose it is and what it is, proposes a name and a folder, and files it only after you say go. Nothing is ever deleted: duplicates, weaker scans and anything unclear go to a Review folder for you to decide.

Built for the papers a family actually has: passports and ID cards from several countries, residence permits, visas, payslips, tax statements, leases, medical results, certificates, often in several languages. It also tells you what matters in them, like a passport that expires soon.

When you apply for something (a visa, a residence permit renewal, a mortgage), paste the list of required documents and Claude gathers them into a ready pack: copies in the list's order, per person, with a checklist of what's still missing.

On an iPhone, one tap in the Share menu (**Share → Document Vault**) drops a photo, PDF or email attachment straight into the Inbox.

## Install

**What you need:** a paid Claude plan (Pro, Max, Team or Enterprise) and the Claude desktop app on a Mac or PC.

1. In the Claude desktop app, open **Cowork**, then **Customize** in the left sidebar, then the **Plugins** tab.
2. Under **Personal plugins**, click **+** and choose **Add marketplace**.
3. Enter `cudjo21/document-vault` and confirm.
4. Find **Document Vault** in the list and click **Install**.

**Start your vault:**

5. Create an empty folder called `DocumentVault`, ideally in iCloud Drive, Google Drive, Dropbox or OneDrive (backed up, reachable from your phone, shareable with a partner).
6. Start a new Cowork task, add that folder with the **Add folder** button, and say **"set up a document vault"**. Claude asks who's in the family and which languages your documents are in, then builds the vault.
7. Drop documents into `00.Inbox` (or use the [iPhone shortcut](#capture-from-your-phone-iphone)) and say **"process my inbox"**.

**Updates:** when a new version is out, click **Update** next to the Document Vault marketplace on the Plugins page.

**Other ways:** upload `document-vault.plugin` from the Releases page on the same Plugins page (no automatic updates), or in Claude Code run `/plugin marketplace add cudjo21/document-vault` and then `/plugin install document-vault@document-vault`.

## Skills

The plugin has five skills. You don't need to call them by name: just say what you want in plain words and Claude picks the right one.

| Skill | Say something like | You get |
|---|---|---|
| Set up a vault | "Set up a document vault" | A ready, empty vault for your family |
| Process inbox | "Process my inbox" | New documents named, filed and catalogued |
| Vault check-up | "Check my vault" | Expiring documents and anything out of place |
| Find a document | "Where is Maria's passport?" | The file, and the facts about it |
| Prepare a pack | "We're applying for a US visa, here's the list" | A folder of copies in the list's order, per person, with a checklist |

### 1. Set up a vault (`set-up-vault`)

Use it once, at the start.

- **Explains the vault in a few lines, then asks:** who gets their own folder (you type the first names; it suggests a short code for each, like AS for Alex Smith), whether you want a Relatives folder, which languages your documents are in, and where to keep the vault (a cloud drive folder is recommended so a partner can share it). It starts from scratch: it doesn't fill anything in from other chats or other vaults.
- **Shows the folder tree** it is about to create and waits for your yes.
- **Creates** the Inbox, one folder per person, Family, Relatives, Review and System folders, the naming rulebook (`NAMING.md`), an empty catalog and move log, and copies the scripts into the vault so it works on its own.
- **Checks your computer** for the tools it needs, downloads the text-recognition languages (English, Portuguese, Russian and Hebrew by default; any others on request), and tells you the one command to run if something is missing.
- **Refuses to touch** a folder that already holds a vault, and never reorganizes existing files in place: your old documents go through the Inbox like everything else.
- **Hands over** with how to add documents, and offers the iPhone shortcut.

### 2. Process inbox (`process-inbox`)

The one you'll use most. Drop files into `00.Inbox`, then say "process my inbox".

- **Reads every file:** PDFs, phone photos (turned upright automatically, however the phone was held), scanner bundles, Word and Excel files, saved web pages, in any of your languages. Text is masked (ID and account numbers, passwords hidden) before anything reaches the chat. Password-protected PDFs are flagged, and Claude identifies them from their name and your answer instead.
- **Works out** whose document it is, what it is, the issuing country, the date on it and the expiry.
- **Handles the messy cases:** combines front and back of a card into one PDF; splits a scanner bundle into separate documents along page boundaries (showing you a page-by-page map first); spots exact and near duplicates and keeps the best copy, judged by the real pixels on the document and how well it is exposed.
- **Proposes one table:** current name, new name, folder, a one-line summary, and notes such as "duplicate, kept copy is sharper" or "expires in 4 months". You edit it in plain words ("that's Maria's, not mine").
- **Files after your go:** moves and renames, sends extras to `90.Review`, updates the catalog and logs every move under a batch name. "Undo the last batch" puts everything back.
- **New family member?** If documents belong to someone without a folder yet (a new baby, a new partner), Claude offers to add them first: they get the next number and Family and Relatives move up one, all logged and undoable. You can also just say "add Leo to the vault".

### 3. Vault check-up (`vault-check-up`)

Run it every month or two, or before a trip. It only reads, until you approve a fix.

- **Expiring documents:** passports, permits and visas expired or expiring in the next 6 months (or any horizon you ask for), per person. Handy because many countries want 6 months of passport validity to enter.
- **Out-of-place files:** documents added to the library by hand and missing from the catalog, catalog entries whose file has gone (or is only in the cloud, not downloaded), names that break the rules.
- **Expired documents:** when a newer one exists (a renewed passport), it suggests moving the old one to an `Archive` folder in the same category. Expired documents are history, not rubbish: forms often ask for previous passports. When there's no replacement, it asks: say you're renewing, and it just reminds you until the new one is filed.
- **Tidy suggestions:** when 5 or more files of one topic pile up in a folder (a course, an assessment, a property), it suggests a subfolder for them, like `06.Education/Language-Course/`.
- **What's waiting for you** in `90.Review` (duplicates, unclear files) and the Inbox.
- **Fixes through the same logged process** as the inbox, so they can be undone. It can also set itself up as a monthly scheduled task.

### 4. Find a document (`find-document`)

Ask anything about what's in the vault.

- "Where is the flat lease?", "Show me all car documents", "What does Sam have in Education?"
- "When does Maria's residence permit expire?", "Which passports expire this year?"
- **Answers from the catalog:** folder and file name, expiry and issue dates, issuer. It opens a file only if the catalog doesn't have the answer, and still never reads out ID, account or policy numbers or passwords.
- **Sends you the file** in the chat only when you ask, since that copies it off your computer.

### 5. Prepare a pack (`prepare-pack`)

For any application that asks for a list of documents: a visa, a residence permit renewal, citizenship, a mortgage, a school or a new job.

- **Paste the list** and say who is applying: "We're applying for US visas for me and Maria, here's what the consulate wants: ..."
- **Claude matches every item** to the vault and shows a table first: what was found, what is missing (photos, forms), and what needs a look: a passport that expires less than 6 months after the trip, bank statements older than the list allows, a translation that may be needed.
- **Several passports?** If someone has more than one (two nationalities, or an old and a new one), Claude asks which to include instead of guessing, and recommends one.
- **Asks if you want combined PDFs:** separate files only, one PDF per person, or one for the whole family (handy for online portals). Lossless. Password-protected PDFs (payslips often are) and saved web pages can't be merged: they stay as separate files next to the combined PDF, and Claude tells you before building. If a portal needs one single file, open the protected PDF with its password, export an unlocked copy and drop it into the Inbox.
- **Builds the pack** in `80.Packs/<name>/` after your go: copies only, numbered in the list's order (`01_`, `02_`...), one folder per person plus `00.Family`, and a `checklist.md` with a to-do list. The originals never move.
- **When you're done,** say "archive the pack": the whole pack moves to `90.Review/Packs` for you to delete, logged and undoable.

## Capture from your phone (iPhone)

Save documents into the vault's Inbox straight from the Share button in Photos, Files, Mail, WhatsApp or Safari.

1. On your iPhone, open **[Add the Document Vault shortcut](https://www.icloud.com/shortcuts/83377abbb92149ab889a9f1d1e554f1b)** and tap **Add Shortcut**.
2. Open the shortcut once in the Shortcuts app and check that both **Save File** steps point to your vault's **00.Inbox** folder; if your vault lives somewhere else, tap the folder and pick yours.
3. From now on: **Share → Document Vault**. Several items at once are fine (front and back of a card). Then say "process my inbox" on your computer.

The shortcut saves PDFs and files unchanged and converts iPhone photos (HEIC) to full-quality JPEG, so front and back scans can be combined into one PDF. It only contains these steps and a folder name; it gives nobody access to your vault. On Android, share to Google Drive or Dropbox and pick the vault's `00.Inbox` folder instead.

## Requirements

- Claude desktop app (Cowork) with the vault folder connected.
- On the computer holding the vault: Python 3 with pillow, numpy, opencv and img2pdf; tesseract (text recognition); poppler (PDF tools). The set-up skill checks all of this and tells you the one command to run if something is missing (on a Mac: `brew install tesseract poppler`).
- Text-recognition languages: English, Portuguese, Russian and Hebrew by default, downloaded into the vault during set-up. Add or remove languages any time by asking Claude.

## How it works

```
You drop files in 00.Inbox → Claude scans and reads them → proposal table (name, folder, notes)
   → you edit or say go → filed + logged, catalog updated
   duplicates and unclear files → 90.Review
```

| Step | Claude does | You do |
|---|---|---|
| 1. Collect | nothing | Drop scans, photos, PDFs, downloads into `00.Inbox`, or Share → Document Vault on your iPhone |
| 2. Scan | Fingerprints each file, reads the text (OCR in your languages), measures scan quality, checks it against everything already in the vault | Say "process my inbox" |
| 3. Understand | Works out whose it is, what it is, the issuing country, the date on it, the expiry; splits scanner bundles into single documents | Answer the odd question ("whose photo is this?") |
| 4. Propose | Shows one table: current name, new name, folder, and notes like "duplicate, the kept copy is sharper" or "expires in 4 months" | Check it, change anything, then say go |
| 5. File | Moves and renames, combines front and back into one PDF, sends extras to Review, logs every step, updates the catalog | Nothing |
| 6. Review | Leaves a short `comparison.md` in each duplicate group | Delete what you don't need from `90.Review`, whenever you like |

## The rules

1. **Nothing is ever deleted by Claude.** Redundant or doubtful files go to `90.Review`. Only you delete. Packs for applications are copies; the originals never move.
2. **Nothing is ever overwritten.** If a new name already exists, the batch stops.
3. **Proposal first, then action.** Nothing moves until you approve the exact list.
4. **Everything is logged and reversible.** Every move is recorded with its old and new place and a fingerprint of the file; any batch can be undone.
5. **Content is never changed.** Combined PDFs are built from the original images without any loss of quality, and scanned pages are never cut apart.
6. **One document, one file.** Front and back of a card become one PDF. Different documents, old and new versions, and visas stay separate.
7. **The best copy stays.** Copies are compared by the real pixels on the document and by how well exposed it is, not by file size. When it's close, you choose.
8. **Private by default.** ID numbers, account numbers and passwords are hidden before anything reaches the conversation.
9. **When unsure, ask.** A file that can't be identified with confidence goes to `90.Review/Unclear` with a note.

## Where to keep it

Create the vault in a cloud drive folder (iCloud Drive, Google Drive, Dropbox or OneDrive):

- **Share it with your partner.** Share the one `DocumentVault` folder and you both see the same, always up-to-date documents. Either of you can drop files into the Inbox; one person processes it with Claude at a time.
- **Reach it from your phone** at a border or a clinic.
- **Survive a lost laptop.**

Two cautions: a cloud drive syncs mistakes too, so keep a separate backup (e.g. Time Machine); and keep the vault folder always downloaded on the computer that processes the Inbox, so Claude can read every file.

## Folder template

Example family (made up): two partners, Alex and Maria, two children, Sam and Emma, plus relatives.

```
DocumentVault/                              (in a cloud drive, shared with your partner)
├── 00.Inbox/                               drop new files here
├── 01.Alex/
│   ├── 01.IDs/
│   │   ├── Archive/AS_passport-GBR_exp2020-06.pdf    (expired, replaced by the new one)
│   │   ├── AS_driving-licence-GBR.pdf
│   │   ├── AS_passport-GBR_exp2030-06.pdf
│   │   ├── AS_residence-permit-ESP_exp2027-03.pdf
│   │   └── AS_visa-USA_exp2033-09.pdf
│   ├── 02.Health/
│   │   ├── AS_2025-04-12_blood-test.pdf
│   │   └── AS_insurance-card.pdf
│   ├── 03.Finance/
│   │   ├── Payslips/2025/AS_payslip-2025-05.pdf
│   │   └── AS_tax-return-2024.pdf
│   ├── 06.Education/Language-Course/            (5+ files on one topic get a subfolder)
│   └── 09.Vehicles/AS_vehicle-registration.pdf
├── 02.Maria/
│   └── 01.IDs/MS_passport-ESP_exp2031-02.pdf …
├── 03.Sam/
│   ├── 01.IDs/SAM_passport-GBR_exp2029-08.pdf
│   └── 06.Education/SAM_school-report-2025.pdf
├── 04.Emma/
│   └── 02.Health/EMA_2025-01-20_vaccination-record.pdf
├── 05.Family/
│   ├── 01.IDs/Archive/FAM_residence-permits-ESP_exp2024-03.pdf
│   ├── 04.Legal/FAM_marriage-certificate-GBR.pdf
│   └── 08.Property/Home-Madrid/FAM_lease-signed.pdf
├── 06.Relatives/
│   ├── AS-MOM_passport-GBR_exp2029-11.pdf
│   └── MS-DAD_birth-certificate-ESP.pdf
├── 80.Packs/                               document packs for applications (copies, temporary)
├── 90.Review/                              yours to clear
│   ├── Duplicates/AS_passport-GBR_exp2030-06/   (weaker copies + comparison.md)
│   ├── Unclear/
│   ├── Packs/                              (finished packs, archived)
│   └── Split-originals/
└── 99.System/                              don't touch
    ├── NAMING.md   vault.json   catalog.csv   move-log.csv
    ├── Scripts/
    └── tessdata/
```

Categories are the same for every person and created only when needed: 01.IDs, 02.Health, 03.Finance, 04.Legal, 05.Work, 06.Education, 07.Activities, 08.Property, 09.Vehicles, 10.Travel, 99.Misc.

## Names

```
{WHO}_{what}[_expYYYY-MM].pdf
{WHO}_{YYYY-MM-DD}_{what}.pdf        medical exams and test results
```

| Part | Rule | Example |
|---|---|---|
| WHO | short person code, so the file is still recognisable when emailed | AS, MS, SAM, FAM, AS-MOM |
| what | 1 to 5 English words: kind, then country, then detail | passport-GBR, birth-certificate-ESP-translation-ENG |
| country | ISO 3-letter code, only when it matters | GBR, ESP, USA |
| expiry | month the document expires; passports, residence permits and visas only | _exp2030-06 |
| exam date | date of the test, first, so results sort by time | AS_2025-04-12_blood-test |
| period | only when it tells files apart | payslip-2025-05 |

No spaces, no non-Latin letters, no sort numbers, no `_old`/`_new`. The original title and all dates stay in the catalog. The full rulebook is `99.System/NAMING.md` in each vault; edit it through Claude if your family wants different rules.

## Privacy

Your files are sorted on your computer; only a masked summary of what's in them reaches the conversation.

| Stays on your computer | Reaches Claude (the chat) |
|---|---|
| All files, the catalog, the move log | File names, page counts, scan quality |
| Full document text | Masked text: names, dates, amounts and titles, with ID, passport, tax, account and phone numbers replaced by "[number hidden]" |
| Passwords and PINs | "[hidden]"; files with credentials are flagged sensitive |
| Passport machine-readable lines | "[machine-readable zone hidden]" |

Images are looked at directly only when the text isn't enough, and Claude says so first. What reaches the chat is handled under Anthropic's privacy terms for your account; check your privacy settings and delete conversations you no longer need. Keep real passwords in a password manager, not in the vault.

## Good practice and limits

- Keep a separate backup; a cloud drive syncs mistakes too.
- Scan at 300 dpi, in colour, with the card filling the frame.
- Clear `90.Review` every few weeks. It's a waiting room, not an archive.
- Archive a pack once the application is done ("archive the pack"), so old copies don't pile up.
- Avoid renaming or moving library files by hand; if you do, run a check-up so the catalog stays right.
- OCR struggles with handwriting, faded stamps and small cards; Claude will ask or look at the image rather than guess.
- Password-protected PDFs can't be read; you'll be asked what they are.

## Troubleshooting

| Problem | What to do |
|---|---|
| Claude says no vault was found | The vault folder isn't connected to this task. Add it with the **Add folder** button and ask again. |
| "MISSING tesseract" or "MISSING pdfinfo" during set-up | Install the tools once: on a Mac `brew install tesseract poppler`, on Linux `sudo apt install tesseract-ocr poppler-utils`. Then say "check the vault tools". |
| A language isn't read (text comes out as gibberish) | Say "add Spanish to the vault languages" (or whichever). Claude downloads the language file and updates `99.System/vault.json`. |
| A file seems missing | Cloud drives can keep files online only. Right-click the vault folder and choose **Keep Downloaded** (iCloud) or **Available offline**, then run a check-up. |
| A batch went wrong | Say "undo the last batch". Every move is logged and reversible. |
| Something was misfiled by hand | Run "check my vault": it lists files missing from the catalog and names that break the rules, and proposes fixes. |
| Password-protected PDF | It can't be read; Claude asks you what it is and files it by your answer. |
| The iPhone shortcut saves somewhere else | Open the shortcut in the Shortcuts app, tap the folder in both **Save File** steps and pick your vault's `00.Inbox`. |

## Support and privacy

- Questions, bugs and ideas: [GitHub issues](https://github.com/cudjo21/document-vault/issues).
- Security or privacy problems: see [SECURITY.md](SECURITY.md) (please don't post real document contents in public issues).
- Privacy policy: [PRIVACY.md](PRIVACY.md). In short: the plugin collects nothing and has no server; your documents stay in your folder.

## What's inside

```
.claude-plugin/     plugin.json, marketplace.json
skills/            set-up-vault, process-inbox, vault-check-up, find-document, prepare-pack
guide/             vault-basics.md (shared rules for all skills)
scripts/           copied into each vault's 99.System/Scripts/
   create_vault.py  add_person.py  make_pack.py  check_tools.py  inbox_scan.py  page_scan.py  merge_images.py
   inbox_file.py  undo_moves.py  audit_duplicates.py  vault_check.py  find_docs.py
   NAMING.template.md
PRIVACY.md  SECURITY.md  CHANGELOG.md  LICENSE
```

Author: Ilya. License: MIT.

# Changelog

## 0.5.0 (25 September 2026)
- Check-up: expired documents that were replaced by a newer one are suggested for an `Archive` folder in the same category; expired ones without a replacement trigger a question (renewing or archive?).
- Check-up: tidy suggestions, a subfolder when 5 or more files of one topic or series sit in one folder.
- iPhone shortcut: save photos, PDFs and files into the Inbox from the Share button (link in the README and offered at set-up). Converts HEIC photos to full-quality JPEG.
- Packs: "archive the pack" moves a finished pack to `90.Review/Packs` (logged, undoable).
- Packs: password-protected PDFs are copied as usual but left out of combined PDFs. Claude says so before building (in the combined-PDF question and the plan table) and explains how to make an unlocked copy if a portal needs one file.
- Inbox scan: password-protected PDFs are now flagged as locked.
- Inbox scan: phone photos taken sideways or upside down are turned upright before reading (they came out as unreadable text before).

## 0.4.0 (25 September 2026)
- New skill **Prepare a pack**: paste the list of documents an application asks for (visa, residence permit renewal, mortgage, school...), and Claude matches it to the vault, asks which passport to use when someone has several, flags expiring or outdated documents, and builds `80.Packs/<name>/` with numbered copies per person and a checklist.
- Optional combined PDF per person or for the whole family, in list order, lossless.
- Check-up lists open packs and no longer counts their copies as duplicates.

## 0.3.1 (24 September 2026)
- Privacy policy, security contact, troubleshooting and support sections.

## 0.3.0 (24 September 2026)
- Masking fix: long numbers next to "/" or "." (e.g. insurance member numbers) are now hidden; better IBAN and password detection.
- Saved web pages (.html) are read as text, without page code.
- Add a family member to an existing vault (logged and undoable).
- Set-up questions written for new users.

## 0.2.0 (24 September 2026)
- Default text-recognition languages: English, Portuguese, Russian, Hebrew; language files download during set-up.

## 0.1.0 (24 September 2026)
- First version: set up a vault, process the inbox, vault check-up, find a document.

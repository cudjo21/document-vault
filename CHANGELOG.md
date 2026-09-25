# Changelog

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

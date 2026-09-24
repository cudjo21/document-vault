# Privacy policy: Document Vault plugin

Last updated: 24 September 2026

## Short version

The Document Vault plugin does not collect, send or store any of your data anywhere. It has no server, no account, no analytics and no tracking. Your documents stay in the folder you choose, on your own computer or your own cloud drive.

## What the plugin does with your files

- The plugin is a set of instructions for Claude plus small Python scripts. The scripts run on your computer, inside the vault folder you connect, and only when you ask Claude to do something (set up, process the inbox, check-up, find).
- The scripts read the files you put in the vault to work out what they are, and move and rename them after you approve. They never delete anything.
- Everything they record (the catalog `99.System/catalog.csv`, the move log `99.System/move-log.csv`, settings `99.System/vault.json`) is written only into your vault folder.
- Before any document text is shown to Claude, the scan script hides ID, passport, tax, account, card and phone numbers, IBANs, passport machine-readable lines and anything after words like password or PIN.

## What reaches Claude

Claude sees what the scripts print in your conversation: file names, page counts, scan quality and the masked text described above. Claude looks at an image of a document only when the text is not enough, and says so first. This content is handled by Anthropic under the terms and privacy settings of your own Claude account, the same as anything else you share in a conversation. The plugin author receives nothing.

## Network use

The plugin makes one kind of network request: during set-up (or when you add a language) it downloads open-source OCR language files from the public tesseract-ocr project on GitHub (`raw.githubusercontent.com/tesseract-ocr/tessdata_fast`). Nothing about you or your documents is sent in that request. If a tool such as tesseract or poppler is missing, Claude tells you the command to install it from your usual package manager.

## Retention and deletion

All data stays in your vault folder for as long as you keep it. To remove everything, delete the vault folder. To remove the plugin, uninstall it in Claude (Customize → Plugins → Document Vault → Uninstall); your vault folder is not touched.

## Contact

Questions or concerns: open an issue at https://github.com/cudjo21/document-vault/issues. For a security problem, see SECURITY.md.

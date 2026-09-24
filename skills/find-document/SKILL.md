---
name: find-document
description: Finds documents in the family Document Vault and answers questions about them from the catalog - where a file is, when something expires, which documents a person has. Use for "find my passport", "where is the lease", "when does Maria's residence permit expire", "show me all insurance documents" and similar.
---

# Find a document

Answer from the vault catalog; open files only when needed. First read `../../guide/vault-basics.md` (relative to this skill's folder), especially the privacy rules.

## Steps

1. **Find the vault**; read `99.System/vault.json` to map names to person codes (FAM = family-wide; relatives use `<CODE>-MOM`, `-DAD`, `-REL`). Make sure `find_docs.py` exists in `99.System/Scripts/` (install it per the basics guide if not).
2. **Translate the question** into a search, for example:
   - "Maria's passport" → `python3 99.System/Scripts/find_docs.py passport --person MS`
   - "what expires this year" → `find_docs.py --expiring 12`
   - "the flat lease" → `find_docs.py lease`
   - "all car documents" → `find_docs.py --category vehicle` or words like `car insurance`
   Try synonyms and English words (names and summaries are in English); add `--all` to include Review items. Fall back to `find . -iname '*word*'` over the vault if the catalog has nothing.
3. **Answer** directly: the file's folder and name (as a clickable local-file link when the interface supports it), plus the relevant catalog facts (expiry, date, issuer). Several matches: a short list. None: say so and suggest checking the inbox or Review.
4. **Details inside a document** (an address, a policy period) that the catalog lacks: tell the user you would need to read the file, and read only masked text: for a PDF run `page_scan.py <pdf> 1 <pages>` and read its output in `~/vault-pages/`; for an image, copy it into a scratch folder under `$HOME` and run `inbox_scan.py --inbox <that folder>`, then run `inbox_scan.py` once more on the real inbox so the working file is reset. Remove the scratch afterwards. Never read out ID, account or policy numbers or passwords; point to the file instead.
5. **Sending the file** into the chat or attaching it to an email copies it off the computer: only when the user asks, and say so in one line.

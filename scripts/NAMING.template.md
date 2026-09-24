# Document Vault naming convention (v3.3, set up {{DATE}})

    {WHO}_{what}[_expYYYY-MM].ext
    {WHO}_{YYYY-MM-DD}_{what}.ext        medical exams and test results (exam date)

The folder says the category; the name says whose it is and what it is.
Category, document kind, issue and expiry dates are all recorded in 99.System/catalog.csv.
This file is the rulebook for the vault. Edit it if your family wants different rules;
Claude reads it at the start of every run and follows it.

## Fields

- WHO: person code, uppercase. Kept so a file is still identifiable when emailed or uploaded.
{{PEOPLE}}
  - FAM: family-wide (marriage certificate, home, shared insurance, grouped family scans)
  - Relatives (Relatives folder, flat): {CODE}-MOM, {CODE}-DAD for a person's parents;
    {CODE}-REL for anyone else (grandparents, aunts...), with the person's first name in "what"
- what: 1 to 5 English words, lowercase-kebab, ASCII only, in this order: kind, COUNTRY, qualifier
  - Kind first: passport, residence-permit, payslip, lease, invoice...
  - Then the issuing country as uppercase ISO 3166 alpha-3 (GBR, USA, DEU, ESP; USSR for Soviet documents),
    only when the document has one that matters
  - Then any qualifier: issuer, period, "translation-ENG", "internal", a first name...
  - passport-GBR, id-card-ESP, birth-certificate-ESP-translation-ENG, payslip-2025-05, invoice-acme
  - This keeps the same kind together and sorts it by country within the folder
- A period (year or year-month) goes in "what" only when it tells files apart: payslip-2025-05,
  tax-return-2024.
- _expYYYY-MM: expiry month, only for passports, residence permits and visas.
  The exact expiry day and the issue date are in the catalog.
- Medical exams (lab results, tests, imaging, doctor reports): the exam date goes right after WHO,
  so the Health folder sorts chronologically: AS_2025-10-06_blood-test.pdf.
  Insurance cards and policies in Health follow the normal pattern.
- Dates are always the date printed on the document, never the scan or file date.

## One document = one file

- Front and back of cards (IDs, permits, licences, vehicle papers), a passport photo page plus
  its extra pages, and any document photographed in several images are combined into ONE PDF
  (lossless, img2pdf; primary frame only for iPhone HDR photos). The separate images go to
  90.Review, not the library.
- Scanner bundles holding several documents are split along page boundaries only. A page is never
  cut into pieces: several cards of one person on one page stay together under a combined name;
  a page mixing several people stays whole as a FAM file. The original bundle goes to
  90.Review/Split-originals.
- Old and new versions of a document (an expired and a renewed passport) are separate files,
  told apart by their expiry.

## Rules

- `_` separates fields, `-` separates words. No spaces, no accents, no non-Latin letters in names.
  The original title and file name are kept in the catalog.
- No numbering for sort order, no _old/_new, no _p01 page numbers, no category codes in names.
- Extensions lowercase; .jpeg becomes .jpg.
- A true same-name clash goes to 90.Review, never overwritten.
- Keep names short; under 60 characters is typical.

## Examples (fictional family: Alex AS, Maria MS, Sam SAM)

- AS_passport-GBR_exp2030-06.pdf
- AS_residence-permit-ESP_exp2028-07.pdf        (front and back)
- AS_driving-licence-GBR.pdf
- AS_payslip-2025-05.pdf                          (in 03.Finance/Payslips/2025)
- AS_2025-10-06_blood-test.pdf                   (in 02.Health)
- MS_passport-ESP_exp2031-02.pdf
- MS_diploma-university-madrid.pdf
- SAM_birth-certificate-ESP-translation-ENG.pdf
- FAM_marriage-certificate-ESP.pdf
- FAM_home-insurance-policy.pdf
- AS-MOM_passport-GBR-helen_exp2029-04.pdf
- MS-REL_photo-grandmother-rosa.jpg

## Folders inside each person (create only when needed)

01.IDs  02.Health  03.Finance  04.Legal  05.Work  06.Education
07.Activities  08.Property  09.Vehicles  10.Travel  99.Misc

One extra subfolder level is fine when volume needs it (Payslips/2025, a property's own folder,
an Archive folder for grouped scans of expired documents).

## Catalog codes (99.System/catalog.csv, not used in names)

- category: ID, HLTH, FIN, LEG, WRK, EDU, ACT, PROP, VEH, TRV, MSC = folders 01.IDs ... 99.Misc
- doc_kind: PAS passport, RPR residence permit, VISA, NID ID card, DL driving licence,
  BRC birth certificate, MAR marriage certificate, PAY payslip, TAX tax document, INV invoice,
  LSE lease, INS insurance, POA power of attorney, DIP diploma, MED medical, and others as needed

## Choosing the best copy (duplicates)

Duplicates are never deleted: the extra copy goes to 90.Review/Duplicates/<group>/ with a note.
Compare ORIGINAL resolution: the native pixels of the embedded image that land on the document
itself (a passport small on an A4 scan has fewer usable pixels than one that fills the frame).
Also judge colour and exposure: a slightly smaller but correctly exposed, colourful scan can beat
an overexposed one. When in doubt, show both and ask.

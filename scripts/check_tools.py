#!/usr/bin/env python3
"""Check that this computer has what the Document Vault scripts need. Read-only.
Usage: python3 check_tools.py [<vault-folder>] [--download]
--download fetches missing OCR language files into 99.System/tessdata/ (needs internet).
Prints OK / MISSING per item and exits 0 when everything essential is present."""
import os, sys, json, shutil, importlib, urllib.request
DEFAULT_LANGS = ["eng", "por", "rus", "heb"]   # English, Portuguese, Russian, Hebrew
TESSDATA_URL = "https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/{}.traineddata"

ESSENTIAL_MODULES = {"PIL": "pillow", "numpy": "numpy", "cv2": "opencv-python-headless", "img2pdf": "img2pdf"}
OPTIONAL_MODULES = {"openpyxl": "openpyxl (reading .xlsx files)"}
ESSENTIAL_BINS = {"tesseract": "tesseract-ocr", "pdfinfo": "poppler-utils", "pdftotext": "poppler-utils",
                  "pdfimages": "poppler-utils", "pdftoppm": "poppler-utils",
                  "pdfseparate": "poppler-utils", "pdfunite": "poppler-utils"}
OPTIONAL_BINS = {"soffice": "LibreOffice (reading Word/Excel files)", "identify": "ImageMagick (HEIC and odd image formats)"}

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    vault = args[0] if args else None; download = "--download" in sys.argv
    bad = []
    print(f"python {sys.version.split()[0]}")
    for m, pkg in ESSENTIAL_MODULES.items():
        try: importlib.import_module(m); print(f"OK       python module {m}")
        except Exception: print(f"MISSING  python module {m}  (pip install {pkg})"); bad.append(pkg)
    for m, what in OPTIONAL_MODULES.items():
        try: importlib.import_module(m); print(f"OK       python module {m}")
        except Exception: print(f"optional python module {m} not found: {what}")
    for b, pkg in ESSENTIAL_BINS.items():
        if shutil.which(b): print(f"OK       {b}")
        else: print(f"MISSING  {b}  (package {pkg})"); bad.append(pkg)
    for b, what in OPTIONAL_BINS.items():
        if shutil.which(b): print(f"OK       {b}")
        else: print(f"optional {b} not found: {what}")
    if vault:
        sysd = os.path.join(vault, "99.System")
        try: langs = json.load(open(os.path.join(sysd, "vault.json"))).get("ocr_languages") or DEFAULT_LANGS
        except Exception: langs = DEFAULT_LANGS
        for l in langs + ["osd"]:
            p = os.path.join(sysd, "tessdata", l + ".traineddata")
            if not os.path.exists(p) and download:
                try:
                    os.makedirs(os.path.dirname(p), exist_ok=True)
                    data = urllib.request.urlopen(TESSDATA_URL.format(l), timeout=120).read()
                    if len(data) > 10000:
                        open(p + ".part", "wb").write(data); os.rename(p + ".part", p)
                except Exception as e: print(f"         download of {l} failed: {e}")
            if os.path.exists(p): print(f"OK       OCR language {l}")
            else:
                print(f"MISSING  OCR language {l}: download {TESSDATA_URL.format(l)} into 99.System/tessdata/ (or re-run with --download)")
                if l != "osd": bad.append("tessdata " + l)
    print("ALL ESSENTIALS PRESENT" if not bad else "MISSING: " + ", ".join(sorted(set(bad))))
    sys.exit(0 if not bad else 1)

if __name__ == "__main__":
    main()

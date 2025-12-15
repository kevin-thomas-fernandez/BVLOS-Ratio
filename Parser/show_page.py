import pdfplumber
from pathlib import Path

with pdfplumber.open(Path('BVLOS_NPRM_website_version.pdf')) as pdf:
    page = pdf.pages[54]
    print(page.extract_text())

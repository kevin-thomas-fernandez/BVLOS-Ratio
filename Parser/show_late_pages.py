import pdfplumber
from pathlib import Path

with pdfplumber.open(Path('BVLOS_NPRM_website_version.pdf')) as pdf:
    for idx in range(600, 610):
        text = pdf.pages[idx].extract_text() or ''
        print('--- Page', idx + 1, '---')
        print(text[:1200])

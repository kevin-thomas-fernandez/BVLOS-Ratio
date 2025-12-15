import pdfplumber
import re
from pathlib import Path

pdf = pdfplumber.open(Path('BVLOS_NPRM_website_version.pdf'))
min_num = None
min_page = None
for page_index, page in enumerate(pdf.pages, start=1):
    text = page.extract_text() or ''
    match = re.search(r'§\s*108\.(\d+)', text)
    if match:
        num = int(match.group(1))
        if min_num is None or num < min_num:
            min_num = num
            min_page = page_index
print('min section:', min_num, 'page', min_page)
pdf.close()

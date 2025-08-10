import pdfplumber
import re
from deep_translator import GoogleTranslator

import pandas as pd

# List of digits to exclude at position 5
exclude_digits = set('246789')

def meets_code_condition(code):
    return len(code) >= 5 and code[4] not in exclude_digits

# Regex to find a typical course line (CODE, Title, [UCTS, etc.])
course_line_re = re.compile(r'(\b[0-9A-Z]{8,}\b)[ \t]+(.+?)(?:\s{2,}|$)')

def is_french_text(title):
    # Naive filter: returns True if the text contains accented characters or is not all ASCII.
    # You may swap in smarter language detection if needed.
    return bool(re.search(r'[éàèçùâêîôûëïüœ]', title)) or not all(ord(c) < 128 for c in title)

results = []

with pdfplumber.open("Offre_de_cours_ST_2024-2025.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if not text:
            continue
        for match in course_line_re.finditer(text):
            code, title = match.groups()
            if not meets_code_condition(code):
                continue
            # Check if French-only and needs translation
            title_en = None
            if is_french_text(title):
                title_en = GoogleTranslator(source='fr', target='en').translate(title)
            results.append({
                "course_code": code,
                "title_fr": title,
                "title_en": title_en or title
            })

# Example output (print or write to CSV)
df = pd.DataFrame(results)
df.to_excel("all_filtered_courses.xlsx", index=False)

print("엑셀 저장 완료: all_filtered_courses.xlsx")
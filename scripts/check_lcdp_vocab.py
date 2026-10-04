import openpyxl
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

wb = openpyxl.load_workbook('Money Heist/La_Casa_de_Papel_S3E01_台词.xlsx')

# Load existing cards to check for duplicates
with open('src/data/LCDP_S3E01_nouns_cards.json', 'r', encoding='utf-8') as f:
    existing_cards = json.load(f)

existing_words = set()
for card in existing_cards:
    existing_words.add(card['target_word'].lower())

print(f"Existing cards: {len(existing_cards)}")
print(f"Existing unique words: {len(existing_words)}")
print()

for sheet_name in ['动词', '形容词', '副词']:
    ws = wb[sheet_name]
    rows = list(ws.iter_rows(min_row=2, values_only=True))
    print(f"=== {sheet_name}: {len(rows)} rows ===")
    
    new_words = []
    dup_words = []
    for row in rows:
        if not row or not row[0]:
            continue
        seq, base, cn, form, sentence_es, sentence_cn = row[:6] if len(row) >= 6 else (row + [None]*6)[:6]
        if not base:
            continue
        form_lower = str(form).strip().lower() if form else ''
        base_lower = str(base).strip().lower() if base else ''
        
        if form_lower in existing_words or base_lower in existing_words:
            dup_words.append(f"  DUP: {base} -> {form} ({cn})")
        else:
            new_words.append(f"  NEW: {base} -> {form} ({cn}) | {sentence_es}")
    
    print(f"  New: {len(new_words)}, Duplicate: {len(dup_words)}")
    for w in new_words[:5]:
        print(w)
    if len(new_words) > 5:
        print(f"  ... and {len(new_words)-5} more")
    for w in dup_words[:3]:
        print(w)
    print()

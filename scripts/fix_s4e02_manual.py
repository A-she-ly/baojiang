import json
import re
import unicodedata
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def normalize(text):
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII').lower()

with open('src/data/LCDP_S4E02_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

manual_fixes = {
    'LCDP_S4E02_004': 'Apostamos',
    'LCDP_S4E02_020': 'explique',
    'LCDP_S4E02_030': 'Pertenecia',
    'LCDP_S4E02_032': 'Protejo',
    'LCDP_S4E02_038': 'Valoro',
    'LCDP_S4E02_042': 'extraña',
    'LCDP_S4E02_043': 'incapaces',
    'LCDP_S4E02_044': 'jodida',
    'LCDP_S4E02_052': 'Maserati',
    'LCDP_S4E02_053': 'Sierra',
    'LCDP_S4E02_055': 'Alberto',
    'LCDP_S4E02_073': 'Penalti',
    'LCDP_S4E02_082': 'Amanda',
    'LCDP_S4E02_121': 'Inmersi\u00f3n',
    'LCDP_S4E02_125': 'Mat\u00edas',
}

fixed = 0
for card in cards:
    cid = card['id']
    if cid in manual_fixes:
        form = manual_fixes[cid]
        sentence = card['sentence_full']
        # Try exact first
        if form in sentence:
            card['sentence_cloze'] = sentence.replace(form, '___', 1)
            fixed += 1
            continue
        # Try accent-insensitive
        norm_form = normalize(form)
        words = sentence.split()
        for word in words:
            clean = re.sub(r'[.,!?;:¿¡"\'()\[\]]', '', word)
            if normalize(clean) == norm_form:
                card['sentence_cloze'] = sentence.replace(word, '___', 1)
                fixed += 1
                break

with open('src/data/LCDP_S4E02_cards.json', 'w', encoding='utf-8') as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

bad = [c for c in cards if c['sentence_cloze'] == c['sentence_full']]
print(f"Fixed: {fixed}, Still bad: {len(bad)}")

"""
Final manual fix for remaining 7 problematic cloze cards.
"""
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/data/LCDP_S3E07_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Manual fixes
manual = {
    'LCDP_S3E07_020': None,  # Cortés is a surname, not the verb - skip
    'LCDP_S3E07_022': 'Descansa',  # descansar -> Descansa (present 3rd person)
    'LCDP_S3E07_036': 'mudito',  # mudar -> mudito (diminutive)
    'LCDP_S3E07_045': 'reconozco',  # reconocer -> reconozco (irregular c->zc)
    'LCDP_S3E07_275': 'completamenta',  # typo in sentence
    'LCDP_S3E07_298': 'Dura',  # duro -> Dura (feminine)
    'LCDP_S3E07_301': 'Europea',  # europeo -> Europea (feminine)
}

fixed = 0
for card in cards:
    cid = card['id']
    if cid in manual:
        form = manual[cid]
        if form is None:
            print(f"SKIP {cid}: proper noun, not a verb form")
            continue
        sentence = card['sentence_full']
        if form in sentence:
            card['sentence_cloze'] = sentence.replace(form, '___', 1)
            fixed += 1
            print(f"Fixed {cid}: '{form}' -> '___'")
        else:
            print(f"NOT FOUND {cid}: '{form}' in sentence")
            # Debug: show actual bytes
            for i, ch in enumerate(sentence):
                if ch.lower() in form.lower()[:3]:
                    print(f"  char at {i}: '{ch}' (U+{ord(ch):04X})")

with open('src/data/LCDP_S3E07_cards.json', 'w', encoding='utf-8') as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

bad = [c for c in cards if c.get('sentence_cloze', '') == c.get('sentence_full', '')]
print(f"\nTotal: {len(cards)}, Still bad: {len(bad)}")

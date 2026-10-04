import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/data/LCDP_S3E07_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

for card in cards:
    if card['id'] == 'LCDP_S3E07_020':
        card['sentence_cloze'] = card['sentence_full'].replace('Cortés', '___', 1)
        break

with open('src/data/LCDP_S3E07_cards.json', 'w', encoding='utf-8') as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

bad = [c for c in cards if c.get('sentence_cloze', '') == c.get('sentence_full', '')]
print(f"Total: {len(cards)}, Still bad: {len(bad)}")

import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path = 'src/data/LCDP_S3E01_nouns_cards.json'
with open(path, 'r', encoding='utf-8') as f:
    cards = json.load(f)

cleared = 0
for card in cards:
    if card['ipa'] != '':
        card['ipa'] = ''
        cleared += 1

with open(path, 'w', encoding='utf-8') as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

print(f"Cleared {cleared} IPA fields.")

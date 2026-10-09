import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/data/LCDP_S4E02_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Clear existing etymology so the generator can rebuild
for card in cards:
    if 'etymology' in card:
        del card['etymology']

with open('src/data/LCDP_S4E02_cards.json', 'w', encoding='utf-8') as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

print(f"Cleared etymology from {len(cards)} cards")

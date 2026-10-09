import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/data/LCDP_S4E02_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

for word in ['libertad', 'espiritu', 'maserati', 'penalti', 'corner', 'shock']:
    card = next((c for c in cards if c['target_word'].lower() == word), None)
    if card:
        print(f"{word} ({card['pos']}): {json.dumps(card.get('etymology'), ensure_ascii=False)}")
    else:
        print(f"{word}: NOT FOUND")

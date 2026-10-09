import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/data/LCDP_S4E02_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

samples = ['advertir', 'huevos', 'tension', 'libertad', 'espiritu', 'incapaz', 'corner', 'shock']
for word in samples:
    card = next((c for c in cards if c['target_word'].lower() == word), None)
    if card:
        print(f"\n{word} ({card['pos']}):")
        for part in card.get('etymology', []):
            print(f"  {part['part']:20s} | {part['origin']:30s} | {part['meaning']}")

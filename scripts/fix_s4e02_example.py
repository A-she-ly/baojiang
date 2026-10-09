import json

with open('src/data/LCDP_S4E02_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

for card in cards:
    card['is_example_sentence'] = False

with open('src/data/LCDP_S4E02_cards.json', 'w', encoding='utf-8') as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

print(f"Updated {len(cards)} cards: is_example_sentence = false")

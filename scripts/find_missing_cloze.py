import json

cards = json.load(open('src/data/S01E01_cards.json', encoding='utf-8'))
bad = [c for c in cards if '___' not in c.get('sentence_cloze', '')]

print(f'Total cards: {len(cards)}')
print(f'Cards without cloze blank: {len(bad)}')
print()
for c in bad:
    print(f"  {c['id']}: target='{c.get('target_word', 'N/A')}'")
    print(f"    cloze: {c.get('sentence_cloze', '')[:80]}")
    print()

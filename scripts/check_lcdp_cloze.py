import json

cards = json.load(open('src/data/LCDP_S01E01_cards.json', encoding='utf-8'))
bad = [c for c in cards if '___' not in c.get('sentence_cloze', '')]

print(f'Total: {len(cards)}, Missing cloze: {len(bad)}')
for c in bad:
    print(f"  {c['id']}: {c.get('target_word')}")

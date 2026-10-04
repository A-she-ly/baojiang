import json

with open('src/data/LCDP_S3E07_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

bad = [c for c in cards if c.get('sentence_cloze', '') == c.get('sentence_full', '')]
print(f"Total: {len(cards)}, Bad cloze: {len(bad)}")
for c in bad[:20]:
    print(f"  {c['id']}: target='{c['target_word']}' in '{c['sentence_full'][:70]}'")

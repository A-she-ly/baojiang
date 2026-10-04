import json

with open('src/data/LCDP_S3E07_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

adjs = [c for c in cards if c['pos'].startswith('adj.')]
print(f'Adjective cards: {len(adjs)}')
print('\nSamples:')
for c in adjs[:3]:
    print(f"  {c['target_word']} -> {c['translation']}")
    print(f"    {c['sentence_full']}")
    print(f"    {c['sentence_translation']}")
    print()

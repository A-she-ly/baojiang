import json

with open('src/data/LCDP_S3E05_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

print(f'Total: {len(cards)}')
translated = sum(1 for c in cards if c.get('translation', '') != c['target_word'])
print(f'Translated: {translated}')

print('\nSamples:')
for c in cards[:15]:
    print(f"  {c['target_word']} -> {c['translation']}")

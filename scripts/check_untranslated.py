import json

with open('src/data/LCDP_S3E05_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

untranslated = [c for c in cards if c.get('translation', '') == c['target_word']]
print(f'Untranslated: {len(untranslated)}')
print('\nFirst 30 untranslated words:')
for c in untranslated[:30]:
    print(f"  {c['target_word']} ({c['pos']})")

import json

with open('src/data/LCDP_S3E05_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Check sentence translation status
with_translation = sum(1 for c in cards if c.get('sentence_translation', '').strip())
without_translation = sum(1 for c in cards if not c.get('sentence_translation', '').strip())

print(f'Total cards: {len(cards)}')
print(f'With sentence translation: {with_translation}')
print(f'Without sentence translation: {without_translation}')

# Show sample sentences without translation
print('\nSample sentences without translation:')
count = 0
for c in cards:
    if not c.get('sentence_translation', '').strip() and c.get('sentence_full', ''):
        print(f"  {c['sentence_full']}")
        count += 1
        if count >= 10:
            break

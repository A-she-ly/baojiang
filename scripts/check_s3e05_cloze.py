import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/data/LCDP_S3E05_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

no_cloze = [c for c in cards if '___' not in c.get('sentence_cloze', '')]
print(f'S3E05 cards without cloze: {len(no_cloze)}/{len(cards)}')
for c in no_cloze[:20]:
    print(f"  {c['target_word']}: {c['sentence_full'][:60]}")

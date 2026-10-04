import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/data/LCDP_S3E07_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

c = [x for x in cards if x['id'] == 'LCDP_S3E07_001'][0]
print(f"Target: {c['target_word']}")
print(f"Full:   {c['sentence_full']}")
print(f"Cloze:  {c['sentence_cloze']}")

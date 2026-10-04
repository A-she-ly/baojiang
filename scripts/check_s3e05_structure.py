import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/data/LCDP_S3E05_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Check a few cards to understand the structure
for c in cards[:5]:
    print(f"Target: {c['target_word']}")
    print(f"POS: {c['pos']}")
    print(f"Sentence: {c['sentence_full']}")
    print(f"Cloze: {c['sentence_cloze']}")
    print()

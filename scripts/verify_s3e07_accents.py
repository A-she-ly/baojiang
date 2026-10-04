import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/data/LCDP_S3E07_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Show some sample cards with accented target_words
print("Sample cards with accented target_words:")
for c in cards[:10]:
    if any(ord(ch) > 127 for ch in c['target_word']):
        print(f"  {c['target_word']} ({c['pos']})")
        print(f"    Sentence: {c['sentence_full'][:60]}")
        print()

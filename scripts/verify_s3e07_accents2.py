import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/data/LCDP_S3E07_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Count cards with accented target_words
accented_count = 0
for c in cards:
    if any(ord(ch) > 127 for ch in c['target_word']):
        accented_count += 1

print(f"Total cards: {len(cards)}")
print(f"Cards with accented target_words: {accented_count}")

# Show some samples
print("\nSample accented cards:")
count = 0
for c in cards:
    if any(ord(ch) > 127 for ch in c['target_word']):
        print(f"  {c['target_word']} ({c['pos']})")
        count += 1
        if count >= 10:
            break

import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/data/LCDP_S3E05_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Check translation stats
total = len(cards)
has_word_trans = sum(1 for c in cards if c.get('translation', '').strip())
has_sent_trans = sum(1 for c in cards if c.get('sentence_translation', '').strip())

print(f"=== S3E05 Translation Stats ===")
print(f"Total cards: {total}")
print(f"Word translations: {has_word_trans}/{total} ({has_word_trans/total*100:.1f}%)")
print(f"Sentence translations: {has_sent_trans}/{total} ({has_sent_trans/total*100:.1f}%)")

# Show some samples
print(f"\n=== Sample Cards ===")
samples = [cards[0], cards[10], cards[50], cards[100], cards[500]]
for i, c in enumerate(samples):
    print(f"\n{i+1}. {c['target_word']} ({c['pos']})")
    print(f"   Translation: {c['translation']}")
    print(f"   Sentence: {c['sentence_full']}")
    print(f"   Sentence Trans: {c['sentence_translation']}")

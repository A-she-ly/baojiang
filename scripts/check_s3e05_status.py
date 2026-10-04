import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Check current S3E05 card translation status
with open('src/data/LCDP_S3E05_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

total = len(cards)
has_translation = sum(1 for c in cards if c.get('translation', '').strip())
has_sentence_trans = sum(1 for c in cards if c.get('sentence_translation', '').strip())

print(f"Total cards: {total}")
print(f"Has word translation: {has_translation}/{total}")
print(f"Has sentence translation: {has_sentence_trans}/{total}")

# Show some untranslated cards
untranslated = [c for c in cards if not c.get('translation', '').strip()]
print(f"\nUntranslated words ({len(untranslated)}):")
for c in untranslated[:20]:
    print(f"  {c['target_word']} ({c['pos']})")

# Show some cards with empty sentence_translation
no_sent_trans = [c for c in cards if not c.get('sentence_translation', '').strip()]
print(f"\nCards without sentence translation ({len(no_sent_trans)}):")
for c in no_sent_trans[:5]:
    print(f"  {c['target_word']}: {c['sentence_full']}")

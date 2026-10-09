import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/data/LCDP_S4E02_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Check translation field
no_trans = [c for c in cards if not c.get('translation') or c['translation'] in ('', '（动词原形）', '(动词原形)')]
print(f"Cards with missing/generic translation: {len(no_trans)}")
for c in no_trans[:20]:
    print(f"  {c['target_word']} ({c['pos']}): '{c.get('translation', '')}'")

# Also check all unique translations
trans_set = set(c.get('translation', '') for c in cards)
print(f"\nUnique translations ({len(trans_set)}):")
for t in sorted(trans_set):
    count = sum(1 for c in cards if c.get('translation') == t)
    print(f"  '{t}': {count} cards")

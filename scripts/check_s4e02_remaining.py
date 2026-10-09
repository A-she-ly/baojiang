import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/data/LCDP_S4E02_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

bad = [c for c in cards if c['sentence_cloze'] == c['sentence_full']]
print(f"Still bad: {len(bad)}")
for c in bad:
    print(f"  {c['id']}: target='{c['target_word']}' | '{c['sentence_full'][:80]}'")

import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/data/LCDP_S4E02_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

with open('src/data/LCDP_S4E02_metadata.json', 'r', encoding='utf-8') as f:
    meta = json.load(f)

print(f"Total cards: {len(cards)}")
print(f"Metadata: {json.dumps(meta, ensure_ascii=False, indent=2)}")

# POS distribution
pos = {}
for c in cards:
    p = c['pos'].split('.')[0]
    pos[p] = pos.get(p, 0) + 1
print(f"\nPOS distribution: {pos}")

# Sample cards
print("\nSample cards:")
for c in cards[:3]:
    print(f"  {c['id']}: {c['target_word']} ({c['pos']}) - {c['translation']}")
    print(f"    Cloze: {c['sentence_cloze']}")
    print(f"    Full:  {c['sentence_full']}")

# Check for bad cloze
bad = [c for c in cards if c['sentence_cloze'] == c['sentence_full']]
print(f"\nBad cloze: {len(bad)}")

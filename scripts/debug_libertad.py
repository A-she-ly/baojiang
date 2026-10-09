import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/data/LCDP_S4E02_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

card = next((c for c in cards if c['target_word'].lower() == 'libertad'), None)
if card:
    w = card['target_word']
    print(f"target_word: '{w}'")
    print(f"repr: {repr(w)}")
    print(f"len: {len(w)}")
    for i, ch in enumerate(w):
        print(f"  [{i}] U+{ord(ch):04X} '{ch}'")
    print(f"lower: '{w.lower()}'")
    print(f"lower repr: {repr(w.lower())}")
    print(f"endswith dad: {w.lower().endswith('dad')}")

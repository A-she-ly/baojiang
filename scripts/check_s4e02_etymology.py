import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, 'scripts')
from spanish_etymology import ETYMOLOGY_DICT

with open('src/data/LCDP_S4E02_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

covered = 0
missing = []
for c in cards:
    word = c['target_word'].lower()
    if word in ETYMOLOGY_DICT:
        covered += 1
    else:
        missing.append(c['target_word'])

print(f"Total: {len(cards)}, Covered: {covered}, Missing: {len(missing)}")
print(f"Missing words: {missing[:30]}")

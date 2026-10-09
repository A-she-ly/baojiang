import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/data/LCDP_S4E02_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

basic = [c for c in cards if len(c.get('etymology', [])) == 1 and c['etymology'][0].get('meaning') == '完整词形']
print(f"Basic etymology (full word only): {len(basic)}")
for c in basic:
    print(f"  {c['target_word']} ({c['pos']})")

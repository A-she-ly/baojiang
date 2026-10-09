import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/data/LCDP_S4E02_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Check first 10 cards' ordering fields
print("First 10 cards:")
for c in cards[:10]:
    print(f"  {c['id']}: {c['target_word']:15s} | scene_id={c.get('scene_id','')} | line_index={c.get('line_index','')} | character={c.get('character','')}")

print(f"\nTotal cards: {len(cards)}")

# Check if cards are already in order
print("\nChecking order...")
for i, c in enumerate(cards[:20]):
    print(f"  [{i}] {c['target_word']:15s} scene={c.get('scene_id','')} line={c.get('line_index','')}")

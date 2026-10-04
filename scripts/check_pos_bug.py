import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

cards = json.load(open('src/data/LCDP_S3E01_nouns_cards.json', 'r', encoding='utf-8'))

# Find cards where pos starts with 'v.' but word looks like a noun
suspects = []
for c in cards:
    pos_lower = c['pos'].lower()
    tw = c['target_word'].lower()
    
    if pos_lower.startswith('v.'):
        noun_endings = ['cion', 'sion', 'dad', 'tad', 'ez', 'eza', 'ura', 'aje', 'ento', 'miento', 'ero', 'era', 'ista', 'nte']
        for ending in noun_endings:
            if tw.endswith(ending):
                suspects.append(f"  {tw:20s} pos='{c['pos']}'")
                break

if suspects:
    print(f"Found {len(suspects)} suspicious verb cards that look like nouns:")
    for s in suspects[:20]:
        print(s)
else:
    print("No obvious POS mismatches found in data")

# Check elefante specifically
print()
print("=== Elefante card details ===")
for c in cards:
    if 'elefante' in c['target_word'].lower():
        print(f"  target_word: {c['target_word']}")
        print(f"  pos: {c['pos']}")
        print(f"  tags: {c['tags']}")
        print(f"  id: {c['id']}")

# Simulate the exact filter logic from Home.tsx
print()
print("=== Simulating POS='v' filter ===")
filtered = []
for c in cards:
    raw = c['pos'].lower()
    key = (
        'n' if raw.startswith('n.') else
        'v' if raw.startswith('v.') else
        'adj' if raw.startswith('adj') else
        'adv' if raw.startswith('adv') else
        'phrasal' if 'phrasal' in raw else
        'contraction' if 'contraction' in raw else
        'phrase' if 'phrase' in raw else
        'other'
    )
    if key == 'v':
        filtered.append(c['target_word'])

print(f"Cards matching verb filter: {len(filtered)}")
if 'elefante' in filtered:
    print("BUG CONFIRMED: elefante IS in verb filter results!")
    for c in cards:
        if c['target_word'].lower() == 'elefante':
            print(f"  Card: id={c['id']}, pos='{c['pos']}', raw.lower()='{c['pos'].lower()}'")
            print(f"  startsWith('n.') = {c['pos'].lower().startswith('n.')}")
            print(f"  startsWith('v.') = {c['pos'].lower().startswith('v.')}")
else:
    print("elefante NOT in verb filter - data is correct")

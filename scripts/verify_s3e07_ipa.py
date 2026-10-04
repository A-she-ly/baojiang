import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/data/LCDP_S3E07_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

empty_ipa = [c for c in cards if not c.get('ipa', '').strip()]
print(f"Total cards: {len(cards)}")
print(f"Cards with empty IPA: {len(empty_ipa)}")
print(f"Cards with IPA: {len(cards) - len(empty_ipa)}")

# Show some samples
print("\nSample cards with IPA:")
for c in cards[:10]:
    if c.get('ipa'):
        print(f"  {c['target_word']} -> {c['ipa']}")

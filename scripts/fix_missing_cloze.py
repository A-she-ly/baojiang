import json

cards = json.load(open('src/data/S01E01_cards.json', encoding='utf-8'))

# Fix cards without cloze blank
fixes = {
    'S01E01_011': ("It's just two people going out", "___'s just two people going out"),
    'S01E01_013': ("Strip joint!", "___ joint!"),
    'S01E01_061': ("So does he have a hump?", "___ does he have a hump?"),
    'S01E01_065': ("No.", "___."),
    'S01E01_070': ("Done with the bookcase!", "___ with the bookcase!"),
    'S01E01_095': ("Really, everyone.", "___, everyone."),
    'S01E01_110': ("This is not even a date.", "___ is not even a date."),
    'S01E01_112': ("Yes!", "___!"),
}

fixed_count = 0
for card in cards:
    if card['id'] in fixes:
        old_text, new_text = fixes[card['id']]
        if old_text in card['sentence_cloze']:
            card['sentence_cloze'] = card['sentence_cloze'].replace(old_text, new_text, 1)
            fixed_count += 1
            print(f"Fixed {card['id']}: {old_text[:30]} -> {new_text[:30]}")
        else:
            print(f"WARNING: Could not find '{old_text}' in {card['id']}")

# Save back
json.dump(cards, open('src/data/S01E01_cards.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"\nFixed {fixed_count} cards")

# Verify
bad = [c for c in cards if '___' not in c.get('sentence_cloze', '')]
print(f"Remaining cards without cloze: {len(bad)}")

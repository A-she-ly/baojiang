"""
Manually fix the remaining 8 problematic cloze cards.
"""
import json

with open('src/data/LCDP_S3E07_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Manual fixes for irregular forms
manual_fixes = {
    'LCDP_S3E07_002': ('Acércate', 'Acércate'),  # acercar -> Acércate (imperative + reflexive)
    'LCDP_S3E07_004': ('Aguantad', 'Aguantad'),   # aguantar -> Aguantad (vosotros imperative)
    'LCDP_S3E07_008': ('atrevería', 'atrevería'),  # atreverse -> se atrevería (conditional)
    'LCDP_S3E07_009': ('Aumentas', 'Aumentas'),    # aumentar -> Aumentas (present 2nd person)
    'LCDP_S3E07_011': ('Blindados', 'Blindados'),  # blindar -> Blindados (past participle plural)
    'LCDP_S3E07_015': ('Cierren', 'Cierren'),      # cerrar -> Cierren (stem-change e->ie, subjunctive)
    'LCDP_S3E07_017': ('communicaciones', 'communicaciones'),  # comunicar -> communicaciones (noun, different word)
    'LCDP_S3E07_019': ('Continuemos', 'Continuemos'),  # continuar -> Continuemos (subjunctive 1st plural)
}

fixed = 0
for card in cards:
    card_id = card['id']
    if card_id in manual_fixes:
        target_form, _ = manual_fixes[card_id]
        sentence = card['sentence_full']
        if target_form in sentence:
            card['sentence_cloze'] = sentence.replace(target_form, '___', 1)
            fixed += 1
            print(f"Fixed {card_id}: '{target_form}' -> '___'")
        else:
            print(f"NOT FOUND {card_id}: '{target_form}' not in '{sentence}'")

with open('src/data/LCDP_S3E07_cards.json', 'w', encoding='utf-8') as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

# Verify
bad = [c for c in cards if c.get('sentence_cloze', '') == c.get('sentence_full', '')]
print(f"\nTotal: {len(cards)}, Still bad: {len(bad)}")

import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/data/LCDP_S4E02_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Fix missing translations for verbs
verb_translations = {
    'advertir': '警告',
    'asegurar': '保证',
    'beber': '喝',
    'contestar': '回答',
    'decidir': '决定',
    'explicar': '解释',
    'ordenar': '命令',
    'pertenecer': '属于',
    'proteger': '保护',
    'recoger': '收集',
}

fixed = 0
for card in cards:
    word = card['target_word'].lower()
    if word in verb_translations and card.get('translation') in ('', '（动词原形）', '(动词原形)'):
        card['translation'] = f"{verb_translations[word]}（动词原形）"
        fixed += 1
        print(f"Fixed: {word} -> {card['translation']}")

with open('src/data/LCDP_S4E02_cards.json', 'w', encoding='utf-8') as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

print(f"\nTotal fixed: {fixed}")

# Verify no more missing translations
remaining = [c for c in cards if not c.get('translation') or c['translation'] in ('', '（动词原形）', '(动词原形)')]
print(f"Remaining with bad translation: {len(remaining)}")

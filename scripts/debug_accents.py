import sys
import io
import json
import unicodedata

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def remove_accents(text):
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))

with open('src/data/LCDP_S3E07_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Check the clasico card
for c in cards:
    if c['target_word'] == 'clasico':
        print(f"Target: {c['target_word']}")
        print(f"Unaccented: {remove_accents(c['target_word'].lower())}")
        print(f"POS: {c['pos']}")
        break

# Check how many cards have unaccented target_words
unaccented_count = 0
for c in cards:
    target = c['target_word']
    unaccented = remove_accents(target.lower())
    if target.lower() != unaccented:
        # Has accents
        pass
    else:
        # Check if it should have accents (compare with sentence)
        sentence = c.get('sentence_full', '')
        # Find the word in sentence
        import re
        words = re.findall(r'\b\w+\b', sentence)
        for word in words:
            if remove_accents(word.lower()) == unaccented and word.lower() != target.lower():
                unaccented_count += 1
                if unaccented_count <= 10:
                    print(f"\nShould be accented: {target} -> {word}")
                    print(f"  Sentence: {sentence[:60]}")
                break

print(f"\nTotal cards that might need accent fix: {unaccented_count}")

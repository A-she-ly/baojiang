import sys
import io
import json
import re
import unicodedata

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def remove_accents(text):
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))

with open('src/data/LCDP_S3E05_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Check first few cards without cloze
no_cloze = [c for c in cards if '___' not in c.get('sentence_cloze', '')]
print(f"Cards without cloze: {len(no_cloze)}")

for c in no_cloze[:5]:
    target = c['target_word']
    sentence = c['sentence_full']
    cloze = c['sentence_cloze']
    
    print(f"\nTarget: {target}")
    print(f"Sentence: {sentence}")
    print(f"Cloze: {cloze}")
    
    # Check if target is in sentence (accent-insensitive)
    sentence_no_accents = remove_accents(sentence.lower())
    target_no_accents = remove_accents(target.lower())
    
    print(f"Target no accents: {target_no_accents}")
    print(f"In sentence (no accents): {target_no_accents in sentence_no_accents}")
    
    # Try to find the word
    words = re.findall(r'\b\w+\b', sentence)
    for word in words:
        if remove_accents(word.lower()) == target_no_accents:
            print(f"Found matching word: {word}")
            break

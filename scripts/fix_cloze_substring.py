"""
Fix the substring matching bug - ensure longest match first with word boundaries.
"""
import json
import re
import unicodedata
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def normalize(text):
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')

def fix_cloze(sentence, target_word):
    """Replace target word form in sentence with ___, using word-boundary matching."""
    words = sentence.split()
    
    # Build list of (form, normalized_form) sorted by length descending
    candidates = []
    
    # Add target word itself
    candidates.append((target_word, normalize(target_word)))
    
    # Generate conjugations and add them
    if target_word.endswith(('ar', 'er', 'ir')):
        stem = target_word[:-2]
        ending = target_word[-2:]
        
        # All regular forms
        all_endings = []
        for e in ['ar', 'er', 'ir']:
            if e == 'ar':
                all_endings.extend(['o', 'as', 'a', 'amos', 'áis', 'an',
                                   'é', 'aste', 'ó', 'amos', 'asteis', 'aron',
                                   'aba', 'abas', 'ábamos', 'abais', 'aban',
                                   'e', 'es', 'emos', 'éis', 'en',
                                   'a', 'e', 'emos', 'ad', 'en',
                                   'ando', 'ado', 'ados', 'ada', 'adas'])
            elif e == 'er':
                all_endings.extend(['o', 'es', 'e', 'emos', 'éis', 'en',
                                   'í', 'iste', 'ió', 'imos', 'isteis', 'ieron',
                                   'ía', 'ías', 'íamos', 'íais', 'ían',
                                   'a', 'as', 'amos', 'áis', 'an',
                                   'e', 'a', 'amos', 'ed', 'an',
                                   'iendo', 'ido', 'idos', 'ida', 'idas'])
            elif e == 'ir':
                all_endings.extend(['o', 'es', 'e', 'imos', 'ís', 'en',
                                   'í', 'iste', 'ió', 'imos', 'isteis', 'ieron',
                                   'ía', 'ías', 'íamos', 'íais', 'ían',
                                   'a', 'as', 'amos', 'áis', 'an',
                                   'e', 'a', 'amos', 'id', 'an',
                                   'iendo', 'ido', 'idos', 'ida', 'idas'])
        
        # Future & conditional
        all_endings.extend(['é', 'ás', 'á', 'emos', 'éis', 'án',
                           'ía', 'ías', 'íamos', 'íais', 'ían'])
        
        for end in all_endings:
            candidates.append((stem + end, normalize(stem + end)))
            candidates.append((target_word + end, normalize(target_word + end)))
        
        # Stem changes
        if 'o' in stem:
            ue = stem.replace('o', 'ue')
            for end in all_endings:
                candidates.append((ue + end, normalize(ue + end)))
        if 'e' in stem:
            ie = stem.replace('e', 'ie')
            for end in all_endings:
                candidates.append((ie + end, normalize(ie + end)))
            i_stem = stem.replace('e', 'i')
            for end in all_endings:
                candidates.append((i_stem + end, normalize(i_stem + end)))
    
    # Sort by length descending to match longest first
    candidates.sort(key=lambda x: len(x[0]), reverse=True)
    
    # Try to match each candidate against words in sentence
    for form, norm_form in candidates:
        for word in words:
            clean = re.sub(r'[.,!?;:¿¡"\'()\[\]]', '', word)
            # Exact match or accent-insensitive match
            if clean == form or normalize(clean) == norm_form:
                # Make sure it's not a substring match
                if len(clean) == len(form) or len(clean) == len(norm_form):
                    return sentence.replace(word, '___', 1)
    
    return sentence

# Load
with open('src/data/LCDP_S3E07_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Fix all cards that have incorrect cloze (substring matches)
fixed = 0
for card in cards:
    cloze = card.get('sentence_cloze', '')
    full = card.get('sentence_full', '')
    
    # Check if cloze has the bug: ___ followed by leftover letters
    if '___' in cloze and cloze != full:
        # Check if there are leftover letters after ___
        parts = cloze.split('___')
        if len(parts) == 2 and parts[1] and parts[1][0].isalpha():
            # Bug detected - redo the cloze
            result = fix_cloze(full, card['target_word'])
            if result != full:
                card['sentence_cloze'] = result
                fixed += 1
                print(f"Fixed {card['id']}: '{card['target_word']}' -> '{result}'")

# Also fix cards where cloze == full
for card in cards:
    if card.get('sentence_cloze', '') == card.get('sentence_full', ''):
        result = fix_cloze(card['sentence_full'], card['target_word'])
        if result != card['sentence_full']:
            card['sentence_cloze'] = result
            fixed += 1

with open('src/data/LCDP_S3E07_cards.json', 'w', encoding='utf-8') as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

bad = [c for c in cards if c.get('sentence_cloze', '') == c.get('sentence_full', '')]
print(f"\nFixed: {fixed}, Still bad: {len(bad)}")

"""
Fix remaining 21 S3E07 cloze cards - handle adjective gender/number and irregular verbs.
"""
import json
import re
import unicodedata
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def normalize(text):
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')

def generate_adjective_forms(word):
    """Generate gender/number variants for adjectives."""
    forms = set()
    forms.add(word)
    
    # Masculine singular -> feminine singular (o -> a)
    if word.endswith('o'):
        forms.add(word[:-1] + 'a')
        forms.add(word[:-1] + 'as')  # feminine plural
        forms.add(word + 's')  # masculine plural
    # Feminine singular -> masculine singular (a -> o)  
    elif word.endswith('a'):
        forms.add(word[:-1] + 'o')
        forms.add(word[:-1] + 'os')  # masculine plural
        forms.add(word + 's')  # feminine plural
    # Consonant ending -> add s for plural
    elif word.endswith(('z', 'n', 'r', 's')):
        if word.endswith('z'):
            forms.add(word[:-1] + 'ces')  # capaz -> capaces
        else:
            forms.add(word + 'es')
    
    # Handle accent variants
    for form in list(forms):
        # Add accent variants
        forms.add(form)
    
    return forms

def generate_verb_forms(lemma):
    """Generate comprehensive verb forms."""
    forms = set()
    forms.add(lemma)
    
    if not lemma.endswith(('ar', 'er', 'ir')):
        return forms
    
    stem = lemma[:-2]
    ending = lemma[-2:]
    
    # All regular forms
    endings_map = {
        'ar': {
            'present': ['o', 'as', 'a', 'amos', 'áis', 'an'],
            'preterite': ['é', 'aste', 'ó', 'amos', 'asteis', 'aron'],
            'imperfect': ['aba', 'abas', 'ábamos', 'abais', 'aban'],
            'subjunctive': ['e', 'es', 'emos', 'éis', 'en'],
            'imperative': ['a', 'e', 'emos', 'ad', 'en'],
        },
        'er': {
            'present': ['o', 'es', 'e', 'emos', 'éis', 'en'],
            'preterite': ['í', 'iste', 'ió', 'imos', 'isteis', 'ieron'],
            'imperfect': ['ía', 'ías', 'íamos', 'íais', 'ían'],
            'subjunctive': ['a', 'as', 'amos', 'áis', 'an'],
            'imperative': ['e', 'a', 'amos', 'ed', 'an'],
        },
        'ir': {
            'present': ['o', 'es', 'e', 'imos', 'ís', 'en'],
            'preterite': ['í', 'iste', 'ió', 'imos', 'isteis', 'ieron'],
            'imperfect': ['ía', 'ías', 'íamos', 'íais', 'ían'],
            'subjunctive': ['a', 'as', 'amos', 'áis', 'an'],
            'imperative': ['e', 'a', 'amos', 'id', 'an'],
        },
    }
    
    for tense, endings in endings_map.get(ending, {}).items():
        forms.update([stem + e for e in endings])
    
    # Future & conditional (full infinitive)
    forms.update([lemma + e for e in ['é', 'ás', 'á', 'emos', 'éis', 'án']])
    forms.update([lemma + e for e in ['ía', 'ías', 'íamos', 'íais', 'ían']])
    
    # Gerund & participle
    forms.add(stem + ('ando' if ending == 'ar' else 'iendo'))
    forms.add(stem + ('ado' if ending == 'ar' else 'ido'))
    forms.add(stem + ('ados' if ending == 'ar' else 'idos'))  # plural participle
    
    # Stem changes
    if 'o' in stem:
        ue = stem.replace('o', 'ue')
        for tense, endings in endings_map.get(ending, {}).items():
            forms.update([ue + e for e in endings])
    if 'e' in stem:
        ie = stem.replace('e', 'ie')
        for tense, endings in endings_map.get(ending, {}).items():
            forms.update([ie + e for e in endings])
        i_stem = stem.replace('e', 'i')
        for e in ['o', 'es', 'e', 'imos', 'ís', 'en', 'ió', 'ieron', 'iendo']:
            forms.add(i_stem + e)
    
    return forms

def find_and_replace(sentence, target_word):
    """Find target word form in sentence and replace with ___."""
    # Exact match
    if target_word in sentence:
        return re.sub(re.escape(target_word), '___', sentence, count=1)
    
    # Accent-insensitive word match
    norm_target = normalize(target_word)
    words = sentence.split()
    for word in words:
        clean = re.sub(r'[.,!?;:¿¡"\'()\[\]]', '', word)
        if normalize(clean) == norm_target:
            return sentence.replace(word, '___', 1)
    
    # Try adjective forms
    adj_forms = generate_adjective_forms(target_word)
    for form in sorted(adj_forms, key=len, reverse=True):
        if form in sentence:
            return re.sub(re.escape(form), '___', sentence, count=1)
        norm_form = normalize(form)
        for word in words:
            clean = re.sub(r'[.,!?;:¿¡"\'()\[\]]', '', word)
            if normalize(clean) == norm_form and len(clean) >= 3:
                return sentence.replace(word, '___', 1)
    
    # Try verb forms
    verb_forms = generate_verb_forms(target_word)
    for form in sorted(verb_forms, key=len, reverse=True):
        if form in sentence:
            return re.sub(re.escape(form), '___', sentence, count=1)
        norm_form = normalize(form)
        for word in words:
            clean = re.sub(r'[.,!?;:¿¡"\'()\[\]]', '', word)
            if normalize(clean) == norm_form and len(clean) >= 3:
                return sentence.replace(word, '___', 1)
    
    return sentence

# Load
with open('src/data/LCDP_S3E07_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

fixed = 0
still_bad = []
for card in cards:
    if card.get('sentence_cloze', '') == card.get('sentence_full', ''):
        result = find_and_replace(card['sentence_full'], card['target_word'])
        if result != card['sentence_full']:
            card['sentence_cloze'] = result
            fixed += 1
        else:
            still_bad.append(card)

with open('src/data/LCDP_S3E07_cards.json', 'w', encoding='utf-8') as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

print(f"Fixed: {fixed}")
print(f"Still bad: {len(still_bad)}")
for c in still_bad:
    print(f"  {c['id']}: '{c['target_word']}' in '{c['sentence_full']}'")

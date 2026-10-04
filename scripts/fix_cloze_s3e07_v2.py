"""
Fix remaining 29 S3E07 cloze cards with irregular verb conjugations.
"""
import json
import re
import unicodedata

def normalize(text):
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')

def generate_all_forms(lemma):
    """Generate comprehensive conjugation forms including irregular patterns."""
    forms = set()
    forms.add(lemma)
    
    if not lemma.endswith(('ar', 'er', 'ir')):
        return forms
    
    stem = lemma[:-2]
    ending = lemma[-2:]
    
    # Regular forms
    # Present
    forms.update([stem + 'o', stem + 'as', stem + 'a', stem + 'amos', stem + 'áis', stem + 'an'])
    # Preterite
    forms.update([stem + 'é', stem + 'aste', stem + 'ó', stem + 'amos', stem + 'asteis', stem + 'aron'])
    # Imperfect
    if ending == 'ar':
        forms.update([stem + 'aba', stem + 'abas', stem + 'ábamos', stem + 'abais', stem + 'aban'])
    else:
        forms.update([stem + 'ía', stem + 'ías', stem + 'íamos', stem + 'íais', stem + 'ían'])
    # Future (full infinitive + endings)
    forms.update([lemma + 'é', lemma + 'ás', lemma + 'á', lemma + 'emos', lemma + 'éis', lemma + 'án'])
    # Conditional
    forms.update([lemma + 'ía', lemma + 'ías', lemma + 'íamos', lemma + 'íais', lemma + 'ían'])
    # Subjunctive present
    if ending == 'ar':
        forms.update([stem + 'e', stem + 'es', stem + 'emos', stem + 'éis', stem + 'en'])
    else:
        forms.update([stem + 'a', stem + 'as', stem + 'amos', stem + 'áis', stem + 'an'])
    # Imperative
    forms.update([stem + 'a', stem + 'e', stem + 'emos', stem + 'ad', stem + 'en', stem + 'ed', stem + 'id'])
    # Gerund & participle
    forms.add(stem + ('ando' if ending == 'ar' else 'iendo'))
    forms.add(stem + ('ado' if ending == 'ar' else 'ido'))
    
    # Stem-changing patterns (o→ue, e→ie, e→i)
    if 'o' in stem:
        ue_stem = stem.replace('o', 'ue')
        forms.update([ue_stem + s for s in ['o', 'as', 'a', 'amos', 'áis', 'an', 'e', 'es', 'emos', 'éis', 'en']])
    if 'e' in stem:
        ie_stem = stem.replace('e', 'ie')
        forms.update([ie_stem + s for s in ['o', 'as', 'a', 'amos', 'áis', 'an', 'e', 'es', 'emos', 'éis', 'en']])
        i_stem = stem.replace('e', 'i')
        forms.update([i_stem + s for s in ['o', 'es', 'e', 'imos', 'ís', 'en', 'ió', 'ieron']])
    
    # Irregular preterite stems
    forms.update([stem + 'iste', stem + 'imos', stem + 'isteis', stem + 'ieron'])
    forms.update([stem + 'í', stem + 'ió'])
    
    # Reflexive handling
    if lemma.endswith('se'):
        base = lemma[:-2]
        if base.endswith('r'):
            base_forms = generate_all_forms(base)
            forms.update(base_forms)
    
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
    
    # Try all conjugation forms
    all_forms = generate_all_forms(target_word)
    for form in sorted(all_forms, key=len, reverse=True):  # longest first
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
still_bad = 0
for card in cards:
    if card.get('sentence_cloze', '') == card.get('sentence_full', ''):
        result = find_and_replace(card['sentence_full'], card['target_word'])
        if result != card['sentence_full']:
            card['sentence_cloze'] = result
            fixed += 1
        else:
            still_bad += 1
            print(f"  STILL BAD: {card['id']}: '{card['target_word']}' in '{card['sentence_full']}'")

with open('src/data/LCDP_S3E07_cards.json', 'w', encoding='utf-8') as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

print(f"\nFixed: {fixed}, Still bad: {still_bad}")

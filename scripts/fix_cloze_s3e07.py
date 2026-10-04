"""
Fix sentence_cloze for S3E07 cards where target_word (lemma) doesn't match
conjugated forms in the sentence.
"""
import json
import re
import unicodedata

def normalize(text):
    """Remove accents for comparison."""
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')

def generate_conjugations(lemma):
    """Generate possible conjugated forms for a Spanish verb lemma."""
    if not lemma.endswith(('ar', 'er', 'ir')):
        return [lemma]
    
    stem = lemma[:-2]
    ending = lemma[-2:]
    forms = [lemma]  # infinitive
    
    # Present indicative
    if ending == 'ar':
        forms.extend([stem + 'o', stem + 'as', stem + 'a', stem + 'amos', stem + 'áis', stem + 'an'])
    elif ending == 'er':
        forms.extend([stem + 'o', stem + 'es', stem + 'e', stem + 'emos', stem + 'éis', stem + 'en'])
    elif ending == 'ir':
        forms.extend([stem + 'o', stem + 'es', stem + 'e', stem + 'imos', stem + 'ís', stem + 'en'])
    
    # Preterite
    if ending == 'ar':
        forms.extend([stem + 'é', stem + 'aste', stem + 'ó', stem + 'amos', stem + 'asteis', stem + 'aron'])
    elif ending == 'er':
        forms.extend([stem + 'í', stem + 'iste', stem + 'ió', stem + 'imos', stem + 'isteis', stem + 'ieron'])
    elif ending == 'ir':
        forms.extend([stem + 'í', stem + 'iste', stem + 'ió', stem + 'imos', stem + 'isteis', stem + 'ieron'])
    
    # Imperfect
    if ending == 'ar':
        forms.extend([stem + 'aba', stem + 'abas', stem + 'ábamos', stem + 'abais', stem + 'aban'])
    elif ending in ('er', 'ir'):
        forms.extend([stem + 'ía', stem + 'ías', stem + 'íamos', stem + 'íais', stem + 'ían'])
    
    # Future
    forms.extend([lemma[:-2] + 'é', lemma[:-2] + 'ás', lemma[:-2] + 'á', lemma[:-2] + 'emos', lemma[:-2] + 'éis', lemma[:-2] + 'án'])
    # Wait, future uses full infinitive + ending
    forms = [f for f in forms if f]  # remove empty
    forms.extend([lemma + 'é', lemma + 'ás', lemma + 'á', lemma + 'emos', lemma + 'éis', lemma + 'án'])
    
    # Conditional
    forms.extend([lemma + 'ía', lemma + 'ías', lemma + 'íamos', lemma + 'íais', lemma + 'ían'])
    
    # Present subjunctive
    if ending == 'ar':
        forms.extend([stem + 'e', stem + 'es', stem + 'emos', stem + 'éis', stem + 'en'])
    elif ending in ('er', 'ir'):
        forms.extend([stem + 'a', stem + 'as', stem + 'amos', stem + 'áis', stem + 'an'])
    
    # Imperative (tú, usted, nosotros, vosotros, ustedes)
    if ending == 'ar':
        forms.extend([stem + 'a', stem + 'e', stem + 'emos', stem + 'ad', stem + 'en'])
    elif ending == 'er':
        forms.extend([stem + 'e', stem + 'a', stem + 'amos', stem + 'ed', stem + 'an'])
    elif ending == 'ir':
        forms.extend([stem + 'e', stem + 'a', stem + 'amos', stem + 'id', stem + 'an'])
    
    # Gerund
    if ending == 'ar':
        forms.append(stem + 'ando')
    elif ending in ('er', 'ir'):
        forms.append(stem + 'iendo')
    
    # Past participle
    if ending == 'ar':
        forms.append(stem + 'ado')
    elif ending in ('er', 'ir'):
        forms.append(stem + 'ido')
    
    # Reflexive forms (for verbs ending in 'se')
    base_lemma = lemma.replace('se', '')
    if base_lemma != lemma:
        base_forms = generate_conjugations(base_lemma + 'ar' if base_lemma.endswith('a') else base_lemma + 'er' if base_lemma.endswith('e') else base_lemma + 'ir')
        forms.extend(base_forms)
    
    return list(set(forms))

def find_and_replace_cloze(sentence, target_word):
    """Find the target word (or its conjugation) in the sentence and replace with ___."""
    # First try exact match
    if target_word in sentence:
        return re.sub(re.escape(target_word), '___', sentence, count=1)
    
    # Try accent-insensitive match
    norm_target = normalize(target_word)
    words = sentence.split()
    for word in words:
        clean_word = re.sub(r'[.,!?;:¿¡"\'()\[\]]', '', word)
        if normalize(clean_word) == norm_target:
            return sentence.replace(word, '___', 1)
    
    # Try conjugations
    conjugations = generate_conjugations(target_word)
    for conj in conjugations:
        if conj in sentence:
            return re.sub(re.escape(conj), '___', sentence, count=1)
        # Accent-insensitive
        norm_conj = normalize(conj)
        words = sentence.split()
        for word in words:
            clean_word = re.sub(r'[.,!?;:¿¡"\'()\[\]]', '', word)
            if normalize(clean_word) == norm_conj and len(clean_word) >= 3:
                return sentence.replace(word, '___', 1)
    
    return sentence  # No match found

# Load cards
with open('src/data/LCDP_S3E07_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

fixed = 0
still_bad = 0
for card in cards:
    if card.get('sentence_cloze', '') == card.get('sentence_full', ''):
        result = find_and_replace_cloze(card['sentence_full'], card['target_word'])
        if result != card['sentence_full']:
            card['sentence_cloze'] = result
            fixed += 1
        else:
            still_bad += 1

# Save
with open('src/data/LCDP_S3E07_cards.json', 'w', encoding='utf-8') as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

print(f"Fixed: {fixed}, Still bad: {still_bad}")

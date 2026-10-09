"""
Fix S4E02 cloze using comprehensive conjugation matching.
"""
import json
import re
import unicodedata
import sys
import io
import os

_orig_fd = os.dup(1)
sys.path.insert(0, 'scripts')
from generate_spanish_ipa import word_to_ipa
sys.stdout = io.TextIOWrapper(os.fdopen(_orig_fd, 'w', encoding='utf-8', closefd=False), encoding='utf-8')

def normalize(text):
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')

def generate_all_forms(lemma):
    forms = set()
    forms.add(lemma)
    if not lemma.endswith(('ar', 'er', 'ir')):
        return forms
    stem = lemma[:-2]
    ending = lemma[-2:]
    all_endings = []
    for e in ['ar', 'er', 'ir']:
        if e == 'ar':
            all_endings.extend(['o','as','a','amos','áis','an','é','aste','ó','amos','asteis','aron',
                'aba','abas','ábamos','abais','aban','e','es','emos','éis','en',
                'a','e','emos','ad','en','ando','ado','ados','ada','adas'])
        elif e == 'er':
            all_endings.extend(['o','es','e','emos','éis','en','í','iste','ió','imos','isteis','ieron',
                'ía','ías','íamos','íais','ían','a','as','amos','áis','an',
                'e','a','amos','ed','an','iendo','ido','idos','ida','idas'])
        elif e == 'ir':
            all_endings.extend(['o','es','e','imos','ís','en','í','iste','ió','imos','isteis','ieron',
                'ía','ías','íamos','íais','ían','a','as','amos','áis','an',
                'e','a','amos','id','an','iendo','ido','idos','ida','idas'])
    all_endings.extend(['é','ás','á','emos','éis','án','ía','ías','íamos','íais','ían'])
    for end in all_endings:
        forms.add(stem + end)
        forms.add(lemma + end)
    if 'o' in stem:
        ue = stem.replace('o', 'ue')
        for end in all_endings: forms.add(ue + end)
    if 'e' in stem:
        ie = stem.replace('e', 'ie')
        for end in all_endings: forms.add(ie + end)
        i_stem = stem.replace('e', 'i')
        for end in all_endings: forms.add(i_stem + end)
    return forms

def fix_cloze(sentence, target_word):
    words = sentence.split()
    # Exact match
    if target_word in sentence:
        return re.sub(re.escape(target_word), '___', sentence, count=1)
    # Accent-insensitive
    norm_target = normalize(target_word)
    for word in words:
        clean = re.sub(r'[.,!?;:¿¡"\'()\[\]]', '', word)
        if normalize(clean) == norm_target:
            return sentence.replace(word, '___', 1)
    # Conjugations
    all_forms = generate_all_forms(target_word)
    for form in sorted(all_forms, key=len, reverse=True):
        for word in words:
            clean = re.sub(r'[.,!?;:¿¡"\'()\[\]]', '', word)
            if clean == form or normalize(clean) == normalize(form):
                if len(clean) == len(form):
                    return sentence.replace(word, '___', 1)
    return sentence

with open('src/data/LCDP_S4E02_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

fixed = 0
still_bad = []
for card in cards:
    if card.get('sentence_cloze', '') == card.get('sentence_full', ''):
        result = fix_cloze(card['sentence_full'], card['target_word'])
        if result != card['sentence_full']:
            card['sentence_cloze'] = result
            fixed += 1
        else:
            still_bad.append(card)

with open('src/data/LCDP_S4E02_cards.json', 'w', encoding='utf-8') as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

print(f"Fixed: {fixed}, Still bad: {len(still_bad)}")
for c in still_bad[:10]:
    print(f"  {c['id']}: '{c['target_word']}' in '{c['sentence_full'][:60]}'")

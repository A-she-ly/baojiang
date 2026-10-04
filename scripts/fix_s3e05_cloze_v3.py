"""
Fix remaining S3E05 cloze fields using Spanish conjugation patterns.
"""

import sys
import io
import json
import re
import unicodedata
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CARDS_PATH = Path(__file__).parent.parent / "src" / "data" / "LCDP_S3E05_cards.json"


def remove_accents(text):
    """Remove accents from text for comparison."""
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


def get_conjugation_forms(lemma):
    """Generate common Spanish conjugation forms from lemma."""
    forms = [lemma]
    
    if not lemma:
        return forms
    
    # Regular -ar verb conjugations
    if lemma.endswith('ar'):
        stem = lemma[:-2]
        forms.extend([
            stem + 'o',           # yo present
            stem + 'as',          # tú present
            stem + 'a',           # él/ella present
            stem + 'amos',        # nosotros present
            stem + 'áis',         # vosotros present
            stem + 'ais',         # vosotros present (no accent)
            stem + 'an',          # ellos present
            stem + 'é',           # yo preterite
            stem + 'aste',        # tú preterite
            stem + 'ó',           # él/ella preterite
            stem + 'o',           # él/ella preterite (no accent)
            stem + 'asteis',      # vosotros preterite
            stem + 'aron',        # ellos preterite
            stem + 'aba',         # yo imperfect
            stem + 'abas',        # tú imperfect
            stem + 'ábamos',      # nosotros imperfect
            stem + 'abamos',      # nosotros imperfect (no accent)
            stem + 'abais',       # vosotros imperfect
            stem + 'aban',        # ellos imperfect
            stem + 'aré',         # yo future
            stem + 'arás',        # tú future
            stem + 'aras',        # tú future (no accent)
            stem + 'ará',         # él/ella future
            stem + 'ara',         # él/ella future (no accent)
            stem + 'aremos',      # nosotros future
            stem + 'aréis',       # vosotros future
            stem + 'areis',       # vosotros future (no accent)
            stem + 'arán',        # ellos future
            stem + 'aran',        # ellos future (no accent)
            stem + 'aría',        # yo conditional
            stem + 'arías',       # tú conditional
            stem + 'arias',       # tú conditional (no accent)
            stem + 'aría',        # él/ella conditional
            stem + 'aria',        # él/ella conditional (no accent)
            stem + 'aríamos',     # nosotros conditional
            stem + 'ariamos',     # nosotros conditional (no accent)
            stem + 'aríais',      # vosotros conditional
            stem + 'ariais',      # vosotros conditional (no accent)
            stem + 'arían',       # ellos conditional
            stem + 'arian',       # ellos conditional (no accent)
            stem + 'ando',        # gerund
            stem + 'ado',         # past participle
        ])
    
    # Regular -er verb conjugations
    elif lemma.endswith('er'):
        stem = lemma[:-2]
        forms.extend([
            stem + 'o',           # yo present
            stem + 'es',          # tú present
            stem + 'e',           # él/ella present
            stem + 'emos',        # nosotros present
            stem + 'éis',         # vosotros present
            stem + 'eis',         # vosotros present (no accent)
            stem + 'en',          # ellos present
            stem + 'í',           # yo preterite
            stem + 'i',           # yo preterite (no accent)
            stem + 'iste',        # tú preterite
            stem + 'ió',          # él/ella preterite
            stem + 'io',          # él/ella preterite (no accent)
            stem + 'imos',        # nosotros preterite
            stem + 'isteis',      # vosotros preterite
            stem + 'ieron',       # ellos preterite
            stem + 'ía',          # yo imperfect
            stem + 'ias',         # tú imperfect (no accent)
            stem + 'íamos',       # nosotros imperfect
            stem + 'iamos',       # nosotros imperfect (no accent)
            stem + 'íais',        # vosotros imperfect
            stem + 'iais',        # vosotros imperfect (no accent)
            stem + 'ían',         # ellos imperfect
            stem + 'ian',         # ellos imperfect (no accent)
            stem + 'eré',         # yo future
            stem + 'ere',         # yo future (no accent)
            stem + 'erás',        # tú future
            stem + 'eras',        # tú future (no accent)
            stem + 'erá',         # él/ella future
            stem + 'era',         # él/ella future (no accent)
            stem + 'eremos',      # nosotros future
            stem + 'eréis',       # vosotros future
            stem + 'ereis',       # vosotros future (no accent)
            stem + 'erán',        # ellos future
            stem + 'eran',        # ellos future (no accent)
            stem + 'ería',        # yo conditional
            stem + 'eria',        # yo conditional (no accent)
            stem + 'erías',       # tú conditional
            stem + 'erias',       # tú conditional (no accent)
            stem + 'eríamos',     # nosotros conditional
            stem + 'eriamos',     # nosotros conditional (no accent)
            stem + 'eríais',      # vosotros conditional
            stem + 'eriais',      # vosotros conditional (no accent)
            stem + 'erían',       # ellos conditional
            stem + 'erian',       # ellos conditional (no accent)
            stem + 'iendo',       # gerund
            stem + 'ido',         # past participle
        ])
    
    # Regular -ir verb conjugations
    elif lemma.endswith('ir'):
        stem = lemma[:-2]
        forms.extend([
            stem + 'o',           # yo present
            stem + 'es',          # tú present
            stem + 'e',           # él/ella present
            stem + 'imos',        # nosotros present
            stem + 'ís',          # vosotros present
            stem + 'is',          # vosotros present (no accent)
            stem + 'en',          # ellos present
            stem + 'í',           # yo preterite
            stem + 'i',           # yo preterite (no accent)
            stem + 'iste',        # tú preterite
            stem + 'ió',          # él/ella preterite
            stem + 'io',          # él/ella preterite (no accent)
            stem + 'imos',        # nosotros preterite
            stem + 'isteis',      # vosotros preterite
            stem + 'ieron',       # ellos preterite
            stem + 'ía',          # yo imperfect
            stem + 'ias',         # tú imperfect (no accent)
            stem + 'íamos',       # nosotros imperfect
            stem + 'iamos',       # nosotros imperfect (no accent)
            stem + 'íais',        # vosotros imperfect
            stem + 'iais',        # vosotros imperfect (no accent)
            stem + 'ían',         # ellos imperfect
            stem + 'ian',         # ellos imperfect (no accent)
            stem + 'iré',         # yo future
            stem + 'ire',         # yo future (no accent)
            stem + 'irás',        # tú future
            stem + 'iras',        # tú future (no accent)
            stem + 'irá',         # él/ella future
            stem + 'ira',         # él/ella future (no accent)
            stem + 'iremos',      # nosotros future
            stem + 'iréis',       # vosotros future
            stem + 'ireis',       # vosotros future (no accent)
            stem + 'irán',        # ellos future
            stem + 'iran',        # ellos future (no accent)
            stem + 'iría',        # yo conditional
            stem + 'iria',        # yo conditional (no accent)
            stem + 'irías',       # tú conditional
            stem + 'irias',       # tú conditional (no accent)
            stem + 'iríamos',     # nosotros conditional
            stem + 'iriamos',     # nosotros conditional (no accent)
            stem + 'iríais',      # vosotros conditional
            stem + 'iria is',     # vosotros conditional (no accent)
            stem + 'irían',       # ellos conditional
            stem + 'irian',       # ellos conditional (no accent)
            stem + 'iendo',       # gerund
            stem + 'ido',         # past participle
        ])
    
    return forms


def find_word_in_sentence(sentence, target_word):
    """Find the actual word form in the sentence using conjugation patterns."""
    target_lower = target_word.lower()
    target_no_accents = remove_accents(target_lower)
    
    # Generate possible forms
    possible_forms = set()
    possible_forms.add(target_lower)
    possible_forms.add(target_no_accents)
    
    # Add conjugation forms
    for form in get_conjugation_forms(target_lower):
        possible_forms.add(form.lower())
        possible_forms.add(remove_accents(form.lower()))
    
    # Find all words in sentence
    words = re.findall(r'\b\w+\b', sentence)
    
    for word in words:
        word_lower = word.lower()
        word_no_accents = remove_accents(word_lower)
        
        if word_lower in possible_forms or word_no_accents in possible_forms:
            return word
    
    return None


def fix_remaining_clozes():
    """Fix remaining cloze fields in S3E05 cards."""
    with open(CARDS_PATH, 'r', encoding='utf-8') as f:
        cards = json.load(f)
    
    fixed_count = 0
    still_not_found = []
    
    for card in cards:
        target_word = card.get('target_word', '')
        sentence_full = card.get('sentence_full', '')
        sentence_cloze = card.get('sentence_cloze', '')
        
        # Check if cloze needs fixing
        if '___' not in sentence_cloze and target_word and sentence_full:
            actual_word = find_word_in_sentence(sentence_full, target_word)
            
            if actual_word:
                new_cloze = sentence_full.replace(actual_word, '___', 1)
                if new_cloze != sentence_cloze:
                    card['sentence_cloze'] = new_cloze
                    fixed_count += 1
            else:
                still_not_found.append((target_word, sentence_full[:50]))
    
    # Save updated cards
    with open(CARDS_PATH, 'w', encoding='utf-8') as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    
    print(f"Fixed {fixed_count} more cloze fields", flush=True)
    print(f"Still not found: {len(still_not_found)} cards", flush=True)
    for target, sentence in still_not_found[:10]:
        print(f"  {target}: {sentence}...", flush=True)


if __name__ == '__main__':
    fix_remaining_clozes()

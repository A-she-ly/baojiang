"""
Fix sentence_cloze fields in S3E05 cards.
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


def create_cloze(sentence, target_word):
    """Create cloze by replacing target_word (accent-insensitive) in sentence."""
    if not sentence or not target_word:
        return sentence
    
    # Remove accents from both for comparison
    sentence_no_accents = remove_accents(sentence.lower())
    target_no_accents = remove_accents(target_word.lower())
    
    if target_no_accents not in sentence_no_accents:
        return sentence
    
    # Try direct replacement first (case-insensitive)
    if target_word.lower() in sentence.lower():
        return re.sub(re.escape(target_word), '___', sentence, flags=re.IGNORECASE)
    
    # If direct match fails, try accent-insensitive match
    words = re.findall(r'\b\w+\b', sentence)
    for word in words:
        if remove_accents(word.lower()) == target_no_accents:
            return sentence.replace(word, '___', 1)
    
    return sentence


def fix_clozes():
    """Fix all cloze fields in S3E05 cards."""
    with open(CARDS_PATH, 'r', encoding='utf-8') as f:
        cards = json.load(f)
    
    fixed_count = 0
    for card in cards:
        target_word = card.get('target_word', '')
        sentence_full = card.get('sentence_full', '')
        sentence_cloze = card.get('sentence_cloze', '')
        
        # Check if cloze needs fixing
        if '___' not in sentence_cloze and target_word and sentence_full:
            new_cloze = create_cloze(sentence_full, target_word)
            if new_cloze != sentence_cloze:
                card['sentence_cloze'] = new_cloze
                fixed_count += 1
    
    # Save updated cards
    with open(CARDS_PATH, 'w', encoding='utf-8') as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    
    print(f"Fixed {fixed_count} cloze fields in S3E05", flush=True)


if __name__ == '__main__':
    fix_clozes()

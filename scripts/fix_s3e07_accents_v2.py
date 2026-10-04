"""
Fix S3E07 target_word accents by comparing with sentence_full.
The sentence_full has correct accents, but target_word may be missing them.
"""

import sys
import io
import json
import re
import unicodedata
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CARDS_PATH = Path(__file__).parent.parent / "src" / "data" / "LCDP_S3E07_cards.json"


def remove_accents(text):
    """Remove accents from text for comparison."""
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


def find_accented_form(sentence, target_word):
    """Find the correctly accented form of target_word in sentence."""
    target_unaccented = remove_accents(target_word.lower())
    
    # Find all words in sentence
    words = re.findall(r'\b\w+\b', sentence)
    
    for word in words:
        word_unaccented = remove_accents(word.lower())
        if word_unaccented == target_unaccented:
            return word.lower()
    
    return None


def fix_accents():
    """Fix target_word accents in S3E07 cards."""
    with open(CARDS_PATH, 'r', encoding='utf-8') as f:
        cards = json.load(f)
    
    fixed_count = 0
    for card in cards:
        target_word = card.get('target_word', '')
        sentence_full = card.get('sentence_full', '')
        
        if not target_word or not sentence_full:
            continue
        
        # Check if target_word has accents
        target_unaccented = remove_accents(target_word.lower())
        if target_word.lower() == target_unaccented:
            # Target word has no accents, try to find accented form in sentence
            accented_form = find_accented_form(sentence_full, target_word)
            if accented_form and accented_form != target_word.lower():
                card['target_word'] = accented_form
                # Update pos field
                pos_parts = card['pos'].split(' ', 1)
                if len(pos_parts) == 2:
                    card['pos'] = f"{pos_parts[0]} {accented_form}"
                fixed_count += 1
    
    # Save updated cards
    with open(CARDS_PATH, 'w', encoding='utf-8') as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    
    print(f"Fixed {fixed_count} target_word accents", flush=True)


if __name__ == '__main__':
    fix_accents()

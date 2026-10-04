"""
Translate S3E05 sentences using word-by-word translation from local dictionary.
This provides rough translations when API is not available.
"""

import sys
import io
import json
import re
from pathlib import Path

# Fix stdout encoding
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent.parent
CARDS_PATH = PROJECT_ROOT / "src" / "data" / "LCDP_S3E05_cards.json"

# Load the dictionary from the JSON file we created earlier
# We'll read it directly from the translate_s3e05_local.py file
DICT_FILE = PROJECT_ROOT / "scripts" / "translate_s3e05_local.py"

# Extract dictionary from the file
SPANISH_CHINESE_DICT = {}
with open(DICT_FILE, 'r', encoding='utf-8') as f:
    content = f.read()
    # Find the dictionary definition
    start = content.find('SPANISH_CHINESE_DICT = {')
    end = content.find('\n}', start) + 2
    dict_str = content[start:end]
    # Execute it to get the dictionary
    local_vars = {}
    exec(dict_str, {}, local_vars)
    SPANISH_CHINESE_DICT = local_vars.get('SPANISH_CHINESE_DICT', {})

print(f"Loaded dictionary with {len(SPANISH_CHINESE_DICT)} entries", flush=True)


def translate_sentence_word_by_word(sentence: str) -> str:
    """Translate sentence word by word using local dictionary."""
    if not sentence or not sentence.strip():
        return ''

    # Remove punctuation and split into words
    words = re.findall(r'\b\w+\b', sentence.lower())

    translated_words = []
    for word in words:
        # Try exact match
        if word in SPANISH_CHINESE_DICT:
            translated_words.append(SPANISH_CHINESE_DICT[word])
        else:
            # Keep original word if not in dictionary
            translated_words.append(word)

    # Join with spaces (simplified - doesn't handle grammar)
    return ' '.join(translated_words)


def main():
    print("Loading cards...", flush=True)
    with open(CARDS_PATH, 'r', encoding='utf-8') as f:
        cards = json.load(f)

    print(f"Total cards: {len(cards)}", flush=True)

    # Count cards needing sentence translation
    need_trans = [c for c in cards if not c.get('sentence_translation', '').strip() and c.get('sentence_full', '')]
    print(f"Need sentence translation: {len(need_trans)}", flush=True)

    if len(need_trans) == 0:
        print("All sentences already translated!", flush=True)
        return

    print(f"\nStarting word-by-word translation...", flush=True)

    translated_count = 0
    for idx, card in enumerate(need_trans):
        sent = card['sentence_full']
        trans = translate_sentence_word_by_word(sent)

        if trans:
            card['sentence_translation'] = trans
            translated_count += 1

        # Progress update every 100 cards
        if (idx + 1) % 100 == 0:
            print(f"  Progress: {idx + 1}/{len(need_trans)}", flush=True)

    print(f"\nDone! Translated: {translated_count}/{len(need_trans)}", flush=True)

    # Save
    with open(CARDS_PATH, 'w', encoding='utf-8') as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    print(f"Saved to {CARDS_PATH}", flush=True)

    # Show samples
    print("\n=== Sample translations ===", flush=True)
    count = 0
    for c in cards:
        if c.get('sentence_translation', '').strip():
            print(f"  ES: {c['sentence_full']}", flush=True)
            print(f"  ZH: {c['sentence_translation']}", flush=True)
            print(flush=True)
            count += 1
            if count >= 10:
                break


if __name__ == '__main__':
    main()

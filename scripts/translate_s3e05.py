"""
Batch translate S3E05 cards using MyMemory free translation API.
Adds Chinese translations for target_word and sentence_full.

MyMemory free tier: 5000 words/day, no API key needed.
Rate limit: ~1 req/sec recommended.

Run:
  python scripts/translate_s3e05.py
"""

import sys
import io
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=== Translation script started ===", flush=True)

PROJECT_ROOT = Path(__file__).parent.parent
CARDS_PATH = PROJECT_ROOT / "src" / "data" / "LCDP_S3E05_cards.json"

DELAY = 1.2  # seconds between API calls (safe for rate limit)


def translate(text: str, source='es', target='zh-CN') -> str:
    """Translate text using MyMemory API."""
    if not text or not text.strip():
        return ''
    url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(text)}&langpair={source}|{target}"
    req = urllib.request.Request(url, headers={'User-Agent': 'BaojiangEnglish/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        result = data.get('responseData', {}).get('translatedText', '')
        if result and result != text:
            return result
        # Fallback: try matches
        matches = data.get('matches', [])
        for m in matches:
            t = m.get('translation', '')
            if t and t != text:
                return t
        return text  # No good translation found
    except Exception as e:
        print(f"  API error: {e}")
        return ''


def main():
    print("Loading cards...", flush=True)
    with open(CARDS_PATH, 'r', encoding='utf-8') as f:
        cards = json.load(f)

    print(f"Total cards: {len(cards)}", flush=True)

    # Phase 1: Translate unique target words
    unique_words = {}
    for i, card in enumerate(cards):
        word = card['target_word']
        if word not in unique_words:
            unique_words[word] = []
        unique_words[word].append(i)

    word_translations = {}
    unique_list = list(unique_words.keys())
    print(f"\nPhase 1: Translating {len(unique_list)} unique words...", flush=True)

    for idx, word in enumerate(unique_list):
        trans = translate(word)
        word_translations[word] = trans if trans else word
        if (idx + 1) % 50 == 0:
            print(f"  Words: {idx + 1}/{len(unique_list)}", flush=True)
        time.sleep(DELAY)

    print(f"  Words: {len(unique_list)}/{len(unique_list)} done.", flush=True)

    # Apply word translations
    for card in cards:
        word = card['target_word']
        trans = word_translations.get(word, word)
        if card['pos'].startswith('v.'):
            card['translation'] = f"{trans}（动词原形）"
        else:
            card['translation'] = trans

    # Save intermediate result
    with open(CARDS_PATH, 'w', encoding='utf-8') as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    print("  Word translations saved.", flush=True)

    # Phase 2: Translate sentences
    print(f"\nPhase 2: Translating {len(cards)} sentences...", flush=True)
    for idx, card in enumerate(cards):
        sent = card.get('sentence_full', '')
        if sent:
            trans = translate(sent)
            card['sentence_translation'] = trans
        if (idx + 1) % 50 == 0:
            print(f"  Sentences: {idx + 1}/{len(cards)}", flush=True)
            # Save checkpoint
            with open(CARDS_PATH, 'w', encoding='utf-8') as f:
                json.dump(cards, f, ensure_ascii=False, indent=2)
        time.sleep(DELAY)

    print(f"  Sentences: {len(cards)}/{len(cards)} done.", flush=True)

    # Final save
    with open(CARDS_PATH, 'w', encoding='utf-8') as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    print(f"\nDone! All translations saved to {CARDS_PATH}", flush=True)

    # Show samples
    print("\n=== Sample translations ===", flush=True)
    for c in cards[:10]:
        print(f"  {c['target_word']} -> {c['translation']}", flush=True)
        print(f"    {c['sentence_full']}", flush=True)
        print(f"    {c['sentence_translation']}", flush=True)
        print()


if __name__ == '__main__':
    main()

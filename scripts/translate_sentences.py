"""
Translate S3E05 sentences using MyMemory API with conservative rate limiting.
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

PROJECT_ROOT = Path(__file__).parent.parent
CARDS_PATH = PROJECT_ROOT / "src" / "data" / "LCDP_S3E05_cards.json"

# Very conservative rate limiting: 5 seconds between requests
DELAY = 5.0


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
        return ''  # No good translation found
    except Exception as e:
        print(f"  API error: {e}", flush=True)
        return ''


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

    print(f"\nStarting translation with {DELAY}s delay between requests...", flush=True)
    print(f"Estimated time: {len(need_trans) * DELAY / 60:.1f} minutes", flush=True)

    translated_count = 0
    error_count = 0

    for idx, card in enumerate(need_trans):
        sent = card['sentence_full']
        trans = translate(sent)

        if trans:
            card['sentence_translation'] = trans
            translated_count += 1
        else:
            error_count += 1

        # Progress update every 10 cards
        if (idx + 1) % 10 == 0:
            print(f"  Progress: {idx + 1}/{len(need_trans)} (translated: {translated_count}, errors: {error_count})", flush=True)
            # Save checkpoint
            with open(CARDS_PATH, 'w', encoding='utf-8') as f:
                json.dump(cards, f, ensure_ascii=False, indent=2)

        time.sleep(DELAY)

    print(f"\nDone! Translated: {translated_count}, Errors: {error_count}", flush=True)

    # Final save
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
            if count >= 5:
                break


if __name__ == '__main__':
    main()

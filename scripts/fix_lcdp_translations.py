"""
补全 LCDP S3E01 名词卡片的中文翻译
使用 MyMemory Translation API (免费，无需 API key)
支持断点续传：每10个词保存一次进度
"""
import json
import sys
import time
import io
import urllib.request
import urllib.parse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_FILE = "src/data/LCDP_S3E01_nouns_cards.json"

def translate_word(word: str, max_retries: int = 2) -> str:
    """Translate using MyMemory API"""
    for attempt in range(max_retries):
        try:
            # MyMemory API: free, no key required
            url = (
                f"https://api.mymemory.translated.net/get"
                f"?q={urllib.parse.quote(word)}&langpair=es|zh-CN"
            )
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                # Response: {"responseData": {"translatedText": "..."}}
                translated = data.get("responseData", {}).get("translatedText", "")
                if translated:
                    return translated
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(0.5)
            else:
                print(f"  ERROR: {e}")
                return ""
    return ""

def save(cards):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)

def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        cards = json.load(f)

    # Find unique words missing translation
    missing_words = []
    seen = set()
    for card in cards:
        w = card.get("target_word", "").strip().lower()
        if w and w not in seen and (not card.get("translation") or not card["translation"].strip()):
            missing_words.append(w)
            seen.add(w)

    # Also collect words that already have translation (to skip)
    has_trans = set()
    for card in cards:
        w = card.get("target_word", "").strip().lower()
        if w and card.get("translation") and card["translation"].strip():
            has_trans.add(w)

    print(f"Total cards: {len(cards)}")
    print(f"Already translated: {len(has_trans)} unique words")
    print(f"Need translation: {len(missing_words)} unique words")

    updated_total = 0
    batch = 0

    for i, word in enumerate(missing_words):
        print(f"[{i+1}/{len(missing_words)}] {word}", end="", flush=True)
        result = translate_word(word)
        if result:
            # Apply to all cards with this word
            count = 0
            for card in cards:
                if card.get("target_word", "").strip().lower() == word and (not card.get("translation") or not card["translation"].strip()):
                    card["translation"] = result
                    count += 1
            updated_total += count
            print(f" -> {result} ({count} cards)")
        else:
            print(" -> FAILED")

        batch += 1
        if batch % 10 == 0:
            save(cards)
            print(f"  [Saved progress: {updated_total} cards updated]")
        time.sleep(0.2)

    # Final save
    save(cards)
    print(f"\nDone! Total updated: {updated_total} cards")

if __name__ == "__main__":
    main()

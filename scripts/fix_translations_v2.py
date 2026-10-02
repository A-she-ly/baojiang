"""
修复 LCDP S3E01 名词卡片的中文翻译
1. 修复翻译错误的卡片（translation = target_word）
2. 补全缺失翻译的卡片
使用 MyMemory Translation API (免费，无需 API key)
"""
import json
import sys
import time
import io
import urllib.request
import urllib.parse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_FILE = "src/data/LCDP_S3E01_nouns_cards.json"

# 手动修正的翻译（MyMemory 可能翻译不准确）
MANUAL_TRANSLATIONS = {
    "casita": "小房子",
    "chunda": "派对音乐（拟声词）",
    "guindo": "酸樱桃",
    "hijaputa": "婊子养的",
    "jarana": "狂欢",
    "jefe": "老板",
    "liarla": "搞砸",
    "loca": "疯女人",
    "m16": "M16步枪",
    "prieto": "黑暗的",
    "puto": "混蛋",
    "robin": "罗宾（人名）",
    "solo": "独自",
    "tatiana": "塔蒂亚娜（人名）",
}

def translate_word(word: str, max_retries: int = 2) -> str:
    """Translate using MyMemory API"""
    for attempt in range(max_retries):
        try:
            url = (
                f"https://api.mymemory.translated.net/get"
                f"?q={urllib.parse.quote(word)}&langpair=es|zh-CN"
            )
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
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

    # 1. 修复错误翻译（translation = target_word）
    print("=" * 50)
    print("修复错误翻译...")
    print("=" * 50)
    fixed_count = 0
    for card in cards:
        w = card.get("target_word", "").strip().lower()
        trans = card.get("translation", "").strip()
        if w and trans and trans.lower() == w.lower():
            if w in MANUAL_TRANSLATIONS:
                card["translation"] = MANUAL_TRANSLATIONS[w]
                print(f"  {w} -> {MANUAL_TRANSLATIONS[w]} (手动修正)")
                fixed_count += 1

    print(f"\n修复了 {fixed_count} 张错误翻译卡片")

    # 2. 补全缺失翻译
    print("\n" + "=" * 50)
    print("补全缺失翻译...")
    print("=" * 50)

    # 收集需要翻译的单词
    missing_words = []
    seen = set()
    for card in cards:
        w = card.get("target_word", "").strip().lower()
        if w and w not in seen and (not card.get("translation") or not card["translation"].strip()):
            missing_words.append(w)
            seen.add(w)

    print(f"需要翻译: {len(missing_words)} 个单词\n")

    updated_total = 0
    batch = 0

    for i, word in enumerate(missing_words):
        print(f"[{i+1}/{len(missing_words)}] {word}", end="", flush=True)
        result = translate_word(word)
        if result:
            count = 0
            for card in cards:
                if card.get("target_word", "").strip().lower() == word and (not card.get("translation") or not card["translation"].strip()):
                    card["translation"] = result
                    count += 1
            updated_total += count
            print(f" -> {result} ({count} 张卡片)")
        else:
            print(" -> 失败")

        batch += 1
        if batch % 10 == 0:
            save(cards)
            print(f"  [保存进度: {updated_total} 张卡片已更新]")
        time.sleep(0.2)

    # 最终保存
    save(cards)
    
    # 统计
    good = sum(1 for c in cards if c.get("translation") and c["translation"].lower() != c.get("target_word", "").lower())
    bad = sum(1 for c in cards if c.get("translation") and c["translation"].lower() == c.get("target_word", "").lower())
    none = sum(1 for c in cards if not c.get("translation"))
    
    print(f"\n{'=' * 50}")
    print(f"完成！统计:")
    print(f"  总卡片数: {len(cards)}")
    print(f"  有正确翻译: {good}")
    print(f"  翻译错误: {bad}")
    print(f"  无翻译: {none}")
    print(f"  覆盖率: {good}/{len(cards)} ({100*good/len(cards):.1f}%)")

if __name__ == "__main__":
    main()

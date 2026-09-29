"""
Script: generate_noun_cards.py
Purpose:
  1. Read nouns from "名词汇总" sheet in La_Casa_de_Papel_S3E01_台词.xlsx
  2. Read dialogue lines from "纸钞屋 S3E01 台词" sheet
  3. For each noun, find dialogue lines containing it (up to 3 contexts)
  4. Generate flashcard JSON files for noun classification
  5. Output: LCDP_S3E01_nouns_cards.json, LCDP_S3E01_nouns_metadata.json

Run:
  python scripts/generate_noun_cards.py
"""

from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

try:
    import openpyxl
except ImportError:
    print("ERROR: openpyxl not installed. Run: pip install openpyxl", file=sys.stderr)
    sys.exit(1)

# Import etymology dictionary
sys.path.insert(0, str(Path(__file__).parent))
from spanish_etymology import ETYMOLOGY_DICT


# ---------------------------------------------------------------------------
# Read nouns from "名词汇总" sheet
# ---------------------------------------------------------------------------
def read_nouns(xlsx_path: Path) -> List[Dict[str, Any]]:
    """Read nouns from the 名词汇总 sheet."""
    wb = openpyxl.load_workbook(str(xlsx_path), read_only=True)
    ws = wb['名词汇总']
    nouns = []
    for row in range(2, ws.max_row + 1):
        no = ws.cell(row, 1).value
        noun = ws.cell(row, 2).value
        count = ws.cell(row, 3).value
        if noun and isinstance(noun, str) and noun.strip():
            nouns.append({
                'no': no,
                'noun': noun.strip(),
                'count': int(count) if count else 1,
            })
    wb.close()
    return nouns


# ---------------------------------------------------------------------------
# Read dialogue lines from "纸钞屋 S3E01 台词" sheet
# ---------------------------------------------------------------------------
def read_dialogue(xlsx_path: Path) -> List[Dict[str, Any]]:
    """Read dialogue lines from the 纸钞屋 S3E01 台词 sheet."""
    wb = openpyxl.load_workbook(str(xlsx_path), read_only=True)
    ws = wb['纸钞屋 S3E01 台词']
    lines = []
    for row in range(2, ws.max_row + 1):
        seq = ws.cell(row, 1).value
        espanol = ws.cell(row, 2).value
        chinese = ws.cell(row, 3).value
        keywords = ws.cell(row, 4).value
        collocations = ws.cell(row, 5).value
        if espanol and isinstance(espanol, str) and espanol.strip():
            lines.append({
                'seq': int(seq) if seq else row - 1,
                'espanol': espanol.strip(),
                'chinese': (chinese.strip() if chinese and isinstance(chinese, str) else ''),
                'keywords': (keywords.strip() if keywords and isinstance(keywords, str) else ''),
                'collocations': (collocations.strip() if collocations and isinstance(collocations, str) else ''),
            })
    wb.close()
    return lines


# ---------------------------------------------------------------------------
# Find dialogue lines containing a noun
# ---------------------------------------------------------------------------
def find_noun_contexts(noun: str, dialogue_lines: List[Dict], max_results: int = 3) -> List[Dict]:
    """Find dialogue lines containing the noun (case-insensitive, whole word)."""
    results = []
    # Escape for regex
    escaped = re.escape(noun.lower())
    # Word boundary pattern - handle accented chars
    pattern = re.compile(r'(?<!\w)' + escaped + r'(?!\w)', re.IGNORECASE)

    for line in dialogue_lines:
        text = line['espanol']
        if pattern.search(text):
            results.append({
                'espanol': text,
                'chinese': line['chinese'],
                'seq': line['seq'],
                'keywords': line['keywords'],
            })
            if len(results) >= max_results:
                break
    return results


# ---------------------------------------------------------------------------
# Pronunciation focus heuristic
# ---------------------------------------------------------------------------
def guess_pronunciation_focus(noun: str) -> str:
    """Guess Spanish pronunciation focus based on spelling."""
    n = noun.lower()
    if n.startswith('h'):
        return 'silent_h'
    if 'rr' in n:
        return 'rolled_r'
    if n.startswith('r') and len(n) > 1 and n[1].isalpha():
        return 'rolled_r'
    if re.search(r'(?<=[aeiou])r(?=[aeiou])', n):
        return 'tapped_r'
    if 'ñ' in n:
        return 'ny_sound'
    if 'll' in n:
        return 'll_y'
    if 'j' in n:
        return 'j_sound'
    if re.search(r'g[ei]', n):
        return 'j_sound'
    if 'z' in n:
        return 'c_z_distinction'
    if re.search(r'c[ei]', n):
        return 'c_z_distinction'
    if 'ie' in n or 'ue' in n or 'ui' in n:
        return 'diphthong'
    # Default based on last vowel
    for ch in reversed(n):
        if ch in 'a':
            return 'vowel_a'
        if ch in 'e':
            return 'vowel_e'
        if ch in 'i':
            return 'vowel_i'
        if ch in 'o':
            return 'vowel_o'
        if ch in 'u':
            return 'vowel_u'
    return 'vowel_a'


# ---------------------------------------------------------------------------
# Cloze generation
# ---------------------------------------------------------------------------
def make_cloze(sentence: str, target: str) -> str:
    """Replace target word in sentence with ___ blank."""
    escaped = re.escape(target)
    result = re.sub(r'(?<!\w)(' + escaped + r')(?!\w)', '___', sentence, count=1, flags=re.IGNORECASE)
    if result == sentence:
        # Try without word boundary (for accented/case differences)
        result = re.sub(re.escape(target), '___', sentence, count=1, flags=re.IGNORECASE)
    return result


# ---------------------------------------------------------------------------
# Level estimation
# ---------------------------------------------------------------------------
def guess_level(noun: str, count: int) -> str:
    """Estimate CEFR level based on frequency and word characteristics."""
    if count >= 7:
        return 'A1'
    if count >= 4:
        return 'A2'
    if count >= 2:
        return 'B1'
    return 'B2'


# ---------------------------------------------------------------------------
# Guess gender from article/noun ending
# ---------------------------------------------------------------------------
def guess_gender(noun: str) -> str:
    """Guess noun gender: m. (masculine) or f. (feminine)."""
    n = noun.lower()
    # Exceptions: el problema, el sistema, etc.
    masculine_exceptions = {'problema', 'sistema', 'planeta', 'tema', 'mapa', 'día', 'idioma'}
    feminine_exceptions = {'mano', 'radio', 'foto'}

    if n in feminine_exceptions:
        return 'f.'
    if n in masculine_exceptions:
        return 'm.'
    if n.endswith('a') or n.endswith('ción') or n.endswith('sión') or n.endswith('dad') or n.endswith('tad') or n.endswith('umbre'):
        return 'f.'
    return 'm.'


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    root = Path(__file__).resolve().parent.parent
    xlsx_path = root / "Money Heist" / "La_Casa_de_Papel_S3E01_台词.xlsx"

    if not xlsx_path.exists():
        print(f"ERROR: xlsx not found: {xlsx_path}", file=sys.stderr)
        return 1

    print("Reading nouns from xlsx...")
    nouns = read_nouns(xlsx_path)
    print(f"  Found {len(nouns)} nouns")

    print("Reading dialogue lines from xlsx...")
    dialogue = read_dialogue(xlsx_path)
    print(f"  Found {len(dialogue)} dialogue lines")

    print("Matching nouns to dialogue contexts...")
    cards = []
    skipped = 0
    for item in nouns:
        noun = item['noun']
        count = item['count']

        contexts = find_noun_contexts(noun, dialogue, max_results=3)
        if not contexts:
            skipped += 1
            continue

        gender = guess_gender(noun)
        pos = f"n.{gender} {noun}"
        level = guess_level(noun, count)
        pron_focus = guess_pronunciation_focus(noun)

        # Primary context (first occurrence)
        first = contexts[0]
        sentence_full = first['espanol']
        sentence_cloze = make_cloze(sentence_full, noun)
        sentence_translation = first['chinese']

        # Get etymology info if available
        etymology_info = ETYMOLOGY_DICT.get(noun.lower())
        translation_cn = etymology_info['translation'] if etymology_info else ''
        etymology = etymology_info['breakdown'] if etymology_info else None

        # Build tags
        tags = ['名词']
        if count >= 5:
            tags.append('高频')
        elif count >= 3:
            tags.append('中频')
        if level in ('A1', 'A2'):
            tags.append('基础')
        elif level in ('C1', 'C2'):
            tags.append('高级')

        card = {
            "id": f"LCDP_S3E01_{len(cards)+1:03d}",
            "episode": "S3E01",
            "scene_id": f"line_{first['seq']:03d}",
            "line_index": len(cards) + 1,
            "character": "S3E01",
            "target_word": noun,
            "ipa": "",
            "pos": pos,
            "level": level,
            "pronunciation_focus": pron_focus,
            "tags": tags,
            "sentence_cloze": sentence_cloze,
            "sentence_full": sentence_full,
            "translation": translation_cn,  # 单词中文释义（从词源字典获取）
            "sentence_translation": sentence_translation,
            "cultural_note": "",
            "screenshot": "",
            "frequency_rank": None,
            "is_example_sentence": False,
        }

        # Add etymology breakdown if available
        if etymology:
            card["etymology"] = etymology

        # Store multiple contexts (up to 3)
        if len(contexts) > 1:
            card["context_examples"] = [
                {"espanol": c['espanol'], "chinese": c['chinese'], "seq": c['seq']}
                for c in contexts
            ]

        cards.append(card)

    print(f"  Generated {len(cards)} noun cards ({skipped} nouns with no context found)")

    # Build metadata
    metadata = {
        "episode": "S3E01",
        "title": "Nouns from S3E01",
        "title_cn": "第三季第一集名词汇总",
        "description": "名词分类 — 从纸钞屋第三季第一集台词中提取的名词闪卡，每张卡背面展示台词上下文。",
        "scenes_count": 0,
        "dialogue_lines_count": len(dialogue),
        "characters": [],
        "scenes_summary": [],
    }

    # Write output files
    src_data_dir = root / "src" / "data"
    src_data_dir.mkdir(parents=True, exist_ok=True)

    cards_path = src_data_dir / "LCDP_S3E01_nouns_cards.json"
    meta_path = src_data_dir / "LCDP_S3E01_nouns_metadata.json"

    cards_path.write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n[OK] Cards:   {cards_path} ({len(cards)} cards)")
    print(f"[OK] Metadata: {meta_path}")

    # Stats
    levels = {}
    for c in cards:
        levels[c['level']] = levels.get(c['level'], 0) + 1
    print(f"\nLevel distribution:")
    for lv in sorted(levels.keys()):
        print(f"  {lv}: {levels[lv]}")

    multi = sum(1 for c in cards if 'context_examples' in c and len(c['context_examples']) > 1)
    print(f"\nNouns with multiple contexts: {multi}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

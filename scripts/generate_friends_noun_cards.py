"""
Script: generate_friends_noun_cards.py
Purpose:
  1. Read nouns from "名词汇总" sheet in Friends_S01E01_台词.xlsx
  2. Read dialogue lines from "台词" sheet
  3. For each noun, find dialogue lines containing it (up to 3 contexts)
  4. Generate flashcard JSON files for Friends S01E01 noun classification
  5. Output: Friends_S01E01_nouns_cards.json, Friends_S01E01_nouns_metadata.json

Run:
  python scripts/generate_friends_noun_cards.py
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
from english_etymology import ETYMOLOGY_DICT
from friends_translations import SENTENCE_TRANSLATIONS


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
# Read dialogue lines from "台词" sheet
# ---------------------------------------------------------------------------
def read_dialogue(xlsx_path: Path) -> List[Dict[str, Any]]:
    """Read dialogue lines from the 台词 sheet.
    Friends xlsx structure:
      Col 1: 序号 (seq)
      Col 2: 场景 (Scene)
      Col 3: 角色 (Speaker)
      Col 4: 台词 (English)
    Note: No Chinese translation column in Friends xlsx.
    """
    wb = openpyxl.load_workbook(str(xlsx_path), read_only=True)
    ws = wb['台词']
    lines = []
    for row in range(2, ws.max_row + 1):
        seq = ws.cell(row, 1).value
        scene = ws.cell(row, 2).value
        speaker = ws.cell(row, 3).value
        english = ws.cell(row, 4).value
        if english and isinstance(english, str) and english.strip():
            text = english.strip()
            # Remove scene descriptions in brackets, e.g. [Scene: ...]
            text = re.sub(r'\[Scene:.*?\]', '', text, flags=re.IGNORECASE).strip()
            text = re.sub(r'\[.*?Scene:.*?\]', '', text, flags=re.IGNORECASE).strip()
            if not text:
                continue
            lines.append({
                'seq': int(seq) if seq else row - 1,
                'scene': (scene.strip() if scene and isinstance(scene, str) else ''),
                'speaker': (speaker.strip() if speaker and isinstance(speaker, str) else ''),
                'english': text,
                'chinese': '',  # No Chinese translation in Friends xlsx
            })
    wb.close()
    return lines


# ---------------------------------------------------------------------------
# Find dialogue lines containing a noun
# ---------------------------------------------------------------------------
def find_noun_contexts(noun: str, dialogue_lines: List[Dict], max_results: int = 3) -> List[Dict]:
    """Find dialogue lines containing the noun (case-insensitive, whole word).
    Only matches against spoken dialogue — parenthetical stage directions are excluded.
    """
    results = []
    # Escape for regex
    escaped = re.escape(noun.lower())
    # Word boundary pattern
    pattern = re.compile(r'(?<!\w)' + escaped + r'(?!\w)', re.IGNORECASE)

    for line in dialogue_lines:
        raw_text = line['english']
        # Remove parenthetical stage directions for matching
        spoken = re.sub(r'\([^)]*\)', '', raw_text).strip()
        # Also remove bracketed stage directions
        spoken = re.sub(r'\[[^\]]*\]', '', spoken).strip()
        # Only match against spoken dialogue
        if not spoken or not pattern.search(spoken):
            continue
        results.append({
            'english': spoken,  # Store cleaned spoken dialogue only
            'chinese': line.get('chinese', ''),
            'seq': line['seq'],
            'scene': line.get('scene', ''),
            'speaker': line.get('speaker', ''),
        })
        if len(results) >= max_results:
            break
    return results


# ---------------------------------------------------------------------------
# Pronunciation focus heuristic (English GenAm)
# ---------------------------------------------------------------------------
def guess_pronunciation_focus(noun: str) -> str:
    """Guess English pronunciation focus based on spelling."""
    n = noun.lower()
    
    # Flap T: water, better, city
    if re.search(r'[aeiou]t[aeiou]', n) or n.endswith('ty'):
        return 'flap_t'
    
    # R-colored: car, bird, work
    if re.search(r'[aeiou]r\b', n) or re.search(r'er\b', n) or re.search(r'ir', n) or re.search(r'ur', n):
        return 'r_colored'
    
    # Long E: see, tree, key
    if re.search(r'ee\b', n) or re.search(r'ey\b', n) or n.endswith('y'):
        return 'long_e'
    
    # O diphthong: go, phone, cold
    if re.search(r'o[aeiou]', n) or re.search(r'oa', n) or re.search(r'ow\b', n):
        return 'o_diphthong'
    
    # Short vowels
    if re.search(r'[aeiou][^aeiou]{2}\b', n):
        if 'a' in n[:3]:
            return 'vowel_ae'  # cat
        if 'e' in n[:3]:
            return 'vowel_eh'  # bed
        if 'i' in n[:3]:
            return 'vowel_ih'  # sit
        if 'u' in n[:3]:
            return 'vowel_uh'  # cup
    
    # Schwa: about, banana
    if len(n) > 5 and n[0] in 'aeiou':
        return 'schwa'
    
    # Y-glide: yes, you
    if n.startswith('y') and len(n) > 1:
        return 'y_glide'
    
    # Default
    return 'vowel_ah'


# ---------------------------------------------------------------------------
# Cloze generation
# ---------------------------------------------------------------------------
def make_cloze(sentence: str, target: str) -> str:
    """Replace target word in sentence with ___ blank."""
    escaped = re.escape(target)
    result = re.sub(r'(?<!\w)(' + escaped + r')(?!\w)', '___', sentence, count=1, flags=re.IGNORECASE)
    if result == sentence:
        # Try without word boundary
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
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    root = Path(__file__).resolve().parent.parent
    xlsx_path = root / "Friends" / "Friends_S01E01_台词.xlsx"

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

        pos = f"n. {noun}"
        level = guess_level(noun, count)
        pron_focus = guess_pronunciation_focus(noun)

        # Primary context (first occurrence)
        first = contexts[0]
        sentence_full = first['english']
        sentence_cloze = make_cloze(sentence_full, noun)
        # Look up Chinese translation from translations dict
        sentence_translation = SENTENCE_TRANSLATIONS.get(sentence_full, '')

        # Get etymology info if available
        etymology_info = ETYMOLOGY_DICT.get(noun.lower())
        translation_cn = etymology_info['translation'] if etymology_info else ''
        etymology = etymology_info['breakdown'] if etymology_info else None

        # Build tags
        tags = ['noun']
        if count >= 5:
            tags.append('high-frequency')
        elif count >= 3:
            tags.append('mid-frequency')
        if level in ('A1', 'A2'):
            tags.append('basic')
        elif level in ('C1', 'C2'):
            tags.append('advanced')

        card = {
            "id": f"FRIENDS_S01E01_{len(cards)+1:03d}",
            "episode": "S01E01",
            "scene_id": f"line_{first['seq']:03d}",
            "line_index": len(cards) + 1,
            "character": "Friends",
            "target_word": noun,
            "ipa": "",
            "pos": pos,
            "level": level,
            "pronunciation_focus": pron_focus,
            "tags": tags,
            "sentence_cloze": sentence_cloze,
            "sentence_full": sentence_full,
            "translation": translation_cn,  # Chinese translation from etymology dict
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
                {"english": c['english'], "chinese": SENTENCE_TRANSLATIONS.get(c['english'], ''), "seq": c['seq']}
                for c in contexts
            ]

        cards.append(card)

    print(f"  Generated {len(cards)} noun cards ({skipped} nouns with no context found)")

    # Build metadata
    metadata = {
        "episode": "S01E01",
        "title": "Nouns from S01E01",
        "title_cn": "第一季第一集名词汇总",
        "description": "名词分类 — 从老友记第一季第一集台词中提取的名词闪卡，每张卡背面展示台词上下文。",
        "scenes_count": 0,
        "dialogue_lines_count": len(dialogue),
        "characters": [],
        "scenes_summary": [],
    }

    # Write output files
    src_data_dir = root / "src" / "data"
    src_data_dir.mkdir(parents=True, exist_ok=True)

    cards_path = src_data_dir / "Friends_S01E01_nouns_cards.json"
    meta_path = src_data_dir / "Friends_S01E01_nouns_metadata.json"

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

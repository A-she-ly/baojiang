"""
Generate S3E07 flashcards from La Casa de Papel Excel file.
Uses S3E05E07 shared vocabulary sheets and S3E07 dialogue.
Deduplicates against existing S3E05 cards.

Run:
  python scripts/generate_s3e07_cards.py
"""

import sys
import io
import json
import re
from pathlib import Path
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import openpyxl

PROJECT_ROOT = Path(__file__).parent.parent
EXCEL_PATH = PROJECT_ROOT / "Money Heist" / "La_Casa_de_Papel_S3E01_台词.xlsx"
S3E05_CARDS_PATH = PROJECT_ROOT / "src" / "data" / "LCDP_S3E05_cards.json"
OUTPUT_CARDS_PATH = PROJECT_ROOT / "src" / "data" / "LCDP_S3E07_cards.json"
OUTPUT_META_PATH = PROJECT_ROOT / "src" / "data" / "LCDP_S3E07_metadata.json"


def load_existing_s3e05_words():
    """Load existing S3E05 card target words for deduplication."""
    if not S3E05_CARDS_PATH.exists():
        return set()
    with open(S3E05_CARDS_PATH, 'r', encoding='utf-8') as f:
        cards = json.load(f)
    return {c['target_word'].lower() for c in cards}


def load_s3e07_dialogue():
    """Load S3E07 dialogue from Excel."""
    wb = openpyxl.load_workbook(str(EXCEL_PATH), data_only=True)
    ws = wb['纸钞屋 S3E07 台词']
    
    dialogues = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] and row[1]:  # Has sequence number and Spanish text
            dialogues.append({
                'seq': row[0],
                'spanish': str(row[1]).strip(),
                'chinese': str(row[2]).strip() if row[2] else ''
            })
    
    print(f"Loaded {len(dialogues)} S3E07 dialogue lines", flush=True)
    return dialogues


def load_s3e05e07_vocab():
    """Load S3E05E07 shared vocabulary (动词, 名词, 副词)."""
    wb = openpyxl.load_workbook(str(EXCEL_PATH), data_only=True)
    
    vocab = {'verbs': [], 'nouns': [], 'adverbs': [], 'adjectives': []}
    
    # Load verbs
    if 'S3E05E07 动词' in wb.sheetnames:
        ws = wb['S3E05E07 动词']
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0] and row[1]:
                vocab['verbs'].append({
                    'lemma': str(row[1]).strip(),
                    'translation': str(row[2]).strip() if row[2] else '',
                    'forms': str(row[3]).strip() if row[3] else '',
                    'example_es': str(row[4]).strip() if row[4] else '',
                    'example_zh': str(row[5]).strip() if row[5] else ''
                })
        print(f"Loaded {len(vocab['verbs'])} verbs from S3E05E07", flush=True)
    
    # Load nouns
    if 'S3E05E07 名词' in wb.sheetnames:
        ws = wb['S3E05E07 名词']
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0] and row[1]:
                vocab['nouns'].append({
                    'word': str(row[1]).strip(),
                    'translation': str(row[2]).strip() if row[2] else '',
                    'frequency': row[3] if row[3] else 0,
                    'example_es': str(row[4]).strip() if row[4] else '',
                    'example_zh': str(row[5]).strip() if row[5] else ''
                })
        print(f"Loaded {len(vocab['nouns'])} nouns from S3E05E07", flush=True)
    
    # Load adverbs
    if 'S3E05E07 副词' in wb.sheetnames:
        ws = wb['S3E05E07 副词']
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0] and row[1]:
                vocab['adverbs'].append({
                    'base': str(row[1]).strip(),
                    'translation': str(row[2]).strip() if row[2] else '',
                    'forms': str(row[3]).strip() if row[3] else '',
                    'example_es': str(row[4]).strip() if row[4] else '',
                    'example_zh': str(row[5]).strip() if row[5] else ''
                })
        print(f"Loaded {len(vocab['adverbs'])} adverbs from S3E05E07", flush=True)
    
    # Load adjectives
    if 'S3E05E07 形容词' in wb.sheetnames:
        ws = wb['S3E05E07 形容词']
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0] and row[1]:
                vocab['adjectives'].append({
                    'base': str(row[1]).strip(),
                    'translation': str(row[2]).strip() if row[2] else '',
                    'forms': str(row[3]).strip() if row[3] else '',
                    'example_es': str(row[4]).strip() if row[4] else '',
                    'example_zh': str(row[5]).strip() if row[5] else ''
                })
        print(f"Loaded {len(vocab['adjectives'])} adjectives from S3E05E07", flush=True)
    
    return vocab


def generate_cards_from_vocab(vocab, existing_words, dialogues):
    """Generate flashcards from vocabulary, deduplicating against S3E05."""
    cards = []
    card_id = 1
    
    # Create a lookup for dialogue examples
    dialogue_lookup = {}
    for d in dialogues:
        spanish_lower = d['spanish'].lower()
        dialogue_lookup[spanish_lower] = d
    
    # Generate verb cards
    for v in vocab['verbs']:
        lemma = v['lemma'].lower()
        if lemma in existing_words:
            continue
        
        # Find example from dialogue or use vocab example
        example_es = v['example_es']
        example_zh = v['example_zh']
        
        # Try to find a matching dialogue line
        for form in v['forms'].split(','):
            form_clean = form.strip().lower()
            for d in dialogues:
                if form_clean in d['spanish'].lower():
                    example_es = d['spanish']
                    example_zh = d['chinese']
                    break
        
        cards.append({
            'id': f'LCDP_S3E07_{card_id:03d}',
            'episode': 'S3E07',
            'scene_id': f'line_s3e07_{card_id:03d}',
            'line_index': card_id,
            'character': 'S3E07',
            'target_word': lemma,
            'ipa': '',  # Will be generated later
            'pos': f'v. {lemma}',
            'level': 'B2',
            'pronunciation_focus': 'vowel_a',
            'tags': ['动词'],
            'sentence_cloze': example_es.replace(lemma, '___') if lemma in example_es.lower() else example_es,
            'sentence_full': example_es,
            'translation': f"{v['translation']}（动词原形）" if v['translation'] else lemma,
            'sentence_translation': example_zh,
            'cultural_note': '',
            'screenshot': '',
            'frequency_rank': None,
            'is_example_sentence': True
        })
        card_id += 1
    
    # Generate noun cards
    for n in vocab['nouns']:
        word = n['word'].lower()
        if word in existing_words:
            continue
        
        example_es = n['example_es']
        example_zh = n['example_zh']
        
        cards.append({
            'id': f'LCDP_S3E07_{card_id:03d}',
            'episode': 'S3E07',
            'scene_id': f'line_s3e07_{card_id:03d}',
            'line_index': card_id,
            'character': 'S3E07',
            'target_word': word,
            'ipa': '',
            'pos': f'n. {word}',
            'level': 'B2',
            'pronunciation_focus': 'vowel_a',
            'tags': ['名词'],
            'sentence_cloze': example_es.replace(word, '___') if word in example_es.lower() else example_es,
            'sentence_full': example_es,
            'translation': n['translation'] if n['translation'] else word,
            'sentence_translation': example_zh,
            'cultural_note': '',
            'screenshot': '',
            'frequency_rank': n['frequency'],
            'is_example_sentence': True
        })
        card_id += 1
    
    # Generate adverb cards
    for adv in vocab['adverbs']:
        base = adv['base'].lower()
        if base in existing_words:
            continue
        
        example_es = adv['example_es']
        example_zh = adv['example_zh']
        
        cards.append({
            'id': f'LCDP_S3E07_{card_id:03d}',
            'episode': 'S3E07',
            'scene_id': f'line_s3e07_{card_id:03d}',
            'line_index': card_id,
            'character': 'S3E07',
            'target_word': base,
            'ipa': '',
            'pos': f'adv. {base}',
            'level': 'B2',
            'pronunciation_focus': 'vowel_a',
            'tags': ['副词'],
            'sentence_cloze': example_es.replace(base, '___') if base in example_es.lower() else example_es,
            'sentence_full': example_es,
            'translation': adv['translation'] if adv['translation'] else base,
            'sentence_translation': example_zh,
            'cultural_note': '',
            'screenshot': '',
            'frequency_rank': None,
            'is_example_sentence': True
        })
        card_id += 1
    
    # Generate adjective cards
    for adj in vocab['adjectives']:
        base = adj['base'].lower()
        if base in existing_words:
            continue
        
        example_es = adj['example_es']
        example_zh = adj['example_zh']
        
        cards.append({
            'id': f'LCDP_S3E07_{card_id:03d}',
            'episode': 'S3E07',
            'scene_id': f'line_s3e07_{card_id:03d}',
            'line_index': card_id,
            'character': 'S3E07',
            'target_word': base,
            'ipa': '',
            'pos': f'adj. {base}',
            'level': 'B2',
            'pronunciation_focus': 'vowel_a',
            'tags': ['形容词'],
            'sentence_cloze': example_es.replace(base, '___') if base in example_es.lower() else example_es,
            'sentence_full': example_es,
            'translation': adj['translation'] if adj['translation'] else base,
            'sentence_translation': example_zh,
            'cultural_note': '',
            'screenshot': '',
            'frequency_rank': None,
            'is_example_sentence': True
        })
        card_id += 1
    
    print(f"Generated {len(cards)} cards from vocabulary", flush=True)
    return cards


def generate_metadata(cards):
    """Generate episode metadata."""
    pos_counts = Counter()
    for c in cards:
        if c['pos'].startswith('v.'):
            pos_counts['verbs'] += 1
        elif c['pos'].startswith('n.'):
            pos_counts['nouns'] += 1
        elif c['pos'].startswith('adv.'):
            pos_counts['adverbs'] += 1
        elif c['pos'].startswith('adj.'):
            pos_counts['adjectives'] += 1
    
    return {
        'episode': 'S3E07',
        'title': 'S3E07 — 词性分类闪卡',
        'title_cn': 'S3E07 — 词性分类闪卡',
        'description': f'第三季第七集台词中提取的闪卡，按词性分类（名词{pos_counts["nouns"]}、动词{pos_counts["verbs"]}、形容词{pos_counts["adjectives"]}、副词{pos_counts["adverbs"]}）。',
        'show': 'la-casa-de-papel',
        'language': 'es',
        'total_cards': len(cards),
        'pos_distribution': dict(pos_counts),
        'scenes_count': 1,
        'dialogue_lines_count': len(cards),
        'characters': ['S3E07'],
        'scenes_summary': []
    }


def main():
    print("Loading existing S3E05 cards for deduplication...", flush=True)
    existing_words = load_existing_s3e05_words()
    print(f"Existing S3E05 words: {len(existing_words)}", flush=True)
    
    print("\nLoading S3E07 dialogue...", flush=True)
    dialogues = load_s3e07_dialogue()
    
    print("\nLoading S3E05E07 shared vocabulary...", flush=True)
    vocab = load_s3e05e07_vocab()
    
    print("\nGenerating S3E07 cards...", flush=True)
    cards = generate_cards_from_vocab(vocab, existing_words, dialogues)
    
    print(f"\nTotal S3E07 cards: {len(cards)}", flush=True)
    
    # Save cards
    with open(OUTPUT_CARDS_PATH, 'w', encoding='utf-8') as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    print(f"Saved cards to {OUTPUT_CARDS_PATH}", flush=True)
    
    # Save metadata
    metadata = generate_metadata(cards)
    with open(OUTPUT_META_PATH, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Saved metadata to {OUTPUT_META_PATH}", flush=True)
    
    # Show samples
    print("\n=== Sample cards ===", flush=True)
    for c in cards[:5]:
        print(f"  {c['target_word']} -> {c['translation']}", flush=True)
        print(f"    {c['sentence_full']}", flush=True)
        print(f"    {c['sentence_translation']}", flush=True)
        print(flush=True)


if __name__ == '__main__':
    main()

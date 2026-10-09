"""
Generate LCDP S4E02 flashcards from Excel vocabulary sheets.
4 POS: nouns, verbs, adjectives, adverbs
"""
import json
import re
import sys
import io
import os
import unicodedata

import openpyxl

# Save original stdout fd before IPA import (it closes stdout.buffer)
_orig_fd = os.dup(1)  # duplicate stdout file descriptor

sys.path.insert(0, 'scripts')
from generate_spanish_ipa import word_to_ipa

# Restore stdout from the saved fd
sys.stdout = io.TextIOWrapper(os.fdopen(_orig_fd, 'w', encoding='utf-8', closefd=False), encoding='utf-8')

EXCEL_PATH = 'Money Heist/La_Casa_de_Papel_S3E01_台词.xlsx'
OUTPUT_CARDS = 'src/data/LCDP_S4E02_cards.json'
OUTPUT_META = 'src/data/LCDP_S4E02_metadata.json'

def normalize(text):
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')

def get_pronunciation_focus(word):
    """Determine pronunciation focus category."""
    w = word.lower()
    if 'rr' in w or w.startswith('r'):
        return 'rolled_r'
    if 'qu' in w or 'k' in w:
        return 'k_sound'
    if 'ñ' in w:
        return 'n_tilde'
    if 'll' in w or 'y' in w:
        return 'll_y'
    if 'gu' in w or 'gü' in w:
        return 'g_sound'
    if 'c' in w and any(v in w for v in ['e', 'i']):
        return 'theta'
    if 'h' in w:
        return 'silent_h'
    # Vowel checks
    vowels = [c for c in w if c in 'aeiouáéíóú']
    if 'ue' in w or 'uo' in w:
        return 'diphthong_ue'
    if 'ie' in w or 'ia' in w:
        return 'diphthong_ie'
    if 'au' in w or 'ai' in w:
        return 'diphthong_au'
    if 'ou' in w or 'oi' in w:
        return 'diphthong_ou'
    # Default by first vowel
    for v in vowels:
        v_clean = unicodedata.normalize('NFKD', v).encode('ASCII', 'ignore').decode('ASCII')
        if v_clean == 'a': return 'vowel_a'
        if v_clean == 'e': return 'vowel_e'
        if v_clean == 'i': return 'vowel_i'
        if v_clean == 'o': return 'vowel_o'
        if v_clean == 'u': return 'vowel_u'
    return 'vowel_a'

def guess_cefr(word):
    """Rough CEFR level guess based on word length and complexity."""
    w = word.lower()
    if len(w) <= 4:
        return 'A1'
    elif len(w) <= 6:
        return 'A2'
    elif len(w) <= 8:
        return 'B1'
    else:
        return 'B2'

def make_cloze(sentence, target_word):
    """Replace target word form in sentence with ___."""
    # Exact match
    if target_word in sentence:
        return re.sub(re.escape(target_word), '___', sentence, count=1)
    
    # Accent-insensitive word match
    norm_target = normalize(target_word)
    words = sentence.split()
    for word in words:
        clean = re.sub(r'[.,!?;:¿¡"\'()\[\]]', '', word)
        if normalize(clean) == norm_target:
            return sentence.replace(word, '___', 1)
    
    return sentence

# Load Excel
wb = openpyxl.load_workbook(EXCEL_PATH, read_only=True)

# Find S4E02 sheets
sheet_names = wb.sheetnames
s4e02_dialogue = None
s4e02_verbs = None
s4e02_adj = None
s4e02_adv = None
s4e02_nouns = None

for name in sheet_names:
    if 'S4E02' in name:
        if '台词' in name or '对话' in name:
            s4e02_dialogue = name
        elif '动词' in name:
            s4e02_verbs = name
        elif '形容词' in name:
            s4e02_adj = name
        elif '副词' in name:
            s4e02_adv = name
        elif '名词' in name:
            s4e02_nouns = name

print(f"Dialogue sheet: {s4e02_dialogue}")
print(f"Verbs sheet: {s4e02_verbs}")
print(f"Adjectives sheet: {s4e02_adj}")
print(f"Adverbs sheet: {s4e02_adv}")
print(f"Nouns sheet: {s4e02_nouns}")

cards = []
card_num = 0

def add_card(target_word, pos_tag, translation, sentence_full, sentence_translation, tag):
    global card_num
    card_num += 1
    card_id = f"LCDP_S4E02_{card_num:03d}"
    
    cloze = make_cloze(sentence_full, target_word)
    ipa = word_to_ipa(target_word)
    pron_focus = get_pronunciation_focus(target_word)
    level = guess_cefr(target_word)
    
    card = {
        "id": card_id,
        "episode": "S4E02",
        "scene_id": f"line_s4e02_{card_num:03d}",
        "line_index": card_num,
        "character": "S4E02",
        "target_word": target_word,
        "ipa": ipa,
        "pos": f"{pos_tag} {target_word}",
        "level": level,
        "pronunciation_focus": pron_focus,
        "tags": [tag],
        "sentence_cloze": cloze,
        "sentence_full": sentence_full,
        "translation": translation,
        "sentence_translation": sentence_translation,
        "cultural_note": "",
        "screenshot": "",
        "frequency_rank": None,
        "is_example_sentence": False
    }
    cards.append(card)

# Process verbs
if s4e02_verbs:
    ws = wb[s4e02_verbs]
    rows = list(ws.iter_rows(min_row=2, values_only=True))
    verb_count = 0
    for row in rows:
        if not row or not row[1]:
            continue
        idx, lemma, cn_meaning, conjugated, sentence_es, sentence_cn = row
        if not lemma:
            continue
        lemma = str(lemma).strip()
        conjugated = str(conjugated).strip() if conjugated else lemma
        sentence_es = str(sentence_es).strip() if sentence_es else ''
        sentence_cn = str(sentence_cn).strip() if sentence_cn else ''
        cn_meaning = str(cn_meaning).strip() if cn_meaning else ''
        
        trans = f"{cn_meaning}（动词原形）" if cn_meaning else f"（动词原形）"
        # Fallback: use common verb translations if Excel cell is empty
        if trans == '（动词原形）':
            fallback = {
                'advertir': '警告', 'asegurar': '保证', 'beber': '喝',
                'contestar': '回答', 'decidir': '决定', 'explicar': '解释',
                'ordenar': '命令', 'pertenecer': '属于', 'proteger': '保护',
                'recoger': '收集',
            }
            if lemma.lower() in fallback:
                trans = f"{fallback[lemma.lower()]}（动词原形）"
        add_card(lemma, 'v.', trans, sentence_es, sentence_cn, '动词')
        verb_count += 1
    print(f"Verbs: {verb_count}")

# Process adjectives
if s4e02_adj:
    ws = wb[s4e02_adj]
    rows = list(ws.iter_rows(min_row=2, values_only=True))
    adj_count = 0
    for row in rows:
        if not row or not row[1]:
            continue
        idx, base, cn_meaning, form, sentence_es, sentence_cn = row
        if not base:
            continue
        base = str(base).strip()
        form = str(form).strip() if form else base
        sentence_es = str(sentence_es).strip() if sentence_es else ''
        sentence_cn = str(sentence_cn).strip() if sentence_cn else ''
        cn_meaning = str(cn_meaning).strip() if cn_meaning else ''
        
        trans = f"{cn_meaning}（形容词）" if cn_meaning else f"（形容词）"
        add_card(base, 'adj.', trans, sentence_es, sentence_cn, '形容词')
        adj_count += 1
    print(f"Adjectives: {adj_count}")

# Process adverbs
if s4e02_adv:
    ws = wb[s4e02_adv]
    rows = list(ws.iter_rows(min_row=2, values_only=True))
    adv_count = 0
    for row in rows:
        if not row or not row[1]:
            continue
        idx, base, cn_meaning, form, sentence_es, sentence_cn = row
        if not base:
            continue
        base = str(base).strip()
        sentence_es = str(sentence_es).strip() if sentence_es else ''
        sentence_cn = str(sentence_cn).strip() if sentence_cn else ''
        cn_meaning = str(cn_meaning).strip() if cn_meaning else ''
        
        trans = f"{cn_meaning}（副词）" if cn_meaning else f"（副词）"
        add_card(base, 'adv.', trans, sentence_es, sentence_cn, '副词')
        adv_count += 1
    print(f"Adverbs: {adv_count}")

# Process nouns
if s4e02_nouns:
    ws = wb[s4e02_nouns]
    rows = list(ws.iter_rows(min_row=2, values_only=True))
    noun_count = 0
    for row in rows:
        if not row or not row[1]:
            continue
        idx, noun, cn_meaning, freq, sentence_es, sentence_cn = row
        if not noun:
            continue
        noun = str(noun).strip()
        sentence_es = str(sentence_es).strip() if sentence_es else ''
        sentence_cn = str(sentence_cn).strip() if sentence_cn else ''
        cn_meaning = str(cn_meaning).strip() if cn_meaning else ''
        
        # Determine gender from noun ending
        pos_tag = 'n.m.' if noun.endswith('o') else 'n.f.'
        trans = f"{cn_meaning}（名词）" if cn_meaning else f"（名词）"
        add_card(noun, pos_tag, trans, sentence_es, sentence_cn, '名词')
        noun_count += 1
    print(f"Nouns: {noun_count}")

wb.close()

# Save cards
with open(OUTPUT_CARDS, 'w', encoding='utf-8') as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

# Count POS distribution
pos_counts = {'verbs': 0, 'nouns': 0, 'adjectives': 0, 'adverbs': 0}
for c in cards:
    pos = c['pos']
    if pos.startswith('v.'): pos_counts['verbs'] += 1
    elif pos.startswith('n.'): pos_counts['nouns'] += 1
    elif pos.startswith('adj'): pos_counts['adjectives'] += 1
    elif pos.startswith('adv'): pos_counts['adverbs'] += 1

# Save metadata
meta = {
    "episode": "S4E02",
    "title": "S4E02 — 词性分类闪卡",
    "title_cn": "S4E02 — 词性分类闪卡",
    "description": f"第四季第二集台词中提取的闪卡，按词性分类（名词{pos_counts['nouns']}、动词{pos_counts['verbs']}、形容词{pos_counts['adjectives']}、副词{pos_counts['adverbs']}）。",
    "show": "la-casa-de-papel",
    "language": "es",
    "total_cards": len(cards),
    "pos_distribution": pos_counts,
    "scenes_count": 1,
    "dialogue_lines_count": len(cards),
    "characters": ["S4E02"],
    "scenes_summary": []
}

with open(OUTPUT_META, 'w', encoding='utf-8') as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)

print(f"\nTotal cards: {len(cards)}")
print(f"POS distribution: {pos_counts}")
print(f"Cards saved to: {OUTPUT_CARDS}")
print(f"Metadata saved to: {OUTPUT_META}")

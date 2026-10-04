"""
Script: generate_lcdp_vocab_cards.py
Purpose:
  Generate flashcards for verbs, adjectives, and adverbs from
  La_Casa_de_Papel_S3E01_台词.xlsx, skipping words that already exist.

Run:
  python scripts/generate_lcdp_vocab_cards.py
"""

from __future__ import annotations
import json
import re
import sys
import io
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import openpyxl
except ImportError:
    print("ERROR: openpyxl not installed. Run: pip install openpyxl", file=sys.stderr)
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent
XLSX_PATH = PROJECT_ROOT / "Money Heist" / "La_Casa_de_Papel_S3E01_台词.xlsx"
EXISTING_CARDS = PROJECT_ROOT / "src" / "data" / "LCDP_S3E01_nouns_cards.json"
OUTPUT_CARDS = PROJECT_ROOT / "src" / "data" / "LCDP_S3E01_vocab_cards.json"

# ---------------------------------------------------------------------------
# Spanish IPA generator (from generate_spanish_ipa.py)
# ---------------------------------------------------------------------------
STRONG_VOWELS = set('aeo')
WEAK_VOWELS = set('iu')
ALL_VOWELS = STRONG_VOWELS | WEAK_VOWELS
ACCENTED_VOWELS = set('áéíóú')

CONSONANT_SIMPLE = {
    'b': 'b', 'd': 'd', 'f': 'f', 'j': 'x', 'k': 'k',
    'l': 'l', 'm': 'm', 'ñ': 'ɲ', 'p': 'p', 's': 's',
    't': 't', 'w': 'w', 'v': 'b', 'x': 'ks', 'y': 'ʝ',
    'z': 'θ', 'h': '', 'q': 'k',
}

SPECIAL_CASES = {'méxico': '/me.xi.ko/', 'mexico': '/ˈme.xi.ko/'}


def preprocess_word(word: str) -> list:
    word_lower = word.lower().strip()
    word_clean = re.sub(r'[.,!?;:\'"()¿¡\[\]]', '', word_lower)
    if not word_clean:
        return []

    tokens = []
    i = 0
    while i < len(word_clean):
        ch = word_clean[i]

        if i + 1 < len(word_clean):
            two = word_clean[i:i+2]
            if two == 'ch':
                tokens.append(('consonant', 'ch', 'tʃ')); i += 2; continue
            if two == 'll':
                tokens.append(('consonant', 'll', 'ʝ')); i += 2; continue
            if two == 'rr':
                tokens.append(('consonant', 'rr', 'r')); i += 2; continue
            if two == 'qu' and i + 2 < len(word_clean) and word_clean[i+2] in 'ei':
                tokens.append(('consonant', 'qu', 'k')); i += 3; continue
            if two == 'qu':
                tokens.append(('consonant', 'qu', 'k')); i += 2; continue
            if two == 'gu' and i + 2 < len(word_clean) and word_clean[i+2] in 'ei':
                if word_clean[i+1] == 'ü':
                    tokens.append(('consonant', 'gü', 'gw')); i += 2; continue
                else:
                    tokens.append(('consonant', 'gu', 'g')); i += 3; continue

        if ch in ALL_VOWELS or ch in ACCENTED_VOWELS or ch == 'ü':
            tokens.append(('vowel', ch, ch))
        elif ch in CONSONANT_SIMPLE:
            tokens.append(('consonant', ch, CONSONANT_SIMPLE[ch]))
        elif ch in 'cgnr':
            tokens.append(('consonant_ctx', ch, ch))
        else:
            tokens.append(('consonant', ch, ch))
        i += 1
    return tokens


def resolve_context(tokens: list) -> list:
    result = []
    for idx, (ptype, orig, _) in enumerate(tokens):
        if ptype != 'consonant_ctx':
            result.append((ptype, orig, _))
            continue

        next_vowel_orig = ''
        for j in range(idx + 1, len(tokens)):
            if tokens[j][0] == 'vowel':
                next_vowel_orig = tokens[j][1].lower()
                break

        if orig == 'c':
            ipa = 'θ' if next_vowel_orig in 'ei' else 'k'
        elif orig == 'g':
            ipa = 'x' if next_vowel_orig in 'ei' else 'g'
        elif orig == 'n':
            next_cons_orig = ''
            for j in range(idx + 1, len(tokens)):
                if tokens[j][0] in ('consonant', 'consonant_ctx'):
                    next_cons_orig = tokens[j][1].lower()
                    break
            if next_cons_orig and next_cons_orig in 'bp':
                ipa = 'm'
            elif next_cons_orig and next_cons_orig in 'kg':
                ipa = 'ŋ'
            else:
                ipa = 'n'
        elif orig == 'r':
            if idx == 0:
                ipa = 'r'
            else:
                prev_orig = tokens[idx - 1][1].lower()
                ipa = 'r' if prev_orig in 'lns' else 'ɾ'
        else:
            ipa = orig

        result.append(('consonant', orig, ipa))
    return result


def get_stress_position(word_lower: str) -> int:
    for i, ch in enumerate(word_lower):
        if ch in ACCENTED_VOWELS:
            rest = word_lower[i+1:]
            count = 0
            in_v = False
            for c in rest:
                if c in ALL_VOWELS or c in ACCENTED_VOWELS or c == 'ü':
                    if not in_v:
                        count += 1
                        in_v = True
                else:
                    in_v = False
            return count
    if word_lower[-1] in 'aeiouáéíóúns':
        return 1
    return 0


def syllabify(tokens: list) -> list:
    vowel_idx = [i for i, (t, _, _) in enumerate(tokens) if t == 'vowel']
    if not vowel_idx:
        return [tokens] if tokens else []

    valid_clusters = {'bl', 'br', 'cl', 'cr', 'dr', 'fl', 'fr',
                      'gl', 'gr', 'pl', 'pr', 'tr'}

    syllables = []
    start = 0

    for vi in range(len(vowel_idx)):
        vidx = vowel_idx[vi]
        if vi == len(vowel_idx) - 1:
            syllables.append(tokens[start:])
            break

        next_vidx = vowel_idx[vi + 1]
        between = tokens[vidx+1:next_vidx]
        between_cons = [t for t in between if t[0] in ('consonant', 'consonant_ctx')]
        between_origs = ''.join(orig for _, orig, _ in between_cons)

        curr_v = tokens[vidx][1].lower()
        next_v = tokens[next_vidx][1].lower()
        is_diphthong = False
        if curr_v in WEAK_VOWELS and next_v in WEAK_VOWELS:
            is_diphthong = True
        elif curr_v in WEAK_VOWELS and next_v in STRONG_VOWELS and curr_v not in 'íú':
            is_diphthong = True
        elif curr_v in STRONG_VOWELS and next_v in WEAK_VOWELS and next_v not in 'íú':
            is_diphthong = True

        if is_diphthong and not between_cons:
            continue

        n_cons = len(between_cons)
        if n_cons == 0 or n_cons == 1:
            syllables.append(tokens[start:vidx+1])
            start = vidx + 1
        elif n_cons == 2:
            if between_origs in valid_clusters:
                syllables.append(tokens[start:vidx+1])
                start = vidx + 1
            else:
                split_at = vidx + 1 + 1
                syllables.append(tokens[start:split_at])
                start = split_at
        else:
            syllables.append(tokens[start:vidx+2])
            start = vidx + 2

    return syllables if syllables else [tokens]


def word_to_ipa(word: str) -> str:
    if not word:
        return ''
    word_lower = word.lower().strip()
    if word_lower in SPECIAL_CASES:
        return SPECIAL_CASES[word_lower]
    word_clean = re.sub(r'[.,!?;:\'"()¿¡\[\]]', '', word_lower)
    if not word_clean:
        return ''

    stress_from_end = get_stress_position(word_clean)
    tokens = preprocess_word(word_clean)
    if not tokens:
        return f'/{word_clean}/'

    tokens = resolve_context(tokens)
    syllables = syllabify(tokens)
    if not syllables:
        return f'/{word_clean}/'

    ipa_syls = []
    for syl in syllables:
        ipa_syls.append(''.join(ipa for _, _, ipa in syl if ipa))

    if stress_from_end < len(ipa_syls):
        idx = len(ipa_syls) - 1 - stress_from_end
        ipa_syls[idx] = 'ˈ' + ipa_syls[idx]

    return '/' + '.'.join(ipa_syls) + '/'


# ---------------------------------------------------------------------------
# Pronunciation focus detection
# ---------------------------------------------------------------------------

def get_pronunciation_focus(word: str) -> str:
    w = word.lower().strip()
    if 'rr' in w or (w.startswith('r') and len(w) > 1):
        return 'rolled_r'
    if 'ñ' in w:
        return 'ny_sound'
    if 'll' in w:
        return 'll_y'
    if 'qu' in w or 'gu' in w:
        return 'gl_gu'
    if 'j' in w:
        return 'j_sound'
    idx_g = w.find('g')
    if idx_g >= 0 and idx_g + 1 < len(w) and w[idx_g+1] in 'ei':
        return 'j_sound'
    if 'h' in w:
        return 'silent_h'
    if 'ie' in w or 'ue' in w or 'ui' in w:
        return 'diphthong'
    if 'c' in w:
        idx_c = w.find('c')
        if idx_c + 1 < len(w) and w[idx_c+1] in 'ei':
            return 'c_z_distinction'
    if 'z' in w:
        return 'c_z_distinction'

    vowels_in_word = [ch for ch in unicodedata.normalize('NFD', w) if ch in 'aeiou']
    if 'a' in vowels_in_word:
        return 'vowel_a'
    if 'e' in vowels_in_word:
        return 'vowel_e'
    if 'i' in vowels_in_word:
        return 'vowel_i'
    if 'o' in vowels_in_word:
        return 'vowel_o'
    if 'u' in vowels_in_word:
        return 'vowel_u'
    return 'vowel_a'


# ---------------------------------------------------------------------------
# CEFR level estimation
# ---------------------------------------------------------------------------

BASIC_WORDS = {
    'ser', 'ir', 'haber', 'tener', 'poder', 'hacer', 'estar',
    'querer', 'saber', 'ver', 'dar', 'venir', 'decir', 'poner',
    'salir', 'volver', 'tomar', 'conocer', 'vivir', 'sentir',
    'tratar', 'llamar', 'dejar', 'creer', 'hablar', 'llevar',
    'seguir', 'encontrar', 'pensar', 'dormir', 'contar', 'empezar',
    'esperar', 'buscar', 'existir', 'pasar', 'perder', 'conseguir',
    'crear', 'recibir', 'comer', 'caer', 'servir', 'abrir',
    'escribir', 'correr', 'morir', 'oír', 'leer', 'entender',
    'necesitar', 'usar', 'trabajar', 'jugar', 'pagar', 'estudiar',
    'cambiar', 'gustar', 'prestar', 'ayudar', 'mirar', 'escuchar',
    'llegar', 'recordar', 'tocar', 'ganar', 'gastar', 'comprar',
    'vender', 'pedir', 'preguntar', 'responder', 'aprender',
    'enseñar', 'cantar', 'bailar', 'nadar', 'cocinar',
    'bueno', 'malo', 'grande', 'pequeño', 'nuevo', 'viejo',
    'mucho', 'poco', 'todo', 'otro', 'mismo', 'primero', 'último',
    'bien', 'mal', 'muy', 'más', 'menos', 'también', 'aquí', 'ahí',
    'ahora', 'siempre', 'nunca', 'ya', 'todavía', 'después', 'antes',
    'claro', 'solo', 'junto', 'libre', 'fuerte', 'importante',
}

INTERMEDIATE_WORDS = {
    'acabar', 'aparecer', 'arreglar', 'atacar', 'intentar',
    'lograr', 'mantener', 'ocurrir', 'permitir', 'proponer',
    'realizar', 'reconocer', 'reducir', 'resultar', 'suceder',
    'suponer', 'transformar', 'valer', 'exigir', 'imaginar',
    'desaparecer', 'atrever', 'carecer', 'soler',
    'bonito', 'casado', 'corriente', 'diferente', 'enorme',
    'especial', 'extraño', 'feliz', 'increíble', 'interesante',
    'nervioso', 'orgulloso', 'perfecto', 'posible', 'propio',
    'real', 'seguro', 'serio', 'simple', 'tranquilo', 'verdadero',
    'absolutamente', 'acaso', 'adelante', 'además', 'apenas',
    'bastante', 'definitivamente', 'exactamente', 'probablemente',
}


def estimate_level(word: str) -> str:
    w = word.lower().strip()
    if w in BASIC_WORDS:
        return 'A2'
    elif w in INTERMEDIATE_WORDS:
        return 'B1'
    else:
        return 'B2'


# ---------------------------------------------------------------------------
# Cloze sentence
# ---------------------------------------------------------------------------

def make_cloze(sentence: str, target: str) -> str:
    pattern = re.compile(re.escape(target), re.IGNORECASE)
    return pattern.sub('___', sentence, count=1)


# ---------------------------------------------------------------------------
# Read Excel sheets
# ---------------------------------------------------------------------------

def read_sheet(wb, sheet_name: str) -> List[Dict[str, Any]]:
    ws = wb[sheet_name]
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        cols = list(row)
        seq = cols[0]
        base = str(cols[1]).strip() if cols[1] else ''
        cn = str(cols[2]).strip() if cols[2] else ''
        form = str(cols[3]).strip() if cols[3] else ''
        sentence_es = str(cols[4]).strip() if len(cols) > 4 and cols[4] else ''
        sentence_cn = str(cols[5]).strip() if len(cols) > 5 and cols[5] else ''
        if base and form:
            rows.append({
                'seq': int(seq) if seq else len(rows) + 1,
                'base': base,
                'cn': cn,
                'form': form,
                'sentence_es': sentence_es,
                'sentence_cn': sentence_cn,
            })
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Load existing cards
    with open(EXISTING_CARDS, 'r', encoding='utf-8') as f:
        existing_cards = json.load(f)
    existing_words: Set[str] = set()
    for card in existing_cards:
        existing_words.add(card['target_word'].lower())
    print(f"Existing cards: {len(existing_cards)}, unique words: {len(existing_words)}")

    wb = openpyxl.load_workbook(str(XLSX_PATH), read_only=True)

    all_new_cards = []
    card_counter = 1

    for sheet_name, pos_tag, tag_label in [
        ('动词', 'v.', '动词'),
        ('形容词', 'adj.', '形容词'),
        ('副词', 'adv.', '副词'),
    ]:
        rows = read_sheet(wb, sheet_name)
        print(f"\n=== {sheet_name}: {len(rows)} rows ===")

        new_count = 0
        dup_count = 0

        for row in rows:
            form = row['form']
            base = row['base']
            form_lower = form.lower()
            base_lower = base.lower()

            # Skip duplicates
            if form_lower in existing_words or base_lower in existing_words:
                dup_count += 1
                continue

            # Also skip if we already added this form in this run
            if form_lower in {c['target_word'].lower() for c in all_new_cards}:
                dup_count += 1
                continue

            # Generate card
            ipa = word_to_ipa(form)
            pron_focus = get_pronunciation_focus(form)
            level = estimate_level(base)
            cloze = make_cloze(row['sentence_es'], form)

            # Build translation with tense/person info for verbs
            translation = row['cn']
            if pos_tag == 'v.':
                # Add base form info
                translation = f"{translation}（原形: {base}）"

            card = {
                "id": f"LCDP_S3E01_{card_counter:03d}",
                "episode": "S3E01",
                "scene_id": f"line_vocab_{card_counter:03d}",
                "line_index": card_counter,
                "character": "S3E01",
                "target_word": form,
                "ipa": ipa,
                "pos": f"{pos_tag} {form}",
                "level": level,
                "pronunciation_focus": pron_focus,
                "tags": [tag_label],
                "sentence_cloze": cloze,
                "sentence_full": row['sentence_es'],
                "translation": translation,
                "sentence_translation": row['sentence_cn'],
                "cultural_note": "",
                "screenshot": "",
                "frequency_rank": None,
                "is_example_sentence": True,
            }

            # Add etymology for verbs
            if pos_tag == 'v.':
                card["etymology"] = [
                    {
                        "part": base + "-",
                        "origin": f"动词原形 {base}",
                        "meaning": row['cn']
                    },
                    {
                        "part": form[len(base):] if form.lower().startswith(base.lower()) else form,
                        "origin": "动词变位后缀",
                        "meaning": "变位形式"
                    }
                ]

            all_new_cards.append(card)
            card_counter += 1
            new_count += 1

        print(f"  New: {new_count}, Duplicate: {dup_count}")

    wb.close()

    print(f"\nTotal new cards: {len(all_new_cards)}")

    # Summary by type
    by_tag = {}
    for c in all_new_cards:
        tag = c['tags'][0]
        by_tag[tag] = by_tag.get(tag, 0) + 1
    print(f"By type: {by_tag}")

    # Summary by level
    by_level = {}
    for c in all_new_cards:
        lv = c['level']
        by_level[lv] = by_level.get(lv, 0) + 1
    print(f"By level: {by_level}")

    # Write output
    with open(OUTPUT_CARDS, 'w', encoding='utf-8') as f:
        json.dump(all_new_cards, f, ensure_ascii=False, indent=2)
    print(f"\nCards written to: {OUTPUT_CARDS}")

    # Print sample cards
    print("\n=== Sample cards ===")
    for c in all_new_cards[:5]:
        print(f"  {c['target_word']} ({c['tags'][0]}) -> {c['ipa']} | {c['translation']}")
        print(f"    {c['sentence_full']}")
        print(f"    {c['sentence_translation']}")
        print()


if __name__ == '__main__':
    main()

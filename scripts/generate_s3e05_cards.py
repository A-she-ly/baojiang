"""
Script: generate_s3e05_cards.py
Purpose:
  Generate flashcards for S3E05 from La_Casa_de_Papel_S3E01_台词.xlsx,
  using stanza for POS tagging. Deduplicates against existing S3E01 cards.

Run:
  python scripts/generate_s3e05_cards.py
"""

from __future__ import annotations
import json
import re
import sys
import io
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import openpyxl
import stanza

PROJECT_ROOT = Path(__file__).parent.parent
XLSX_PATH = PROJECT_ROOT / "Money Heist" / "La_Casa_de_Papel_S3E01_台词.xlsx"
EXISTING_CARDS = PROJECT_ROOT / "src" / "data" / "LCDP_S3E01_nouns_cards.json"
OUTPUT_CARDS = PROJECT_ROOT / "src" / "data" / "LCDP_S3E05_cards.json"
OUTPUT_META = PROJECT_ROOT / "src" / "data" / "LCDP_S3E05_metadata.json"

# Spanish stopwords / function words to exclude
STOPWORDS = {
    'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
    'de', 'del', 'al', 'a', 'en', 'por', 'para', 'con', 'sin',
    'sobre', 'tras', 'entre', 'hacia', 'hasta', 'desde',
    'y', 'e', 'o', 'u', 'ni', 'que', 'si', 'como', 'cuando',
    'donde', 'mientras', 'aunque', 'porque', 'pues', 'sino',
    'no', 'sí', 'también', 'tampoco', 'solo', 'sólo',
    'más', 'menos', 'muy', 'tan', 'tanto', 'poco', 'mucho',
    'algo', 'nada', 'alguien', 'nadie', 'todo', 'todos', 'todas',
    'otro', 'otra', 'otros', 'otras', 'mismo', 'misma', 'mismos',
    'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos', 'esas',
    'aquel', 'aquella', 'aquellos', 'aquellas',
    'mi', 'tu', 'su', 'mis', 'tus', 'sus', 'nuestro', 'vuestro',
    'me', 'te', 'se', 'nos', 'os', 'le', 'les', 'lo', 'la', 'los', 'las',
    'yo', 'tú', 'él', 'ella', 'usted', 'nosotros', 'vosotros', 'ellos', 'ellas',
    'qué', 'quién', 'cuál', 'cuánto', 'cuánta',
    'hay', 'ha', 'he', 'has', 'han', 'hemos',
    'es', 'son', 'ser', 'estar', 'está', 'están', 'estoy',
    'ya', 'aquí', 'ahí', 'allí', 'ahora', 'entonces', 'luego',
    'bien', 'mal', 'así',
    'oh', 'eh', 'ah', 'oye', 'vale', 'bueno', 'venga',
}

# Names to exclude (from S3E01 + common LCDP names)
NAMES = {
    'profesor', 'tokio', 'berlín', 'nairobi', 'denver', 'helsinki',
    'oslo', 'moscú', 'raquel', 'ángel', 'arturo', 'alison', 'mercedes',
    'tamayo', 'suárez', 'alicia', 'gandía', 'palermo', 'manila',
    'bogotá', 'lisboa', 'marseille', 'señor', 'señora', 'señorita',
}

# ---------------------------------------------------------------------------
# Reuse IPA generator from generate_lcdp_vocab_cards.py
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
                ipa = ''
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


def make_cloze(sentence: str, target: str) -> str:
    pattern = re.compile(re.escape(target), re.IGNORECASE)
    return pattern.sub('___', sentence, count=1)


# ---------------------------------------------------------------------------
# Stanza POS tag mapping: Universal POS -> our format
# ---------------------------------------------------------------------------
UPOS_TO_POS = {
    'NOUN': 'n.',
    'VERB': 'v.',
    'ADJ': 'adj.',
    'ADV': 'adv.',
}

# UPOS tags we want to extract
TARGET_UPOS = {'NOUN', 'VERB', 'ADJ', 'ADV'}


def main():
    # Load existing cards for dedup
    with open(EXISTING_CARDS, 'r', encoding='utf-8') as f:
        existing_cards = json.load(f)
    existing_words: Set[str] = set()
    for card in existing_cards:
        existing_words.add(card['target_word'].lower())
    print(f"Existing S3E01 cards: {len(existing_cards)}, unique words: {len(existing_words)}")

    # Read S3E05 dialogue
    wb = openpyxl.load_workbook(str(XLSX_PATH), read_only=True)
    ws = wb['纸钞屋 S3E05 台词']

    dialogue_lines = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        seq = row[0]
        es_text = str(row[1]).strip() if row[1] else ''
        cn_text = str(row[2]).strip() if row[2] else ''
        if es_text:
            dialogue_lines.append({
                'seq': int(seq) if seq else len(dialogue_lines) + 1,
                'es': es_text,
                'cn': cn_text,
            })

    wb.close()
    print(f"S3E05 dialogue lines: {len(dialogue_lines)}")

    # POS tag all sentences with stanza
    print("Loading stanza Spanish model...")
    nlp = stanza.Pipeline('es', processors='tokenize,pos,lemma', verbose=False)

    print("POS tagging all sentences...")
    # Build a map: word_lower -> list of (upos, lemma, sentence_es, sentence_cn)
    word_info: Dict[str, List[Dict]] = {}

    for line in dialogue_lines:
        doc = nlp(line['es'])
        for sentence in doc.sentences:
            for word in sentence.words:
                upos = word.upos
                if upos not in TARGET_UPOS:
                    continue

                text = word.text
                lemma = word.lemma if word.lemma else text
                text_lower = text.lower()

                # Skip very short words
                if len(text_lower) < 3:
                    continue

                # Skip stopwords
                if text_lower in STOPWORDS or lemma.lower() in STOPWORDS:
                    continue

                # Skip names
                if text_lower in NAMES or lemma.lower() in NAMES:
                    continue

                # Skip punctuation-only
                if not re.match(r'^[a-zA-ZáéíóúñüÁÉÍÓÚÑÜ]+$', text):
                    continue

                key = text_lower
                if key not in word_info:
                    word_info[key] = []
                word_info[key].append({
                    'upos': upos,
                    'lemma': lemma,
                    'sentence_es': line['es'],
                    'sentence_cn': line['cn'],
                })

    print(f"Unique content words found: {len(word_info)}")

    # For verbs: group by lemma, only keep infinitive form
    # For nouns/adjectives: keep the most common surface form
    lemma_groups: Dict[str, List[Dict]] = {}  # lemma -> list of word infos

    for word_lower, infos in word_info.items():
        for info in infos:
            lemma = info['lemma'].lower()
            if lemma not in lemma_groups:
                lemma_groups[lemma] = []
            lemma_groups[lemma].append({
                'surface': word_lower,
                'upos': info['upos'],
                'sentence_es': info['sentence_es'],
                'sentence_cn': info['sentence_cn'],
            })

    print(f"Unique lemmas: {len(lemma_groups)}")

    # Generate cards, deduplicating against existing
    all_new_cards = []
    card_counter = 1
    seen_lemmas: Set[str] = set()

    for lemma, entries in sorted(lemma_groups.items()):
        # Skip if lemma already in existing cards
        if lemma in existing_words:
            continue
        if lemma in seen_lemmas:
            continue

        # Determine primary POS (most common across all forms)
        pos_counts = {}
        for e in entries:
            upos = e['upos']
            pos_counts[upos] = pos_counts.get(upos, 0) + 1
        primary_upos = max(pos_counts, key=pos_counts.get)

        # For verbs: use infinitive (lemma) as target word
        # For nouns/adjectives/adverbs: use most common surface form
        if primary_upos == 'VERB':
            target_word = lemma
            # Pick a sentence that uses the infinitive if possible
            best_entry = None
            for e in entries:
                if e['surface'] == lemma:
                    best_entry = e
                    break
            if not best_entry:
                best_entry = entries[0]
        else:
            # Use most common surface form
            surface_counts = {}
            for e in entries:
                s = e['surface']
                surface_counts[s] = surface_counts.get(s, 0) + 1
            target_word = max(surface_counts, key=surface_counts.get)
            best_entry = None
            for e in entries:
                if e['surface'] == target_word:
                    best_entry = e
                    break
            if not best_entry:
                best_entry = entries[0]

        pos_tag = UPOS_TO_POS.get(primary_upos)
        if not pos_tag:
            continue

        sentence_es = best_entry['sentence_es']
        sentence_cn = best_entry['sentence_cn']

        # Generate card fields
        ipa = word_to_ipa(target_word)
        pron_focus = get_pronunciation_focus(target_word)
        level = estimate_level(lemma)
        cloze = make_cloze(sentence_es, target_word)

        # Translation
        translation = lemma
        if primary_upos == 'VERB':
            translation = f"{lemma}（动词原形）"

        # Tag label in Chinese
        tag_map = {'NOUN': '名词', 'VERB': '动词', 'ADJ': '形容词', 'ADV': '副词'}
        tag_label = tag_map.get(primary_upos, primary_upos)

        card = {
            "id": f"LCDP_S3E05_{card_counter:03d}",
            "episode": "S3E05",
            "scene_id": f"line_s3e05_{card_counter:03d}",
            "line_index": card_counter,
            "character": "S3E05",
            "target_word": target_word,
            "ipa": ipa,
            "pos": f"{pos_tag} {target_word}",
            "level": level,
            "pronunciation_focus": pron_focus,
            "tags": [tag_label],
            "sentence_cloze": cloze,
            "sentence_full": sentence_es,
            "translation": translation,
            "sentence_translation": sentence_cn,
            "cultural_note": "",
            "screenshot": "",
            "frequency_rank": None,
            "is_example_sentence": True,
        }

        all_new_cards.append(card)
        seen_lemmas.add(lemma)
        card_counter += 1

    print(f"\nTotal new S3E05 cards: {len(all_new_cards)}")

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

    # Write cards
    with open(OUTPUT_CARDS, 'w', encoding='utf-8') as f:
        json.dump(all_new_cards, f, ensure_ascii=False, indent=2)
    print(f"\nCards written to: {OUTPUT_CARDS}")

    # Write metadata
    metadata = {
        "episode": "S3E05",
        "title": "Nouns and verbs from S3E05",
        "title_cn": "第五集词性分类闪卡",
        "description": f"从纸钞屋第三季第五集台词中提取的闪卡，共 {len(all_new_cards)} 张，按词性分类。",
        "scenes_count": 0,
        "dialogue_lines_count": len(dialogue_lines),
        "characters": [],
        "scenes_summary": [],
    }
    with open(OUTPUT_META, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Metadata written to: {OUTPUT_META}")

    # Print sample cards
    print("\n=== Sample cards ===")
    for c in all_new_cards[:10]:
        print(f"  {c['target_word']} ({c['tags'][0]}) -> {c['ipa']} | {c['translation']}")
        print(f"    {c['sentence_full']}")
        print(f"    {c['sentence_translation']}")
        print()


if __name__ == '__main__':
    main()

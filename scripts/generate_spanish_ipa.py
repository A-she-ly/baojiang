"""
Spanish IPA generator using rule-based phonetic transcription.
Based on standard Spanish pronunciation rules (RFE/RAE).
"""
import json
import re
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ---------------------------------------------------------------------------
# Vowel classification
# ---------------------------------------------------------------------------
STRONG_VOWELS = set('aeo')
WEAK_VOWELS = set('iu')
ALL_VOWELS = STRONG_VOWELS | WEAK_VOWELS

VOWEL_IPA = {
    'a': 'a', 'e': 'e', 'i': 'i', 'o': 'o', 'u': 'u',
    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
    'ü': 'u',
}

# Consonant IPA (simple mapping, before context resolution)
CONSONANT_SIMPLE = {
    'b': 'b', 'd': 'd', 'f': 'f', 'j': 'x', 'k': 'k',
    'l': 'l', 'm': 'm', 'ñ': 'ɲ', 'p': 'p', 's': 's',
    't': 't', 'w': 'w', 'v': 'b', 'x': 'ks', 'y': 'ʝ',
    'z': 'θ', 'h': '', 'q': 'k',
}


def preprocess_word(word):
    """
    Preprocess word into tokens.
    Each token: (type, original_letters, ipa_value)
    type: 'vowel', 'consonant', 'consonant_ctx'
    """
    word_lower = word.lower().strip()
    word_clean = re.sub(r'[.,!?;:\'"()¿¡\[\]]', '', word_lower)
    if not word_clean:
        return []

    tokens = []
    i = 0
    while i < len(word_clean):
        ch = word_clean[i]

        # Digraphs
        if i + 1 < len(word_clean):
            two = word_clean[i:i+2]
            if two == 'ch':
                tokens.append(('consonant', 'ch', 'tʃ'))
                i += 2; continue
            if two == 'll':
                tokens.append(('consonant', 'll', 'ʝ'))
                i += 2; continue
            if two == 'rr':
                tokens.append(('consonant', 'rr', 'r'))
                i += 2; continue
            if two == 'qu' and i + 2 < len(word_clean) and word_clean[i+2] in 'ei':
                tokens.append(('consonant', 'qu', 'k'))
                i += 3; continue  # skip q, u, next vowel handled separately
            if two == 'qu':
                tokens.append(('consonant', 'qu', 'k'))
                i += 2; continue
            if two == 'gu' and i + 2 < len(word_clean) and word_clean[i+2] in 'ei':
                if i + 1 < len(word_clean) and word_clean[i+1] == 'ü':
                    tokens.append(('consonant', 'gü', 'gw'))
                    i += 2; continue
                else:
                    tokens.append(('consonant', 'gu', 'g'))
                    i += 3; continue  # skip g, u (silent)

        # Single char
        if ch in ALL_VOWELS or ch in 'áéíóúü':
            tokens.append(('vowel', ch, ch))
        elif ch in CONSONANT_SIMPLE:
            tokens.append(('consonant', ch, CONSONANT_SIMPLE[ch]))
        elif ch in 'cgnr':
            tokens.append(('consonant_ctx', ch, ch))
        else:
            tokens.append(('consonant', ch, ch))

        i += 1
    return tokens


def resolve_context(tokens):
    """Resolve context-dependent consonants using original letters."""
    result = []
    for idx, (ptype, orig, _) in enumerate(tokens):
        if ptype != 'consonant_ctx':
            result.append((ptype, orig, _))
            continue

        # Find next vowel's original letter
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
            # Assimilation: n -> m before b/p
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
            # Trilled at word start or after l/n/s
            if idx == 0:
                ipa = 'r'
            else:
                prev_orig = tokens[idx - 1][1].lower()
                ipa = 'r' if prev_orig in 'lns' else 'ɾ'
        else:
            ipa = orig

        result.append(('consonant', orig, ipa))
    return result


def get_stress_position(word_lower):
    """Returns syllable index from end (0=last, 1=penultimate)."""
    for i, ch in enumerate(word_lower):
        if ch in 'áéíóú':
            rest = word_lower[i+1:]
            count = 0
            in_v = False
            for c in rest:
                if c in ALL_VOWELS or c in 'áéíóúü':
                    if not in_v:
                        count += 1
                        in_v = True
                else:
                    in_v = False
            return count
    if word_lower[-1] in 'aeiouáéíóúns':
        return 1
    return 0


def syllabify(tokens):
    """Group tokens into syllables using original letters for cluster detection."""
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
        # Count consonant tokens between vowels (use type, not IPA value)
        between_cons = [t for t in between if t[0] in ('consonant', 'consonant_ctx')]
        between_origs = ''.join(orig for _, orig, _ in between_cons)

        # Diphthong check
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
        if n_cons == 0:
            syllables.append(tokens[start:vidx+1])
            start = vidx + 1
        elif n_cons == 1:
            syllables.append(tokens[start:vidx+1])
            start = vidx + 1
        elif n_cons == 2:
            # Check if two tokens form a valid onset cluster
            cluster_key = between_origs
            if cluster_key in valid_clusters:
                syllables.append(tokens[start:vidx+1])
                start = vidx + 1
            else:
                # Split: first cons with current, second with next
                split_at = vidx + 1 + 1  # after first consonant token
                syllables.append(tokens[start:split_at])
                start = split_at
        else:
            syllables.append(tokens[start:vidx+2])
            start = vidx + 2

    return syllables if syllables else [tokens]


def word_to_ipa(word):
    if not word:
        return ''

    word_lower = word.lower().strip()
    special = {'méxico': '/me.xi.ko/', 'mexico': '/ˈme.xi.ko/'}
    if word_lower in special:
        return special[word_lower]

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


def process_cards(input_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        cards = json.load(f)

    updated = 0
    for card in cards:
        if card['ipa'] == '':
            word = card['target_word']
            card['ipa'] = word_to_ipa(word)
            updated += 1
            print(f"  {word} -> {card['ipa']}")

    with open(input_path, 'w', encoding='utf-8') as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Updated {updated} cards.")


if __name__ == '__main__':
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, 'src', 'data', 'LCDP_S3E01_nouns_cards.json')
    print("Processing LCDP_S3E01_nouns_cards.json...")
    process_cards(path)

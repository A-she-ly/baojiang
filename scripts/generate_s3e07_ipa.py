"""
Generate IPA for all S3E07 cards using the Spanish IPA generator.
"""
import sys
import io
import json
import re
import os

# Copy the necessary functions from generate_spanish_ipa.py
# to avoid import issues with stdout

STRONG_VOWELS = set('aeo')
WEAK_VOWELS = set('iu')
ALL_VOWELS = STRONG_VOWELS | WEAK_VOWELS

VOWEL_IPA = {
    'a': 'a', 'e': 'e', 'i': 'i', 'o': 'o', 'u': 'u',
    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
    'ü': 'u',
}

CONSONANT_SIMPLE = {
    'b': 'b', 'd': 'd', 'f': 'f', 'j': 'x', 'k': 'k',
    'l': 'l', 'm': 'm', 'ñ': 'ɲ', 'p': 'p', 's': 's',
    't': 't', 'w': 'w', 'v': 'b', 'x': 'ks', 'y': 'ʝ',
    'z': 'θ', 'h': '', 'q': 'k',
}

SPECIAL_CASES = {'méxico': '/me.xi.ko/', 'mexico': '/ˈme.xi.ko/'}


def preprocess_word(word):
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
            if two == 'rr':
                tokens.append(('consonant', 'rr', 'r')); i += 2; continue
            if two == 'll':
                tokens.append(('consonant', 'll', 'ʝ')); i += 2; continue
            if two == 'ch':
                tokens.append(('consonant', 'ch', 'tʃ')); i += 2; continue
            if two == 'qu' and i + 2 < len(word_clean) and word_clean[i+2] in 'ei':
                tokens.append(('consonant', 'qu', 'k')); i += 3; continue
            if two == 'qu':
                tokens.append(('consonant', 'q', 'k')); i += 2; continue
            if two == 'gu' and i + 2 < len(word_clean) and word_clean[i+2] in 'ei':
                tokens.append(('consonant', 'gu', 'g')); i += 3; continue
            if two == ' gü' and i + 3 < len(word_clean) and word_clean[i+3] in 'ei':
                tokens.append(('consonant', 'gü', 'gw')); i += 4; continue

        if ch in ALL_VOWELS:
            tokens.append(('vowel', ch, VOWEL_IPA.get(ch, ch)))
        elif ch in CONSONANT_SIMPLE:
            tokens.append(('consonant_ctx', ch, CONSONANT_SIMPLE[ch]))
        else:
            tokens.append(('consonant_ctx', ch, ''))
        i += 1

    return tokens


def resolve_context(tokens):
    for i, (ttype, orig, ipa) in enumerate(tokens):
        if ttype != 'consonant_ctx':
            continue
        if orig == 'c':
            if i + 1 < len(tokens) and tokens[i+1][1] in 'ei':
                tokens[i] = ('consonant', orig, 'θ')
            else:
                tokens[i] = ('consonant', orig, 'k')
        elif orig == 'g':
            if i + 1 < len(tokens) and tokens[i+1][1] in 'ei':
                tokens[i] = ('consonant', orig, 'x')
            else:
                tokens[i] = ('consonant', orig, 'g')
        elif orig == 'r':
            if i == 0:
                tokens[i] = ('consonant', orig, 'r')
            elif i > 0 and tokens[i-1][0] in ('consonant', 'consonant_ctx'):
                tokens[i] = ('consonant', orig, 'r')
            else:
                tokens[i] = ('consonant', orig, '')
        elif orig == 'n':
            if i + 1 < len(tokens) and tokens[i+1][1] in 'bp':
                tokens[i] = ('consonant', orig, 'm')
            else:
                tokens[i] = ('consonant', orig, 'n')
        else:
            tokens[i] = ('consonant', orig, ipa)
    return tokens


def is_diphthong(v1, v2):
    if v1 in WEAK_VOWELS and v2 in WEAK_VOWELS:
        return True
    if v1 in WEAK_VOWELS and v2 in STRONG_VOWELS:
        return True
    if v1 in STRONG_VOWELS and v2 in WEAK_VOWELS:
        return True
    return False


def syllabify(tokens):
    vowel_indices = [i for i, (t, _, _) in enumerate(tokens) if t == 'vowel']
    if not vowel_indices:
        return [tokens] if tokens else []

    syllables = []
    vi = 0
    token_idx = 0

    while vi < len(vowel_indices):
        v_start = vowel_indices[vi]
        syl_start = token_idx if vi == 0 else syllables[-1][-1][0] + 1 if syllables else token_idx

        if vi + 1 < len(vowel_indices):
            v_end = vowel_indices[vi + 1]
            between = tokens[v_start+1:v_end]
            between_cons = [t for t in between if t[0] in ('consonant', 'consonant_ctx')]

            if len(between_cons) == 0:
                if is_diphthong(tokens[v_start][1], tokens[v_end][1]):
                    pass
                else:
                    syl_end = v_start
                    syllables.append([(j, tokens[j]) for j in range(syl_start, syl_end + 1)])
                    token_idx = syl_end + 1
                    vi += 1
                    continue
            elif len(between_cons) == 1:
                syl_end = v_start
                syllables.append([(j, tokens[j]) for j in range(syl_start, syl_end + 1)])
                token_idx = syl_end + 1
                vi += 1
                continue
            elif len(between_cons) >= 2:
                if between_cons[0][1] in 'bcdfgpst' and between_cons[1][1] in 'lr':
                    syl_end = v_start + 1
                    syllables.append([(j, tokens[j]) for j in range(syl_start, syl_end + 1)])
                    token_idx = syl_end + 1
                    vi += 1
                    continue
                else:
                    syl_end = v_start
                    syllables.append([(j, tokens[j]) for j in range(syl_start, syl_end + 1)])
                    token_idx = syl_end + 1
                    vi += 1
                    continue
        else:
            syl_end = len(tokens) - 1
            syllables.append([(j, tokens[j]) for j in range(syl_start, syl_end + 1)])
            vi += 1

    return [[t for _, t in syl] for syl in syllables if syl]


def get_stress_position(word):
    word_lower = word.lower()
    if any(c in word_lower for c in 'áéíóú'):
        for i, ch in enumerate(word_lower):
            if ch in 'áéíóú':
                pass
        vowels_with_stress = [i for i, ch in enumerate(word_lower) if ch in 'áéíóú']
        if vowels_with_stress:
            stressed_vowel_idx = vowels_with_stress[-1]
            vowel_indices = [i for i, ch in enumerate(word_lower) if ch in 'aeiouáéíóú']
            for pos, vi in enumerate(vowel_indices):
                if vi == stressed_vowel_idx:
                    return len(vowel_indices) - 1 - pos
    if word_lower[-1] in 'aeiosn':
        return 1
    else:
        return 0


def word_to_ipa(word):
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


# Main logic
CARDS_PATH = 'src/data/LCDP_S3E07_cards.json'

with open(CARDS_PATH, 'r', encoding='utf-8') as f:
    cards = json.load(f)

fixed_count = 0
for card in cards:
    if not card.get('ipa', '').strip():
        target_word = card.get('target_word', '')
        if target_word:
            ipa = word_to_ipa(target_word)
            card['ipa'] = ipa
            fixed_count += 1

with open(CARDS_PATH, 'w', encoding='utf-8') as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

print(f"Generated IPA for {fixed_count} cards")

# Verify
with open(CARDS_PATH, 'r', encoding='utf-8') as f:
    cards = json.load(f)

empty_ipa = [c for c in cards if not c.get('ipa', '').strip()]
print(f"Remaining cards with empty IPA: {len(empty_ipa)}")

# Show some samples
for c in cards[:5]:
    print(f"  {c['target_word']} -> {c['ipa']}")

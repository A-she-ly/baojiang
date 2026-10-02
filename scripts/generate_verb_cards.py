"""
Script: generate_verb_cards.py
Purpose:
  1. Read verbs from "La_Casa_de_Papel_S3E01_动词表.xlsx"
  2. Generate flashcard JSON files for verb classification
  3. Output: LCDP_S3E01_verbs_cards.json, LCDP_S3E01_verbs_metadata.json

Run:
  python scripts/generate_verb_cards.py
"""

from __future__ import annotations
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import openpyxl
except ImportError:
    print("ERROR: openpyxl not installed. Run: pip install openpyxl", file=sys.stderr)
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent
XLSX_PATH = PROJECT_ROOT / "Money Heist" / "La_Casa_de_Papel_S3E01_动词表.xlsx"
OUTPUT_CARDS = PROJECT_ROOT / "src" / "data" / "LCDP_S3E01_verbs_cards.json"
OUTPUT_META = PROJECT_ROOT / "src" / "data" / "LCDP_S3E01_verbs_metadata.json"


# ---------------------------------------------------------------------------
# Spanish stress / IPA helpers
# ---------------------------------------------------------------------------

def strip_accents(s: str) -> str:
    """Remove accent marks for syllable analysis."""
    return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('ascii')


def find_stressed_syllable(word: str) -> int:
    """
    Return the 0-based index of the stressed syllable.
    Rules (simplified):
    - If word ends in n, s, or vowel → stress on penultimate syllable
    - Otherwise → stress on last syllable
    - If there's an explicit accent mark (á, é, í, ó, ú) → that syllable is stressed
    """
    # Check for explicit accent
    for i, ch in enumerate(word):
        if ch in 'áéíóú':
            # Count syllables up to this point
            clean = strip_accents(word[:i+1]).lower()
            syllables = _split_syllables(clean)
            return len(syllables) - 1

    # No explicit accent → apply default rules
    last_char = strip_accents(word)[-1].lower() if word else ''
    syllables = _split_syllables(strip_accents(word).lower())

    if last_char in 'nsaeiou':
        return max(0, len(syllables) - 2)  # penultimate
    else:
        return max(0, len(syllables) - 1)  # last


def _split_syllables(word: str) -> List[str]:
    """Simple syllable splitter for Spanish."""
    word = word.lower()
    vowels = 'aeiou'
    syllables = []
    current = ''
    i = 0
    while i < len(word):
        ch = word[i]
        current += ch
        if ch in vowels:
            # Check for diphthong
            if i + 1 < len(word) and word[i+1] in vowels and word[i+1] != ch:
                current += word[i+1]
                i += 1
                # Check for triphthong
                if i + 1 < len(word) and word[i+1] in vowels:
                    current += word[i+1]
                    i += 1
            syllables.append(current)
            current = ''
        i += 1
    if current:
        if syllables:
            syllables[-1] += current
        else:
            syllables.append(current)
    return syllables if syllables else [word]


# Spanish phoneme mapping (simplified GenAm-style for Spanish)
PHONEME_MAP = {
    'a': 'a', 'á': 'a',
    'e': 'e', 'é': 'e',
    'i': 'i', 'í': 'i', 'y': 'i',
    'o': 'o', 'ó': 'o',
    'u': 'u', 'ú': 'u', 'ü': 'u',
    'b': 'b', 'v': 'b',  # b/v merger in Spanish
    'c': 'k',  # simplified
    'd': 'd',
    'f': 'f',
    'g': 'g',
    'h': '',   # silent
    'j': 'x',  # /x/ sound
    'k': 'k',
    'l': 'l',
    'm': 'm',
    'n': 'n',
    'ñ': 'ɲ',
    'p': 'p',
    'q': 'k',
    'r': 'ɾ',
    's': 's', 'z': 's',  # Latin American: z → /s/
    't': 't',
    'w': 'w',
    'x': 'ks',
}


def word_to_ipa(word: str) -> str:
    """Generate a simplified IPA transcription for a Spanish word."""
    stressed_idx = find_stressed_syllable(word)
    syllables = _split_syllables(strip_accents(word).lower())

    ipa_syllables = []
    for idx, syl in enumerate(syllables):
        ipa_chars = []
        for ch in syl:
            ipa_chars.append(PHONEME_MAP.get(ch, ch))
        ipa_syl = ''.join(ipa_chars)
        # Mark stress with ˈ before stressed syllable
        if idx == stressed_idx:
            ipa_syllables.append('ˈ' + ipa_syl)
        else:
            ipa_syllables.append(ipa_syl)

    return '/' + '.'.join(ipa_syllables) + '/'


# ---------------------------------------------------------------------------
# Conjugation suffix detection
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Irregular verb conjugation lookup
# ---------------------------------------------------------------------------

# Known irregular conjugations: (infinitive, conjugated) -> (stem_display, suffix_display, tense_desc)
IRREGULAR_VERBS = {
    # ser
    ('ser', 'soy'): ('ser-', '-oy', '第一人称单数现在时（不规则）'),
    ('ser', 'eres'): ('ser-', '-eres', '第二人称单数现在时（不规则）'),
    ('ser', 'es'): ('ser-', '-es', '第三人称单数现在时（不规则）'),
    ('ser', 'somos'): ('ser-', '-somos', '第一人称复数现在时（不规则）'),
    ('ser', 'sois'): ('ser-', '-sois', '第二人称复数现在时（不规则）'),
    ('ser', 'son'): ('ser-', '-son', '第三人称复数现在时（不规则）'),
    ('ser', 'fui'): ('ser-', '-fui', '第一人称单数简单过去时（不规则）'),
    ('ser', 'fuiste'): ('ser-', '-fuiste', '第二人称单数简单过去时（不规则）'),
    ('ser', 'fue'): ('ser-', '-fue', '第三人称单数简单过去时（不规则）'),
    ('ser', 'fuimos'): ('ser-', '-fuimos', '第一人称复数简单过去时（不规则）'),
    ('ser', 'fuisteis'): ('ser-', '-fuisteis', '第二人称复数简单过去时（不规则）'),
    ('ser', 'fueron'): ('ser-', '-fueron', '第三人称复数简单过去时（不规则）'),
    ('ser', 'era'): ('ser-', '-era', '第一/三人称单数过去未完成时（不规则）'),
    ('ser', 'eras'): ('ser-', '-eras', '第二人称单数过去未完成时（不规则）'),
    ('ser', 'éramos'): ('ser-', '-éramos', '第一人称复数过去未完成时（不规则）'),
    ('ser', 'eran'): ('ser-', '-eran', '第三人称复数过去未完成时（不规则）'),
    ('ser', 'seré'): ('ser-', '-é', '第一人称单数简单将来时'),
    ('ser', 'será'): ('ser-', '-á', '第三人称单数简单将来时'),
    ('ser', 'serán'): ('ser-', '-án', '第三人称复数简单将来时'),
    ('ser', 'sea'): ('ser-', '-sea', '第一/三人称单数现在虚拟式（不规则）'),
    ('ser', 'seas'): ('ser-', '-seas', '第二人称单数现在虚拟式（不规则）'),
    ('ser', 'seamos'): ('ser-', '-seamos', '第一人称复数现在虚拟式（不规则）'),
    ('ser', 'sean'): ('ser-', '-sean', '第三人称复数现在虚拟式（不规则）'),
    ('ser', 'sido'): ('ser-', '-sido', '过去分词（不规则）'),
    ('ser', 'siendo'): ('ser-', '-siendo', '副动词（不规则）'),
    # ir
    ('ir', 'voy'): ('ir-', '-voy', '第一人称单数现在时（不规则）'),
    ('ir', 'vas'): ('ir-', '-vas', '第二人称单数现在时（不规则）'),
    ('ir', 'va'): ('ir-', '-va', '第三人称单数现在时（不规则）'),
    ('ir', 'vamos'): ('ir-', '-vamos', '第一人称复数现在时'),
    ('ir', 'vais'): ('ir-', '-vais', '第二人称复数现在时（不规则）'),
    ('ir', 'van'): ('ir-', '-van', '第三人称复数现在时（不规则）'),
    ('ir', 'fui'): ('ir-', '-fui', '第一人称单数简单过去时（不规则）'),
    ('ir', 'fuiste'): ('ir-', '-fuiste', '第二人称单数简单过去时（不规则）'),
    ('ir', 'fue'): ('ir-', '-fue', '第三人称单数简单过去时（不规则）'),
    ('ir', 'fuimos'): ('ir-', '-fuimos', '第一人称复数简单过去时（不规则）'),
    ('ir', 'fuisteis'): ('ir-', '-fuisteis', '第二人称复数简单过去时（不规则）'),
    ('ir', 'fueron'): ('ir-', '-fueron', '第三人称复数简单过去时（不规则）'),
    ('ir', 'iba'): ('ir-', '-iba', '第一/三人称单数过去未完成时（不规则）'),
    ('ir', 'ibas'): ('ir-', '-ibas', '第二人称单数过去未完成时（不规则）'),
    ('ir', 'íamos'): ('ir-', '-íamos', '第一人称复数过去未完成时（不规则）'),
    ('ir', 'iban'): ('ir-', '-iban', '第三人称复数过去未完成时（不规则）'),
    ('ir', 'iré'): ('ir-', '-é', '第一人称单数简单将来时'),
    ('ir', 'irá'): ('ir-', '-á', '第三人称单数简单将来时'),
    ('ir', 'irán'): ('ir-', '-án', '第三人称复数简单将来时'),
    ('ir', 'vaya'): ('ir-', '-vaya', '第一/三人称单数现在虚拟式（不规则）'),
    ('ir', 'vayas'): ('ir-', '-vayas', '第二人称单数现在虚拟式（不规则）'),
    ('ir', 'vamos'): ('ir-', '-vamos', '第一人称复数现在虚拟式'),
    ('ir', 'vayan'): ('ir-', '-vayan', '第三人称复数现在虚拟式（不规则）'),
    ('ir', 'ido'): ('ir-', '-ido', '过去分词（不规则）'),
    ('ir', 'yendo'): ('ir-', '-yendo', '副动词（不规则）'),
    # haber
    ('haber', 'he'): ('haber-', '-he', '第一人称单数现在时（不规则）'),
    ('haber', 'has'): ('haber-', '-has', '第二人称单数现在时（不规则）'),
    ('haber', 'ha'): ('haber-', '-ha', '第三人称单数现在时（不规则）'),
    ('haber', 'hemos'): ('haber-', '-hemos', '第一人称复数现在时（不规则）'),
    ('haber', 'habéis'): ('haber-', '-habéis', '第二人称复数现在时（不规则）'),
    ('haber', 'han'): ('haber-', '-han', '第三人称复数现在时（不规则）'),
    ('haber', 'habrá'): ('habr-', '-á', '第三人称单数简单将来时（不规则）'),
    ('haber', 'habrán'): ('habr-', '-án', '第三人称复数简单将来时（不规则）'),
    ('haber', 'habría'): ('habr-', '-ía', '第一/三人称单数条件式（不规则）'),
    ('haber', 'habría'): ('habr-', '-ía', '第一/三人称单数条件式（不规则）'),
    ('haber', 'haya'): ('haber-', '-haya', '第一/三人称单数现在虚拟式（不规则）'),
    ('haber', 'hayas'): ('haber-', '-hayas', '第二人称单数现在虚拟式（不规则）'),
    ('haber', 'hayamos'): ('haber-', '-hayamos', '第一人称复数现在虚拟式（不规则）'),
    ('haber', 'hayan'): ('haber-', '-hayan', '第三人称复数现在虚拟式（不规则）'),
    ('haber', 'habido'): ('haber-', '-habido', '过去分词（不规则）'),
    ('haber', 'habiendo'): ('haber-', '-habiendo', '副动词（不规则）'),
    # tener
    ('tener', 'tengo'): ('tener-', '-go', '第一人称单数现在时（不规则）'),
    ('tener', 'tienes'): ('tener-', '-ienes', '第二人称单数现在时（不规则）'),
    ('tener', 'tiene'): ('tener-', '-iene', '第三人称单数现在时（不规则）'),
    ('tener', 'tenemos'): ('tener-', '-emos', '第一人称复数现在时'),
    ('tener', 'tenéis'): ('tener-', '-éis', '第二人称复数现在时'),
    ('tener', 'tienen'): ('tener-', '-ienen', '第三人称复数现在时（不规则）'),
    ('tener', 'tuve'): ('tener-', '-uve', '第一人称单数简单过去时（不规则）'),
    ('tener', 'tuvo'): ('tener-', '-uvo', '第三人称单数简单过去时（不规则）'),
    ('tener', 'tuvieron'): ('tener-', '-uvieron', '第三人称复数简单过去时（不规则）'),
    ('tener', 'tenía'): ('tener-', '-ía', '第一/三人称单数过去未完成时'),
    ('tener', 'tendré'): ('tendr-', '-é', '第一人称单数简单将来时（不规则）'),
    ('tener', 'tendrá'): ('tendr-', '-á', '第三人称单数简单将来时（不规则）'),
    ('tener', 'tenga'): ('tener-', '-ga', '第一/三人称单数现在虚拟式（不规则）'),
    ('tener', 'tengas'): ('tener-', '-gas', '第二人称单数现在虚拟式（不规则）'),
    ('tener', 'tengamos'): ('tener-', '-gamos', '第一人称复数现在虚拟式（不规则）'),
    ('tener', 'tengan'): ('tener-', '-gan', '第三人称复数现在虚拟式（不规则）'),
    ('tener', 'tenido'): ('tener-', '-tenido', '过去分词'),
    ('tener', 'teniendo'): ('tener-', '-teniendo', '副动词'),
    # poder
    ('poder', 'puedo'): ('poder-', '-uedo', '第一人称单数现在时（不规则）'),
    ('poder', 'puedes'): ('poder-', '-uedes', '第二人称单数现在时（不规则）'),
    ('poder', 'puede'): ('poder-', '-uede', '第三人称单数现在时（不规则）'),
    ('poder', 'podemos'): ('poder-', '-emos', '第一人称复数现在时'),
    ('poder', 'podéis'): ('poder-', '-éis', '第二人称复数现在时'),
    ('poder', 'pueden'): ('poder-', '-ueden', '第三人称复数现在时（不规则）'),
    ('poder', 'pude'): ('poder-', '-ude', '第一人称单数简单过去时（不规则）'),
    ('poder', 'pudo'): ('poder-', '-udo', '第三人称单数简单过去时（不规则）'),
    ('poder', 'podré'): ('podr-', '-é', '第一人称单数简单将来时（不规则）'),
    ('poder', 'podrá'): ('podr-', '-á', '第三人称单数简单将来时（不规则）'),
    ('poder', 'podría'): ('podr-', '-ía', '第一/三人称单数条件式（不规则）'),
    ('poder', 'pueda'): ('poder-', '-ueda', '第一/三人称单数现在虚拟式（不规则）'),
    ('poder', 'puedas'): ('poder-', '-uedas', '第二人称单数现在虚拟式（不规则）'),
    ('poder', 'podamos'): ('poder-', '-amos', '第一人称复数现在虚拟式'),
    ('poder', 'puedan'): ('poder-', '-uedan', '第三人称复数现在虚拟式（不规则）'),
    ('poder', 'podido'): ('poder-', '-podido', '过去分词'),
    ('poder', 'pudiendo'): ('poder-', '-pudiendo', '副动词（不规则）'),
    # hacer
    ('hacer', 'hago'): ('hacer-', '-go', '第一人称单数现在时（不规则）'),
    ('hacer', 'haces'): ('hacer-', '-aces', '第二人称单数现在时'),
    ('hacer', 'hace'): ('hacer-', '-ace', '第三人称单数现在时'),
    ('hacer', 'hacemos'): ('hacer-', '-emos', '第一人称复数现在时'),
    ('hacer', 'hacéis'): ('hacer-', '-éis', '第二人称复数现在时'),
    ('hacer', 'hacen'): ('hacer-', '-acen', '第三人称复数现在时'),
    ('hacer', 'hice'): ('hacer-', '-ice', '第一人称单数简单过去时（不规则）'),
    ('hacer', 'hizo'): ('hacer-', '-izo', '第三人称单数简单过去时（不规则）'),
    ('hacer', 'hicieron'): ('hacer-', '-icieron', '第三人称复数简单过去时（不规则）'),
    ('hacer', 'haré'): ('har-', '-é', '第一人称单数简单将来时（不规则）'),
    ('hacer', 'hará'): ('har-', '-á', '第三人称单数简单将来时（不规则）'),
    ('hacer', 'harán'): ('har-', '-án', '第三人称复数简单将来时（不规则）'),
    ('hacer', 'haría'): ('har-', '-ía', '第一/三人称单数条件式（不规则）'),
    ('hacer', 'haga'): ('hacer-', '-ga', '第一/三人称单数现在虚拟式（不规则）'),
    ('hacer', 'hagas'): ('hacer-', '-gas', '第二人称单数现在虚拟式（不规则）'),
    ('hacer', 'hagamos'): ('hacer-', '-gamos', '第一人称复数现在虚拟式（不规则）'),
    ('hacer', 'hagan'): ('hacer-', '-gan', '第三人称复数现在虚拟式（不规则）'),
    ('hacer', 'hecho'): ('hacer-', '-hecho', '过去分词（不规则）'),
    ('hacer', 'haciendo'): ('hacer-', '-haciendo', '副动词'),
    # estar
    ('estar', 'estoy'): ('estar-', '-oy', '第一人称单数现在时（不规则）'),
    ('estar', 'estás'): ('estar-', '-ás', '第二人称单数现在时'),
    ('estar', 'está'): ('estar-', '-á', '第三人称单数现在时'),
    ('estar', 'estamos'): ('estar-', '-amos', '第一人称复数现在时'),
    ('estar', 'estáis'): ('estar-', '-áis', '第二人称复数现在时'),
    ('estar', 'están'): ('estar-', '-án', '第三人称复数现在时'),
    ('estar', 'estuve'): ('estar-', '-uve', '第一人称单数简单过去时（不规则）'),
    ('estar', 'estuvo'): ('estar-', '-uvo', '第三人称单数简单过去时（不规则）'),
    ('estar', 'estaba'): ('estar-', '-aba', '第一/三人称单数过去未完成时'),
    ('estar', 'estaré'): ('estar-', '-é', '第一人称单数简单将来时'),
    ('estar', 'estaré'): ('estar-', '-é', '第一人称单数简单将来时'),
    ('estar', 'estará'): ('estar-', '-á', '第三人称单数简单将来时'),
    ('estar', 'estaré'): ('estar-', '-é', '第一人称单数简单将来时'),
    ('estar', 'estaría'): ('estar-', '-ía', '第一/三人称单数条件式'),
    ('estar', 'esté'): ('estar-', '-é', '第一/三人称单数现在虚拟式（不规则）'),
    ('estar', 'estés'): ('estar-', '-és', '第二人称单数现在虚拟式（不规则）'),
    ('estar', 'estemos'): ('estar-', '-emos', '第一人称复数现在虚拟式'),
    ('estar', 'estén'): ('estar-', '-én', '第三人称复数现在虚拟式（不规则）'),
    ('estar', 'estado'): ('estar-', '-estado', '过去分词'),
    ('estar', 'estando'): ('estar-', '-estando', '副动词'),
    # querer
    ('querer', 'quiero'): ('querer-', '-iero', '第一人称单数现在时（不规则）'),
    ('querer', 'quieres'): ('querer-', '-ieres', '第二人称单数现在时（不规则）'),
    ('querer', 'quiere'): ('querer-', '-iere', '第三人称单数现在时（不规则）'),
    ('querer', 'queremos'): ('querer-', '-emos', '第一人称复数现在时'),
    ('querer', 'queréis'): ('querer-', '-éis', '第二人称复数现在时'),
    ('querer', 'quieren'): ('querer-', '-ieren', '第三人称复数现在时（不规则）'),
    ('querer', 'quise'): ('querer-', '-ise', '第一人称单数简单过去时（不规则）'),
    ('querer', 'quiso'): ('querer-', '-iso', '第三人称单数简单过去时（不规则）'),
    ('querer', 'quería'): ('querer-', '-ía', '第一/三人称单数过去未完成时'),
    ('querer', 'querré'): ('querr-', '-é', '第一人称单数简单将来时（不规则）'),
    ('querer', 'querrá'): ('querr-', '-á', '第三人称单数简单将来时（不规则）'),
    ('querer', 'querría'): ('querr-', '-ía', '第一/三人称单数条件式（不规则）'),
    ('querer', 'quiera'): ('querer-', '-iera', '第一/三人称单数现在虚拟式（不规则）'),
    ('querer', 'quieras'): ('querer-', '-ieras', '第二人称单数现在虚拟式（不规则）'),
    ('querer', 'queramos'): ('querer-', '-amos', '第一人称复数现在虚拟式'),
    ('querer', 'quieran'): ('querer-', '-ieran', '第三人称复数现在虚拟式（不规则）'),
    ('querer', 'querido'): ('querer-', '-querido', '过去分词'),
    ('querer', 'queriendo'): ('querer-', '-queriendo', '副动词'),
    # saber
    ('saber', 'sé'): ('saber-', '-é', '第一人称单数现在时（不规则）'),
    ('saber', 'sabes'): ('saber-', '-es', '第二人称单数现在时'),
    ('saber', 'sabe'): ('saber-', '-e', '第三人称单数现在时'),
    ('saber', 'sabemos'): ('saber-', '-emos', '第一人称复数现在时'),
    ('saber', 'sabéis'): ('saber-', '-éis', '第二人称复数现在时'),
    ('saber', 'saben'): ('saber-', '-en', '第三人称复数现在时'),
    ('saber', 'supe'): ('saber-', '-upe', '第一人称单数简单过去时（不规则）'),
    ('saber', 'supo'): ('saber-', '-upo', '第三人称单数简单过去时（不规则）'),
    ('saber', 'sabía'): ('saber-', '-ía', '第一/三人称单数过去未完成时'),
    ('saber', 'sabré'): ('sabr-', '-é', '第一人称单数简单将来时（不规则）'),
    ('saber', 'sabrá'): ('sabr-', '-á', '第三人称单数简单将来时（不规则）'),
    ('saber', 'sabría'): ('sabr-', '-ía', '第一/三人称单数条件式（不规则）'),
    ('saber', 'sepa'): ('saber-', '-pa', '第一/三人称单数现在虚拟式（不规则）'),
    ('saber', 'sepas'): ('saber-', '-pas', '第二人称单数现在虚拟式（不规则）'),
    ('saber', 'sepamos'): ('saber-', '-pamos', '第一人称复数现在虚拟式（不规则）'),
    ('saber', 'sepan'): ('saber-', '-pan', '第三人称复数现在虚拟式（不规则）'),
    ('saber', 'sabido'): ('saber-', '-sabido', '过去分词'),
    ('saber', 'sabiendo'): ('saber-', '-sabiendo', '副动词'),
    # ver
    ('ver', 'veo'): ('ver-', '-eo', '第一人称单数现在时（不规则）'),
    ('ver', 'ves'): ('ver-', '-es', '第二人称单数现在时'),
    ('ver', 've'): ('ver-', '-e', '第三人称单数现在时'),
    ('ver', 'vemos'): ('ver-', '-emos', '第一人称复数现在时'),
    ('ver', 'veis'): ('ver-', '-eis', '第二人称复数现在时'),
    ('ver', 'ven'): ('ver-', '-en', '第三人称复数现在时'),
    ('ver', 'vi'): ('ver-', '-i', '第一人称单数简单过去时（不规则）'),
    ('ver', 'vio'): ('ver-', '-io', '第三人称单数简单过去时（不规则）'),
    ('ver', 'vieron'): ('ver-', '-ieron', '第三人称复数简单过去时（不规则）'),
    ('ver', 'veía'): ('ver-', '-ía', '第一/三人称单数过去未完成时'),
    ('ver', 'veré'): ('ver-', '-é', '第一人称单数简单将来时'),
    ('ver', 'verá'): ('ver-', '-á', '第三人称单数简单将来时'),
    ('ver', 'verán'): ('ver-', '-án', '第三人称复数简单将来时'),
    ('ver', 'vería'): ('ver-', '-ía', '第一/三人称单数条件式'),
    ('ver', 'vea'): ('ver-', '-ea', '第一/三人称单数现在虚拟式（不规则）'),
    ('ver', 'veas'): ('ver-', '-eas', '第二人称单数现在虚拟式（不规则）'),
    ('ver', 'veamos'): ('ver-', '-eamos', '第一人称复数现在虚拟式'),
    ('ver', 'vean'): ('ver-', '-ean', '第三人称复数现在虚拟式（不规则）'),
    ('ver', 'visto'): ('ver-', '-visto', '过去分词（不规则）'),
    ('ver', 'viendo'): ('ver-', '-viendo', '副动词'),
    # dar
    ('dar', 'doy'): ('dar-', '-oy', '第一人称单数现在时（不规则）'),
    ('dar', 'das'): ('dar-', '-as', '第二人称单数现在时'),
    ('dar', 'da'): ('dar-', '-a', '第三人称单数现在时'),
    ('dar', 'damos'): ('dar-', '-amos', '第一人称复数现在时'),
    ('dar', 'dais'): ('dar-', '-ais', '第二人称复数现在时'),
    ('dar', 'dan'): ('dar-', '-an', '第三人称复数现在时'),
    ('dar', 'di'): ('dar-', '-i', '第一人称单数简单过去时（不规则）'),
    ('dar', 'dio'): ('dar-', '-io', '第三人称单数简单过去时（不规则）'),
    ('dar', 'dieron'): ('dar-', '-ieron', '第三人称复数简单过去时（不规则）'),
    ('dar', 'daba'): ('dar-', '-aba', '第一/三人称单数过去未完成时'),
    ('dar', 'daré'): ('dar-', '-é', '第一人称单数简单将来时'),
    ('dar', 'dará'): ('dar-', '-á', '第三人称单数简单将来时'),
    ('dar', 'den'): ('dar-', '-en', '第一/三人称复数现在虚拟式'),
    ('dar', 'dado'): ('dar-', '-dado', '过去分词'),
    ('dar', 'dando'): ('dar-', '-dando', '副动词'),
    # venir
    ('venir', 'vengo'): ('venir-', '-go', '第一人称单数现在时（不规则）'),
    ('venir', 'vienes'): ('venir-', '-ienes', '第二人称单数现在时（不规则）'),
    ('venir', 'viene'): ('venir-', '-iene', '第三人称单数现在时（不规则）'),
    ('venir', 'venimos'): ('venir-', '-imos', '第一人称复数现在时'),
    ('venir', 'venís'): ('venir-', '-ís', '第二人称复数现在时'),
    ('venir', 'vienen'): ('venir-', '-ienen', '第三人称复数现在时（不规则）'),
    ('venir', 'vine'): ('venir-', '-ine', '第一人称单数简单过去时（不规则）'),
    ('venir', 'vino'): ('venir-', '-ino', '第三人称单数简单过去时（不规则）'),
    ('venir', 'vinieron'): ('venir-', '-inieron', '第三人称复数简单过去时（不规则）'),
    ('venir', 'venía'): ('venir-', '-ía', '第一/三人称单数过去未完成时'),
    ('venir', 'vendré'): ('vendr-', '-é', '第一人称单数简单将来时（不规则）'),
    ('venir', 'vendrá'): ('vendr-', '-á', '第三人称单数简单将来时（不规则）'),
    ('venir', 'vendría'): ('vendr-', '-ía', '第一/三人称单数条件式（不规则）'),
    ('venir', 'venga'): ('venir-', '-ga', '第一/三人称单数现在虚拟式（不规则）'),
    ('venir', 'vengas'): ('venir-', '-gas', '第二人称单数现在虚拟式（不规则）'),
    ('venir', 'vengamos'): ('venir-', '-gamos', '第一人称复数现在虚拟式（不规则）'),
    ('venir', 'vengan'): ('venir-', '-gan', '第三人称复数现在虚拟式（不规则）'),
    ('venir', 'venido'): ('venir-', '-venido', '过去分词'),
    ('venir', 'viniendo'): ('venir-', '-viniendo', '副动词'),
    # decir
    ('decir', 'digo'): ('decir-', '-go', '第一人称单数现在时（不规则）'),
    ('decir', 'dices'): ('decir-', '-ices', '第二人称单数现在时'),
    ('decir', 'dice'): ('decir-', '-ice', '第三人称单数现在时'),
    ('decir', 'decimos'): ('decir-', '-imos', '第一人称复数现在时'),
    ('decir', 'decís'): ('decir-', '-ís', '第二人称复数现在时'),
    ('decir', 'dicen'): ('decir-', '-icen', '第三人称复数现在时（不规则）'),
    ('decir', 'dije'): ('decir-', '-ije', '第一人称单数简单过去时（不规则）'),
    ('decir', 'dijo'): ('decir-', '-ijo', '第三人称单数简单过去时（不规则）'),
    ('decir', 'dijeron'): ('decir-', '-ijeron', '第三人称复数简单过去时（不规则）'),
    ('decir', 'decía'): ('decir-', '-ía', '第一/三人称单数过去未完成时'),
    ('decir', 'diré'): ('dir-', '-é', '第一人称单数简单将来时（不规则）'),
    ('decir', 'dirá'): ('dir-', '-á', '第三人称单数简单将来时（不规则）'),
    ('decir', 'dirían'): ('dir-', '-ían', '第三人称复数条件式（不规则）'),
    ('decir', 'digamos'): ('decir-', '-gamos', '第一人称复数现在虚拟式（不规则）'),
    ('decir', 'digan'): ('decir-', '-gan', '第三人称复数现在虚拟式（不规则）'),
    ('decir', 'dicho'): ('decir-', '-dicho', '过去分词（不规则）'),
    ('decir', 'diciendo'): ('decir-', '-diciendo', '副动词'),
    # pensar
    ('pensar', 'pienso'): ('pensar-', '-ienso', '第一人称单数现在时（元音变换 e→ie）'),
    ('pensar', 'piensas'): ('pensar-', '-iensas', '第二人称单数现在时（元音变换 e→ie）'),
    ('pensar', 'piensa'): ('pensar-', '-iensa', '第三人称单数现在时（元音变换 e→ie）'),
    ('pensar', 'pensamos'): ('pensar-', '-amos', '第一人称复数现在时'),
    ('pensar', 'pensáis'): ('pensar-', '-áis', '第二人称复数现在时'),
    ('pensar', 'piensan'): ('pensar-', '-iensan', '第三人称复数现在时（元音变换 e→ie）'),
    ('pensar', 'pensé'): ('pensar-', '-é', '第一人称单数简单过去时'),
    ('pensar', 'pensó'): ('pensar-', '-ó', '第三人称单数简单过去时'),
    ('pensar', 'pensaba'): ('pensar-', '-aba', '第一/三人称单数过去未完成时'),
    ('pensar', 'pensaré'): ('pensar-', '-é', '第一人称单数简单将来时'),
    ('pensar', 'pensará'): ('pensar-', '-á', '第三人称单数简单将来时'),
    ('pensar', 'pensaría'): ('pensar-', '-ía', '第一/三人称单数条件式'),
    ('pensar', 'piense'): ('pensar-', '-iense', '第一/三人称单数现在虚拟式（元音变换 e→ie）'),
    ('pensar', 'pienses'): ('pensar-', '-ienses', '第二人称单数现在虚拟式（元音变换 e→ie）'),
    ('pensar', 'pensemos'): ('pensar-', '-emos', '第一人称复数现在虚拟式'),
    ('pensar', 'piensen'): ('pensar-', '-iensen', '第三人称复数现在虚拟式（元音变换 e→ie）'),
    ('pensar', 'pensado'): ('pensar-', '-pensado', '过去分词'),
    ('pensar', 'pensando'): ('pensar-', '-pensando', '副动词'),
    # entender
    ('entender', 'entiendo'): ('entender-', '-iendo', '第一人称单数现在时（元音变换 e→ie）'),
    ('entender', 'entiendes'): ('entender-', '-iendes', '第二人称单数现在时（元音变换 e→ie）'),
    ('entender', 'entiende'): ('entender-', '-iende', '第三人称单数现在时（元音变换 e→ie）'),
    ('entender', 'entendemos'): ('entender-', '-emos', '第一人称复数现在时'),
    ('entender', 'entendéis'): ('entender-', '-éis', '第二人称复数现在时'),
    ('entender', 'entienden'): ('entender-', '-ienden', '第三人称复数现在时（元音变换 e→ie）'),
    ('entender', 'entendí'): ('entender-', '-í', '第一人称单数简单过去时'),
    ('entender', 'entendió'): ('entender-', '-ió', '第三人称单数简单过去时'),
    ('entender', 'entendía'): ('entender-', '-ía', '第一/三人称单数过去未完成时'),
    ('entender', 'entenderé'): ('entender-', '-é', '第一人称单数简单将来时'),
    ('entender', 'entenderá'): ('entender-', '-á', '第三人称单数简单将来时'),
    ('entender', 'entendería'): ('entender-', '-ía', '第一/三人称单数条件式'),
    ('entender', 'entienda'): ('entender-', '-ienda', '第一/三人称单数现在虚拟式（元音变换 e→ie）'),
    ('entender', 'entiendas'): ('entender-', '-iendas', '第二人称单数现在虚拟式（元音变换 e→ie）'),
    ('entender', 'entendamos'): ('entender-', '-amos', '第一人称复数现在虚拟式'),
    ('entender', 'entiendan'): ('entender-', '-iendan', '第三人称复数现在虚拟式（元音变换 e→ie）'),
    ('entender', 'entendido'): ('entender-', '-entendido', '过去分词'),
    ('entender', 'entendiendo'): ('entender-', '-entendiendo', '副动词'),
    # dejar
    ('dejar', 'dejo'): ('dejar-', '-o', '第一人称单数现在时'),
    ('dejar', 'dejas'): ('dejar-', '-as', '第二人称单数现在时'),
    ('dejar', 'deja'): ('dejar-', '-a', '第三人称单数现在时'),
    ('dejar', 'dejamos'): ('dejar-', '-amos', '第一人称复数现在时'),
    ('dejar', 'dejáis'): ('dejar-', '-áis', '第二人称复数现在时'),
    ('dejar', 'dejan'): ('dejar-', '-an', '第三人称复数现在时'),
    ('dejar', 'dejé'): ('dejar-', '-é', '第一人称单数简单过去时'),
    ('dejar', 'dejó'): ('dejar-', '-ó', '第三人称单数简单过去时'),
    ('dejar', 'dejaron'): ('dejar-', '-aron', '第三人称复数简单过去时'),
    ('dejar', 'dejaba'): ('dejar-', '-aba', '第一/三人称单数过去未完成时'),
    ('dejar', 'dejaré'): ('dejar-', '-é', '第一人称单数简单将来时'),
    ('dejar', 'dejará'): ('dejar-', '-á', '第三人称单数简单将来时'),
    ('dejar', 'dejarían'): ('dejar-', '-ían', '第三人称复数条件式'),
    ('dejar', 'deje'): ('dejar-', '-e', '第一/三人称单数现在虚拟式'),
    ('dejar', 'dejes'): ('dejar-', '-es', '第二人称单数现在虚拟式'),
    ('dejar', 'dejemos'): ('dejar-', '-emos', '第一人称复数现在虚拟式'),
    ('dejar', 'dejen'): ('dejar-', '-en', '第三人称复数现在虚拟式'),
    ('dejar', 'dejado'): ('dejar-', '-dejado', '过去分词'),
    ('dejar', 'dejando'): ('dejar-', '-dejando', '副动词'),
    # vivir
    ('vivir', 'vivo'): ('vivir-', '-o', '第一人称单数现在时'),
    ('vivir', 'vives'): ('vivir-', '-es', '第二人称单数现在时'),
    ('vivir', 'vive'): ('vivir-', '-e', '第三人称单数现在时'),
    ('vivir', 'vivimos'): ('vivir-', '-imos', '第一人称复数现在时'),
    ('vivir', 'vivís'): ('vivir-', '-ís', '第二人称复数现在时'),
    ('vivir', 'viven'): ('vivir-', '-en', '第三人称复数现在时'),
    ('vivir', 'viví'): ('vivir-', '-í', '第一人称单数简单过去时'),
    ('vivir', 'vivió'): ('vivir-', '-ió', '第三人称单数简单过去时'),
    ('vivir', 'vivieron'): ('vivir-', '-ieron', '第三人称复数简单过去时'),
    ('vivir', 'vivía'): ('vivir-', '-ía', '第一/三人称单数过去未完成时'),
    ('vivir', 'viviré'): ('vivir-', '-é', '第一人称单数简单将来时'),
    ('vivir', 'vivirá'): ('vivir-', '-á', '第三人称单数简单将来时'),
    ('vivir', 'viviría'): ('vivir-', '-ía', '第一/三人称单数条件式'),
    ('vivir', 'viva'): ('vivir-', '-a', '第一/三人称单数现在虚拟式'),
    ('vivir', 'vivas'): ('vivir-', '-as', '第二人称单数现在虚拟式'),
    ('vivir', 'vivamos'): ('vivir-', '-amos', '第一人称复数现在虚拟式'),
    ('vivir', 'vivan'): ('vivir-', '-an', '第三人称复数现在虚拟式'),
    ('vivir', 'vivido'): ('vivir-', '-vivido', '过去分词'),
    ('vivir', 'viviendo'): ('vivir-', '-viviendo', '副动词'),
    # llamar
    ('llamar', 'llamo'): ('llamar-', '-o', '第一人称单数现在时'),
    ('llamar', 'llamas'): ('llamar-', '-as', '第二人称单数现在时'),
    ('llamar', 'llama'): ('llamar-', '-a', '第三人称单数现在时'),
    ('llamar', 'llamamos'): ('llamar-', '-amos', '第一人称复数现在时'),
    ('llamar', 'llamáis'): ('llamar-', '-áis', '第二人称复数现在时'),
    ('llamar', 'llaman'): ('llamar-', '-an', '第三人称复数现在时'),
    ('llamar', 'llamé'): ('llamar-', '-é', '第一人称单数简单过去时'),
    ('llamar', 'llamó'): ('llamar-', '-ó', '第三人称单数简单过去时'),
    ('llamar', 'llamaron'): ('llamar-', '-aron', '第三人称复数简单过去时'),
    ('llamar', 'llamaba'): ('llamar-', '-aba', '第一/三人称单数过去未完成时'),
    ('llamar', 'llamaré'): ('llamar-', '-é', '第一人称单数简单将来时'),
    ('llamar', 'llamará'): ('llamar-', '-á', '第三人称单数简单将来时'),
    ('llamar', 'llamarían'): ('llamar-', '-ían', '第三人称复数条件式'),
    ('llamar', 'llame'): ('llamar-', '-e', '第一/三人称单数现在虚拟式'),
    ('llamar', 'llames'): ('llamar-', '-es', '第二人称单数现在虚拟式'),
    ('llamar', 'llamemos'): ('llamar-', '-emos', '第一人称复数现在虚拟式'),
    ('llamar', 'llamen'): ('llamar-', '-en', '第三人称复数现在虚拟式'),
    ('llamar', 'llamado'): ('llamar-', '-llamado', '过去分词'),
    ('llamar', 'llamando'): ('llamar-', '-llamando', '副动词'),
    # necesitar
    ('necesitar', 'necesito'): ('necesitar-', '-o', '第一人称单数现在时'),
    ('necesitar', 'necesitas'): ('necesitar-', '-as', '第二人称单数现在时'),
    ('necesitar', 'necesita'): ('necesitar-', '-a', '第三人称单数现在时'),
    ('necesitar', 'necesitamos'): ('necesitar-', '-amos', '第一人称复数现在时'),
    ('necesitar', 'necesitáis'): ('necesitar-', '-áis', '第二人称复数现在时'),
    ('necesitar', 'necesitan'): ('necesitar-', '-an', '第三人称复数现在时'),
    ('necesitar', 'necesité'): ('necesitar-', '-é', '第一人称单数简单过去时'),
    ('necesitar', 'necesitó'): ('necesitar-', '-ó', '第三人称单数简单过去时'),
    ('necesitar', 'necesitaba'): ('necesitar-', '-aba', '第一/三人称单数过去未完成时'),
    ('necesitar', 'necesitaré'): ('necesitar-', '-é', '第一人称单数简单将来时'),
    ('necesitar', 'necesitará'): ('necesitar-', '-á', '第三人称单数简单将来时'),
    ('necesitar', 'necesite'): ('necesitar-', '-e', '第一/三人称单数现在虚拟式'),
    ('necesitar', 'necesites'): ('necesitar-', '-es', '第二人称单数现在虚拟式'),
    ('necesitar', 'necesitemos'): ('necesitar-', '-emos', '第一人称复数现在虚拟式'),
    ('necesitar', 'necesiten'): ('necesitar-', '-en', '第三人称复数现在虚拟式'),
    ('necesitar', 'necesitado'): ('necesitar-', '-necesitado', '过去分词'),
    ('necesitar', 'necesitando'): ('necesitar-', '-necesitando', '副动词'),
    # pasar
    ('pasar', 'paso'): ('pasar-', '-o', '第一人称单数现在时'),
    ('pasar', 'pasas'): ('pasar-', '-as', '第二人称单数现在时'),
    ('pasar', 'pasa'): ('pasar-', '-a', '第三人称单数现在时'),
    ('pasar', 'pasamos'): ('pasar-', '-amos', '第一人称复数现在时'),
    ('pasar', 'pasáis'): ('pasar-', '-áis', '第二人称复数现在时'),
    ('pasar', 'pasan'): ('pasar-', '-an', '第三人称复数现在时'),
    ('pasar', 'pasé'): ('pasar-', '-é', '第一人称单数简单过去时'),
    ('pasar', 'pasó'): ('pasar-', '-ó', '第三人称单数简单过去时'),
    ('pasar', 'pasaron'): ('pasar-', '-aron', '第三人称复数简单过去时'),
    ('pasar', 'pasaba'): ('pasar-', '-aba', '第一/三人称单数过去未完成时'),
    ('pasar', 'pasaré'): ('pasar-', '-é', '第一人称单数简单将来时'),
    ('pasar', 'pasará'): ('pasar-', '-á', '第三人称单数简单将来时'),
    ('pasar', 'pasaría'): ('pasar-', '-ía', '第一/三人称单数条件式'),
    ('pasar', 'pase'): ('pasar-', '-e', '第一/三人称单数现在虚拟式'),
    ('pasar', 'pases'): ('pasar-', '-es', '第二人称单数现在虚拟式'),
    ('pasar', 'pasemos'): ('pasar-', '-emos', '第一人称复数现在虚拟式'),
    ('pasar', 'pasen'): ('pasar-', '-en', '第三人称复数现在虚拟式'),
    ('pasar', 'pasado'): ('pasar-', '-pasado', '过去分词'),
    ('pasar', 'pasando'): ('pasar-', '-pasando', '副动词'),
}


def detect_conjugation_suffix(infinitive: str, conjugated: str) -> Dict[str, str]:
    """
    Detect the conjugation pattern and return etymology breakdown.
    Returns: {"stem": "...", "suffix": "...", "tense_desc": "..."}
    """
    inf = infinitive.lower().strip()
    conj = conjugated.lower().strip()

    # First check irregular verb lookup
    irregular_key = (inf, conj)
    if irregular_key in IRREGULAR_VERBS:
        stem_display, suffix_display, tense_desc = IRREGULAR_VERBS[irregular_key]
        return {"stem": stem_display, "suffix": suffix_display, "tense_desc": tense_desc}

    # Remove infinitive ending to get stem
    if inf.endswith('ar'):
        stem = inf[:-2]
        inf_type = 'ar'
    elif inf.endswith('er'):
        stem = inf[:-2]
        inf_type = 'er'
    elif inf.endswith('ir'):
        stem = inf[:-2]
        inf_type = 'ir'
    else:
        stem = inf
        inf_type = 'unknown'

    # Try to find the suffix by removing stem from conjugated form
    # Handle stem-changing verbs
    suffix = ''
    tense_desc = ''

    # Common conjugation patterns
    patterns = [
        # Present indicative
        (stem + 'o', '第一人称单数现在时', '-o'),
        (stem + 'as', '第二人称单数现在时', '-as'),
        (stem + 'a', '第三人称单数现在时', '-a'),
        (stem + 'amos', '第一人称复数现在时', '-amos'),
        (stem + 'áis', '第二人称复数现在时', '-áis'),
        (stem + 'an', '第三人称复数现在时', '-an'),
        # Preterite (simple past)
        (stem + 'é', '第一人称单数简单过去时', '-é'),
        (stem + 'aste', '第二人称单数简单过去时', '-aste'),
        (stem + 'ó', '第三人称单数简单过去时', '-ó'),
        (stem + 'amos', '第一人称复数简单过去时', '-amos'),
        (stem + 'asteis', '第二人称复数简单过去时', '-asteis'),
        (stem + 'aron', '第三人称复数简单过去时', '-aron'),
        # Imperfect
        (stem + 'aba', '第一/三人称单数过去未完成时', '-aba'),
        (stem + 'abas', '第二人称单数过去未完成时', '-abas'),
        (stem + 'ábamos', '第一人称复数过去未完成时', '-ábamos'),
        (stem + 'aban', '第三人称复数过去未完成时', '-aban'),
        (stem + 'ía', '第一/三人称单数过去未完成时(er/ir)', '-ía'),
        (stem + 'ías', '第二人称单数过去未完成时(er/ir)', '-ías'),
        (stem + 'íamos', '第一人称复数过去未完成时(er/ir)', '-íamos'),
        (stem + 'ían', '第三人称复数过去未完成时(er/ir)', '-ían'),
        # Future
        (inf + 'é', '第一人称单数简单将来时', '原形 + -é'),
        (inf + 'ás', '第二人称单数简单将来时', '原形 + -ás'),
        (inf + 'á', '第三人称单数简单将来时', '原形 + -á'),
        (inf + 'emos', '第一人称复数简单将来时', '原形 + -emos'),
        (inf + 'éis', '第二人称复数简单将来时', '原形 + -éis'),
        (inf + 'án', '第三人称复数简单将来时', '原形 + -án'),
        # Conditional
        (inf + 'ía', '第一/三人称单数条件式', '原形 + -ía'),
        (inf + 'ías', '第二人称单数条件式', '原形 + -ías'),
        (inf + 'íamos', '第一人称复数条件式', '原形 + -íamos'),
        (inf + 'ían', '第三人称复数条件式', '原形 + -ían'),
        # Present subjunctive
        # For -ar verbs: stem + e, es, e, emos, éis, en
        # For -er/-ir verbs: stem + a, as, a, amos, áis, an
        # Gerund
        (stem + 'ando', '副动词(gerundio) -ar', '-ando'),
        (stem + 'iendo', '副动词(gerundio) -er/-ir', '-iendo'),
        # Past participle
        (stem + 'ado', '过去分词 -ar', '-ado'),
        (stem + 'ido', '过去分词 -er/-ir', '-ido'),
        # Imperative
        (stem + 'a', '命令式第二人称单数', '-a'),
        (stem + 'e', '命令式第一/三人称单数', '-e'),
        (stem + 'emos', '命令式第一人称复数', '-emos'),
        (stem + 'ed', '命令式第二人称复数', '-ed'),
        (stem + 'en', '命令式第一/三人称复数', '-en'),
    ]

    for pattern_form, desc, suffix_form in patterns:
        if conj == pattern_form:
            return {"stem": stem, "suffix": suffix_form, "tense_desc": desc}

    # Fallback: try to detect suffix by comparing stem and conjugated
    # Find the longest common prefix
    common_len = 0
    for a, b in zip(stem, conj):
        if a == b:
            common_len += 1
        else:
            break

    detected_suffix = conj[common_len:]
    if detected_suffix:
        return {"stem": stem, "suffix": detected_suffix, "tense_desc": "动词变位后缀"}

    return {"stem": stem, "suffix": conj, "tense_desc": "动词变位"}


# ---------------------------------------------------------------------------
# Determine CEFR level for verbs
# ---------------------------------------------------------------------------

def get_verb_level(infinitive: str) -> str:
    """Assign CEFR level based on verb frequency/commonness."""
    basic_verbs = {
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
        'caminar', 'cansar', 'llegar', 'recordar', 'tocar', 'ganar',
        'gastar', 'comprar', 'vender', 'pedir', 'preguntar', 'responder',
        'aprender', 'enseñar', 'cantar', 'bailar', 'nadar', 'cocinar',
    }
    intermediate_verbs = {
        'amanecer', 'atrever', 'carecer', 'desaparecer', 'despertar',
        'disponer', 'exigir', 'imaginar', 'mantener', 'ocurrir',
        'permitir', 'proponer', 'realizar', 'reconocer', 'reducir',
        'referir', 'resultar', 'soler', 'suceder', 'suponer',
        'transformar', 'transformarse', 'valer',
    }

    inf = infinitive.lower().strip()
    if inf in basic_verbs:
        return 'A2'
    elif inf in intermediate_verbs:
        return 'B1'
    else:
        return 'B2'


# ---------------------------------------------------------------------------
# Determine pronunciation focus
# ---------------------------------------------------------------------------

def get_pronunciation_focus(conjugated: str, infinitive: str) -> str:
    """Determine the key pronunciation focus for a verb form."""
    word = conjugated.lower().strip()

    # Check for specific Spanish pronunciation features
    if 'rr' in word or (word.startswith('r') and len(word) > 1):
        return 'rolled_r'
    if 'ñ' in word:
        return 'ny_sound'
    if 'll' in word:
        return 'll_y'
    if 'qu' in word or 'gu' in word:
        return 'gl_gu'
    if 'j' in word or 'g' in word:
        # Check if g is before e/i (j sound)
        idx = word.find('g')
        if idx >= 0 and idx + 1 < len(word) and word[idx+1] in 'ei':
            return 'j_sound'
    if 'h' in word:
        return 'silent_h'
    if 'ie' in word or 'ue' in word or 'ui' in word:
        return 'diphthong'

    # Check vowel sounds
    vowels_in_word = [ch for ch in strip_accents(word) if ch in 'aeiou']
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

    return 'vowel_a'  # default


# ---------------------------------------------------------------------------
# Create cloze sentence
# ---------------------------------------------------------------------------

def make_cloze(sentence: str, target: str) -> str:
    """Replace the target word in the sentence with ___."""
    # Case-insensitive replacement, preserve surrounding punctuation
    pattern = re.compile(re.escape(target), re.IGNORECASE)
    return pattern.sub('___', sentence, count=1)


# ---------------------------------------------------------------------------
# Read verbs from Excel
# ---------------------------------------------------------------------------

def read_verbs(xlsx_path: Path) -> List[Dict[str, Any]]:
    """Read verbs from the Excel file."""
    wb = openpyxl.load_workbook(str(xlsx_path), read_only=True)
    ws = wb.active
    verbs = []
    for row in range(2, ws.max_row + 1):
        no = ws.cell(row, 1).value
        infinitive = ws.cell(row, 2).value
        translation = ws.cell(row, 3).value
        conjugated = ws.cell(row, 4).value
        sentence_es = ws.cell(row, 5).value
        sentence_cn = ws.cell(row, 6).value

        if infinitive and conjugated:
            verbs.append({
                'no': int(no) if no else row - 1,
                'infinitive': str(infinitive).strip(),
                'translation': str(translation).strip() if translation else '',
                'conjugated': str(conjugated).strip(),
                'sentence_es': str(sentence_es).strip() if sentence_es else '',
                'sentence_cn': str(sentence_cn).strip() if sentence_cn else '',
            })
    wb.close()
    return verbs


# ---------------------------------------------------------------------------
# Generate flashcards
# ---------------------------------------------------------------------------

def generate_cards(verbs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate flashcard JSON from verb data."""
    cards = []
    for i, verb in enumerate(verbs, 1):
        conj = verb['conjugated']
        inf = verb['infinitive']

        # Etymology breakdown
        conj_info = detect_conjugation_suffix(inf, conj)
        stem_part = conj_info["stem"]
        if not stem_part.endswith('-'):
            stem_part += '-'

        etymology = [
            {
                "part": stem_part,
                "origin": f"动词原形 {inf}",
                "meaning": verb['translation']
            },
            {
                "part": conj_info["suffix"],
                "origin": "动词变位后缀",
                "meaning": conj_info["tense_desc"]
            }
        ]

        card = {
            "id": f"LCDP_S3E01_V{i:03d}",
            "episode": "S3E01",
            "scene_id": f"verb_{i:03d}",
            "line_index": i,
            "character": "S3E01",
            "target_word": conj,
            "ipa": word_to_ipa(conj),
            "pos": f"v. {conj}",
            "level": get_verb_level(inf),
            "pronunciation_focus": get_pronunciation_focus(conj, inf),
            "tags": ["动词"],
            "sentence_cloze": make_cloze(verb['sentence_es'], conj),
            "sentence_full": verb['sentence_es'],
            "translation": verb['translation'],
            "sentence_translation": verb['sentence_cn'],
            "cultural_note": "",
            "screenshot": "",
            "frequency_rank": None,
            "is_example_sentence": True,
            "etymology": etymology,
        }
        cards.append(card)

    return cards


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"Reading verbs from: {XLSX_PATH}")
    verbs = read_verbs(XLSX_PATH)
    print(f"Found {len(verbs)} verbs")

    print("Generating flashcards...")
    cards = generate_cards(verbs)
    print(f"Generated {len(cards)} flashcards")

    # Write cards JSON
    with open(OUTPUT_CARDS, 'w', encoding='utf-8') as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    print(f"Cards written to: {OUTPUT_CARDS}")

    # Write metadata JSON
    metadata = {
        "episode": "S3E01",
        "title": "Verbs from S3E01",
        "title_cn": "第三季第一集动词汇总",
        "description": "动词分类 — 从纸钞屋第三季第一集台词中提取的动词闪卡，每张卡展示动词变位及词源学拆分。",
        "scenes_count": 0,
        "dialogue_lines_count": len(cards),
        "characters": [],
        "scenes_summary": []
    }
    with open(OUTPUT_META, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Metadata written to: {OUTPUT_META}")

    # Summary
    levels = {}
    for c in cards:
        lv = c['level']
        levels[lv] = levels.get(lv, 0) + 1
    print(f"\nLevel distribution: {levels}")
    print("Done!")


if __name__ == '__main__':
    main()

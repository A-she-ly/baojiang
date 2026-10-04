/**
 * Spanish IPA generator using rule-based phonetic transcription.
 * Based on standard Spanish pronunciation rules (RFE/RAE).
 * Ported from scripts/generate_spanish_ipa.py
 */

// ---------------------------------------------------------------------------
// Vowel classification
// ---------------------------------------------------------------------------
const STRONG_VOWELS = new Set(['a', 'e', 'o'])
const WEAK_VOWELS = new Set(['i', 'u'])
const ALL_VOWELS = new Set([...STRONG_VOWELS, ...WEAK_VOWELS])
const ACCENTED_VOWELS = new Set(['á', 'é', 'í', 'ó', 'ú'])

const VOWEL_IPA: Record<string, string> = {
  'a': 'a', 'e': 'e', 'i': 'i', 'o': 'o', 'u': 'u',
  'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
  'ü': 'u',
}

const CONSONANT_SIMPLE: Record<string, string> = {
  'b': 'b', 'd': 'd', 'f': 'f', 'j': 'x', 'k': 'k',
  'l': 'l', 'm': 'm', 'ñ': 'ɲ', 'p': 'p', 's': 's',
  't': 't', 'w': 'w', 'v': 'b', 'x': 'ks', 'y': 'ʝ',
  'z': 'θ', 'h': '', 'q': 'k',
}

type Token = ['vowel' | 'consonant' | 'consonant_ctx', string, string]

const SPECIAL_CASES: Record<string, string> = {
  'méxico': '/me.xi.ko/',
  'mexico': '/ˈme.xi.ko/',
}

function preprocessWord(word: string): Token[] {
  const wordLower = word.toLowerCase().trim()
  const wordClean = wordLower.replace(/[.,!?;:'"()¿¡\[\]]/g, '')
  if (!wordClean) return []

  const tokens: Token[] = []
  let i = 0

  while (i < wordClean.length) {
    const ch = wordClean[i]

    // Digraphs
    if (i + 1 < wordClean.length) {
      const two = wordClean.substring(i, i + 2)

      if (two === 'ch') {
        tokens.push(['consonant', 'ch', 'tʃ'])
        i += 2; continue
      }
      if (two === 'll') {
        tokens.push(['consonant', 'll', ''])
        i += 2; continue
      }
      if (two === 'rr') {
        tokens.push(['consonant', 'rr', 'r'])
        i += 2; continue
      }
      if (two === 'qu' && i + 2 < wordClean.length && 'ei'.includes(wordClean[i + 2])) {
        tokens.push(['consonant', 'qu', 'k'])
        i += 3; continue
      }
      if (two === 'qu') {
        tokens.push(['consonant', 'qu', 'k'])
        i += 2; continue
      }
      if (two === 'gu' && i + 2 < wordClean.length && 'ei'.includes(wordClean[i + 2])) {
        if (wordClean[i + 1] === 'ü') {
          tokens.push(['consonant', 'gü', 'gw'])
          i += 2; continue
        } else {
          tokens.push(['consonant', 'gu', 'g'])
          i += 3; continue
        }
      }
    }

    // Single char
    if (ALL_VOWELS.has(ch) || ACCENTED_VOWELS.has(ch) || ch === 'ü') {
      tokens.push(['vowel', ch, ch])
    } else if (CONSONANT_SIMPLE[ch] !== undefined) {
      tokens.push(['consonant', ch, CONSONANT_SIMPLE[ch]])
    } else if ('cgnr'.includes(ch)) {
      tokens.push(['consonant_ctx', ch, ch])
    } else {
      tokens.push(['consonant', ch, ch])
    }

    i += 1
  }

  return tokens
}

function resolveContext(tokens: Token[]): Token[] {
  const result: Token[] = []

  for (let idx = 0; idx < tokens.length; idx++) {
    const [ptype, orig] = tokens[idx]

    if (ptype !== 'consonant_ctx') {
      result.push(tokens[idx])
      continue
    }

    // Find next vowel's original letter
    let nextVowelOrig = ''
    for (let j = idx + 1; j < tokens.length; j++) {
      if (tokens[j][0] === 'vowel') {
        nextVowelOrig = tokens[j][1].toLowerCase()
        break
      }
    }

    let ipa: string

    if (orig === 'c') {
      ipa = 'ei'.includes(nextVowelOrig) ? 'θ' : 'k'
    } else if (orig === 'g') {
      ipa = 'ei'.includes(nextVowelOrig) ? 'x' : 'g'
    } else if (orig === 'n') {
      // Assimilation: n -> m before b/p, n -> ŋ before k/g
      let nextConsOrig = ''
      for (let j = idx + 1; j < tokens.length; j++) {
        if (tokens[j][0] === 'consonant' || tokens[j][0] === 'consonant_ctx') {
          nextConsOrig = tokens[j][1].toLowerCase()
          break
        }
      }
      if (nextConsOrig && 'bp'.includes(nextConsOrig)) {
        ipa = 'm'
      } else if (nextConsOrig && 'kg'.includes(nextConsOrig)) {
        ipa = ''
      } else {
        ipa = 'n'
      }
    } else if (orig === 'r') {
      // Trilled at word start or after l/n/s
      if (idx === 0) {
        ipa = 'r'
      } else {
        const prevOrig = tokens[idx - 1][1].toLowerCase()
        ipa = 'lns'.includes(prevOrig) ? 'r' : 'ɾ'
      }
    } else {
      ipa = orig
    }

    result.push(['consonant', orig, ipa])
  }

  return result
}

function getStressPosition(wordLower: string): number {
  // Returns syllable index from end (0=last, 1=penultimate)
  for (let i = 0; i < wordLower.length; i++) {
    const ch = wordLower[i]
    if (ACCENTED_VOWELS.has(ch)) {
      const rest = wordLower.substring(i + 1)
      let count = 0
      let inV = false
      for (const c of rest) {
        if (ALL_VOWELS.has(c) || ACCENTED_VOWELS.has(c) || c === 'ü') {
          if (!inV) {
            count += 1
            inV = true
          }
        } else {
          inV = false
        }
      }
      return count
    }
  }

  const lastChar = wordLower[wordLower.length - 1]
  if ('aeiouáéíóúns'.includes(lastChar)) {
    return 1
  }
  return 0
}

function syllabify(tokens: Token[]): Token[][] {
  const vowelIdx: number[] = []
  for (let i = 0; i < tokens.length; i++) {
    if (tokens[i][0] === 'vowel') vowelIdx.push(i)
  }

  if (vowelIdx.length === 0) {
    return tokens.length > 0 ? [tokens] : []
  }

  const validClusters = new Set([
    'bl', 'br', 'cl', 'cr', 'dr', 'fl', 'fr',
    'gl', 'gr', 'pl', 'pr', 'tr',
  ])

  const syllables: Token[][] = []
  let start = 0

  for (let vi = 0; vi < vowelIdx.length; vi++) {
    const vidx = vowelIdx[vi]

    if (vi === vowelIdx.length - 1) {
      syllables.push(tokens.slice(start))
      break
    }

    const nextVidx = vowelIdx[vi + 1]
    const between = tokens.slice(vidx + 1, nextVidx)
    const betweenCons = between.filter((t) => t[0] === 'consonant' || t[0] === 'consonant_ctx')
    const betweenOrigs = betweenCons.map((t) => t[1]).join('')

    // Diphthong check
    const currV = tokens[vidx][1].toLowerCase()
    const nextV = tokens[nextVidx][1].toLowerCase()
    let isDiphthong = false

    if (WEAK_VOWELS.has(currV) && WEAK_VOWELS.has(nextV)) {
      isDiphthong = true
    } else if (WEAK_VOWELS.has(currV) && STRONG_VOWELS.has(nextV) && !'íú'.includes(currV)) {
      isDiphthong = true
    } else if (STRONG_VOWELS.has(currV) && WEAK_VOWELS.has(nextV) && !'íú'.includes(nextV)) {
      isDiphthong = true
    }

    if (isDiphthong && betweenCons.length === 0) {
      continue
    }

    const nCons = betweenCons.length

    if (nCons === 0 || nCons === 1) {
      syllables.push(tokens.slice(start, vidx + 1))
      start = vidx + 1
    } else if (nCons === 2) {
      if (validClusters.has(betweenOrigs)) {
        syllables.push(tokens.slice(start, vidx + 1))
        start = vidx + 1
      } else {
        const splitAt = vidx + 1 + 1
        syllables.push(tokens.slice(start, splitAt))
        start = splitAt
      }
    } else {
      syllables.push(tokens.slice(start, vidx + 2))
      start = vidx + 2
    }
  }

  return syllables.length > 0 ? syllables : [tokens]
}

/**
 * Convert a Spanish word to IPA transcription.
 * @example wordToIpa('todo') => '/ˈto.ðo/'
 */
export function wordToIpa(word: string): string {
  if (!word) return ''

  const wordLower = word.toLowerCase().trim()

  if (SPECIAL_CASES[wordLower]) {
    return SPECIAL_CASES[wordLower]
  }

  const wordClean = wordLower.replace(/[.,!?;:'"()¿¡\[\]]/g, '')
  if (!wordClean) return ''

  const stressFromEnd = getStressPosition(wordClean)
  let tokens = preprocessWord(wordClean)

  if (tokens.length === 0) {
    return `/${wordClean}/`
  }

  tokens = resolveContext(tokens)
  const syllables = syllabify(tokens)

  if (syllables.length === 0) {
    return `/${wordClean}/`
  }

  const ipaSyls = syllables.map((syl) =>
    syl.map((t) => t[2]).filter(Boolean).join('')
  )

  if (stressFromEnd < ipaSyls.length) {
    const idx = ipaSyls.length - 1 - stressFromEnd
    ipaSyls[idx] = 'ˈ' + ipaSyls[idx]
  }

  return '/' + ipaSyls.join('.') + '/'
}

import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import BilingualText, { Bi } from './BilingualText'
import type { Flashcard, SrsRating } from '../data/types'
import { useStore } from '../utils/store'
import { autoRateFromAttempts } from '../utils/srs'

const LEVEL_COLORS: Record<Flashcard['level'], string> = {
  A1: 'bg-green-100 text-green-800',
  A2: 'bg-emerald-100 text-emerald-800',
  B1: 'bg-yellow-100 text-yellow-800',
  B2: 'bg-orange-100 text-orange-800',
  C1: 'bg-red-100 text-red-800',
  C2: 'bg-rose-100 text-rose-800',
}

const CHAR_AVATAR: Record<string, string> = {
  Rachel: '‍♀️',
  Monica: '👩',
  Phoebe: '',
  Ross: '🦕',
  Chandler: '💼',
  Joey: '',
  All: '👥',
  Paul: '🍷',
  Frannie: '💅',
  Waitress: '',
}

interface Props {
  card: Flashcard
  canGoNext: boolean
  canGoPrev: boolean
  onCardComplete: (card: Flashcard, rating: SrsRating) => void
  onSessionComplete: () => void
  onRate: (rating: 'again' | 'hard' | 'good' | 'easy') => void
  onNext: () => void
  onPrev: () => void
  onDislike: (cardId: string) => void
  onMastered: (cardId: string) => void
  onWordClick: (cardId: string) => void
  wordMap: Map<string, string>
  progress: { current: number; total: number }
}

function renderCloze(sentence: string) {
  const parts = sentence.split(/(_{3,})/g)
  return parts.map((p, i) =>
    /^_+$/.test(p) ? <span key={i} className="cloze-blank">______</span> : <span key={i}>{p}</span>,
  )
}

function highlightWord(text: string, word: string) {
  const escaped = word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text
    .replace(new RegExp(`(${escaped})`, 'i'), '**$1**')
    .split('**')
    .map((seg, i) =>
      i % 2 === 1 ? (
        <mark key={i} className="bg-friends-accent/60 px-1 rounded">{seg}</mark>
      ) : (
        <span key={i}>{seg}</span>
      ),
    )
}

// ---------------------------------------------------------------------------
// Word link helpers
// ---------------------------------------------------------------------------

function normalizeWord(w: string): string {
  return w
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
}

/** Generate all normalized forms of a Spanish word (singular + plural) */
function wordForms(word: string): string[] {
  const base = normalizeWord(word)
  const forms = new Set<string>([base])
  if (base.endsWith('z')) forms.add(base.slice(0, -1) + 'ces')
  else if (base.endsWith('n') || base.endsWith('r') || base.endsWith('l')) forms.add(base + 'es')
  else if (base.endsWith('s') && base.length > 2) forms.add(base.slice(0, -1))
  else if (base.endsWith('es') && base.length > 3) forms.add(base.slice(0, -2))
  else forms.add(base + 's')
  return [...forms]
}

/** Build a word → cardId map from all cards */
export function buildWordMap(cards: Flashcard[]): Map<string, string> {
  const map = new Map<string, string>()
  for (const card of cards) {
    for (const form of wordForms(card.target_word)) {
      if (!map.has(form)) map.set(form, card.id)
    }
  }
  return map
}

interface SentenceWithLinksProps {
  text: string
  wordMap: Map<string, string>
  onWordClick: (cardId: string) => void
  highlightWord?: string
}

/** Render a sentence with clickable word links */
function SentenceWithLinks({ text, wordMap, onWordClick, highlightWord: hlWord }: SentenceWithLinksProps) {
  const tokens = text.split(/(\S+)/g)
  const hlNorm = hlWord ? normalizeWord(hlWord) : null

  return (
    <>
      {tokens.map((token, i) => {
        if (!/\S/.test(token)) return <span key={i}>{token}</span>
        const clean = token.replace(/[^\w\u00C0-\u024F]/g, '')
        const norm = normalizeWord(clean)
        const cardId = wordMap.get(norm)
        const isHl = hlNorm !== null && norm === hlNorm

        if (cardId) {
          return (
            <span
              key={i}
              onClick={(e) => { e.stopPropagation(); onWordClick(cardId) }}
              className={`cursor-pointer border-b border-dashed transition-colors ${
                isHl
                  ? 'bg-friends-accent/60 px-1 rounded border-friends-accent text-friends-sofa'
                  : 'text-friends-accent border-friends-accent/50 hover:text-friends-perk hover:border-friends-perk'
              }`}
              title="点击跳转到该单词闪卡"
            >
              {token}
            </span>
          )
        }
        return <span key={i}>{token}</span>
      })}
    </>
  )
}

export default function FlashcardView({
  card,
  canGoNext,
  canGoPrev,
  onCardComplete,
  onSessionComplete,
  onRate,
  onNext,
  onPrev,
  onDislike,
  onMastered,
  progress,
  onWordClick,
  wordMap,
}: Props) {
  const { t } = useTranslation()
  const [flipped, setFlipped] = useState(false)
  const [hintLevel, setHintLevel] = useState<'none' | 'light' | 'full'>('none')
  const [isPlaying, setIsPlaying] = useState(false)
  const favorites = useStore((s) => s.favorites)
  const toggleFavorite = useStore((s) => s.toggleFavorite)
  const disliked = useStore((s) => s.disliked)
  const toggleDislike = useStore((s) => s.toggleDislike)
  const mastered = useStore((s) => s.mastered)
  const toggleMastered = useStore((s) => s.toggleMastered)
  const markSeen = useStore((s) => s.markSeen)
  const isFav = favorites.has(card.id)
  const isDisliked = disliked.has(card.id)
  const isMastered = mastered.has(card.id)

  // Mark card as seen when it appears
  useEffect(() => {
    markSeen(card.id)
  }, [card.id, markSeen])

  // --- Quiz / answer input state ---
  const [userAnswer, setUserAnswer] = useState('')
  const [answerState, setAnswerState] = useState<'idle' | 'correct' | 'wrong' | 'revealed'>('idle')
  const [feedbackLevel, setFeedbackLevel] = useState<'almost' | 'not_quite'>('not_quite')
  const [attempts, setAttempts] = useState(0)
  const [autoRating, setAutoRating] = useState<SrsRating | null>(null)
  const [cardRated, setCardRated] = useState(false)  // Prevent double-counting
  const inputRef = useRef<HTMLInputElement>(null)

  // Focus input when card changes OR when flipping back to front
  useEffect(() => {
    // Skip focus when answer is correct/revealed (card will auto-advance)
    if (answerState === 'correct' || answerState === 'revealed') return
    let cancelled = false
    const focusInput = () => {
      if (cancelled) return
      const el = inputRef.current || document.querySelector('.cloze-input') as HTMLInputElement | null
      if (el && document.activeElement !== el) {
        el.focus()
      }
    }
    focusInput()
    const t1 = setTimeout(focusInput, 50)
    const t2 = setTimeout(focusInput, 150)
    const t3 = setTimeout(focusInput, 400)
    return () => {
      cancelled = true
      clearTimeout(t1)
      clearTimeout(t2)
      clearTimeout(t3)
    }
  }, [card.id, flipped, answerState])

  // Pronunciation focus label (main text only for badge)
  const pronLabel = (t(`pronunciation.${card.pronunciation_focus}`, { returnObjects: true }) as { main?: string })?.main ?? card.pronunciation_focus

  // Preload speech voices
  useEffect(() => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.getVoices()
      window.speechSynthesis.onvoiceschanged = () => {
        window.speechSynthesis.getVoices()
      }
    }
  }, [])

  function playTTS(text: string) {
    if (isPlaying) {
      window.speechSynthesis.cancel()
      setIsPlaying(false)
      return
    }
    const cleanText = text.replace(/\*|\(.*?\)/g, '').trim()
    if (!cleanText) return

    const isSpanish = card.id.startsWith('LCDP_')
    const lang = isSpanish ? 'es' : 'en'
    const encoded = encodeURIComponent(cleanText)
    const audio = new Audio(`/api/tts?text=${encoded}&lang=${lang}`)
    audio.onplay = () => setIsPlaying(true)
    audio.onended = () => setIsPlaying(false)
    audio.onerror = () => playBrowserTTS(cleanText)
    audio.play().catch(() => playBrowserTTS(cleanText))
  }

  function playBrowserTTS(text: string) {
    const utterance = new SpeechSynthesisUtterance(text)
    // Detect language from card ID prefix
    const isSpanish = card.id.startsWith('LCDP_')
    utterance.lang = isSpanish ? 'es-ES' : 'en-US'
    utterance.rate = 0.9
    const voices = window.speechSynthesis.getVoices()
    const targetLang = isSpanish ? 'es' : 'en'
    const langVoices = voices.filter((v) => v.lang.startsWith(targetLang))
    const preferred =
      langVoices.find((v) => v.name.includes('Microsoft') && v.name.includes('Online')) ||
      langVoices.find((v) => v.name.includes('Google')) ||
      langVoices.find((v) => v.name.includes('Microsoft')) ||
      langVoices[0]
    if (preferred) utterance.voice = preferred
    utterance.onstart = () => setIsPlaying(true)
    utterance.onend = () => setIsPlaying(false)
    utterance.onerror = () => setIsPlaying(false)
    window.speechSynthesis.speak(utterance)
  }

  const avatar = CHAR_AVATAR[card.character] ?? ''

  // Reset quiz state when card changes
  useEffect(() => {
    setUserAnswer('')
    setAnswerState('idle')
    setFeedbackLevel('not_quite')
    setAttempts(0)
    setAutoRating(null)
    setCardRated(false)
    setFlipped(false)
    setHintLevel('none')
  }, [card.id])

  const clozeLength = card.sentence_cloze.length
  const clozeFontSize = clozeLength > 120 ? 'text-lg' : clozeLength > 80 ? 'text-xl' : clozeLength > 50 ? 'text-2xl' : 'text-2xl sm:text-3xl'

  const fullLength = card.sentence_full.length
  const backFontSize = fullLength > 150 ? 'text-base' : fullLength > 100 ? 'text-lg' : 'text-lg'

  const ratingActions = useMemo(
    () => [
      { key: 'again' as const, label: 'rating.again', time: 'rating.againTime', cls: 'bg-green-700 hover:bg-green-800' },
      { key: 'hard' as const, label: 'rating.hard', time: 'rating.hardTime', cls: 'bg-green-600 hover:bg-green-700' },
      { key: 'good' as const, label: 'rating.good', time: 'rating.goodTime', cls: 'bg-green-400 hover:bg-green-500' },
      { key: 'easy' as const, label: 'rating.easy', time: 'rating.easyTime', cls: 'bg-green-200 hover:bg-green-300' },
    ],
    [],
  )

  const ratingBadge: Record<SrsRating, { label: string; time: string; cls: string }> = {
    again: { label: 'rating.again', time: 'rating.againTime', cls: 'bg-green-700 text-black' },
    hard: { label: 'rating.hard', time: 'rating.hardTime', cls: 'bg-green-600 text-black' },
    good: { label: 'rating.good', time: 'rating.goodTime', cls: 'bg-green-400 text-black' },
    easy: { label: 'rating.easy', time: 'rating.easyTime', cls: 'bg-green-200 text-black' },
  }

  function handleRate(r: 'again' | 'hard' | 'good' | 'easy') {
    onRate(r)
    setFlipped(false)
    setHintLevel('none')
    setAnswerState('idle')
    setFeedbackLevel('not_quite')
    setUserAnswer('')
    setAttempts(0)
    setAutoRating(null)
    if (canGoNext) onNext()
    else onSessionComplete()
  }

  // --- Answer checking ---
  function normalizeForMatch(text: string): string {
    return text
      .toLowerCase()
      .trim()
      .replace(/^(a|an|the)\s+/i, '')
      .replace(/[^\w\s]/g, '')
      .trim()
  }

  function isAnswerCorrect(input: string, target: string): boolean {
    if (!input.trim()) return false
    return normalizeForMatch(input) === normalizeForMatch(target)
  }

  /** Find the end index of the first vowel group in a word (for syllable-based feedback) */
  function firstVowelGroupEnd(word: string): number {
    const vowels = 'aeiou'
    let i = 0
    while (i < word.length && !vowels.includes(word[i])) i++
    if (i >= word.length) return Math.ceil(word.length / 2)
    while (i < word.length && vowels.includes(word[i])) i++
    return i
  }

  /** Evaluate answer: returns 'correct' | 'almost' | 'wrong' */
  function evaluateAnswer(input: string, target: string): 'correct' | 'almost' | 'wrong' {
    const normInput = normalizeForMatch(input)
    const normTarget = normalizeForMatch(target)
    if (!normInput) return 'wrong'
    if (normInput === normTarget) return 'correct'
    if (normTarget.includes(' ')) return 'wrong'
    let cpl = 0
    while (cpl < normInput.length && cpl < normTarget.length && normInput[cpl] === normTarget[cpl]) cpl++
    if (cpl === 0) return 'wrong'
    const fvgEnd = firstVowelGroupEnd(normTarget)
    if (cpl >= fvgEnd || cpl >= Math.ceil(normTarget.length / 2)) return 'almost'
    return 'wrong'
  }

  const ENCOURAGEMENTS = [
    'feedback.correct.youRock', 'feedback.correct.nailedIt', 'feedback.correct.spotOn', 'feedback.correct.perfect',
    'feedback.correct.brilliant', 'feedback.correct.thatsRight', 'feedback.correct.youGotIt', 'feedback.correct.excellent',
    'feedback.correct.amazing', 'feedback.correct.rightOn',
  ]
  const ALMOST_MESSAGES = [
    'feedback.almost.almostThere', 'feedback.almost.soClose', 'feedback.almost.justABitMore', 'feedback.almost.onFire',
  ]
  const NOT_QUITE_MESSAGES = [
    'feedback.notQuite.notQuite', 'feedback.notQuite.keepGoing', 'feedback.notQuite.notTheRightWord', 'feedback.notQuite.giveItAnotherShot',
  ]

  function checkAnswer() {
    if (!userAnswer.trim() || answerState === 'revealed') return
    const result = evaluateAnswer(userAnswer, card.target_word)
    if (result === 'correct') {
      const rating = autoRateFromAttempts(attempts, feedbackLevel, false)
      onRate(rating)
      setAutoRating(rating)
      setAnswerState('correct')
      if (!cardRated) {
        onCardComplete(card, rating)
        setCardRated(true)
      }
      // Auto-advance after showing encouragement
      setTimeout(() => {
        if (canGoNext) onNext()
        else onSessionComplete()
      }, 1500)
    } else {
      const nextAttempts = attempts + 1
      setAttempts(nextAttempts)
      setFeedbackLevel(result === 'almost' ? 'almost' : 'not_quite')
      setAnswerState('wrong')
      setUserAnswer('')
      setTimeout(() => setAnswerState('idle'), 1500)
    }
  }

  function revealAnswer() {
    const rating = autoRateFromAttempts(attempts, feedbackLevel, true)
    onRate(rating)
    setAutoRating(rating)
    setAnswerState('revealed')
    setUserAnswer('')
    onCardComplete(card, rating)
    setCardRated(true)  // Mark as rated to prevent double-counting
    // Auto-advance after showing answer
    setTimeout(() => {
      if (canGoNext) onNext()
      else onSessionComplete()
    }, 2500)
  }

  return (
    <div className="w-full max-w-2xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 text-sm text-friends-sofa/80">
        <div className="flex items-center gap-2">
          <button
            disabled={!canGoPrev}
            onClick={onPrev}
            className="px-3 py-1 rounded-full bg-white/60 hover:bg-white border border-friends-coffee/30 transition disabled:opacity-40 disabled:hover:bg-white/60"
          >
            <Bi i18nKey="card.prev" />
          </button>
          <span className="font-medium">
            {progress.current} / {progress.total}
          </span>
          <button
            disabled={!canGoNext}
            onClick={onNext}
            className="px-3 py-1 rounded-full bg-white/60 hover:bg-white border border-friends-coffee/30 transition disabled:opacity-40 disabled:hover:bg-white/60"
          >
            <Bi i18nKey="card.next" />
          </button>
        </div>
        <div className="flex items-center gap-3">
          <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${LEVEL_COLORS[card.level]}`}>
            {card.level}
          </span>
          <span
            title={t('card.pronunciationFocus', { label: pronLabel, returnObjects: true }) as any}
            className="px-2.5 py-0.5 rounded-full bg-white/70 border border-friends-coffee/30 text-xs font-medium"
          >
            {pronLabel}
          </span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="w-full h-1.5 rounded-full bg-friends-coffee/20 mb-5 overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-friends-perk to-friends-accent transition-all"
          style={{ width: `${(progress.current / progress.total) * 100}%` }}
        />
      </div>

      {/* Flip Card */}
      <div className="perspective w-full aspect-[4/5] sm:aspect-[5/4]">
        <div className={`card-3d ${flipped ? 'is-flipped' : ''}`}>
          {/* FRONT */}
          <div
            className="card-face front paper-texture cursor-pointer"
            onClick={() => {
              if (!cardRated && answerState !== 'correct' && answerState !== 'revealed') {
                // Peeking at back = revealed the answer, but still allow answering
                const rating = autoRateFromAttempts(attempts, feedbackLevel, true)
                onRate(rating)
                setAutoRating(rating)
                onCardComplete(card, rating)
                setCardRated(true)  // Prevent duplicate recording
              }
              setFlipped(true)
            }}
          >
            <div className="relative h-full w-full flex flex-col">
              <div className="flex-1 p-5 sm:p-7 flex flex-col">
                <div className="flex items-center justify-between mb-3 text-sm text-friends-sofa/80">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{avatar}</span>
                    <span className="font-semibold text-friends-sofa">{card.character}</span>
                    <span className="mx-1 text-friends-coffee/40">·</span>
                    <span className="text-xs">{card.id}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <button
                      className={`w-9 h-9 rounded-full flex items-center justify-center text-lg transition ${
                        isFav ? 'bg-green-100 text-green-600' : 'hover:bg-green-50 text-friends-coffee/60'
                      }`}
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleFavorite(card.id)
                      }}
                      title=" 喜欢"
                    >
                      👍
                    </button>
                    <button
                      className={`w-9 h-9 rounded-full flex items-center justify-center text-lg transition ${
                        isMastered ? 'bg-purple-100 text-purple-600' : 'hover:bg-purple-50 text-friends-coffee/60'
                      }`}
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleMastered(card.id)
                        onMastered(card.id)
                      }}
                      title="🧬 刻进 DNA（已掌握，不再复习）"
                    >
                      🧬
                    </button>
                    <button
                      className={`w-9 h-9 rounded-full flex items-center justify-center text-lg transition ${
                        isDisliked ? 'bg-red-100 text-red-600' : 'hover:bg-red-50 text-friends-coffee/60'
                      }`}
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleDislike(card.id)
                        onDislike(card.id)
                      }}
                      title=" 不喜欢（不再复习）"
                    >
                      👎
                    </button>
                  </div>
                </div>

                <div className={`${clozeFontSize} font-semibold text-friends-sofa leading-snug flex-1 flex items-start gap-2`} style={{ columnCount: 1 }}>
                  <div className="flex-1">
                    {answerState === 'revealed'
                      ? renderCloze(card.sentence_cloze)
                      : (
                        <>
                          {card.sentence_cloze.split(/(_{3,})/g).map((p, i) =>
                            /^_+$/.test(p)
                              ? (
                                <span key={i} className="inline-flex items-center gap-2">
                                  <input
                                    ref={i === 0 ? inputRef : undefined}
                                    autoFocus
                                    type="text"
                                    value={userAnswer}
                                    onChange={(e) => {
                                      setUserAnswer(e.target.value)
                                      if (answerState === 'wrong') setAnswerState('idle')
                                    }}
                                    onKeyDown={(e) => {
                                      if (e.key === 'Enter') checkAnswer()
                                    }}
                                    onClick={(e) => e.stopPropagation()}
                                    onFocus={(e) => e.stopPropagation()}
                                    disabled={false}
                                    placeholder=""
                                    autoComplete="off"
                                    autoCorrect="off"
                                    autoCapitalize="off"
                                    spellCheck={false}
                                    className="cloze-input"
                                  />
                                  {/* Play target word button */}
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      playTTS(card.target_word)
                                    }}
                                    className="w-6 h-6 rounded-full flex items-center justify-center transition text-sm bg-friends-accent/15 text-friends-accent hover:bg-friends-accent/30"
                                    title={`播放单词: ${card.target_word}`}
                                  >
                                    🔈
                                  </button>
                                </span>
                              )
                              : <SentenceWithLinks key={i} text={p} wordMap={wordMap} onWordClick={onWordClick} highlightWord={card.target_word} />
                          )}
                        </>
                      )
                    }
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      if (isPlaying) {
                        window.speechSynthesis.cancel()
                        setIsPlaying(false)
                      } else {
                        playTTS(card.sentence_full)
                      }
                    }}
                    className={`mt-1 flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center transition text-base ${
                      isPlaying
                        ? 'bg-friends-perk text-white animate-pulse'
                        : 'bg-friends-perk/15 text-friends-perk hover:bg-friends-perk/30'
                    }`}
                    title={t('card.readSentence', { returnObjects: true }) as any}
                  >
                    🔊
                  </button>
                </div>

                {/* Chinese translation */}
                {card.sentence_translation && (
                  <div className="mt-2 text-sm text-friends-coffee/70">
                    {card.sentence_translation}
                  </div>
                )}

                {/* Answer check button & feedback */}
                {answerState !== 'revealed' && (
                  <div className="mt-3 flex items-center justify-center gap-2">
                    <button
                      onClick={(e) => { e.stopPropagation(); checkAnswer(); }}
                      disabled={!userAnswer.trim()}
                      className="px-5 py-2 rounded-lg bg-friends-perk text-white text-sm font-semibold hover:bg-friends-perk/90 transition disabled:opacity-40 disabled:pointer-events-none"
                    >
                      <Bi i18nKey="card.checkAnswer" />
                    </button>
                  </div>
                )}

                {/* Feedback messages */}
                {answerState === 'correct' && (
                  <div className="mt-2 text-center">
                    <div className="text-lg font-semibold text-friends-perk animate-bounce">
                      <Bi i18nKey={ENCOURAGEMENTS[Math.floor(Math.random() * ENCOURAGEMENTS.length)]} />
                    </div>
                    {autoRating && (
                      <div className={`mt-2 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold ${ratingBadge[autoRating].cls}`}>
                        <Bi i18nKey="rating.autoScheduled" />
                        <span>·</span>
                        <Bi i18nKey={ratingBadge[autoRating].label} />
                        <span>·</span>
                        <Bi i18nKey={ratingBadge[autoRating].time} />
                      </div>
                    )}
                  </div>
                )}
                {answerState === 'wrong' && feedbackLevel === 'almost' && (
                  <div className="mt-2 text-center text-sm text-amber-600 font-medium">
                    <Bi i18nKey={ALMOST_MESSAGES[attempts % ALMOST_MESSAGES.length]} />
                  </div>
                )}
                {answerState === 'wrong' && feedbackLevel === 'not_quite' && (
                  <div className="mt-2 text-center text-sm text-rose-500 font-medium">
                    <Bi i18nKey={NOT_QUITE_MESSAGES[attempts % NOT_QUITE_MESSAGES.length]} />
                  </div>
                )}
                {answerState === 'revealed' && (
                  <div className="mt-2 text-center">
                    <div className="text-sm text-friends-accent font-medium mb-1">
                      <Bi i18nKey="card.answer" />
                    </div>
                    <div className="text-lg font-hand text-friends-sofa">{card.target_word}</div>
                    <div className="text-sm text-friends-coffee">{card.ipa} · {card.pos}</div>
                    {autoRating && (
                      <div className={`mt-2 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold ${ratingBadge[autoRating].cls}`}>
                        <Bi i18nKey="rating.autoScheduled" />
                        <span>·</span>
                        <Bi i18nKey={ratingBadge[autoRating].label} />
                        <span>·</span>
                        <Bi i18nKey={ratingBadge[autoRating].time} />
                      </div>
                    )}
                  </div>
                )}

                {/* Show Answer button (after 2 wrong attempts) */}
                {answerState !== 'revealed' && attempts >= 2 && (
                  <div className="mt-2 text-center">
                    <button
                      onClick={(e) => { e.stopPropagation(); revealAnswer(); }}
                      className="text-xs text-friends-accent hover:text-friends-accent/80 underline"
                    >
                      <Bi i18nKey="card.showAnswer" />
                    </button>
                  </div>
                )}

                {/* Hint buttons (hidden when answer is revealed) */}
                {answerState !== 'revealed' && (
                <div className="mt-4 flex flex-col items-center gap-2">
                  {hintLevel === 'none' && (
                    <div className="flex gap-2">
                      <button
                        onClick={(e) => { e.stopPropagation(); setHintLevel('light'); }}
                        className="px-3 py-1.5 rounded-full bg-friends-perk/20 text-friends-perk text-xs font-medium hover:bg-friends-perk/30 transition border border-friends-perk/30"
                      >
                        <Bi i18nKey="card.lightHint" />
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); revealAnswer(); }}
                        className="px-3 py-1.5 rounded-full bg-friends-accent/20 text-friends-accent text-xs font-medium hover:bg-friends-accent/30 transition border border-friends-accent/30"
                      >
                        <Bi i18nKey="card.giveAnswer" />
                      </button>
                    </div>
                  )}

                  {hintLevel === 'light' && (
                    <div className="text-center">
                      <div className="text-sm text-friends-perk font-medium mb-2">
                        <Bi i18nKey="card.lightHint" />
                      </div>
                      <div className="text-base text-friends-sofa">{card.pos}</div>
                      {card.translation && (
                        <div className="text-sm text-friends-perk mt-1">{card.translation}</div>
                      )}
                      <button
                        onClick={(e) => { e.stopPropagation(); setHintLevel('none'); }}
                        className="mt-2 text-xs text-friends-coffee/60 hover:text-friends-coffee"
                      >
                        <Bi i18nKey="card.collapseHint" />
                      </button>
                    </div>
                  )}

                  {hintLevel === 'full' && (
                    <div className="text-center">
                      <div className="text-sm text-friends-accent font-medium mb-2">
                        <Bi i18nKey="card.answer" />
                      </div>
                      <div className="text-lg font-hand text-friends-sofa mb-1">{card.target_word}</div>
                      <div className="text-sm text-friends-coffee mb-2">{card.ipa} · {card.pos}</div>
                      {card.is_example_sentence ? (
                        <div className="text-sm text-friends-coffee/80">{card.translation}</div>
                      ) : (
                        <div className="text-sm text-friends-coffee/80">
                          <Bi i18nKey="card.dialogueLine" values={{ character: card.character }} />
                        </div>
                      )}
                      <button
                        onClick={(e) => { e.stopPropagation(); setHintLevel('none'); }}
                        className="mt-2 text-xs text-friends-coffee/60 hover:text-friends-coffee"
                      >
                        <Bi i18nKey="card.collapseHint" />
                      </button>
                    </div>
                  )}

                  {hintLevel === 'none' && answerState !== 'correct' && (
                    <div className="text-center text-sm text-friends-coffee animate-pulse">
                      <Bi i18nKey="card.tapToShow" />
                    </div>
                  )}
                </div>
                )}
              </div>
            </div>
          </div>

          {/* BACK */}
          <div
            className="card-face back paper-texture cursor-pointer"
            onClick={() => setFlipped(false)}
          >
            <div className="h-full w-full flex flex-col p-5 sm:p-7 gap-4 overflow-y-auto">
              {/* Target word */}
              <div className="flex items-start justify-between gap-4 flex-wrap">
                <div className="flex items-start gap-3">
                  <div>
                    <div className="font-hand text-5xl sm:text-6xl text-friends-sofa leading-none">
                      {card.target_word}
                    </div>
                    {card.translation && (
                      <div className="mt-1 text-lg text-friends-perk font-medium">{card.translation}</div>
                    )}

                    {/* Etymology breakdown */}
                    {(card as any).etymology && (
                      <div className="mt-3 bg-white/70 rounded-xl p-4 border border-friends-coffee/20">
                        <div className="text-xs font-semibold mb-2 text-friends-perk flex items-center gap-1">
                          📚 词源学拆分
                        </div>
                        {/* Main breakdown formula */}
                        <div className="text-sm text-friends-sofa font-medium mb-3">
                          {card.target_word} = {(card as any).etymology.map((e: { part: string }, i: number) => (
                            <span key={i}>
                              {i > 0 && ' + '}
                              <span className="text-friends-accent font-semibold">{e.part}</span>
                            </span>
                          ))}
                        </div>
                        {/* Detailed table */}
                        <div className="space-y-2">
                          {(card as any).etymology.map((e: { part: string; origin: string; meaning: string }, idx: number) => (
                            <div key={idx} className="flex items-start gap-2 text-xs">
                              <span className="font-semibold text-friends-accent min-w-[3rem]">{e.part}</span>
                              <span className="text-friends-coffee/70 italic min-w-[6rem]">{e.origin}</span>
                              <span className="text-friends-sofa/90 flex-1">{e.meaning}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="mt-1 flex items-center gap-2 text-lg text-friends-coffee font-medium">
                      <span>{card.ipa}</span>
                      <span className="rounded bg-friends-perk/15 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-friends-perk">
                        {card.id.startsWith('LCDP_') ? 'Español' : 'GenAm'}
                      </span>
                    </div>
                    <div className="mt-1 text-sm text-friends-coffee/80">{card.pos}</div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      if (isPlaying) {
                        window.speechSynthesis.cancel()
                        setIsPlaying(false)
                      } else {
                        playTTS(card.target_word)
                      }
                    }}
                    className={`mt-1 flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center transition text-lg ${
                      isPlaying
                        ? 'bg-friends-perk text-white animate-pulse'
                        : 'bg-friends-perk/15 text-friends-perk hover:bg-friends-perk/30'
                    }`}
                    title={t('card.readWord', { returnObjects: true }) as any}
                  >
                    🔊
                  </button>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {card.tags.map((tg) => (
                    <span
                      key={tg}
                      className="px-2 py-0.5 rounded-full bg-friends-accent/20 text-friends-sofa text-xs font-medium border border-friends-accent/40"
                    >
                      #{tg}
                    </span>
                  ))}
                </div>
              </div>

              {/* Character + scene info */}
              <div className="flex items-center gap-2 text-sm text-friends-coffee/80">
                <span className="text-lg">{avatar}</span>
                <span className="font-medium text-friends-sofa">{card.character}</span>
                <span className="text-friends-coffee/40">·</span>
                <span className="text-xs">{card.scene_id.replace(/^scene_\d+_/, '').replace(/_/g, ' ')}</span>
              </div>

              {/* Context (transcript) or Example sentence */}
              {card.is_example_sentence ? (
                <div className="bg-white/70 rounded-xl p-4 border border-friends-coffee/20">
                  <div className="text-xs font-semibold mb-2 flex items-center gap-1">
                    <span className="text-friends-perk"><Bi i18nKey="card.exampleSentence" /></span>
                    <span className="ml-auto px-2 py-0.5 rounded bg-friends-coffee/10 text-friends-coffee/70 text-[10px] font-medium">
                      <Bi i18nKey="card.exampleNote" />
                    </span>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className={`${backFontSize} text-friends-sofa font-medium leading-relaxed flex-1`} style={{ columnCount: 1 }}>
                      {highlightWord(card.sentence_full, card.target_word)}
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        if (isPlaying) {
                          window.speechSynthesis.cancel()
                          setIsPlaying(false)
                        } else {
                          playTTS(card.sentence_full)
                        }
                      }}
                      className={`mt-0.5 flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center transition text-lg ${
                        isPlaying
                          ? 'bg-friends-perk text-white animate-pulse'
                          : 'bg-friends-perk/15 text-friends-perk hover:bg-friends-perk/30'
                      }`}
                      title={t('card.readExample', { returnObjects: true }) as any}
                    >
                      🔊
                    </button>
                  </div>
                  {card.sentence_translation && (
                    <div className="mt-2 text-base text-friends-coffee/90">
                       {card.sentence_translation}
                    </div>
                  )}
                </div>
              ) : (
                <div className="bg-white/70 rounded-xl p-4 border border-friends-coffee/20">
                  <div className="text-xs font-semibold mb-3 text-friends-perk">
                    <Bi i18nKey="card.context" />
                  </div>
                  {card.context_prev && (
                    <div className="mb-1" style={{ columnCount: 1 }}>
                      <div className="text-xs text-friends-coffee/70 italic">
                        <span className="text-friends-coffee/50">← </span>
                        {card.context_prev}
                      </div>
                      {card.context_prev_cn && (
                        <div className="text-xs text-friends-perk/80 mt-0.5 pl-3">
                          {card.context_prev_cn}
                        </div>
                      )}
                    </div>
                  )}
                  <div className="flex items-start gap-2">
                    <div className={`${backFontSize} text-friends-sofa font-medium leading-relaxed border-y border-friends-perk/30 py-2 flex-1`} style={{ columnCount: 1 }}>
                      <SentenceWithLinks text={card.sentence_full} wordMap={wordMap} onWordClick={onWordClick} highlightWord={card.target_word} />
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        if (isPlaying) {
                          window.speechSynthesis.cancel()
                          setIsPlaying(false)
                        } else {
                          playTTS(card.sentence_full)
                        }
                      }}
                      className={`mt-2 flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center transition text-lg ${
                        isPlaying
                          ? 'bg-friends-perk text-white animate-pulse'
                          : 'bg-friends-perk/15 text-friends-perk hover:bg-friends-perk/30'
                      }`}
                      title={t('card.readLine', { returnObjects: true }) as any}
                    >
                      {isPlaying ? '' : '🔊'}
                    </button>
                  </div>
                  {card.sentence_translation && (
                    <div className="text-base text-friends-perk font-medium mb-2" style={{ columnCount: 1 }}>
                      {card.sentence_translation}
                    </div>
                  )}
                  {card.context_next && (
                    <div className="mt-1" style={{ columnCount: 1 }}>
                      <div className="text-xs text-friends-coffee/70 italic">
                        <span className="text-friends-coffee/50">→ </span>
                        {card.context_next}
                      </div>
                      {card.context_next_cn && (
                        <div className="text-xs text-friends-perk/80 mt-0.5 pl-3">
                          {card.context_next_cn}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Additional context examples (for noun cards with multiple occurrences) */}
              {(card as any).context_examples && (card as any).context_examples.length > 1 && (
                <div className="bg-white/70 rounded-xl p-4 border border-friends-coffee/20">
                  <div className="text-xs font-semibold mb-3 text-friends-perk">
                    📖 更多台词引用 ({(card as any).context_examples.length})
                  </div>
                  <div className="space-y-3">
                    {(card as any).context_examples.slice(1).map((ctx: { espanol?: string; english?: string; chinese: string; seq: number }, idx: number) => {
                      const sentenceText = ctx.espanol || ctx.english || '';
                      return (
                      <div key={idx} className="border-l-2 border-friends-perk/30 pl-3">
                        <div className="text-sm text-friends-sofa font-medium leading-relaxed" style={{ columnCount: 1 }}>
                          <SentenceWithLinks text={sentenceText} wordMap={wordMap} onWordClick={onWordClick} highlightWord={card.target_word} />
                        </div>
                        {ctx.chinese && (
                          <div className="text-xs text-friends-perk/80 mt-1">
                            {ctx.chinese}
                          </div>
                        )}
                      </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Cultural note */}
              {card.cultural_note && (
                <div className="bg-friends-cream rounded-xl p-4 border-l-4 border-friends-perk">
                  <div className="text-xs uppercase tracking-wide text-friends-perk font-bold mb-1">
                    <Bi i18nKey="card.culturalNote" />
                  </div>
                  <div className="text-sm text-friends-sofa/90 leading-relaxed">
                    {card.cultural_note}
                  </div>
                </div>
              )}

              <div className="mt-auto pt-2 text-center text-xs text-friends-coffee/70">
                <Bi i18nKey="card.tapToHide" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

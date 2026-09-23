import { useEffect, useMemo, useRef, useState } from 'react'
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
  onComplete: () => void
  onRate: (rating: 'again' | 'hard' | 'good' | 'easy') => void
  onNext: () => void
  onPrev: () => void
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

export default function FlashcardView({
  card,
  canGoNext,
  canGoPrev,
  onComplete,
  onRate,
  onNext,
  onPrev,
  progress,
}: Props) {
  const { t } = useTranslation()
  const [flipped, setFlipped] = useState(false)
  const [hintLevel, setHintLevel] = useState<'none' | 'light' | 'full'>('none')
  const [isPlaying, setIsPlaying] = useState(false)
  const favorites = useStore((s) => s.favorites)
  const toggleFavorite = useStore((s) => s.toggleFavorite)
  const isFav = favorites.has(card.id)

  // --- Quiz / answer input state ---
  const [userAnswer, setUserAnswer] = useState('')
  const [answerState, setAnswerState] = useState<'idle' | 'correct' | 'wrong' | 'revealed'>('idle')
  const [feedbackLevel, setFeedbackLevel] = useState<'almost' | 'not_quite'>('not_quite')
  const [attempts, setAttempts] = useState(0)
  const [autoRating, setAutoRating] = useState<SrsRating | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

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

    const encoded = encodeURIComponent(cleanText)
    const audio = new Audio(`/api/tts?type=2&audio=${encoded}`)
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

  // Reset quiz state & autofocus when card changes
  useEffect(() => {
    setUserAnswer('')
    setAnswerState('idle')
    setFeedbackLevel('not_quite')
    setAttempts(0)
    setAutoRating(null)
    setFlipped(false)
    setHintLevel('none')
    setTimeout(() => inputRef.current?.focus(), 100)
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
    else onComplete()
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
      // Auto-advance after showing encouragement
      setTimeout(() => {
        if (canGoNext) onNext()
        else onComplete()
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
    // Auto-advance after showing answer
    setTimeout(() => {
      if (canGoNext) onNext()
      else onComplete()
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
            onClick={() => setFlipped(true)}
          >
            <div className="relative h-full w-full flex flex-col">
              <div className="h-1/2 w-full bg-friends-coffee/20 relative overflow-hidden">
                <img
                  src={card.screenshot}
                  alt="scene"
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    ;(e.target as HTMLImageElement).src =
                      '/episodes/S01E01/images/scene_001_central_perk.png'
                  }}
                />
                <div className="absolute top-3 left-3 flex items-center gap-2">
                  <span className="px-2.5 py-1 rounded-full bg-black/50 backdrop-blur text-white text-xs font-medium">
                    {card.scene_id.replace(/^scene_\d+_/, '').replace(/_/g, ' ')}
                  </span>
                </div>
                <button
                  className="absolute top-3 right-3 w-9 h-9 rounded-full bg-black/50 backdrop-blur text-white text-lg hover:bg-black/70 transition"
                  onClick={(e) => {
                    e.stopPropagation()
                    toggleFavorite(card.id)
                  }}
                  title={t('card.favorite', { returnObjects: true }) as any}
                >
                  {isFav ? '⭐' : '☆'}
                </button>
              </div>

              <div className="flex-1 p-5 sm:p-7 flex flex-col">
                <div className="flex items-center gap-2 mb-3 text-sm text-friends-sofa/80">
                  <span className="text-2xl">{avatar}</span>
                  <span className="font-semibold text-friends-sofa">{card.character}</span>
                  <span className="mx-1 text-friends-coffee/40">·</span>
                  <span className="text-xs">{card.id}</span>
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
                                <input
                                  key={i}
                                  ref={inputRef}
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
                                  placeholder="___"
                                  autoComplete="off"
                                  autoCorrect="off"
                                  autoCapitalize="off"
                                  spellCheck={false}
                                  className="cloze-input"
                                />
                              )
                              : <span key={i}>{p}</span>
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
                        onClick={(e) => { e.stopPropagation(); setHintLevel('full'); }}
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
                  {card.translation && (
                    <div className="mt-2 text-base text-friends-coffee/90">
                       {card.translation}
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

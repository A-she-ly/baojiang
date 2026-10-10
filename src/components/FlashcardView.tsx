import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import BilingualText, { Bi } from './BilingualText'
import type { Flashcard, SrsRating } from '../data/types'
import { useStore } from '../utils/store'
import { autoRateFromAttempts } from '../utils/srs'
import { playTTS as playTTSUtil, stopTTS } from '../utils/tts'

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
  onCreateCard?: (selectedText: string) => void
  onSearchStart: (cardIds: string[]) => void
  wordMap: Map<string, string>
  allCards: Flashcard[]
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
  phraseMap?: Map<string, string>  // 多词短语 → cardId 映射
}

/** Render a sentence with clickable word links */
function SentenceWithLinks({ text, wordMap, onWordClick, highlightWord: hlWord, phraseMap }: SentenceWithLinksProps) {
  const hlNorm = hlWord ? normalizeWord(hlWord) : null

  // 收集所有短语匹配位置（字符索引）
  interface PhraseMatch {
    start: number
    end: number
    cardId: string
    text: string
  }
  const matches: PhraseMatch[] = []
  if (phraseMap && phraseMap.size > 0) {
    const textLower = text.toLowerCase()
    for (const [phrase, cardId] of phraseMap) {
      const phraseLower = phrase.toLowerCase()
      let startIdx = 0
      while (true) {
        const idx = textLower.indexOf(phraseLower, startIdx)
        if (idx === -1) break
        matches.push({
          start: idx,
          end: idx + phrase.length,
          cardId,
          text: text.substring(idx, idx + phrase.length)
        })
        startIdx = idx + phrase.length
      }
    }
    // 按起始位置排序，长的优先
    matches.sort((a, b) => a.start - b.start || b.end - a.end)
  }

  // 构建非短语区域的列表
  interface TextSegment {
    text: string
    isPhrase: boolean
    cardId?: string
  }
  const segments: TextSegment[] = []
  let pos = 0
  for (const match of matches) {
    if (match.start >= pos) {
      // 添加前面的非短语文本
      if (match.start > pos) {
        segments.push({ text: text.substring(pos, match.start), isPhrase: false })
      }
      // 添加短语
      segments.push({ text: match.text, isPhrase: true, cardId: match.cardId })
      pos = match.end
    }
  }
  // 添加最后的非短语文本
  if (pos < text.length) {
    segments.push({ text: text.substring(pos), isPhrase: false })
  }

  // 渲染每个段落
  const elements: JSX.Element[] = []
  segments.forEach((seg, segIdx) => {
    if (seg.isPhrase) {
      // 短语作为整体链接
      elements.push(
        <span
          key={`phrase-${segIdx}`}
          onClick={(e) => { e.stopPropagation(); onWordClick(seg.cardId!) }}
          className="cursor-pointer border-b border-dashed text-friends-accent border-friends-accent/50 hover:text-friends-perk hover:border-friends-perk transition-colors"
          title="点击跳转到该短语闪卡"
        >
          {seg.text}
        </span>
      )
    } else {
      // 非短语文本，按单词处理
      const tokens = seg.text.split(/(\S+)/g)
      tokens.forEach((token, tokenIdx) => {
        const key = `seg-${segIdx}-tok-${tokenIdx}`
        if (!/\S/.test(token)) {
          elements.push(<span key={key}>{token}</span>)
          return
        }
        const clean = token.replace(/[^\w\u00C0-\u024F]/g, '')
        const norm = normalizeWord(clean)
        const cardId = wordMap.get(norm)
        const isHl = hlNorm !== null && norm === hlNorm

        if (cardId) {
          elements.push(
            <span
              key={key}
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
        } else {
          elements.push(<span key={key}>{token}</span>)
        }
      })
    }
  })

  return <>{elements}</>
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
  onCreateCard,
  onSearchStart,
  wordMap,
  allCards,
}: Props) {
  const { t } = useTranslation()
  const [flipped, setFlipped] = useState(false)
  const [hintLevel, setHintLevel] = useState<'none' | 'light' | 'full'>('none')
  const [isPlaying, setIsPlaying] = useState(false)
  const [ttsError, setTtsError] = useState<string | null>(null)

  // Search state
  const [searchQuery, setSearchQuery] = useState('')
  const [searchOpen, setSearchOpen] = useState(false)

  const searchResults = useMemo(() => {
    const q = searchQuery.trim().toLowerCase()
    if (!q) return []
    type ScoredCard = { card: Flashcard; score: number }
    const results: ScoredCard[] = []
    for (const c of allCards) {
      let score = 0
      const tw = c.target_word.toLowerCase()
      if (tw === q) score = 100
      else if (tw.startsWith(q)) score = 80
      else if (tw.includes(q)) score = 60
      if (c.translation?.toLowerCase().includes(q)) score = Math.max(score, 40)
      if (c.sentence_full?.toLowerCase().includes(q)) score = Math.max(score, 20)
      if (score > 0) results.push({ card: c, score })
    }
    results.sort((a, b) => b.score - a.score)
    return results.slice(0, 30).map((r) => r.card)
  }, [searchQuery, allCards])

  // Text selection state for creating new cards
  const [selectionPopup, setSelectionPopup] = useState<{ text: string; x: number; y: number } | null>(null)
  const cardAreaRef = useRef<HTMLDivElement>(null)
  const favorites = useStore((s) => s.favorites)
  const toggleFavorite = useStore((s) => s.toggleFavorite)
  const disliked = useStore((s) => s.disliked)
  const toggleDislike = useStore((s) => s.toggleDislike)
  const mastered = useStore((s) => s.mastered)
  const toggleMastered = useStore((s) => s.toggleMastered)
  const markSeen = useStore((s) => s.markSeen)
  const mnemonics = useStore((s) => s.mnemonics)
  const addMnemonic = useStore((s) => s.addMnemonic)
  const removeMnemonic = useStore((s) => s.removeMnemonic)
  const isFav = favorites.has(card.id)
  const isDisliked = disliked.has(card.id)
  const isMastered = mastered.has(card.id)

  // 构建短语映射：从 related_cards 中提取 target_word → cardId
  const phraseMap = useMemo(() => {
    const map = new Map<string, string>()
    if (card.related_cards) {
      for (const rel of card.related_cards) {
        // 从 label 中提取短语（括号前的部分）
        const match = rel.label.match(/^(.+?)（/)
        const phrase = match ? match[1].trim() : rel.label
        map.set(phrase, rel.cardId)
      }
    }
    return map
  }, [card.related_cards])

  // Mark card as seen when it appears
  useEffect(() => {
    markSeen(card.id)
  }, [card.id, markSeen])

  // Clear selection popup when card changes
  useEffect(() => {
    setSelectionPopup(null)
  }, [card.id])

  // Text selection detection
  useEffect(() => {
    const handleMouseUp = () => {
      const sel = window.getSelection()
      const text = sel?.toString().trim()
      if (text && text.length > 0 && text.length < 50 && cardAreaRef.current?.contains(sel?.anchorNode ?? null)) {
        const range = sel?.getRangeAt(0)
        if (range) {
          const rect = range.getBoundingClientRect()
          setSelectionPopup({
            text,
            x: rect.left + rect.width / 2,
            y: rect.top - 10,
          })
        }
      }
    }
    const handleMouseDown = () => {
      setSelectionPopup(null)
    }
    document.addEventListener('mouseup', handleMouseUp)
    document.addEventListener('mousedown', handleMouseDown)
    return () => {
      document.removeEventListener('mouseup', handleMouseUp)
      document.removeEventListener('mousedown', handleMouseDown)
    }
  }, [])

  // --- Quiz / answer input state ---
  const [userAnswer, setUserAnswer] = useState('')
  const [answerState, setAnswerState] = useState<'idle' | 'correct' | 'wrong' | 'revealed'>('idle')
  const [feedbackLevel, setFeedbackLevel] = useState<'almost' | 'not_quite'>('not_quite')
  const [attempts, setAttempts] = useState(0)
  const [autoRating, setAutoRating] = useState<SrsRating | null>(null)
  const [cardRated, setCardRated] = useState(false)  // Prevent double-counting
  const inputRef = useRef<HTMLInputElement>(null)

  // Mnemonic input state
  const [mnemonicInput, setMnemonicInput] = useState('')
  const [showMnemonicInput, setShowMnemonicInput] = useState(false)
  const cardMnemonics = mnemonics[card.id] || []

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

  // TTS wrapper
  const ttsLang = card.id.startsWith('LCDP_') ? 'es' as const : 'en' as const
  function handlePlay(text: string) {
    if (isPlaying) {
      stopTTS()
      setIsPlaying(false)
      return
    }
    playTTSUtil(text, ttsLang, () => setIsPlaying(true), () => setIsPlaying(false), (msg) => {
      setTtsError(msg)
      setTimeout(() => setTtsError(null), 5000)
    })
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
    <div ref={cardAreaRef} className="w-full max-w-2xl mx-auto px-4 py-6 relative">
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
            title={t('card.pronunciationFocus.main', { label: pronLabel })}
            className="px-2.5 py-0.5 rounded-full bg-white/70 border border-friends-coffee/30 text-xs font-medium"
          >
            {pronLabel}
          </span>
          {/* Search box */}
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => { setSearchQuery(e.target.value); setSearchOpen(true) }}
              onFocus={() => setSearchOpen(true)}
              onBlur={() => setTimeout(() => setSearchOpen(false), 200)}
              placeholder="🔍 查词..."
              className="w-36 px-2.5 py-1 text-xs rounded-lg border border-friends-coffee/30 bg-white/90 text-friends-sofa placeholder-friends-coffee/50 focus:outline-none focus:ring-2 focus:ring-friends-perk/40 focus:border-transparent transition-all"
            />
            {searchOpen && searchResults.length > 0 && (
              <div className="absolute right-0 top-full mt-1 w-72 max-h-80 overflow-y-auto bg-white rounded-xl shadow-xl border border-friends-coffee/20 z-50">
                {searchResults.map((c) => (
                  <div
                    key={c.id}
                    className="px-3 py-2 hover:bg-friends-accent/10 cursor-pointer border-b border-friends-coffee/10 last:border-0"
                    onMouseDown={(e) => {
                      e.preventDefault()
                      onSearchStart([c.id])
                      setSearchOpen(false)
                      setSearchQuery('')
                    }}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-friends-sofa text-sm">{c.target_word}</span>
                      <span className="text-xs text-friends-coffee/60">{c.pos}</span>
                    </div>
                    {c.translation && <div className="text-xs text-friends-perk mt-0.5">{c.translation}</div>}
                    {c.sentence_full && <div className="text-xs text-friends-coffee/60 mt-0.5 truncate">{c.sentence_full}</div>}
                  </div>
                ))}
              </div>
            )}
            {searchOpen && searchQuery && searchResults.length === 0 && (
              <div className="absolute right-0 top-full mt-1 w-72 bg-white rounded-xl shadow-xl border border-friends-coffee/20 z-50 px-3 py-4 text-center text-sm text-friends-coffee/60">
                没有找到匹配的词 / Sin resultados
              </div>
            )}
          </div>
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
              // Don't flip if user is selecting text (for creating cards)
              const sel = window.getSelection()
              if (sel && sel.toString().trim()) return

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
                                      handlePlay(card.target_word)
                                    }}
                                    className="w-6 h-6 rounded-full flex items-center justify-center transition text-sm bg-friends-accent/15 text-friends-accent hover:bg-friends-accent/30"
                                    title={`播放单词: ${card.target_word}`}
                                  >
                                    🔈
                                  </button>
                                </span>
                              )
                              : <SentenceWithLinks key={i} text={p} wordMap={wordMap} onWordClick={onWordClick} highlightWord={card.target_word} phraseMap={phraseMap} />
                          )}
                        </>
                      )
                    }
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handlePlay(card.sentence_full)
                    }}
                    className={`mt-1 flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center transition text-base ${
                      isPlaying
                        ? 'bg-friends-perk text-white animate-pulse'
                        : 'bg-friends-perk/15 text-friends-perk hover:bg-friends-perk/30'
                    }`}
                    title={t('card.readSentence.main')}
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
            onClick={() => {
              // Don't flip if user is selecting text (for creating cards)
              const sel = window.getSelection()
              if (sel && sel.toString().trim()) return
              setFlipped(false)
            }}
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

                    {/* Usage note for discourse markers and special usage */}
                    {(card as any).usage_note && (
                      <div className="mt-2 bg-amber-50 rounded-lg p-3 border-l-4 border-amber-400">
                        <div className="text-xs uppercase tracking-wide text-amber-700 font-bold mb-1">
                          💡 用法提示
                        </div>
                        <div className="text-sm text-amber-900 leading-relaxed">
                          {(card as any).usage_note}
                        </div>
                      </div>
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
                      handlePlay(card.target_word)
                    }}
                    className={`mt-1 flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center transition text-lg ${
                      isPlaying
                        ? 'bg-friends-perk text-white animate-pulse'
                        : 'bg-friends-perk/15 text-friends-perk hover:bg-friends-perk/30'
                    }`}
                    title={t('card.readWord.main')}
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
                  <div className="text-xs font-semibold mb-2">
                    <span className="text-friends-perk"><Bi i18nKey="card.exampleSentence" /></span>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className={`${backFontSize} text-friends-sofa font-medium leading-relaxed flex-1`} style={{ columnCount: 1 }}>
                      {highlightWord(card.sentence_full, card.target_word)}
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handlePlay(card.sentence_full)
                      }}
                      className={`mt-0.5 flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center transition text-lg ${
                        isPlaying
                          ? 'bg-friends-perk text-white animate-pulse'
                          : 'bg-friends-perk/15 text-friends-perk hover:bg-friends-perk/30'
                      }`}
                      title={t('card.readExample.main')}
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
                      <SentenceWithLinks text={card.sentence_full} wordMap={wordMap} onWordClick={onWordClick} highlightWord={card.target_word} phraseMap={phraseMap} />
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handlePlay(card.sentence_full)
                      }}
                      className={`mt-2 flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center transition text-lg ${
                        isPlaying
                          ? 'bg-friends-perk text-white animate-pulse'
                          : 'bg-friends-perk/15 text-friends-perk hover:bg-friends-perk/30'
                      }`}
                      title={t('card.readLine.main')}
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
                          <SentenceWithLinks text={sentenceText} wordMap={wordMap} onWordClick={onWordClick} highlightWord={card.target_word} phraseMap={phraseMap} />
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
                  <div className="text-xs uppercase tracking-wide text-friends-perk font-bold mb-2">
                    <Bi i18nKey="card.culturalNote" />
                  </div>
                  <div className="text-sm text-friends-sofa/90 leading-relaxed space-y-1">
                    {card.cultural_note.split('\n').map((line, i) => {
                      // Detect lines with IPA pattern: "word /ipa/ = description"
                      const ipaMatch = line.match(/^(.+?)\s+(\/[^/]+\/)\s*=\s*(.+)$/)
                      if (ipaMatch) {
                        const word = ipaMatch[1].trim()
                        const ipa = ipaMatch[2]
                        const rest = ipaMatch[3]
                        return (
                          <div key={i} className="flex items-start gap-1.5">
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                handlePlay(word)
                              }}
                              className={`flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center transition text-xs mt-0.5 ${
                                isPlaying
                                  ? 'bg-friends-perk text-white animate-pulse'
                                  : 'bg-friends-perk/15 text-friends-perk hover:bg-friends-perk/30'
                              }`}
                              title={`播放: ${word}`}
                            >
                              🔊
                            </button>
                            <span>
                              <span className="font-semibold text-friends-coffee">{word}</span>
                              <span className="text-[10px] text-primary-400 font-mono ml-1">{ipa}</span>
                              {' = '}{rest}
                            </span>
                          </div>
                        )
                      }
                      return <div key={i}>{line}</div>
                    })}
                  </div>
                </div>
              )}

              {/* Memory associations / Mnemonics */}
              <div className="bg-violet-50/80 rounded-xl p-4 border border-violet-200">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-xs uppercase tracking-wide text-violet-700 font-bold flex items-center gap-1">
                    🧠 记忆联想
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setShowMnemonicInput(!showMnemonicInput)
                    }}
                    className="text-xs text-violet-600 hover:text-violet-800 font-medium transition"
                  >
                    {showMnemonicInput ? '收起' : '+ 添加'}
                  </button>
                </div>

                {/* Existing mnemonics */}
                {cardMnemonics.length > 0 && (
                  <div className="space-y-2 mb-2">
                    {cardMnemonics.map((m, i) => (
                      <div key={i} className="flex items-start gap-2 text-sm text-violet-900 bg-white/60 rounded-lg px-3 py-2">
                        <span className="flex-1 leading-relaxed">{m}</span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            removeMnemonic(card.id, i)
                          }}
                          className="text-violet-400 hover:text-red-500 transition text-xs flex-shrink-0 mt-0.5"
                          title="删除"
                        >
                          ✕
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Input form */}
                {showMnemonicInput && (
                  <div className="mt-2" onMouseDown={(e) => e.stopPropagation()} onClick={(e) => e.stopPropagation()}>
                    <textarea
                      value={mnemonicInput}
                      onChange={(e) => setMnemonicInput(e.target.value)}
                      placeholder="例如：feas → fear（恐惧），恐惧是丑陋的"
                      className="w-full px-3 py-2 text-sm rounded-lg border border-violet-200 bg-white focus:outline-none focus:ring-2 focus:ring-violet-400 resize-none"
                      rows={2}
                      onMouseDown={(e) => e.stopPropagation()}
                      onClick={(e) => e.stopPropagation()}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault()
                          if (mnemonicInput.trim()) {
                            addMnemonic(card.id, mnemonicInput.trim())
                            setMnemonicInput('')
                          }
                        }
                      }}
                    />
                    <div className="flex justify-end mt-1.5">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          if (mnemonicInput.trim()) {
                            addMnemonic(card.id, mnemonicInput.trim())
                            setMnemonicInput('')
                          }
                        }}
                        disabled={!mnemonicInput.trim()}
                        className="px-3 py-1 text-xs rounded-lg bg-violet-600 text-white font-medium hover:bg-violet-700 transition disabled:opacity-40 disabled:pointer-events-none"
                      >
                        保存
                      </button>
                    </div>
                  </div>
                )}

                {cardMnemonics.length === 0 && !showMnemonicInput && (
                  <div className="text-xs text-violet-500 italic">
                    点击“+ 添加”记录你的记忆联想，帮助加深印象
                  </div>
                )}
              </div>

              <div className="mt-auto pt-2 text-center text-xs text-friends-coffee/70">
                <Bi i18nKey="card.tapToHide" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Floating "Create Card" button on text selection */}
      {selectionPopup && onCreateCard && (
        <div
          className="fixed z-50 transform -translate-x-1/2 -translate-y-full"
          style={{ left: selectionPopup.x, top: selectionPopup.y }}
          onMouseDown={(e) => e.stopPropagation()}
        >
          <button
            onClick={(e) => {
              e.stopPropagation()
              onCreateCard(selectionPopup.text)
              setSelectionPopup(null)
              window.getSelection()?.removeAllRanges()
            }}
            className="px-3 py-1.5 rounded-lg bg-friends-perk text-white text-xs font-semibold shadow-lg hover:bg-friends-perk/90 transition-all whitespace-nowrap animate-bounce"
          >
            ✨ Crear tarjeta / 创建闪卡
          </button>
          <div className="w-2 h-2 bg-friends-perk transform rotate-45 mx-auto -mt-1" />
        </div>
      )}

      {/* TTS error toast */}
      {ttsError && (
        <div className="fixed top-6 left-1/2 -translate-x-1/2 z-50 px-5 py-3 bg-red-500 text-white text-sm rounded-xl shadow-lg animate-pulse">
          {ttsError}
        </div>
      )}
    </div>
  )
}

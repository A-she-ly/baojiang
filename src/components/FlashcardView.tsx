import { useEffect, useMemo, useState } from 'react'
import { PRONUNCIATION_FOCUS_LABELS } from '../data/types'
import type { Flashcard } from '../data/types'
import { useStore } from '../utils/store'

const LEVEL_COLORS: Record<Flashcard['level'], string> = {
  A1: 'bg-green-100 text-green-800',
  A2: 'bg-emerald-100 text-emerald-800',
  B1: 'bg-yellow-100 text-yellow-800',
  B2: 'bg-orange-100 text-orange-800',
  C1: 'bg-red-100 text-red-800',
  C2: 'bg-rose-100 text-rose-800',
}

const CHAR_AVATAR: Record<string, string> = {
  Rachel: '👱♀️',
  Monica: '👩',
  Phoebe: '🎸',
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
  const [flipped, setFlipped] = useState(false)
  const [hintLevel, setHintLevel] = useState<'none' | 'light' | 'full'>('none')
  const [isPlaying, setIsPlaying] = useState(false)
  const favorites = useStore((s) => s.favorites)
  const toggleFavorite = useStore((s) => s.toggleFavorite)
  const isFav = favorites.has(card.id)

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

    // Youdao dictvoice API is designed for single words, not sentences
    // Use Youdao for short text (words), browser TTS for longer text (sentences)
    if (cleanText.length <= 20) {
      // Youdao API for words - more natural pronunciation
      const encoded = encodeURIComponent(cleanText)
      const audio = new Audio(`/api/tts?type=2&audio=${encoded}`)
      audio.onplay = () => setIsPlaying(true)
      audio.onended = () => setIsPlaying(false)
      audio.onerror = () => playBrowserTTS(cleanText)
      audio.play().catch(() => playBrowserTTS(cleanText))
    } else {
      // Browser TTS for sentences - Youdao fails on long text
      playBrowserTTS(cleanText)
    }
  }

  function playBrowserTTS(text: string) {
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'en-US'
    utterance.rate = 0.9
    // Pick the best available English voice (prefer neural/online voices)
    const voices = window.speechSynthesis.getVoices()
    const enVoices = voices.filter((v) => v.lang.startsWith('en'))
    const preferred =
      enVoices.find((v) => v.name.includes('Microsoft') && v.name.includes('Online')) ||
      enVoices.find((v) => v.name.includes('Google')) ||
      enVoices.find((v) => v.name.includes('Microsoft')) ||
      enVoices[0]
    if (preferred) utterance.voice = preferred
    utterance.onstart = () => setIsPlaying(true)
    utterance.onend = () => setIsPlaying(false)
    utterance.onerror = () => setIsPlaying(false)
    window.speechSynthesis.speak(utterance)
  }

  const avatar = CHAR_AVATAR[card.character] ?? '🎬'

  // Dynamic font size based on sentence length
  const clozeLength = card.sentence_cloze.length
  const clozeFontSize = clozeLength > 120 ? 'text-lg' : clozeLength > 80 ? 'text-xl' : clozeLength > 50 ? 'text-2xl' : 'text-2xl sm:text-3xl'

  // Back side sentence font size
  const fullLength = card.sentence_full.length
  const backFontSize = fullLength > 150 ? 'text-base' : fullLength > 100 ? 'text-lg' : 'text-lg'

  const ratingActions = useMemo(
    () => [
      { key: 'again' as const, label: '还不会', time: '10分钟', cls: 'bg-rose-500 hover:bg-rose-600' },
      { key: 'hard' as const, label: '有点印象', time: '1天', cls: 'bg-amber-500 hover:bg-amber-600' },
      { key: 'good' as const, label: '记住了', time: '3天', cls: 'bg-friends-perk hover:bg-green-700' },
      { key: 'easy' as const, label: '太简单', time: '7天+', cls: 'bg-sky-500 hover:bg-sky-600' },
    ],
    [],
  )

  function handleRate(r: 'again' | 'hard' | 'good' | 'easy') {
    onRate(r)
    setFlipped(false)
    setHintLevel('none')
    if (canGoNext) onNext()
    else onComplete()
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
            ← 上一张
          </button>
          <span className="font-medium">
            {progress.current} / {progress.total}
          </span>
          <button
            disabled={!canGoNext}
            onClick={onNext}
            className="px-3 py-1 rounded-full bg-white/60 hover:bg-white border border-friends-coffee/30 transition disabled:opacity-40 disabled:hover:bg-white/60"
          >
            下一张 →
          </button>
        </div>
        <div className="flex items-center gap-3">
          <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${LEVEL_COLORS[card.level]}`}>
            {card.level}
          </span>
          <span
            title={`发音重点：${PRONUNCIATION_FOCUS_LABELS[card.pronunciation_focus]}`}
            className="px-2.5 py-0.5 rounded-full bg-white/70 border border-friends-coffee/30 text-xs font-medium"
          >
            {PRONUNCIATION_FOCUS_LABELS[card.pronunciation_focus]}
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
                  title="收藏"
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

                <div className={`${clozeFontSize} font-semibold text-friends-sofa leading-snug flex-1 flex items-center`} style={{ columnCount: 1 }}>
                  {renderCloze(card.sentence_cloze)}
                </div>

                {/* Hint buttons */}
                <div className="mt-4 flex flex-col items-center gap-2">
                  {hintLevel === 'none' && (
                    <div className="flex gap-2">
                      <button
                        onClick={(e) => { e.stopPropagation(); setHintLevel('light'); }}
                        className="px-3 py-1.5 rounded-full bg-friends-perk/20 text-friends-perk text-xs font-medium hover:bg-friends-perk/30 transition border border-friends-perk/30"
                      >
                        💡 轻微提示
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); setHintLevel('full'); }}
                        className="px-3 py-1.5 rounded-full bg-friends-accent/20 text-friends-accent text-xs font-medium hover:bg-friends-accent/30 transition border border-friends-accent/30"
                      >
                         直接给答案
                      </button>
                    </div>
                  )}

                  {hintLevel === 'light' && (
                    <div className="text-center">
                      <div className="text-sm text-friends-perk font-medium mb-2">💡 轻微提示</div>
                      <div className="text-base text-friends-sofa">{card.pos}</div>
                      {card.translation && (
                        <div className="text-sm text-friends-perk mt-1">{card.translation}</div>
                      )}
                      <button
                        onClick={(e) => { e.stopPropagation(); setHintLevel('none'); }}
                        className="mt-2 text-xs text-friends-coffee/60 hover:text-friends-coffee"
                      >
                        收起提示
                      </button>
                    </div>
                  )}

                  {hintLevel === 'full' && (
                    <div className="text-center">
                      <div className="text-sm text-friends-accent font-medium mb-2">🎯 答案</div>
                      <div className="text-lg font-hand text-friends-sofa mb-1">{card.target_word}</div>
                      <div className="text-sm text-friends-coffee mb-2">{card.ipa} · {card.pos}</div>
                      {card.is_example_sentence ? (
                        <div className="text-sm text-friends-coffee/80">{card.translation}</div>
                      ) : (
                        <div className="text-sm text-friends-coffee/80">
                           {card.character} 的台词
                        </div>
                      )}
                      <button
                        onClick={(e) => { e.stopPropagation(); setHintLevel('none'); }}
                        className="mt-2 text-xs text-friends-coffee/60 hover:text-friends-coffee"
                      >
                        收起提示
                      </button>
                    </div>
                  )}

                  {hintLevel === 'none' && (
                    <div className="text-center text-sm text-friends-coffee animate-pulse">
                      👆 点击卡片查看答案
                    </div>
                  )}
                </div>
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
                        GenAm
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
                    title="朗读单词"
                  >
                    🔊
                  </button>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {card.tags.map((t) => (
                    <span
                      key={t}
                      className="px-2 py-0.5 rounded-full bg-friends-accent/20 text-friends-sofa text-xs font-medium border border-friends-accent/40"
                    >
                      #{t}
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
                    <span className="text-friends-perk">📖 包浆例句</span>
                    <span className="ml-auto px-2 py-0.5 rounded bg-friends-coffee/10 text-friends-coffee/70 text-[10px] font-medium">
                      示例句，非台词
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
                      title="朗读例句"
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
                     上下文
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
                      title="朗读台词"
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
                    💡 包浆注解
                  </div>
                  <div className="text-sm text-friends-sofa/90 leading-relaxed">
                    {card.cultural_note}
                  </div>
                </div>
              )}

              <div className="mt-auto pt-2 text-center text-xs text-friends-coffee/70">
                👆 点击卡片返回正面
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Rating buttons */}
      <div
        className={`mt-6 grid grid-cols-2 sm:grid-cols-4 gap-3 transition-all duration-500 ${
          flipped ? 'opacity-100 translate-y-0 pointer-events-auto' : 'opacity-0 translate-y-4 pointer-events-none'
        }`}
      >
        {ratingActions.map((a) => (
          <button
            key={a.key}
            onClick={() => handleRate(a.key)}
            className={`${a.cls} text-white py-3 px-2 rounded-xl shadow-md hover:shadow-lg transition-all font-semibold`}
          >
            <div className="text-base">{a.label}</div>
            <div className="text-xs opacity-90 mt-0.5">{a.time}后再见</div>
          </button>
        ))}
      </div>
    </div>
  )
}

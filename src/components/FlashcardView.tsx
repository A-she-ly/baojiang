import { useMemo, useState } from 'react'
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
  Rachel: '👱‍♀️',
  Monica: '👩',
  Phoebe: '🎸',
  Ross: '🦕',
  Chandler: '💼',
  Joey: '🍕',
  All: '👥',
  Paul: '🍷',
  Frannie: '💅',
  Waitress: '☕',
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
  // Replace ___ with styled blank span
  const parts = sentence.split(/(_{3,})/g)
  return parts.map((p, i) =>
    /^_+$/.test(p) ? <span key={i} className="cloze-blank">______</span> : <span key={i}>{p}</span>,
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
  const favorites = useStore((s) => s.favorites)
  const toggleFavorite = useStore((s) => s.toggleFavorite)
  const isFav = favorites.has(card.id)

  const avatar = CHAR_AVATAR[card.character] ?? '🎬'

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
          <span className="px-2.5 py-0.5 rounded-full bg-white/70 border border-friends-coffee/30 text-xs font-medium">
            {card.vowel_category}
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
              {/* Scene screenshot */}
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

              {/* Sentence area */}
              <div className="flex-1 p-5 sm:p-7 flex flex-col">
                <div className="flex items-center gap-2 mb-3 text-sm text-friends-sofa/80">
                  <span className="text-2xl">{avatar}</span>
                  <span className="font-semibold text-friends-sofa">{card.character}</span>
                  <span className="mx-1 text-friends-coffee/40">·</span>
                  <span className="text-xs">{card.id}</span>
                </div>

                <div className="text-2xl sm:text-3xl font-semibold text-friends-sofa leading-snug flex-1 flex items-center">
                  {renderCloze(card.sentence_cloze)}
                </div>

                <div className="mt-5 text-center text-sm text-friends-coffee animate-pulse">
                  👆 点击卡片查看答案
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
                <div>
                  <div className="font-hand text-5xl sm:text-6xl text-friends-sofa leading-none">
                    {card.target_word}
                  </div>
                  <div className="mt-2 text-lg text-friends-coffee font-medium">
                    {card.ipa}
                  </div>
                  <div className="mt-1 text-sm text-friends-coffee/80">{card.pos}</div>
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

              {/* Full sentence + translation */}
              <div className="bg-white/70 rounded-xl p-4 border border-friends-coffee/20">
                <div className="text-lg text-friends-sofa font-medium leading-relaxed">
                  {card.sentence_full.replace(
                    new RegExp(`(${card.target_word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'i'),
                    '**$1**',
                  ).split('**').map((seg, i) =>
                    i % 2 === 1 ? (
                      <mark key={i} className="bg-friends-accent/60 px-1 rounded">
                        {seg}
                      </mark>
                    ) : (
                      <span key={i}>{seg}</span>
                    ),
                  )}
                </div>
                <div className="mt-2 text-base text-friends-coffee/90">
                  🇨🇳 {card.translation}
                </div>
              </div>

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

      {/* Rating buttons - only visible when flipped */}
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

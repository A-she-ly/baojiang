import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import BilingualText, { Bi } from './BilingualText'
import type { Flashcard, SrsRating } from '../data/types'
import { useStore } from '../utils/store'
import { playTTS as playTTSUtil, stopTTS } from '../utils/tts'

const LEVEL_COLORS: Record<Flashcard['level'], string> = {
  A1: 'bg-green-100 text-green-800',
  A2: 'bg-emerald-100 text-emerald-800',
  B1: 'bg-yellow-100 text-yellow-800',
  B2: 'bg-orange-100 text-orange-800',
  C1: 'bg-red-100 text-red-800',
  C2: 'bg-rose-100 text-rose-800',
}

interface Props {
  card: Flashcard
  canGoNext: boolean
  canGoPrev: boolean
  onCardComplete: (card: Flashcard, rating: SrsRating) => void
  onSessionComplete: () => void
  onRate: (rating: SrsRating) => void
  onNext: () => void
  onPrev: () => void
  onDislike: (cardId: string) => void
  onMastered: (cardId: string) => void
  progress: { current: number; total: number }
}

export default function GrammarFlashcardView({
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
}: Props) {
  const { t } = useTranslation()
  const [flipped, setFlipped] = useState(false)
  const [answerState, setAnswerState] = useState<'idle' | 'correct' | 'wrong' | 'revealed'>('idle')
  const [attempts, setAttempts] = useState(0)
  const [cardRated, setCardRated] = useState(false)
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
  const [playing, setPlaying] = useState(false)

  function handlePlay() {
    if (playing) {
      stopTTS()
      setPlaying(false)
      return
    }
    playTTSUtil(card.target_word, 'es', () => setPlaying(true), () => setPlaying(false), () => {})
  }

  useEffect(() => {
    markSeen(card.id)
  }, [card.id, markSeen])

  useEffect(() => {
    setFlipped(false)
    setAnswerState('idle')
    setAttempts(0)
    setCardRated(false)
  }, [card.id])

  // Check grammar answers
  function checkAnswers() {
    const inputs = document.querySelectorAll('.grammar-input') as NodeListOf<HTMLInputElement>
    let allCorrect = true
    let filledCount = 0

    inputs.forEach((input) => {
      const answer = input.dataset.answer || ''
      const userVal = input.value.trim()
      if (userVal) filledCount++

      const possibleAnswers = answer.split('/').map((a) => a.trim())
      const isCorrect = possibleAnswers.some((a) => userVal === a)

      if (isCorrect) {
        input.classList.remove('grammar-input-wrong')
        input.classList.add('grammar-input-correct')
      } else if (userVal) {
        input.classList.remove('grammar-input-correct')
        input.classList.add('grammar-input-wrong')
        allCorrect = false
      } else {
        allCorrect = false
      }
    })

    if (filledCount === 0) return

    if (allCorrect) {
      const rating: SrsRating = 'easy'
      onRate(rating)
      setAnswerState('correct')
      if (!cardRated) {
        onCardComplete(card, rating)
        setCardRated(true)
      }
      setTimeout(() => setFlipped(true), 800)
    } else {
      const rating: SrsRating = attempts >= 2 ? 'hard' : 'again'
      onRate(rating)
      setAnswerState('wrong')
      if (!cardRated) {
        onCardComplete(card, rating)
        setCardRated(true)
      }
      setAttempts((a) => a + 1)
      setTimeout(() => setFlipped(true), 1200)
    }
  }

  function handleCardClick() {
    if (answerState === 'revealed') {
      setFlipped(false)
      return
    }
    if (!flipped) {
      // Front clicked - check answers
      if (answerState !== 'correct' && answerState !== 'wrong') {
        checkAnswers()
      } else {
        setFlipped(true)
      }
    } else {
      // Back clicked - flip back
      setFlipped(false)
    }
  }

  return (
    <div className="w-full max-w-2xl mx-auto px-4 py-6 relative">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 text-sm text-friends-sofa/80">
        <div className="flex items-center gap-2">
          <button
            disabled={!canGoPrev}
            onClick={onPrev}
            className="px-3 py-1 rounded-full bg-white/60 hover:bg-white border border-friends-coffee/30 transition disabled:opacity-40"
          >
            <Bi i18nKey="card.prev" />
          </button>
          <span className="font-medium">{progress.current} / {progress.total}</span>
          <button
            disabled={!canGoNext}
            onClick={onNext}
            className="px-3 py-1 rounded-full bg-white/60 hover:bg-white border border-friends-coffee/30 transition disabled:opacity-40"
          >
            <Bi i18nKey="card.next" />
          </button>
        </div>
        <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${LEVEL_COLORS[card.level]}`}>
          {card.level}
        </span>
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
          {/* FRONT - Quiz */}
          <div
            className="card-face front paper-texture cursor-pointer"
            onClick={handleCardClick}
          >
            <div className="relative h-full w-full flex flex-col">
              <div className="flex-1 p-5 sm:p-7 flex flex-col">
                {/* Action buttons */}
                <div className="flex items-center justify-between mb-3 text-sm text-friends-sofa/80">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">📚</span>
                    <span className="font-semibold text-friends-sofa">{card.grammar_topic}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <button
                      className={`w-9 h-9 rounded-full flex items-center justify-center text-lg transition ${
                        isFav ? 'bg-green-100 text-green-600' : 'hover:bg-green-50 text-friends-coffee/60'
                      }`}
                      onClick={(e) => { e.stopPropagation(); toggleFavorite(card.id) }}
                      title="喜欢"
                    >
                      👍
                    </button>
                    <button
                      className={`w-9 h-9 rounded-full flex items-center justify-center text-lg transition ${
                        isMastered ? 'bg-purple-100 text-purple-600' : 'hover:bg-purple-50 text-friends-coffee/60'
                      }`}
                      onClick={(e) => { e.stopPropagation(); toggleMastered(card.id); onMastered(card.id) }}
                      title="已掌握"
                    >
                      🧬
                    </button>
                    <button
                      className={`w-9 h-9 rounded-full flex items-center justify-center text-lg transition ${
                        isDisliked ? 'bg-red-100 text-red-600' : 'hover:bg-red-50 text-friends-coffee/60'
                      }`}
                      onClick={(e) => { e.stopPropagation(); toggleDislike(card.id); onDislike(card.id) }}
                      title="不喜欢"
                    >
                      👎
                    </button>
                  </div>
                </div>

                {/* Title */}
                <div className="flex items-center gap-2 mb-2">
                  <div className="text-2xl font-semibold text-friends-sofa">{card.target_word}</div>
                  <button
                    onClick={(e) => { e.stopPropagation(); handlePlay() }}
                    className={`p-1 rounded-full transition-all ${
                      playing
                        ? 'bg-friends-perk/20 text-friends-perk'
                        : 'text-friends-coffee/50 hover:text-friends-perk hover:bg-friends-perk/10'
                    }`}
                    title="Pronunciar / 朗读"
                  >
                    🔊
                  </button>
                </div>
                <div className="text-sm text-friends-perk mb-4">{card.translation}</div>

                {/* Quiz content */}
                {card.grammar_front_html && (
                  <div
                    className="grammar-quiz-content flex-1 overflow-y-auto"
                    dangerouslySetInnerHTML={{ __html: card.grammar_front_html }}
                  />
                )}

                {/* Feedback */}
                {answerState === 'correct' && (
                  <div className="mt-3 text-center">
                    <div className="text-lg font-semibold text-friends-perk animate-bounce">
                      太棒了！全部正确！🎉
                    </div>
                  </div>
                )}
                {answerState === 'wrong' && (
                  <div className="mt-3 text-center text-sm text-rose-500 font-medium">
                    有些答案不对，翻开卡片查看正确答案
                  </div>
                )}

                {/* Hint */}
                {answerState === 'idle' && (
                  <div className="mt-4 text-center text-sm text-friends-coffee animate-pulse">
                    填写答案后点击卡片检查，或直接翻开查看讲解
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* BACK - Explanation */}
          <div
            className="card-face back paper-texture cursor-pointer"
            onClick={() => setFlipped(false)}
          >
            <div className="h-full w-full flex flex-col p-5 sm:p-7 gap-4 overflow-y-auto">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="text-xl font-semibold text-friends-sofa">{card.target_word}</div>
                  <button
                    onClick={(e) => { e.stopPropagation(); handlePlay() }}
                    className={`p-1 rounded-full transition-all ${
                      playing
                        ? 'bg-friends-perk/20 text-friends-perk'
                        : 'text-friends-coffee/50 hover:text-friends-perk hover:bg-friends-perk/10'
                    }`}
                    title="Pronunciar / 朗读"
                  >
                    🔊
                  </button>
                </div>
                <div className="text-xs text-friends-coffee/60">点击翻回正面</div>
              </div>

              {card.grammar_content && (
                <div
                  className="grammar-content text-sm text-friends-sofa/90 leading-relaxed flex-1"
                  dangerouslySetInnerHTML={{ __html: card.grammar_content }}
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

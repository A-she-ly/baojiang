import { useEffect, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import FlashcardView from './components/FlashcardView'
import Home from './components/Home'
import ShowSelector from './components/ShowSelector'
import BilingualText, { Bi } from './components/BilingualText'
import { useStore } from './utils/store'
import type { EpisodeMetadata, Flashcard, SrsRating, SrsState } from './data/types'
import { SHOW_MAP } from './data/shows'

type SessionStats = {
  perfect: Flashcard[]    // 一把过 (easy)
  bumpy: Flashcard[]      // 小磕绊 (good/hard)
  needsWork: Flashcard[]  // 需夯实 (again)
}

import friendsCards from './data/S01E01_cards.json'
import friendsMeta from './data/S01E01_metadata.json'
import lcdpCards from './data/LCDP_S01E01_cards.json'
import lcdpMeta from './data/LCDP_S01E01_metadata.json'

const friendsCardsData = friendsCards as Flashcard[]
const friendsMetaData = friendsMeta as EpisodeMetadata
const lcdpCardsData = lcdpCards as Flashcard[]
const lcdpMetaData = lcdpMeta as EpisodeMetadata

/** Map of "showId:episodeId" → { cards, metadata } */
const EPISODE_DATA: Record<string, { cards: Flashcard[]; metadata: EpisodeMetadata }> = {
  'friends:S01E01': { cards: friendsCardsData, metadata: friendsMetaData },
  'la-casa-de-papel:S01E01': { cards: lcdpCardsData, metadata: lcdpMetaData },
}

const LS_SESSION_KEY = 'bjy_session_v1'

function loadSession(): { showId: string | null; episodeId: string | null } {
  try {
    const raw = localStorage.getItem(LS_SESSION_KEY)
    if (raw) return JSON.parse(raw)
  } catch { /* ignore */ }
  return { showId: null, episodeId: null }
}

function saveSession(showId: string | null, episodeId: string | null) {
  localStorage.setItem(LS_SESSION_KEY, JSON.stringify({ showId, episodeId }))
}

export default function App() {
  const { t } = useTranslation()
  const load = useStore((s) => s.load)
  const hydrate = useStore((s) => s.hydrate)
  const view = useStore((s) => s.view)
  const setView = useStore((s) => s.setView)
  const rateCard = useStore((s) => s.rateCard)
  const allCards = useStore((s) => s.cards)

  const savedSession = useMemo(() => loadSession(), [])
  const [ready, setReady] = useState(false)
  const [selectedShowId, setSelectedShowId] = useState<string | null>(savedSession.showId)
  const [selectedEpisodeId, setSelectedEpisodeId] = useState<string | null>(savedSession.episodeId)

  useEffect(() => {
    hydrate()
    setReady(true)
  }, [hydrate])

  // Persist session state
  useEffect(() => {
    saveSession(selectedShowId, selectedEpisodeId)
  }, [selectedShowId, selectedEpisodeId])

  // Load cards when episode is selected
  useEffect(() => {
    if (!selectedShowId || !selectedEpisodeId) return
    const key = `${selectedShowId}:${selectedEpisodeId}`
    const data = EPISODE_DATA[key]
    if (data) {
      load(data.cards)
    }
  }, [selectedShowId, selectedEpisodeId, load])

  const queueCards = useMemo(() => {
    if (view.name !== 'study') return []
    const byId = new Map(allCards.map((c) => [c.id, c]))
    return view.queueIds.map((id) => byId.get(id)).filter(Boolean) as Flashcard[]
  }, [view, allCards])

  const [queueIndex, setQueueIndex] = useState(0)
  const [sessionCompleted, setSessionCompleted] = useState(false)
  const [sessionStats, setSessionStats] = useState<SessionStats>({ perfect: [], bumpy: [], needsWork: [] })
  const [sessionCounter, setSessionCounter] = useState(0)  // Force remount on new session
  const srs = useStore((s) => s.srs)

  useEffect(() => {
    setQueueIndex(0)
    setSessionCompleted(false)
    setSessionStats({ perfect: [], bumpy: [], needsWork: [] })
  }, [view])

  // Current show & episode info
  const selectedShow = selectedShowId ? SHOW_MAP[selectedShowId] : null
  const episodeKey = selectedShowId && selectedEpisodeId ? `${selectedShowId}:${selectedEpisodeId}` : null
  const episodeData = episodeKey ? EPISODE_DATA[episodeKey] : null
  const selectedEpisode = selectedShow?.episodes.find((e) => e.episodeId === selectedEpisodeId)

  function handleSelectShow(showId: string) {
    const show = SHOW_MAP[showId]
    if (!show) return

    // If show has only one episode, auto-select it
    if (show.episodes.length === 1) {
      const ep = show.episodes[0]
      setSelectedShowId(showId)
      setSelectedEpisodeId(ep.episodeId)
    } else {
      setSelectedShowId(showId)
      setSelectedEpisodeId(null)
    }
    setView({ name: 'home' })
  }

  function handleSelectEpisode(episodeId: string) {
    setSelectedEpisodeId(episodeId)
  }

  function handleChangeShow() {
    setSelectedShowId(null)
    setSelectedEpisodeId(null)
    setView({ name: 'home' })
  }

  function handleCardComplete(card: Flashcard, rating: SrsRating) {
    setSessionStats((prev) => {
      const next = { ...prev }
      // Remove card from all categories first (allow re-rating)
      next.perfect = prev.perfect.filter((c) => c.id !== card.id)
      next.bumpy = prev.bumpy.filter((c) => c.id !== card.id)
      next.needsWork = prev.needsWork.filter((c) => c.id !== card.id)
      // Add to new category based on current rating
      if (rating === 'easy') next.perfect = [...next.perfect, card]
      else if (rating === 'good') next.bumpy = [...next.bumpy, card]
      else next.needsWork = [...next.needsWork, card]  // hard / again → 需夯实
      return next
    })
  }

  if (!ready) {
    return (
      <div className="min-h-screen flex items-center justify-center text-friends-sofa">
        <div className="text-center">
          <BilingualText
            i18nKey="app.name"
            as="div"
            className="font-hand text-5xl text-friends-sofa"
            zhClassName="text-friends-coffee/60"
          />
          <div className="mt-2 text-sm text-friends-coffee">
            <Bi i18nKey="app.loading" />
          </div>
        </div>
      </div>
    )
  }

  // No show selected → show selector
  if (!selectedShow) {
    return <ShowSelector onSelectShow={handleSelectShow} />
  }

  // Show selected but episode not yet chosen → episode list
  if (!selectedEpisodeId) {
    return (
      <div className="min-h-full">
        <div className="max-w-3xl mx-auto pt-4 px-4">
          <button
            onClick={handleChangeShow}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/80 border border-friends-coffee/30 text-friends-sofa text-sm font-medium hover:bg-white hover:shadow-md transition-all"
          >
            <Bi i18nKey="nav.changeShow" />
          </button>
        </div>
        <div className="max-w-3xl mx-auto px-4 py-8">
          <div className="flex items-center gap-3 mb-6">
            <span className="text-4xl">{selectedShow.coverEmoji}</span>
            <div>
              <BilingualText
                i18nKey={selectedShow.titleKey}
                as="h1"
                className="text-2xl font-bold text-friends-sofa"
                zhClassName="text-friends-coffee/60"
              />
              <p className="text-sm text-friends-coffee/80">
                <Bi i18nKey={selectedShow.descKey} />
              </p>
            </div>
          </div>

          <div className="space-y-3">
            {selectedShow.episodes.map((ep) => (
              <button
                key={ep.episodeId}
                onClick={() => ep.hasCards && handleSelectEpisode(ep.episodeId)}
                disabled={!ep.hasCards}
                className={`w-full text-left p-4 rounded-xl border transition-all ${
                  ep.hasCards
                    ? 'bg-white border-friends-coffee/10 hover:border-friends-perk/40 hover:shadow-card cursor-pointer'
                    : 'bg-friends-cream/50 border-friends-coffee/10 opacity-60 cursor-not-allowed'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-friends-sofa">{ep.title}</div>
                    <div className="text-sm text-friends-coffee/70 mt-0.5">{ep.description}</div>
                  </div>
                  {ep.hasCards ? (
                    <span className="px-3 py-1 rounded-full bg-friends-perk/15 text-friends-perk text-xs font-semibold">
                      ▶ <Bi i18nKey="show.episodes" />
                    </span>
                  ) : (
                    <span className="px-3 py-1 rounded-full bg-friends-coffee/10 text-friends-coffee/60 text-xs font-semibold">
                      <Bi i18nKey="show.comingSoon" />
                    </span>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    )
  }

  // Episode selected but no card data → Coming Soon
  if (!episodeData) {
    return (
      <div className="min-h-full">
        <div className="max-w-3xl mx-auto pt-4 px-4">
          <button
            onClick={() => setSelectedEpisodeId(null)}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/80 border border-friends-coffee/30 text-friends-sofa text-sm font-medium hover:bg-white hover:shadow-md transition-all"
          >
            ← <Bi i18nKey="show.episodes" />
          </button>
        </div>
        <div className="max-w-xl mx-auto px-4 py-16 text-center">
          <div className="text-6xl mb-4">🎬</div>
          <BilingualText
            i18nKey="show.comingSoon"
            as="h2"
            className="text-2xl font-bold text-friends-sofa mb-2"
            zhClassName="text-friends-coffee/60"
          />
          <p className="text-friends-coffee/80">
            <Bi i18nKey="show.comingSoonDesc" />
          </p>
          <p className="mt-4 text-sm text-friends-coffee/60">
            {selectedEpisode?.title}
          </p>
        </div>
      </div>
    )
  }

  // Study view
  if (view.name === 'study' && queueCards.length > 0) {
    const current = queueCards[queueIndex]

    return (
      <div className="min-h-full">
        <div className="max-w-3xl mx-auto pt-4 px-4">
          <button
            onClick={() => setView({ name: 'home' })}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/80 border border-friends-coffee/30 text-friends-sofa text-sm font-medium hover:bg-white hover:shadow-md transition-all"
          >
            <Bi i18nKey="nav.backHome" />
          </button>
        </div>

        {current ? (
          <FlashcardView
            key={`${current.id}-${sessionCounter}`}
            card={current}
            canGoNext={queueIndex < queueCards.length - 1}
            canGoPrev={queueIndex > 0}
            progress={{ current: queueIndex + 1, total: queueCards.length }}
            onCardComplete={handleCardComplete}
            onSessionComplete={() => setSessionCompleted(true)}
            onRate={(r) => rateCard(current.id, r)}
            onNext={() => {
              setQueueIndex((i) => Math.min(queueCards.length - 1, i + 1))
            }}
            onPrev={() => {
              setQueueIndex((i) => Math.max(0, i - 1))
            }}
          />
        ) : (
          <div className="text-center py-20 text-friends-coffee">
            <Bi i18nKey="session.empty" />
          </div>
        )}

        {sessionCompleted && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
            <div className="max-w-2xl w-full max-h-[90vh] overflow-y-auto bg-gradient-to-br from-friends-cream to-white border border-friends-perk/30 rounded-2xl p-6 shadow-2xl">
              {/* Header */}
              <div className="text-center mb-6">
                <div className="text-4xl mb-2">🎉</div>
                <BilingualText
                  i18nKey="session.complete"
                  as="div"
                  className="font-hand text-3xl text-friends-sofa"
                  zhClassName="text-friends-coffee/60"
                />
                <div className="mt-1 text-sm text-friends-coffee/90">
                  <Bi i18nKey="session.completeSub" />
                </div>
              </div>

              {/* Stats */}
              <div className="space-y-3 mb-6">
                {/* Perfect */}
                {sessionStats.perfect.length > 0 && (
                  <button
                    onClick={() => {
                      setSessionStats({ perfect: [], bumpy: [], needsWork: [] })
                      setSessionCompleted(false)
                      setQueueIndex(0)
                      setSessionCounter((c) => c + 1)  // Force remount
                      setView({ name: 'study', queueIds: sessionStats.perfect.map((c) => c.id) })
                    }}
                    className="w-full text-left bg-green-50 border border-green-200 rounded-xl p-4 hover:shadow-md hover:scale-[1.01] transition-all cursor-pointer"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-lg font-semibold text-green-800">
                        ✅ <Bi i18nKey="session.perfect" /> · {sessionStats.perfect.length}
                      </span>
                      <span className="text-sm text-green-700">
                        <Bi i18nKey="session.perfectTime" />
                      </span>
                    </div>
                    <div className="text-sm text-green-700">
                      <Bi i18nKey="session.perfectMsg" />
                    </div>
                  </button>
                )}

                {/* Bumpy */}
                {sessionStats.bumpy.length > 0 && (
                  <button
                    onClick={() => {
                      setSessionStats({ perfect: [], bumpy: [], needsWork: [] })
                      setSessionCompleted(false)
                      setQueueIndex(0)
                      setSessionCounter((c) => c + 1)  // Force remount
                      setView({ name: 'study', queueIds: sessionStats.bumpy.map((c) => c.id) })
                    }}
                    className="w-full text-left bg-amber-50 border border-amber-200 rounded-xl p-4 hover:shadow-md hover:scale-[1.01] transition-all cursor-pointer"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-lg font-semibold text-amber-800">
                        💪 <Bi i18nKey="session.bumpy" /> · {sessionStats.bumpy.length}
                      </span>
                      <span className="text-sm text-amber-700">
                        <Bi i18nKey="session.bumpyTime" />
                      </span>
                    </div>
                    <div className="text-sm text-amber-700">
                      <Bi i18nKey="session.bumpyMsg" />
                    </div>
                  </button>
                )}

                {/* Needs Work */}
                {sessionStats.needsWork.length > 0 && (
                  <button
                    onClick={() => {
                      setSessionStats({ perfect: [], bumpy: [], needsWork: [] })
                      setSessionCompleted(false)
                      setQueueIndex(0)
                      setSessionCounter((c) => c + 1)  // Force remount
                      setView({ name: 'study', queueIds: sessionStats.needsWork.map((c) => c.id) })
                    }}
                    className="w-full text-left bg-rose-50 border border-rose-200 rounded-xl p-4 hover:shadow-md hover:scale-[1.01] transition-all cursor-pointer"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-lg font-semibold text-rose-800">
                        🔥 <Bi i18nKey="session.needsWork" /> · {sessionStats.needsWork.length}
                      </span>
                      <span className="text-sm text-rose-700">
                        <Bi i18nKey="session.needsWorkTime" />
                      </span>
                    </div>
                    <div className="text-sm text-rose-700">
                      <Bi i18nKey="session.needsWorkMsg" />
                    </div>
                  </button>
                )}
              </div>

              {/* Actions */}
              <div className="flex flex-col gap-3">
                <button
                  onClick={() => setView({ name: 'home' })}
                  className="w-full py-3 rounded-xl bg-friends-paper text-friends-sofa font-semibold border border-friends-coffee/25 hover:bg-friends-accent/30 transition-all flex items-center justify-center gap-2"
                >
                  <span>🏠</span>
                  <Bi i18nKey="nav.home" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }

  // Home view with episode data
  return (
    <Home
      cards={allCards.length ? allCards : episodeData.cards}
      metadata={episodeData.metadata}
      show={selectedShow}
      episode={selectedEpisode}
      onChangeShow={handleChangeShow}
      onStart={(queueIds) => setView({ name: 'study', queueIds })}
    />
  )
}

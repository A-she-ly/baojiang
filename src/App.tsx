import { useEffect, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import FlashcardView from './components/FlashcardView'
import Home from './components/Home'
import ShowSelector from './components/ShowSelector'
import BilingualText, { Bi } from './components/BilingualText'
import { useStore } from './utils/store'
import type { EpisodeMetadata, Flashcard } from './data/types'
import { SHOW_MAP } from './data/shows'

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

export default function App() {
  const { t } = useTranslation()
  const load = useStore((s) => s.load)
  const hydrate = useStore((s) => s.hydrate)
  const view = useStore((s) => s.view)
  const setView = useStore((s) => s.setView)
  const rateCard = useStore((s) => s.rateCard)
  const allCards = useStore((s) => s.cards)

  const [ready, setReady] = useState(false)
  const [selectedShowId, setSelectedShowId] = useState<string | null>(null)
  const [selectedEpisodeId, setSelectedEpisodeId] = useState<string | null>(null)

  useEffect(() => {
    hydrate()
    setReady(true)
  }, [hydrate])

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

  useEffect(() => {
    setQueueIndex(0)
    setSessionCompleted(false)
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
            key={current.id}
            card={current}
            canGoNext={queueIndex < queueCards.length - 1}
            canGoPrev={queueIndex > 0}
            progress={{ current: queueIndex + 1, total: queueCards.length }}
            onComplete={() => setSessionCompleted(true)}
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
          <div className="max-w-2xl mx-auto mb-10 px-4">
            <div className="bg-gradient-to-r from-friends-perk/15 to-friends-accent/25 border border-friends-perk/30 rounded-2xl p-5 text-center">
              <BilingualText
                i18nKey="session.complete"
                as="div"
                className="font-hand text-3xl text-friends-sofa"
                zhClassName="text-friends-coffee/60"
              />
              <div className="mt-1 text-sm text-friends-coffee/90">
                <Bi i18nKey="session.completeSub" />
              </div>
              <button
                onClick={() => setView({ name: 'home' })}
                className="mt-4 px-6 py-2 rounded-xl bg-friends-sofa text-white font-semibold hover:bg-friends-coffee transition-all"
              >
                <Bi i18nKey="nav.home" />
              </button>
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

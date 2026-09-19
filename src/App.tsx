import { useEffect, useMemo, useState } from 'react'
import FlashcardView from './components/FlashcardView'
import Home from './components/Home'
import { useStore } from './utils/store'
import type { EpisodeMetadata, Flashcard } from './data/types'

import cardsData from './data/S01E01_cards.json'
import metadataData from './data/S01E01_metadata.json'

const cards = cardsData as Flashcard[]
const metadata = metadataData as EpisodeMetadata

export default function App() {
  const load = useStore((s) => s.load)
  const hydrate = useStore((s) => s.hydrate)
  const view = useStore((s) => s.view)
  const setView = useStore((s) => s.setView)
  const rateCard = useStore((s) => s.rateCard)
  const allCards = useStore((s) => s.cards)

  const [ready, setReady] = useState(false)

  useEffect(() => {
    load(cards)
    hydrate()
    setReady(true)
  }, [load, hydrate])

  const queueCards = useMemo(() => {
    if (view.name !== 'study') return []
    const byId = new Map(allCards.map((c) => [c.id, c]))
    return view.queueIds.map((id) => byId.get(id)).filter(Boolean) as Flashcard[]
  }, [view, allCards])

  const [queueIndex, setQueueIndex] = useState(0)

  useEffect(() => {
    setQueueIndex(0)
  }, [view.name])

  if (!ready) {
    return (
      <div className="min-h-screen flex items-center justify-center text-friends-sofa">
        <div className="text-center">
          <div className="font-hand text-5xl text-friends-sofa">包浆英语</div>
          <div className="mt-2 text-sm text-friends-coffee">泡杯咖啡，正在磨卡… ☕</div>
        </div>
      </div>
    )
  }

  if (view.name === 'home' || queueCards.length === 0) {
    return (
      <Home
        cards={allCards.length ? allCards : cards}
        metadata={metadata}
        onStart={(queueIds) => setView({ name: 'study', queueIds })}
      />
    )
  }

  const current = queueCards[queueIndex]

  return (
    <div className="min-h-full">
      <div className="max-w-3xl mx-auto pt-4 px-4">
        <button
          onClick={() => setView({ name: 'home' })}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/80 border border-friends-coffee/30 text-friends-sofa text-sm font-medium hover:bg-white hover:shadow-md transition-all"
        >
          ← 返回首页
        </button>
      </div>

      {current ? (
        <FlashcardView
          key={current.id}
          card={current}
          progress={{ current: queueIndex + 1, total: queueCards.length }}
          onRate={(r) => rateCard(current.id, r)}
          onNext={() => {
            setQueueIndex((i) => Math.min(queueCards.length - 1, i + 1))
          }}
          onPrev={() => {
            setQueueIndex((i) => Math.max(0, i - 1))
          }}
        />
      ) : (
        <div className="text-center py-20 text-friends-coffee">空的 🫥</div>
      )}

      {queueIndex === queueCards.length - 1 && (
        <div className="max-w-2xl mx-auto mb-10 px-4">
          <div className="bg-gradient-to-r from-friends-perk/15 to-friends-accent/25 border border-friends-perk/30 rounded-2xl p-5 text-center">
            <div className="font-hand text-3xl text-friends-sofa">🎉 本轮完成！</div>
            <div className="mt-1 text-sm text-friends-coffee/90">
              今天的包浆已经烤上了，下次见面继续磨～
            </div>
            <button
              onClick={() => setView({ name: 'home' })}
              className="mt-4 px-6 py-2 rounded-xl bg-friends-sofa text-white font-semibold hover:bg-friends-coffee transition-all"
            >
              返回首页
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

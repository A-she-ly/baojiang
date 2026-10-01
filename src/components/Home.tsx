import { useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import LanguageSwitcher from './LanguageSwitcher'
import BilingualText, { Bi } from './BilingualText'
import type { EpisodeMetadata, Flashcard, PronunciationFocus } from '../data/types'
import type { ShowDefinition, ShowEpisode } from '../data/showTypes'
import { useStore } from '../utils/store'

type FilterKey = 'all' | 'pos' | 'pronunciation' | 'character' | 'scene' | 'level' | 'tags'

interface Props {
  cards: Flashcard[]
  metadata: EpisodeMetadata
  show: ShowDefinition
  episode?: ShowEpisode
  onStart: (queueIds: string[]) => void
}

/** Helper: get the main (target language) text from a bilingual key */
function useBi(i18nKey: string, values?: Record<string, string | number>): string {
  const { t } = useTranslation()
  const raw = t(i18nKey, { ...values, returnObjects: true }) as { main?: string } | string
  return typeof raw === 'string' ? raw : (raw.main ?? i18nKey)
}

export default function Home({ cards, metadata, show, episode, onStart }: Props) {
  const { t } = useTranslation()
  const srs = useStore((s) => s.srs)
  const favorites = useStore((s) => s.favorites)

  const [selectedFilter, setSelectedFilter] = useState<FilterKey>('all')
  const [selectedValue, setSelectedValue] = useState<string | null>(null)

  // POS labels: use main text for filter logic, Bi component for display
  const POS_MAIN: Record<string, string> = {
    n: useBi('pos.n'), v: useBi('pos.v'), adj: useBi('pos.adj'), adv: useBi('pos.adv'),
    phrase: useBi('pos.phrase'), phrasal: useBi('pos.phrasal'), contraction: useBi('pos.contraction'),
  }

  const PRON_MAIN: Record<string, string> = {
    flap_t: useBi('pronunciation.flap_t'),
    vowel_uh: useBi('pronunciation.vowel_uh'),
    y_glide: useBi('pronunciation.y_glide'),
    vowel_ih: useBi('pronunciation.vowel_ih'),
    r_colored: useBi('pronunciation.r_colored'),
    o_diphthong: useBi('pronunciation.o_diphthong'),
    long_e: useBi('pronunciation.long_e'),
    weak_forms: useBi('pronunciation.weak_forms'),
    vowel_ah: useBi('pronunciation.vowel_ah'),
    vowel_ae: useBi('pronunciation.vowel_ae'),
    vowel_eh: useBi('pronunciation.vowel_eh'),
    schwa: useBi('pronunciation.schwa'),
  }

  const filters = useMemo(() => {
    const uniq = <T,>(arr: T[]) => Array.from(new Set(arr)).sort()

    const pos = uniq(
      cards.map((c) => {
        const raw = c.pos.toLowerCase()
        if (raw.startsWith('n.')) return 'n'
        if (raw.startsWith('v.')) return 'v'
        if (raw.startsWith('adj')) return 'adj'
        if (raw.startsWith('adv')) return 'adv'
        if (raw.includes('phrasal')) return 'phrasal'
        if (raw.includes('contraction')) return 'contraction'
        if (raw.includes('phrase')) return 'phrase'
        return 'other'
      }),
    )
    const pronunciation = uniq(cards.map((c) => c.pronunciation_focus))
    const chars = uniq(cards.map((c) => c.character))
    const scenes = metadata.scenes_summary.map((s) => s.scene_id)
    const levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'] as const
    const tags = uniq(cards.flatMap((c) => c.tags))
    return { pos, pronunciation, chars, scenes, levels, tags }
  }, [cards, metadata])

  const filteredCards = useMemo(() => {
    if (selectedFilter === 'all' || !selectedValue) return cards
    return cards.filter((c) => {
      if (selectedFilter === 'pos') {
        const raw = c.pos.toLowerCase()
        const key =
          raw.startsWith('n.') ? 'n' :
          raw.startsWith('v.') ? 'v' :
          raw.startsWith('adj') ? 'adj' :
          raw.startsWith('adv') ? 'adv' :
          raw.includes('phrasal') ? 'phrasal' :
          raw.includes('contraction') ? 'contraction' :
          raw.includes('phrase') ? 'phrase' : 'other'
        return key === selectedValue
      }
      if (selectedFilter === 'pronunciation') return c.pronunciation_focus === selectedValue
      if (selectedFilter === 'character') return c.character === selectedValue
      if (selectedFilter === 'scene') return c.scene_id === selectedValue
      if (selectedFilter === 'level') return c.level === selectedValue
      if (selectedFilter === 'tags') return c.tags.includes(selectedValue)
      return true
    })
  }, [cards, selectedFilter, selectedValue])

  const recommendedCards = useMemo(() => {
    const now = Date.now()
    const dueCards = filteredCards
      .filter((card) => !srs[card.id] || srs[card.id].dueAt <= now)
      .sort((a, b) => {
        const aState = srs[a.id]
        const bState = srs[b.id]
        if (Boolean(aState) !== Boolean(bState)) return aState ? -1 : 1
        return (aState?.dueAt ?? 0) - (bState?.dueAt ?? 0)
      })
    // Fall back to new cards when no due cards
    if (dueCards.length === 0) {
      return filteredCards.filter((card) => !srs[card.id])
    }
    return dueCards
  }, [filteredCards, srs])

  const stats = useMemo(() => {
    const due = cards.filter((c) => !srs[c.id] || srs[c.id].dueAt <= Date.now()).length
    const learned = cards.filter((c) => srs[c.id]?.status === 'review').length
    const learning = cards.filter((c) => srs[c.id]?.status === 'learning').length
    const newCount = cards.filter((c) => !srs[c.id]).length
    return { due, learned, learning, new: newCount, favCount: favorites.size }
  }, [cards, srs, favorites])

  const sceneName = (id: string) =>
    metadata.scenes_summary.find((s) => s.scene_id === id)?.scene_name || id

  function pickChips() {
    if (selectedFilter === 'pos')
      return filters.pos.map((v) => ({ value: v, label: POS_MAIN[v] || v, i18nKey: `pos.${v}` }))
    if (selectedFilter === 'pronunciation')
      return filters.pronunciation.map((v) => ({
        value: v,
        label: PRON_MAIN[v] || v,
        i18nKey: `pronunciation.${v}`,
      }))
    if (selectedFilter === 'character')
      return filters.chars.map((v) => ({ value: v, label: v, i18nKey: null }))
    if (selectedFilter === 'scene')
      return filters.scenes.map((v) => ({
        value: v,
        label: sceneName(v).slice(0, 18) + (sceneName(v).length > 18 ? '…' : ''),
        i18nKey: null,
      }))
    if (selectedFilter === 'level')
      return filters.levels.map((v) => ({ value: v, label: v, i18nKey: null }))
    if (selectedFilter === 'tags')
      return filters.tags.map((v) => ({ value: v, label: '#' + v, i18nKey: null }))
    return []
  }

  function startSession(sessionCards: Flashcard[]) {
    if (sessionCards.length === 0) return
    onStart(sessionCards.map((card) => card.id))
  }

  const tabItems: { key: FilterKey; i18nKey: string; icon: string }[] = [
    { key: 'all', i18nKey: 'home.filterAll', icon: '📚' },
    { key: 'pos', i18nKey: 'home.filterPos', icon: '🔤' },
    { key: 'pronunciation', i18nKey: 'home.filterPronunciation', icon: '️' },
  ]

  return (
    <div className="min-h-full">
      {/* Header */}
      <header className="relative overflow-hidden">
        <div className="relative px-6 pt-10 pb-14 max-w-4xl mx-auto">
          {/* Top bar: language */}
          <div className="absolute top-4 right-4 flex items-center gap-2">
            <LanguageSwitcher />
          </div>

          <div className="flex items-center gap-3">
            <span className="text-4xl">{show.coverEmoji}</span>
            <div>
              <BilingualText
                i18nKey={show.titleKey}
                as="div"
                className="text-3xl sm:text-4xl font-semibold text-primary-900 tracking-tight"
                zhClassName="text-primary-600"
              />
              <div className="mt-1 text-sm text-primary-500 font-medium">
                {episode?.title || metadata.title}
              </div>
            </div>
          </div>

          <BilingualText
            i18nKey={show.descKey}
            as="div"
            className="mt-4 text-base text-primary-700 leading-relaxed"
            zhClassName="text-primary-500"
          />

          <div className="mt-6 bg-surface-secondary rounded-2xl p-5 border border-border-light">
            <div className="text-lg font-semibold text-primary-900">
              {metadata.episode} · {metadata.title}
            </div>
            <p className="mt-2 text-sm text-primary-600 leading-relaxed">
              {metadata.description}
            </p>
          </div>

          {/* Rating category buttons */}
          <div className="mt-6 space-y-3">
            {stats.learned > 0 || stats.learning > 0 ? (
              // Show rating buttons when there's data
              <>
                {stats.learned > 0 && (
                  <button
                    onClick={() => onStart(cards.filter((c) => srs[c.id]?.status === 'review' && srs[c.id]?.lastRating === 'easy').map((c) => c.id))}
                    className="w-full text-left bg-accent-50 border border-accent-200 rounded-xl p-4 hover:shadow-subtle transition-all cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-base font-semibold text-accent-800">✅ <Bi i18nKey="session.perfect" /></span>
                      <span className="text-sm text-accent-700">{stats.learned} <Bi i18nKey="home.cards" /></span>
                    </div>
                    <div className="text-xs text-accent-600 mt-1"><Bi i18nKey="home.reviewPerfect" /></div>
                  </button>
                )}
                {stats.learning > 0 && (
                  <button
                    onClick={() => onStart(cards.filter((c) => srs[c.id]?.status === 'learning').map((c) => c.id))}
                    className="w-full text-left bg-amber-50 border border-amber-200 rounded-xl p-4 hover:shadow-subtle transition-all cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-base font-semibold text-amber-800"> <Bi i18nKey="session.bumpy" /></span>
                      <span className="text-sm text-amber-700">{stats.learning} <Bi i18nKey="home.cards" /></span>
                    </div>
                    <div className="text-xs text-amber-600 mt-1"><Bi i18nKey="home.reviewBumpy" /></div>
                  </button>
                )}
              </>
            ) : (
              // Encouragement message when no data
              <div className="bg-accent-50 border border-accent-200 rounded-xl p-5 text-center">
                <div className="text-base font-semibold text-accent-800 mb-1"> <Bi i18nKey="home.startYourJourney" /></div>
                <div className="text-sm text-accent-700"><Bi i18nKey="home.noDataYet" /></div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Filter section */}
      <section className="max-w-4xl mx-auto px-4 -mt-6 sm:px-6">
        <div className="bg-white rounded-2xl shadow-card border border-border-light p-6">
          <div className="text-sm font-semibold text-primary-700 flex items-center gap-2">
            <span className="w-1 h-4 bg-accent-600 rounded-full inline-block" />
            <Bi i18nKey="home.filterTitle" />
          </div>
          <p className="mt-2 mb-4 text-xs text-primary-500">
            <Bi i18nKey="home.filterDesc" />
          </p>

          <div className="flex flex-wrap gap-2">
            {tabItems.map((t2) => (
              <button
                key={t2.key}
                onClick={() => {
                  setSelectedFilter(t2.key)
                  setSelectedValue(null)
                }}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                  selectedFilter === t2.key
                    ? 'bg-primary-900 text-white shadow-subtle'
                    : 'bg-surface-secondary text-primary-700 hover:bg-primary-100 border border-border-light'
                }`}
              >
                <span className="mr-1.5">{t2.icon}</span>
                <Bi i18nKey={t2.i18nKey} />
              </button>
            ))}
          </div>

          {selectedFilter !== 'all' && (
            <div className="mt-4 pt-4 border-t border-border-light">
              <div className="flex flex-wrap gap-2">
                {pickChips().map((chip) => (
                  <button
                    key={chip.value}
                    onClick={() =>
                      setSelectedValue((cur) => (cur === chip.value ? null : chip.value))
                    }
                    className={`px-3 py-1.5 rounded-full text-sm transition-all ${
                      selectedValue === chip.value
                        ? 'bg-accent-600 text-white shadow-subtle'
                        : 'bg-surface-secondary text-primary-700 hover:bg-primary-100 border border-border-light'
                    }`}
                  >
                    {chip.i18nKey ? <Bi i18nKey={chip.i18nKey} /> : chip.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="mt-6 flex items-center justify-between gap-4 flex-wrap">
            <div className="text-sm text-primary-600">
              <div>
                <Bi i18nKey="home.currentFilter" />
                <span className="font-semibold text-primary-900">
                  <Bi i18nKey="home.cardsCount" values={{ count: filteredCards.length }} />
                </span>
                {selectedFilter !== 'all' && selectedValue && (
                  <span className="ml-2 text-accent-600 font-medium">
                    → {tabItems.find((t2) => t2.key === selectedFilter) && <Bi i18nKey={tabItems.find((t2) => t2.key === selectedFilter)!.i18nKey} />}:{' '}
                    {selectedFilter === 'pronunciation'
                      ? PRON_MAIN[selectedValue as PronunciationFocus] || selectedValue
                      : selectedValue}
                  </span>
                )}
              </div>
              <div className="mt-1 text-xs text-primary-500">
                <Bi i18nKey="home.practiceCount" values={{ count: recommendedCards.length }} />
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                disabled={recommendedCards.length === 0}
                onClick={() => startSession(recommendedCards.slice(0, 7))}
                className="px-5 py-2.5 rounded-xl bg-accent-600 text-white font-semibold shadow-subtle hover:shadow-card hover:scale-[1.02] transition-all disabled:opacity-40 disabled:pointer-events-none disabled:hover:scale-100"
              >
                <Bi i18nKey="home.startSession" values={{ count: Math.min(7, recommendedCards.length) }} />
              </button>
              <button
                disabled={filteredCards.length === 0}
                onClick={() => startSession(filteredCards)}
                className="px-4 py-2.5 rounded-xl bg-surface-secondary text-primary-700 font-semibold border border-border-light hover:bg-primary-100 transition-all disabled:opacity-40 disabled:pointer-events-none"
              >
                <Bi i18nKey="home.studyAll" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Preview grid */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-primary-900 flex items-center gap-2">
            <span className="w-1 h-6 bg-accent-600 rounded-full inline-block" />
            <Bi i18nKey="home.previewTitle" />
          </h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {recommendedCards.slice(0, 12).map((c) => (
            <div
              key={c.id}
              className="group bg-white rounded-xl border border-border-light hover:border-accent-300 shadow-subtle hover:shadow-card transition-all p-4 cursor-pointer"
              onClick={() => onStart([c.id, ...filteredCards.filter((x) => x.id !== c.id).map((x) => x.id)])}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="text-xl font-semibold text-primary-900 group-hover:text-accent-600 transition">
                  {c.target_word}
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                  c.level === 'A1' ? 'bg-accent-50 text-accent-700' :
                  c.level === 'A2' ? 'bg-accent-100 text-accent-800' :
                  c.level === 'B1' ? 'bg-yellow-50 text-yellow-700' :
                  c.level === 'B2' ? 'bg-orange-50 text-orange-700' :
                  c.level === 'C1' ? 'bg-red-50 text-red-700' : 'bg-rose-50 text-rose-700'
                }`}>
                  {c.level}
                </span>
              </div>
              <div className="text-xs text-primary-500 mb-1">GenAm {c.ipa} · {c.pos}</div>
              {c.translation && (
                <div className="text-xs text-accent-600 font-medium mb-2">{c.translation}</div>
              )}
              <div className="mb-2 inline-flex w-fit rounded-full border border-accent-200 bg-accent-50 px-2 py-0.5 text-xs font-medium text-accent-700">
                ️ {PRON_MAIN[c.pronunciation_focus] || c.pronunciation_focus}
              </div>
              <div className="text-sm text-primary-700 line-clamp-2 leading-relaxed">
                {c.sentence_full}
              </div>
              <div className="mt-3 pt-3 border-t border-border-light flex items-center justify-between text-xs text-primary-500">
                <span>🎭 {c.character}</span>
                <span> {c.scene_id.replace(/scene_\d+_/, '').slice(0, 12)}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <footer className="py-8 text-center text-xs text-primary-400">
        <Bi i18nKey="app.footer" values={{ year: new Date().getFullYear() }} />
      </footer>
    </div>
  )
}

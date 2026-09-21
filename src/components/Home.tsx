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
  onChangeShow: () => void
  onStart: (queueIds: string[]) => void
}

/** Helper: get the main (target language) text from a bilingual key */
function useBi(i18nKey: string, values?: Record<string, string | number>): string {
  const { t } = useTranslation()
  const raw = t(i18nKey, { ...values, returnObjects: true }) as { main?: string } | string
  return typeof raw === 'string' ? raw : (raw.main ?? i18nKey)
}

export default function Home({ cards, metadata, show, episode, onChangeShow, onStart }: Props) {
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
    return filteredCards
      .filter((card) => !srs[card.id] || srs[card.id].dueAt <= now)
      .sort((a, b) => {
        const aState = srs[a.id]
        const bState = srs[b.id]
        if (Boolean(aState) !== Boolean(bState)) return aState ? -1 : 1
        return (aState?.dueAt ?? 0) - (bState?.dueAt ?? 0)
      })
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
    { key: 'character', i18nKey: 'home.filterCharacter', icon: '🎭' },
    { key: 'scene', i18nKey: 'home.filterScene', icon: '🎬' },
    { key: 'level', i18nKey: 'home.filterLevel', icon: '📶' },
    { key: 'tags', i18nKey: 'home.filterTags', icon: '️' },
  ]

  return (
    <div className="min-h-full">
      {/* Header */}
      <header className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-friends-sofa via-friends-coffee to-friends-sofa opacity-90" />
        <div className="absolute inset-0 opacity-20" style={{
          backgroundImage:
            "radial-gradient(circle at 20% 20%, #FFB74D 0, transparent 40%), radial-gradient(circle at 80% 60%, #FFF8E1 0, transparent 35%)",
        }} />
        <div className="relative px-6 pt-10 pb-14 text-white max-w-4xl mx-auto">
          {/* Top bar: language + change show */}
          <div className="absolute top-4 right-4 flex items-center gap-2">
            <LanguageSwitcher />
            <button
              onClick={onChangeShow}
              className="px-3 py-1.5 rounded-full bg-white/20 backdrop-blur border border-white/30 text-white text-sm font-medium hover:bg-white/30 transition-all"
            >
              <Bi i18nKey="nav.changeShow" />
            </button>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-4xl">{show.coverEmoji}</span>
            <div>
              <BilingualText
                i18nKey={show.titleKey}
                as="div"
                className="font-hand text-4xl sm:text-5xl text-friends-cream drop-shadow-md"
                zhClassName="text-friends-cream/80"
              />
              <div className="mt-1 text-sm text-friends-cream/80">
                {episode?.title || metadata.title}
              </div>
            </div>
          </div>

          <BilingualText
            i18nKey={show.descKey}
            as="div"
            className="mt-3 text-sm text-friends-accent/90 font-medium tracking-wide"
            zhClassName="text-friends-accent/70"
          />

          <div className="mt-4 bg-white/10 backdrop-blur rounded-2xl p-4 border border-white/20">
            <div className="text-xl font-semibold">
              {metadata.episode} · {metadata.title}
            </div>
            <p className="mt-2 text-sm text-friends-cream/80 max-w-2xl leading-relaxed">
              {metadata.description}
            </p>
          </div>

          {/* stats */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mt-5">
            {[
              { i18nKey: 'home.totalCards', num: cards.length, color: 'from-amber-400/80 to-orange-400/80' },
              { i18nKey: 'home.toLearn', num: stats.new, color: 'from-sky-400/80 to-indigo-400/80' },
              { i18nKey: 'home.learning', num: stats.learning, color: 'from-yellow-400/80 to-amber-400/80' },
              { i18nKey: 'home.mastered', num: stats.learned, color: 'from-green-400/80 to-emerald-400/80' },
              { i18nKey: 'home.favorites', num: stats.favCount, color: 'from-rose-400/80 to-pink-400/80' },
            ].map((s) => (
              <div
                key={s.i18nKey}
                className={`rounded-xl p-3 bg-gradient-to-br ${s.color} backdrop-blur border border-white/20`}
              >
                <div className="text-xs opacity-90"><Bi i18nKey={s.i18nKey} /></div>
                <div className="text-2xl font-bold mt-0.5">{s.num}</div>
              </div>
            ))}
          </div>
        </div>
      </header>

      {/* Filter section */}
      <section className="max-w-4xl mx-auto px-4 -mt-6 sm:px-6">
        <div className="bg-white rounded-2xl shadow-card border border-friends-coffee/10 p-5">
          <div className="text-sm font-semibold text-friends-sofa/80 flex items-center gap-2">
            <span className="w-1 h-4 bg-friends-perk rounded-full inline-block" />
            <Bi i18nKey="home.filterTitle" />
          </div>
          <p className="mt-1 mb-3 text-xs text-friends-coffee/70">
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
                    ? 'bg-friends-sofa text-white shadow-md'
                    : 'bg-friends-cream text-friends-sofa hover:bg-friends-coffee/15 border border-friends-coffee/20'
                }`}
              >
                <span className="mr-1.5">{t2.icon}</span>
                <Bi i18nKey={t2.i18nKey} />
              </button>
            ))}
          </div>

          {selectedFilter !== 'all' && (
            <div className="mt-4 pt-4 border-t border-friends-coffee/10">
              <div className="flex flex-wrap gap-2">
                {pickChips().map((chip) => (
                  <button
                    key={chip.value}
                    onClick={() =>
                      setSelectedValue((cur) => (cur === chip.value ? null : chip.value))
                    }
                    className={`px-3 py-1.5 rounded-full text-sm transition-all ${
                      selectedValue === chip.value
                        ? 'bg-friends-perk text-white shadow'
                        : 'bg-friends-paper text-friends-sofa hover:bg-friends-accent/30 border border-friends-coffee/20'
                    }`}
                  >
                    {chip.i18nKey ? <Bi i18nKey={chip.i18nKey} /> : chip.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="mt-5 flex items-center justify-between gap-4 flex-wrap">
            <div className="text-sm text-friends-coffee/90">
              <div>
                <Bi i18nKey="home.currentFilter" />
                <span className="font-semibold text-friends-sofa">
                  <Bi i18nKey="home.cardsCount" values={{ count: filteredCards.length }} />
                </span>
                {selectedFilter !== 'all' && selectedValue && (
                  <span className="ml-2 text-friends-perk font-medium">
                    → {tabItems.find((t2) => t2.key === selectedFilter) && <Bi i18nKey={tabItems.find((t2) => t2.key === selectedFilter)!.i18nKey} />}:{' '}
                    {selectedFilter === 'pronunciation'
                      ? PRON_MAIN[selectedValue as PronunciationFocus] || selectedValue
                      : selectedValue}
                  </span>
                )}
              </div>
              <div className="mt-1 text-xs text-friends-coffee/70">
                <Bi i18nKey="home.practiceCount" values={{ count: recommendedCards.length }} />
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                disabled={recommendedCards.length === 0}
                onClick={() => startSession(recommendedCards.slice(0, 10))}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-friends-perk to-emerald-500 text-white font-semibold shadow-lg hover:shadow-xl hover:scale-[1.02] transition-all disabled:opacity-40 disabled:pointer-events-none disabled:hover:scale-100"
              >
                <Bi i18nKey="home.startSession" values={{ count: Math.min(10, recommendedCards.length) }} />
              </button>
              <button
                disabled={filteredCards.length === 0}
                onClick={() => startSession(filteredCards)}
                className="px-4 py-2.5 rounded-xl bg-friends-paper text-friends-sofa font-semibold border border-friends-coffee/25 hover:bg-friends-accent/30 transition-all disabled:opacity-40 disabled:pointer-events-none"
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
          <h2 className="text-xl font-semibold text-friends-sofa flex items-center gap-2">
            <span className="w-1 h-6 bg-friends-accent rounded-full inline-block" />
            <Bi i18nKey="home.previewTitle" />
          </h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredCards.slice(0, 12).map((c) => (
            <div
              key={c.id}
              className="group bg-white rounded-xl border border-friends-coffee/10 hover:border-friends-perk/40 shadow-sm hover:shadow-card transition-all p-4 cursor-pointer"
              onClick={() => onStart([c.id, ...filteredCards.filter((x) => x.id !== c.id).map((x) => x.id)])}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="font-hand text-2xl text-friends-sofa group-hover:text-friends-perk transition">
                  {c.target_word}
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                  c.level === 'A1' ? 'bg-green-100 text-green-800' :
                  c.level === 'A2' ? 'bg-emerald-100 text-emerald-800' :
                  c.level === 'B1' ? 'bg-yellow-100 text-yellow-800' :
                  c.level === 'B2' ? 'bg-orange-100 text-orange-800' :
                  c.level === 'C1' ? 'bg-red-100 text-red-800' : 'bg-rose-100 text-rose-800'
                }`}>
                  {c.level}
                </span>
              </div>
              <div className="text-xs text-friends-coffee mb-1">GenAm {c.ipa} · {c.pos}</div>
              {c.translation && (
                <div className="text-xs text-friends-perk font-medium mb-2">{c.translation}</div>
              )}
              <div className="mb-2 inline-flex w-fit rounded-full border border-friends-perk/25 bg-friends-perk/10 px-2 py-0.5 text-xs font-medium text-friends-perk">
                🗣️ {PRON_MAIN[c.pronunciation_focus] || c.pronunciation_focus}
              </div>
              <div className="text-sm text-friends-sofa/80 line-clamp-2 leading-relaxed">
                {c.sentence_full}
              </div>
              <div className="mt-3 pt-3 border-t border-friends-coffee/10 flex items-center justify-between text-xs text-friends-coffee/80">
                <span>🎭 {c.character}</span>
                <span> {c.scene_id.replace(/scene_\d+_/, '').slice(0, 12)}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <footer className="py-8 text-center text-xs text-friends-coffee/60">
        <Bi i18nKey="app.footer" values={{ year: new Date().getFullYear() }} />
      </footer>
    </div>
  )
}

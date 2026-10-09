import { useMemo, useState, useEffect, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import LanguageSwitcher from './LanguageSwitcher'
import BilingualText, { Bi } from './BilingualText'
import type { EpisodeMetadata, Flashcard, PronunciationFocus } from '../data/types'
import type { ShowDefinition, ShowEpisode } from '../data/showTypes'
import { useStore } from '../utils/store'
import { playTTS as playTTSUtil, stopTTS } from '../utils/tts'

type FilterKey = 'all' | 'pos' | 'pronunciation' | 'character' | 'scene' | 'level' | 'tags'

interface Props {
  cards: Flashcard[]
  metadata: EpisodeMetadata
  show: ShowDefinition
  episode?: ShowEpisode
  showEpisodes: ShowEpisode[]
  onStart: (queueIds: string[]) => void
  selectedFilter: string
  setSelectedFilter: (filter: string) => void
  selectedValue: string | null
  setSelectedValue: (value: string | null) => void
  selectedEpisode: string | null
  setSelectedEpisode: (episode: string | null) => void
  grammarCards: Flashcard[]
  grammarMode: boolean
  setGrammarMode: (mode: boolean) => void
}

/** Helper: get the main (target language) text from a bilingual key */
function useBi(i18nKey: string, values?: Record<string, string | number>): string {
  const { t } = useTranslation()
  const raw = t(i18nKey, { ...values, returnObjects: true }) as { main?: string } | string
  return typeof raw === 'string' ? raw : (raw.main ?? i18nKey)
}

export default function Home({ cards, metadata, show, episode, showEpisodes, onStart, selectedFilter, setSelectedFilter, selectedValue, setSelectedValue, selectedEpisode, setSelectedEpisode, grammarCards, grammarMode, setGrammarMode }: Props) {
  const { t } = useTranslation()
  const srs = useStore((s) => s.srs)
  const favorites = useStore((s) => s.favorites)
  const disliked = useStore((s) => s.disliked)
  const mastered = useStore((s) => s.mastered)
  const seen = useStore((s) => s.seen)
  const toggleMastered = useStore((s) => s.toggleMastered)
  const previewPage = useStore((s) => s.previewPage)
  const setPreviewPage = useStore((s) => s.setPreviewPage)
  const sessionBatch = useStore((s) => s.sessionBatch)
  const setSessionBatch = useStore((s) => s.setSessionBatch)
  const previewMode = useStore((s) => s.previewMode)
  const setPreviewMode = useStore((s) => s.setPreviewMode)
  const [playingId, setPlayingId] = useState<string | null>(null)
  const [ttsError, setTtsError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchOpen, setSearchOpen] = useState(false)
  const PREVIEW_PER_PAGE = 8
  const BLIND_SPOT_PER_PAGE = 16

  // Search: substring match with relevance scoring
  const searchResults = useMemo(() => {
    const q = searchQuery.trim().toLowerCase()
    if (!q) return []

    type ScoredCard = { card: Flashcard; score: number }
    const results: ScoredCard[] = []

    for (const c of cards) {
      const word = c.target_word.toLowerCase()
      const trans = (c.translation || '').toLowerCase()
      const sentence = (c.sentence_full || '').toLowerCase()
      const sentTrans = (c.sentence_translation || '').toLowerCase()

      let score = 0

      // 1. Exact match on target_word (highest priority)
      if (word === q) { score = 1000 }
      // 2. Target word starts with query
      else if (word.startsWith(q)) { score = 800 }
      // 3. Target word contains query
      else if (word.includes(q)) { score = 600 }
      // 4. Translation contains query
      else if (trans.includes(q)) { score = 400 }
      // 5. Sentence contains query as whole word
      else if (sentence.includes(q)) { score = 200 }
      // 6. Sentence translation contains query
      else if (sentTrans.includes(q)) { score = 100 }
      // 7. Fuzzy: query chars appear in order in target_word, with >= 60% density
      else {
        let qi = 0
        for (let i = 0; i < word.length && qi < q.length; i++) {
          if (word[i] === q[qi]) qi++
        }
        if (qi === q.length && q.length >= 3 && qi / word.length >= 0.6) {
          score = 50 + Math.round((qi / word.length) * 50)
        }
      }

      if (score > 0) results.push({ card: c, score })
    }

    results.sort((a, b) => b.score - a.score)
    return results.slice(0, 30).map((r) => r.card)
  }, [searchQuery, cards])

  // TTS play function
  function handlePlay(text: string, playKey: string) {
    if (playingId === playKey) {
      stopTTS()
      setPlayingId(null)
      return
    }
    // Detect language from card ID: LCDP_/GRAMMAR_ = Spanish, others = English (GenAm)
    const cardId = playKey.startsWith('sent-') ? playKey.slice(5) : playKey
    const lang = cardId.startsWith('LCDP_') || cardId.startsWith('GRAMMAR_') ? 'es' : 'en'
    playTTSUtil(text, lang, () => setPlayingId(playKey), () => setPlayingId(null), (msg) => {
      setTtsError(msg)
      setTimeout(() => setTtsError(null), 5000)
    })
  }

  // Reset preview page ONLY when filter/mode actually changes (not on remount)
  const prevFilterRef = useRef({ selectedFilter, selectedValue, selectedEpisode, previewMode })
  useEffect(() => {
    const prev = prevFilterRef.current
    const curr = { selectedFilter, selectedValue, selectedEpisode, previewMode }
    if (
      prev.selectedFilter !== curr.selectedFilter ||
      prev.selectedValue !== curr.selectedValue ||
      prev.selectedEpisode !== curr.selectedEpisode ||
      prev.previewMode !== curr.previewMode
    ) {
      setPreviewPage(0)
      setSessionBatch(0)
    }
    prevFilterRef.current = curr
  }, [selectedFilter, selectedValue, selectedEpisode, previewMode])

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
    const episodes = uniq(cards.map((c) => c.episode))
    const chars = uniq(cards.map((c) => c.character))
    const scenes = metadata.scenes_summary.map((s) => s.scene_id)
    const levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'] as const
    const tags = uniq(cards.flatMap((c) => c.tags))
    return { pos, pronunciation, episodes, chars, scenes, levels, tags }
  }, [cards, metadata])

  // Count cards per episode (for showing "how far the road is")
  const episodeCounts = useMemo(() => {
    const counts: Record<string, number> = {}
    for (const c of cards) {
      counts[c.episode] = (counts[c.episode] || 0) + 1
    }
    return counts
  }, [cards])

  // Count cards per POS category, scoped to selected episode (for showing task size)
  const scopedCards = useMemo(() => {
    if (selectedEpisode) return cards.filter((c) => c.episode === selectedEpisode)
    return cards
  }, [cards, selectedEpisode])

  const posCounts = useMemo(() => {
    const counts: Record<string, number> = {}
    for (const c of scopedCards) {
      const raw = c.pos.toLowerCase()
      const key =
        raw.startsWith('n.') ? 'n' :
        raw.startsWith('v.') ? 'v' :
        raw.startsWith('adj') ? 'adj' :
        raw.startsWith('adv') ? 'adv' :
        raw.includes('phrasal') ? 'phrasal' :
        raw.includes('contraction') ? 'contraction' :
        raw.includes('phrase') ? 'phrase' : 'other'
      counts[key] = (counts[key] || 0) + 1
    }
    return counts
  }, [scopedCards])

  const filteredCards = useMemo(() => {
    // Grammar mode: show grammar cards
    if (grammarMode) {
      return grammarCards.filter((c) => !disliked.has(c.id) && !mastered.has(c.id))
    }

    // Filter out disliked and mastered cards
    let availableCards = cards.filter((c) => !disliked.has(c.id) && !mastered.has(c.id))

    // Level 1: Episode scope
    if (selectedEpisode) {
      availableCards = availableCards.filter((c) => c.episode === selectedEpisode)
    }

    // Level 2: Secondary filter
    if (selectedFilter === 'all' || !selectedValue) return availableCards
    const result = availableCards.filter((c) => {
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

    // Sort by dialogue order (line_index from Excel row number)
    return result.sort((a, b) => (a.line_index ?? 0) - (b.line_index ?? 0))
  }, [cards, grammarCards, grammarMode, selectedFilter, selectedValue, selectedEpisode, disliked, mastered])

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
      const newCards = filteredCards.filter((card) => !srs[card.id])
      // If no new cards either, return all filtered cards (for review mode)
      return newCards.length > 0 ? newCards : filteredCards
    }
    return dueCards
  }, [filteredCards, srs])

  const stats = useMemo(() => {
    const due = filteredCards.filter((c) => !srs[c.id] || srs[c.id].dueAt <= Date.now()).length
    const learned = filteredCards.filter((c) => srs[c.id]?.status === 'review').length
    const learning = filteredCards.filter((c) => srs[c.id]?.status === 'learning').length
    const newCount = filteredCards.filter((c) => !srs[c.id]).length
    // Cards needing consolidation: 5+ cumulative errors AND still in learning status
    const needsWork = filteredCards.filter((c) => (srs[c.id]?.totalErrors ?? 0) >= 5 && srs[c.id]?.status !== 'review').length
    // Blind spots: cards never seen in any session (based on current filter)
    // A card is considered "seen" if it's in the seen set OR has an SRS entry (learned before this feature existed)
    const blindSpots = filteredCards.filter((c) => !seen.has(c.id) && !srs[c.id]).length
    return { due, learned, learning, new: newCount, needsWork, favCount: favorites.size, dislikedCount: disliked.size, masteredCount: mastered.size, blindSpots }
  }, [filteredCards, srs, favorites, disliked, mastered, seen])

  // Card lists for each category
  const perfectCards = useMemo(() => {
    return filteredCards.filter((c) => srs[c.id]?.status === 'review' && srs[c.id]?.lastRating === 'easy')
  }, [filteredCards, srs])

  const bumpyCards = useMemo(() => {
    return filteredCards.filter((c) => srs[c.id]?.status === 'learning')
  }, [filteredCards, srs])

  const needsWorkCards = useMemo(() => {
    return filteredCards.filter((c) => (srs[c.id]?.totalErrors ?? 0) >= 5 && srs[c.id]?.status !== 'review')
  }, [filteredCards, srs])

  // Blind spot cards: never seen, not disliked, not mastered
  const blindSpotCards = useMemo(() => {
    return filteredCards.filter((c) => !seen.has(c.id) && !srs[c.id])
  }, [filteredCards, seen, srs])

  // Favorited cards within current filter
  const favCards = useMemo(() => {
    return filteredCards.filter((c) => favorites.has(c.id))
  }, [filteredCards, favorites])

  // Mastered cards (Ya lo sé) - from original cards since they're filtered out
  const masteredCards = useMemo(() => {
    return cards.filter((c) => mastered.has(c.id))
  }, [cards, mastered])

  // Preview cards based on mode
  const previewCards = useMemo(() => {
    if (previewMode === 'session') {
      // Pull from blind spots first, then fill with remaining filtered cards
      const blindSpots = blindSpotCards
      const remaining = filteredCards.filter((c) => !blindSpots.some((b) => b.id === c.id))
      const ordered = [...blindSpots, ...remaining]
      const start = sessionBatch * 7
      return ordered.slice(start, start + 7)
    }
    if (previewMode === 'blindSpots') {
      return blindSpotCards
    }
    return filteredCards
  }, [previewMode, filteredCards, blindSpotCards, sessionBatch])

  // Dynamic page size based on mode
  const currentPageSize = previewMode === 'blindSpots' ? BLIND_SPOT_PER_PAGE : PREVIEW_PER_PAGE

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
    { key: 'pos', i18nKey: 'home.filterPos', icon: '' },
    { key: 'pronunciation', i18nKey: 'home.filterPronunciation', icon: '️' },
  ]

  return (
    <div className="min-h-full">
      {/* Header */}
      <header className="relative overflow-hidden">
        <div className="relative px-6 pt-10 pb-14 max-w-4xl mx-auto">
          {/* Top bar: search + language */}
          <div className="absolute top-4 right-4 flex items-center gap-2">
            {/* Search */}
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => { setSearchQuery(e.target.value); setSearchOpen(true) }}
                onFocus={() => setSearchOpen(true)}
                onBlur={() => setTimeout(() => setSearchOpen(false), 200)}
                placeholder="🔍 查词..."
                className="w-40 px-3 py-1.5 text-sm rounded-lg border border-primary-200 bg-white/90 backdrop-blur text-primary-900 placeholder-primary-400 focus:outline-none focus:ring-2 focus:ring-accent-400 focus:border-transparent transition-all"
              />
              {searchOpen && searchResults.length > 0 && (
                <div className="absolute right-0 top-full mt-1 w-72 max-h-80 overflow-y-auto bg-white rounded-xl shadow-xl border border-border-light z-50">
                  {searchResults.map((c) => (
                    <div
                      key={c.id}
                      className="px-3 py-2 hover:bg-accent-50 cursor-pointer border-b border-border-light last:border-0"
                      onMouseDown={(e) => {
                        e.preventDefault()
                        onStart([c.id])
                        setSearchOpen(false)
                        setSearchQuery('')
                      }}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-primary-900 text-sm">{c.target_word}</span>
                        <span className="text-xs text-primary-400">{c.pos}</span>
                      </div>
                      {c.translation && <div className="text-xs text-accent-600 mt-0.5">{c.translation}</div>}
                      {c.sentence_full && <div className="text-xs text-primary-500 mt-0.5 line-clamp-1">{c.sentence_full}</div>}
                    </div>
                  ))}
                </div>
              )}
              {searchOpen && searchQuery && searchResults.length === 0 && (
                <div className="absolute right-0 top-full mt-1 w-72 bg-white rounded-xl shadow-xl border border-border-light z-50 px-3 py-4 text-center text-sm text-primary-400">
                  没有找到匹配的词 / Sin resultados
                </div>
              )}
            </div>
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

          {/* Filter section */}
          <section className="mt-6">
            <div className="bg-white rounded-2xl shadow-card border border-border-light p-6">
              <div className="text-sm font-semibold text-primary-700 flex items-center gap-2">
                <span className="w-1 h-4 bg-accent-600 rounded-full inline-block" />
                <Bi i18nKey="home.filterTitle" />
              </div>
              <p className="mt-2 mb-4 text-xs text-primary-500">
                <Bi i18nKey="home.filterDesc" />
              </p>

              {/* Episode buttons row */}
              <div className="flex flex-wrap gap-2 mb-4">
                  {/* Grammar button */}
                  <button
                    onClick={() => {
                      setGrammarMode(!grammarMode)
                      if (grammarMode) {
                        setSelectedEpisode(null)
                      } else {
                        setSelectedFilter('pos')
                        setSelectedValue(null)
                      }
                    }}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                      grammarMode
                        ? 'bg-accent-600 text-white shadow-subtle'
                        : 'bg-surface-secondary text-primary-700 hover:bg-primary-100 border border-border-light'
                    }`}
                  >
                    📚 语法
                    <span className="ml-1.5 text-xs opacity-75">{grammarCards.length}</span>
                  </button>
                  {filters.episodes.map((epId) => {
                    const count = episodeCounts[epId] || 0
                    return (
                      <button
                        key={epId}
                        onClick={() => {
                          setGrammarMode(false)
                          setSelectedEpisode(selectedEpisode === epId ? null : epId)
                        }}
                        className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                          selectedEpisode === epId && !grammarMode
                            ? 'bg-primary-900 text-white shadow-subtle'
                            : 'bg-surface-secondary text-primary-700 hover:bg-primary-100 border border-border-light'
                        }`}
                      >
                        {epId}
                        <span className="ml-1.5 text-xs opacity-75">{count}</span>
                      </button>
                    )
                  })}
                </div>

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
                    {pickChips().filter((chip) => {
                      const cnt = selectedFilter === 'pos' ? (posCounts[chip.value] || 0) : 1
                      return cnt > 0
                    }).map((chip) => {
                      // Get count for this chip
                      const chipCount = selectedFilter === 'pos' 
                        ? (posCounts[chip.value] || 0)
                        : filteredCards.filter((c) => {
                            if (selectedFilter === 'pronunciation') return c.pronunciation_focus === chip.value
                            if (selectedFilter === 'character') return c.character === chip.value
                            if (selectedFilter === 'scene') return c.scene_id === chip.value
                            if (selectedFilter === 'level') return c.level === chip.value
                            if (selectedFilter === 'tags') return c.tags.includes(chip.value)
                            return false
                          }).length
                      
                      return (
                        <button
                          key={chip.value}
                          onClick={() =>
                            setSelectedValue(selectedValue === chip.value ? null : chip.value)
                          }
                          className={`px-3 py-1.5 rounded-full text-sm transition-all ${
                            selectedValue === chip.value
                              ? 'bg-accent-600 text-white shadow-subtle'
                              : 'bg-surface-secondary text-primary-700 hover:bg-primary-100 border border-border-light'
                          }`}
                        >
                          {chip.i18nKey ? <Bi i18nKey={chip.i18nKey} /> : chip.label}
                          <span className="ml-1.5 text-xs opacity-75">{chipCount}</span>
                        </button>
                      )
                    })}
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
                  {stats.blindSpots > 0 && (
                    <div className="mt-1 text-xs font-medium text-amber-600">
                       <Bi i18nKey="home.blindSpots" values={{ count: stats.blindSpots }} />
                    </div>
                  )}
                </div>
                <div className="flex flex-wrap gap-2">
                  {favCards.length > 0 && (
                    <button
                      onClick={() => {
                        setPreviewMode('session')
                        startSession(favCards)
                      }}
                      className="px-4 py-2.5 rounded-xl bg-green-500 text-white font-semibold shadow-subtle hover:shadow-card hover:scale-[1.02] transition-all"
                    >
                      <Bi i18nKey="home.studyFavorites" values={{ count: favCards.length }} />
                    </button>
                  )}
                  <button
                    disabled={filteredCards.length === 0}
                    onClick={() => {
                      setPreviewMode('all')
                      startSession(filteredCards)
                    }}
                    className="px-4 py-2.5 rounded-xl bg-surface-secondary text-primary-700 font-semibold border border-border-light hover:bg-primary-100 transition-all disabled:opacity-40 disabled:pointer-events-none"
                  >
                    <Bi i18nKey="home.studyAll" />
                  </button>
                </div>
              </div>
            </div>
          </section>

          {/* Rating category bar chart */}
          {(stats.learned > 0 || stats.learning > 0 || stats.needsWork > 0 || blindSpotCards.length > 0 || favCards.length > 0 || masteredCards.length > 0) && (
            <section className="mt-6">
              <div className="bg-white rounded-2xl shadow-card border border-border-light p-5">
                <div className="text-sm font-semibold text-primary-700 flex items-center gap-2 mb-4">
                  <span className="w-1 h-4 bg-accent-600 rounded-full inline-block" />
                  Distribución de tarjetas / 卡片分布
                </div>

                {(() => {
                  const bars = [
                    { label: '¡Perfecto! 一把过', count: stats.learned, color: 'bg-green-500', textColor: 'text-green-700', onClick: () => onStart(perfectCards.map((c) => c.id)) },
                    { label: 'Casi lo tienes 小磕绊', count: stats.learning, color: 'bg-amber-500', textColor: 'text-amber-700', onClick: () => onStart(bumpyCards.map((c) => c.id)) },
                    { label: 'Necesita consolidación 需巩固', count: stats.needsWork, color: 'bg-rose-500', textColor: 'text-rose-700', onClick: () => onStart(needsWorkCards.map((c) => c.id)) },
                    { label: 'Zona ciega 盲区词', count: blindSpotCards.length, color: 'bg-orange-500', textColor: 'text-orange-700', onClick: () => { setPreviewMode('blindSpots'); setPreviewPage(0); } },
                    { label: 'Favoritas 收藏', count: favCards.length, color: 'bg-emerald-500', textColor: 'text-emerald-700', onClick: () => onStart(favCards.map((c) => c.id)) },
                    { label: 'Ya lo sé 已掌握', count: masteredCards.length, color: 'bg-teal-500', textColor: 'text-teal-700', onClick: () => onStart(masteredCards.map((c) => c.id)) },
                  ].filter((b) => b.count > 0)

                  const maxCount = Math.max(...bars.map((b) => b.count), 1)
                  const total = bars.reduce((s, b) => s + b.count, 0)

                  return (
                    <>
                      {/* Stacked progress bar */}
                      <div className="flex h-4 rounded-full overflow-hidden mb-3 bg-gray-100">
                        {bars.map((bar, i) => (
                          <div
                            key={i}
                            className={`${bar.color} transition-all duration-500 cursor-pointer hover:opacity-80`}
                            style={{ width: `${(bar.count / total) * 100}%` }}
                            onClick={bar.onClick}
                            title={`${bar.label}: ${bar.count}`}
                          />
                        ))}
                      </div>

                      {/* Individual bars */}
                      <div className="space-y-2.5">
                        {bars.map((bar, i) => (
                          <button
                            key={i}
                            onClick={bar.onClick}
                            className="w-full text-left group"
                          >
                            <div className="flex items-center justify-between mb-1">
                              <span className={`text-xs font-medium ${bar.textColor}`}>
                                {bar.label}
                              </span>
                              <span className={`text-xs font-bold ${bar.textColor}`}>
                                {bar.count} <span className="font-normal opacity-70">tarjetas</span>
                              </span>
                            </div>
                            <div className="w-full h-2.5 bg-gray-100 rounded-full overflow-hidden">
                              <div
                                className={`${bar.color} h-full rounded-full transition-all duration-500 group-hover:opacity-80`}
                                style={{ width: `${(bar.count / maxCount) * 100}%` }}
                              />
                            </div>
                          </button>
                        ))}
                      </div>

                      {/* Total */}
                      <div className="mt-3 pt-3 border-t border-border-light text-center text-xs text-primary-500">
                        Total: <span className="font-bold text-primary-700">{total}</span> tarjetas
                      </div>
                    </>
                  )
                })()}
              </div>
            </section>
          )}

          {/* Rating category buttons */}
          <div className="mt-6 space-y-3">
            {stats.learned > 0 || stats.learning > 0 || stats.needsWork > 0 ? (
              // Show rating buttons when there's data
              <>
                {stats.needsWork > 0 && (
                  <button
                    onClick={() => onStart(needsWorkCards.map((c) => c.id))}
                    className="w-full text-left bg-rose-50 border border-rose-200 rounded-xl p-4 hover:shadow-subtle transition-all cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-base font-semibold text-rose-800">🔥 <Bi i18nKey="home.needsWork" /></span>
                      <span className="text-sm text-rose-700">{stats.needsWork} <Bi i18nKey="home.cards" /></span>
                    </div>
                    <div className="text-xs text-rose-600 mt-1"><Bi i18nKey="home.needsWorkDesc" /></div>
                  </button>
                )}
                {stats.learned > 0 && (
                  <button
                    onClick={() => onStart(perfectCards.map((c) => c.id))}
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
                    onClick={() => onStart(bumpyCards.map((c) => c.id))}
                    className="w-full text-left bg-amber-50 border border-amber-200 rounded-xl p-4 hover:shadow-subtle transition-all cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-base font-semibold text-amber-800"> <Bi i18nKey="session.bumpy" /></span>
                      <span className="text-sm text-amber-700">{stats.learning} <Bi i18nKey="home.cards" /></span>
                    </div>
                    <div className="text-xs text-amber-600 mt-1"><Bi i18nKey="home.reviewBumpy" /></div>
                  </button>
                )}
                {favCards.length > 0 && (
                  <button
                    onClick={() => onStart(favCards.map((c) => c.id))}
                    className="w-full text-left bg-green-50 border border-green-200 rounded-xl p-4 hover:shadow-subtle transition-all cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-base font-semibold text-green-800">❤️ <Bi i18nKey="home.favoritesPreview" /></span>
                      <span className="text-sm text-green-700">{favCards.length} <Bi i18nKey="home.cards" /></span>
                    </div>
                    <div className="text-xs text-green-600 mt-1"><Bi i18nKey="home.favoritesPreviewDesc" /></div>
                  </button>
                )}
                {masteredCards.length > 0 && (
                  <button
                    onClick={() => onStart(masteredCards.map((c) => c.id))}
                    className="w-full text-left bg-emerald-50 border border-emerald-200 rounded-xl p-4 hover:shadow-subtle transition-all cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-base font-semibold text-emerald-800">✅ <Bi i18nKey="home.masteredPreview" /></span>
                      <span className="text-sm text-emerald-700">{masteredCards.length} <Bi i18nKey="home.cards" /></span>
                    </div>
                    <div className="text-xs text-emerald-600 mt-1"><Bi i18nKey="home.masteredPreviewDesc" /></div>
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

      {/* Preview grid */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-primary-900 flex items-center gap-2">
            <span className="w-1 h-6 bg-accent-600 rounded-full inline-block" />
            <Bi i18nKey="home.previewTitle" />
            <span className="text-sm font-normal text-primary-500 ml-2">
              ({previewCards.length} <Bi i18nKey="home.cards" />)
            </span>
          </h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {previewCards.slice(previewPage * currentPageSize, (previewPage + 1) * currentPageSize).map((c) => {
            // Grammar card: show compact preview
            if (c.grammar_topic) {
              return (
                <div
                  key={c.id}
                  className="group bg-white rounded-xl border border-border-light hover:border-accent-300 shadow-subtle hover:shadow-card transition-all p-3 cursor-pointer"
                  onClick={() => onStart([c.id, ...previewCards.filter((x) => x.id !== c.id).map((x) => x.id)])}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className="text-base font-semibold text-primary-900 group-hover:text-accent-600 transition">
                        {c.target_word}
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handlePlay(c.target_word, c.id)
                        }}
                        className={`p-0.5 rounded-full transition-all ${
                          playingId === c.id
                            ? 'bg-accent-100 text-accent-600'
                            : 'text-primary-400 hover:text-accent-600 hover:bg-accent-50'
                        }`}
                        title="Pronunciar palabra / 朗读单词"
                      >
                        🔊
                      </button>
                      {c.ipa && (
                        <span className="text-[10px] text-primary-400 font-mono">{c.ipa}</span>
                      )}
                    </div>
                    <span className="text-[10px] px-1.5 py-0.5 rounded-full font-semibold bg-accent-50 text-accent-700">
                      {c.pos ? c.pos.split(' ')[0] : c.level}
                    </span>
                  </div>
                  <div className="text-[11px] text-accent-600 font-medium mb-2 line-clamp-2">{c.translation}</div>
                  {c.grammar_content && (
                    <div
                      className="grammar-preview text-xs text-primary-600 leading-relaxed"
                      dangerouslySetInnerHTML={{ __html: c.grammar_content }}
                    />
                  )}
                  <div className="mt-2 pt-2 border-t border-border-light flex items-center justify-between text-[10px] text-primary-500">
                    <span>📚 语法卡片</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleMastered(c.id)
                      }}
                      className="px-2 py-0.5 rounded-lg bg-accent-50 border border-accent-200 text-accent-700 hover:bg-accent-100 transition-all text-[10px] font-medium"
                      title="Marcar como dominada / 标记为已掌握"
                    >
                      {mastered.has(c.id) ? '️ Deshacer' : '✅ Ya lo sé'}
                    </button>
                  </div>
                </div>
              )
            }

            // Regular card
            return (
            <div
              key={c.id}
              className="group bg-white rounded-xl border border-border-light hover:border-accent-300 shadow-subtle hover:shadow-card transition-all p-4 cursor-pointer"
              onClick={() => onStart([c.id, ...previewCards.filter((x) => x.id !== c.id).map((x) => x.id)])}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="text-xl font-semibold text-primary-900 group-hover:text-accent-600 transition">
                    {c.target_word}
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handlePlay(c.target_word, c.id)
                    }}
                    className={`p-1 rounded-full transition-all ${
                      playingId === c.id
                        ? 'bg-accent-100 text-accent-600'
                        : 'text-primary-400 hover:text-accent-600 hover:bg-accent-50'
                    }`}
                    title="Pronunciar palabra / 朗读单词"
                  >
                    🔊
                  </button>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                  c.pos?.startsWith('n.') ? 'bg-blue-50 text-blue-700' :
                  c.pos?.startsWith('v.') ? 'bg-green-50 text-green-700' :
                  c.pos?.startsWith('adj') ? 'bg-purple-50 text-purple-700' :
                  c.pos?.startsWith('adv') ? 'bg-amber-50 text-amber-700' :
                  'bg-accent-50 text-accent-700'
                }`}>
                  {c.pos ? c.pos.split(' ')[0] : c.level}
                </span>
              </div>
              <div className="text-xs text-primary-500 mb-1">
                <span className="rounded bg-friends-perk/15 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-friends-perk">
                  {c.id.startsWith('LCDP_') ? 'IPA' : 'GenAm'}
                </span>
                {' '}{c.ipa} · {c.pos}
              </div>
              {c.translation && (
                <div className="text-xs text-accent-600 font-medium mb-2">{c.translation}</div>
              )}
              <div className="mb-2 inline-flex w-fit rounded-full border border-accent-200 bg-accent-50 px-2 py-0.5 text-xs font-medium text-accent-700">
                ️ {PRON_MAIN[c.pronunciation_focus] || c.pronunciation_focus}
              </div>
              <div className="flex items-start gap-2">
                <div className="text-sm text-primary-700 line-clamp-2 leading-relaxed flex-1">
                  {c.sentence_full}
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handlePlay(c.sentence_full, `sent-${c.id}`)
                  }}
                  className={`p-1 rounded-full transition-all flex-shrink-0 ${
                    playingId === `sent-${c.id}`
                      ? 'bg-accent-100 text-accent-600'
                      : 'text-primary-400 hover:text-accent-600 hover:bg-accent-50'
                  }`}
                  title="Pronunciar oración / 朗读例句"
                >
                  🔊
                </button>
              </div>
              {c.sentence_translation && (
                <div className="text-xs text-primary-500 mt-1">{c.sentence_translation}</div>
              )}
              <div className="mt-3 pt-3 border-t border-border-light flex items-center justify-between text-xs text-primary-500">
                <div className="flex items-center gap-2">
                  <span> {c.character}</span>
                  <span> {c.scene_id.replace(/scene_\d+_/, '').slice(0, 12)}</span>
                  
                  {/* SRS Status Badge */}
                  {srs[c.id] && (
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${
                      srs[c.id].status === 'review' 
                        ? 'bg-green-100 text-green-700'
                        : 'bg-amber-100 text-amber-700'
                    }`}>
                      {srs[c.id].status === 'review' ? '📚 Review' : '📖 Learning'}
                      {srs[c.id].lastRating && (
                        <span className="ml-1">
                          {srs[c.id].lastRating === 'easy' ? '✅' :
                           srs[c.id].lastRating === 'good' ? '' :
                           srs[c.id].lastRating === 'hard' ? '💪' : '🔄'}
                        </span>
                      )}
                    </span>
                  )}
                  
                  {/* Mastered Badge */}
                  {mastered.has(c.id) && (
                    <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-700 text-[10px] font-medium">
                      ✅ Ya lo sé
                    </span>
                  )}
                </div>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    toggleMastered(c.id)
                  }}
                  className="px-2 py-1 rounded-lg bg-accent-50 border border-accent-200 text-accent-700 hover:bg-accent-100 transition-all text-xs font-medium"
                  title="Marcar como dominada / 标记为已掌握"
                >
                  {mastered.has(c.id) ? '️ Deshacer' : '✅ Ya lo sé'}
                </button>
              </div>
            </div>
            )
          })}
          {/* 换一批 button: show in session mode when there are more batches */}
          {previewMode === 'session' && (() => {
            const blindSpots = blindSpotCards
            const remaining = filteredCards.filter((c) => !blindSpots.some((b) => b.id === c.id))
            const totalOrdered = [...blindSpots, ...remaining]
            const totalBatches = Math.ceil(totalOrdered.length / 7)
            const isLastBatch = sessionBatch >= totalBatches - 1
            if (totalBatches <= 1) return null
            return (
              <div
                onClick={() => setSessionBatch(isLastBatch ? 0 : sessionBatch + 1)}
                className="group bg-white rounded-xl border-2 border-dashed border-accent-300 hover:border-accent-500 shadow-subtle hover:shadow-card transition-all p-4 cursor-pointer flex items-center justify-center min-h-[200px]"
              >
                <div className="text-center">
                  <div className="text-3xl mb-2">🔄</div>
                  <div className="text-sm font-semibold text-accent-600 group-hover:text-accent-700">
                    Cambiar / 换一批
                  </div>
                  <div className="text-xs text-primary-400 mt-1">
                    {isLastBatch
                      ? `Volver al inicio / 回到开头 (${totalOrdered.length} 张)`
                      : `Siguiente lote / 下一批 (${sessionBatch + 1}/${totalBatches})`}
                  </div>
                </div>
              </div>
            )
          })()}
        </div>

        {/* Pagination */}
        {previewCards.length > currentPageSize && (
          <div className="mt-6 flex items-center justify-center gap-3">
            <button
              onClick={() => setPreviewPage(Math.max(0, previewPage - 1))}
              disabled={previewPage === 0}
              className="px-4 py-2 rounded-lg text-sm font-medium border border-border-light bg-white text-primary-700 hover:bg-primary-50 transition-all disabled:opacity-30 disabled:pointer-events-none"
            >
              ← <Bi i18nKey="home.prevPage" />
            </button>
            <span className="text-sm text-primary-500">
              {previewPage + 1} / {Math.ceil(previewCards.length / currentPageSize)}
            </span>
            <button
              onClick={() => setPreviewPage(Math.min(Math.ceil(previewCards.length / currentPageSize) - 1, previewPage + 1))}
              disabled={previewPage >= Math.ceil(previewCards.length / currentPageSize) - 1}
              className="px-4 py-2 rounded-lg text-sm font-medium border border-border-light bg-white text-primary-700 hover:bg-primary-50 transition-all disabled:opacity-30 disabled:pointer-events-none"
            >
              <Bi i18nKey="home.nextPage" /> →
            </button>
          </div>
        )}

      </section>

      <footer className="py-8 text-center text-xs text-primary-400">
        <Bi i18nKey="app.footer" values={{ year: new Date().getFullYear() }} />
      </footer>

      {/* TTS error toast */}
      {ttsError && (
        <div className="fixed top-6 left-1/2 -translate-x-1/2 z-50 px-5 py-3 bg-red-500 text-white text-sm rounded-xl shadow-lg animate-pulse">
          {ttsError}
        </div>
      )}
    </div>
  )
}

import { useMemo, useState } from 'react'
import type { EpisodeMetadata, Flashcard } from '../data/types'
import { useStore } from '../utils/store'

type FilterKey = 'all' | 'pos' | 'vowel' | 'character' | 'scene' | 'level' | 'tags'

interface Props {
  cards: Flashcard[]
  metadata: EpisodeMetadata
  onStart: (queueIds: string[]) => void
}

const POS_LABELS: Record<string, string> = {
  n: '名词', v: '动词', adj: '形容词', adv: '副词',
  phrase: '短语', phrasal: '动词短语', contraction: '缩读',
}

export default function Home({ cards, metadata, onStart }: Props) {
  const srs = useStore((s) => s.srs)
  const favorites = useStore((s) => s.favorites)

  const [selectedFilter, setSelectedFilter] = useState<FilterKey>('all')
  const [selectedValue, setSelectedValue] = useState<string | null>(null)

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
    const vowel = uniq(cards.map((c) => c.vowel_category))
    const chars = uniq(cards.map((c) => c.character))
    const scenes = metadata.scenes_summary.map((s) => s.scene_id)
    const levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'] as const
    const tags = uniq(cards.flatMap((c) => c.tags))
    return { pos, vowel, chars, scenes, levels, tags }
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
      if (selectedFilter === 'vowel') return c.vowel_category === selectedValue
      if (selectedFilter === 'character') return c.character === selectedValue
      if (selectedFilter === 'scene') return c.scene_id === selectedValue
      if (selectedFilter === 'level') return c.level === selectedValue
      if (selectedFilter === 'tags') return c.tags.includes(selectedValue)
      return true
    })
  }, [cards, selectedFilter, selectedValue])

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
      return filters.pos.map((v) => ({ value: v, label: POS_LABELS[v] || v }))
    if (selectedFilter === 'vowel')
      return filters.vowel.map((v) => ({ value: v, label: v }))
    if (selectedFilter === 'character')
      return filters.chars.map((v) => ({ value: v, label: v }))
    if (selectedFilter === 'scene')
      return filters.scenes.map((v) => ({
        value: v,
        label: sceneName(v).slice(0, 18) + (sceneName(v).length > 18 ? '…' : ''),
      }))
    if (selectedFilter === 'level')
      return filters.levels.map((v) => ({ value: v, label: v }))
    if (selectedFilter === 'tags')
      return filters.tags.map((v) => ({ value: v, label: '#' + v }))
    return []
  }

  function startSession() {
    const ids = filteredCards.map((c) => c.id)
    if (ids.length === 0) return
    onStart(ids)
  }

  const tabItems: { key: FilterKey; label: string; icon: string }[] = [
    { key: 'all', label: '全部', icon: '📚' },
    { key: 'pos', label: '词性', icon: '🔤' },
    { key: 'vowel', label: '元音/发音', icon: '🎵' },
    { key: 'character', label: '角色', icon: '🎭' },
    { key: 'scene', label: '场景', icon: '🎬' },
    { key: 'level', label: '难度', icon: '📶' },
    { key: 'tags', label: '主题标签', icon: '🏷️' },
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
          <div className="font-hand text-6xl sm:text-7xl text-friends-cream drop-shadow-md">
            包浆英语
          </div>
          <div className="mt-1 text-lg text-friends-accent/90 font-medium tracking-wide">
            Bāo Jiāng English · 跟着《老友记》把英语磨到包浆
          </div>
          <div className="mt-5 bg-white/10 backdrop-blur rounded-2xl p-4 border border-white/20">
            <div className="text-xl font-semibold">
              {metadata.episode} · {metadata.title}
            </div>
            <div className="text-base text-friends-cream/80 mt-0.5">
              {metadata.title_cn}
            </div>
            <p className="mt-2 text-sm text-friends-cream/80 max-w-2xl leading-relaxed">
              {metadata.description}
            </p>
          </div>

          {/* stats */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mt-5">
            {[
              { label: '总闪卡', num: cards.length, color: 'from-amber-400/80 to-orange-400/80' },
              { label: '待学习', num: stats.new, color: 'from-sky-400/80 to-indigo-400/80' },
              { label: '学习中', num: stats.learning, color: 'from-yellow-400/80 to-amber-400/80' },
              { label: '已掌握', num: stats.learned, color: 'from-green-400/80 to-emerald-400/80' },
              { label: '收藏金句', num: stats.favCount, color: 'from-rose-400/80 to-pink-400/80' },
            ].map((s) => (
              <div
                key={s.label}
                className={`rounded-xl p-3 bg-gradient-to-br ${s.color} backdrop-blur border border-white/20`}
              >
                <div className="text-xs opacity-90">{s.label}</div>
                <div className="text-2xl font-bold mt-0.5">{s.num}</div>
              </div>
            ))}
          </div>
        </div>
      </header>

      {/* Filter section */}
      <section className="max-w-4xl mx-auto px-4 -mt-6 sm:px-6">
        <div className="bg-white rounded-2xl shadow-card border border-friends-coffee/10 p-5">
          <div className="text-sm font-semibold text-friends-sofa/80 mb-3 flex items-center gap-2">
            <span className="w-1 h-4 bg-friends-perk rounded-full inline-block" />
            选择闪卡分类维度
          </div>

          <div className="flex flex-wrap gap-2">
            {tabItems.map((t) => (
              <button
                key={t.key}
                onClick={() => {
                  setSelectedFilter(t.key)
                  setSelectedValue(null)
                }}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                  selectedFilter === t.key
                    ? 'bg-friends-sofa text-white shadow-md'
                    : 'bg-friends-cream text-friends-sofa hover:bg-friends-coffee/15 border border-friends-coffee/20'
                }`}
              >
                <span className="mr-1.5">{t.icon}</span>
                {t.label}
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
                    {chip.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="mt-5 flex items-center justify-between gap-4 flex-wrap">
            <div className="text-sm text-friends-coffee/90">
              当前筛选：<span className="font-semibold text-friends-sofa">{filteredCards.length}</span> 张闪卡
              {selectedFilter !== 'all' && selectedValue && (
                <span className="ml-2 text-friends-perk font-medium">
                  → {tabItems.find((t) => t.key === selectedFilter)?.label}: {selectedValue}
                </span>
              )}
            </div>
            <div className="flex gap-3">
              <button
                disabled={filteredCards.length === 0}
                onClick={startSession}
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-friends-perk to-emerald-500 text-white font-semibold shadow-lg hover:shadow-xl hover:scale-[1.02] transition-all disabled:opacity-40 disabled:pointer-events-none disabled:hover:scale-100"
              >
                🚀 开始学习 ({filteredCards.length})
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
            闪卡预览（前 12 张）
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
              <div className="text-xs text-friends-coffee mb-2">{c.ipa} · {c.pos}</div>
              <div className="text-sm text-friends-sofa/80 line-clamp-2 leading-relaxed">
                {c.sentence_full}
              </div>
              <div className="mt-3 pt-3 border-t border-friends-coffee/10 flex items-center justify-between text-xs text-friends-coffee/80">
                <span>🎭 {c.character}</span>
                <span>🎬 {c.scene_id.replace(/scene_\d+_/, '').slice(0, 12)}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <footer className="py-8 text-center text-xs text-friends-coffee/60">
        Made with ☕ at Central Perk · 包浆英语 © {new Date().getFullYear()}
      </footer>
    </div>
  )
}

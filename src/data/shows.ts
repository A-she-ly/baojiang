import type { ShowDefinition } from './showTypes'

export const SHOWS: ShowDefinition[] = [
  {
    id: 'friends',
    titleKey: 'shows.friends.name',
    descKey: 'shows.friends.description',
    language: 'en',
    coverEmoji: '☕',
    accentFrom: 'from-amber-500',
    accentTo: 'to-orange-600',
    episodes: [
      {
        episodeId: 'S01E01-NOUNS',
        title: 'S01E01 — The Pilot 试播集',
        description: 'Rachel leaves her fiancé and moves in with Monica; Ross reels from his wife leaving him. 瑞秋离开未婚夫搬去和莫妮卡住；罗斯因妻子离开而陷入痛苦。',
        hasCards: true,
      },
    ],
  },
  {
    id: 'modern-family',
    titleKey: 'shows.modern-family.name',
    descKey: 'shows.modern-family.description',
    language: 'en',
    coverEmoji: '🏠',
    accentFrom: 'from-teal-500',
    accentTo: 'to-cyan-600',
    episodes: [
      {
        episodeId: 'S01E01',
        title: 'S01E01 — Pilot',
        description: 'Meet the Dunphys, Pritchetts, and Tuckers in the mockumentary pilot.',
        hasCards: false,
      },
    ],
  },
  {
    id: 'transformers',
    titleKey: 'shows.transformers.name',
    descKey: 'shows.transformers.description',
    language: 'en',
    coverEmoji: '🤖',
    accentFrom: 'from-red-500',
    accentTo: 'to-blue-600',
    episodes: [
      {
        episodeId: 'S01E01',
        title: 'S01E01 — More Than Meets the Eye (Part 1)',
        description: 'The origin of the Autobots and Decepticons on Cybertron.',
        hasCards: false,
      },
    ],
  },
  {
    id: 'la-casa-de-papel',
    titleKey: 'shows.la-casa-de-papel.name',
    descKey: 'shows.la-casa-de-papel.description',
    language: 'es',
    coverEmoji: '🎭',
    accentFrom: 'from-red-600',
    accentTo: 'to-rose-800',
    episodes: [
      {
        episodeId: 'S1E01',
        title: 'S1E01 — 第一季第一集',
        description: '第一季第一集台词中提取的闪卡。',
        hasCards: true,
      },
      {
        episodeId: 'S3E01',
        title: 'S3E01 — 名词和动词分类',
        description: '第三季第一集台词中提取的名词和动词闪卡，每张卡背面展示台词上下文和词源学拆分。',
        hasCards: true,
      },
      {
        episodeId: 'S3E05',
        title: 'S3E05 — 词性分类闪卡',
        description: '第三季第五集台词中提取的闪卡，按词性分类（名词、动词、形容词、副词）。',
        hasCards: true,
      },
      {
        episodeId: 'S3E07',
        title: 'S3E07 — 词性分类闪卡',
        description: '第三季第七集台词中提取的闪卡，按词性分类（名词、动词、副词）。',
        hasCards: true,
      },
      {
        episodeId: 'S4E02',
        title: 'S4E02 — 词性分类闪卡',
        description: '第四季第二集台词中提取的闪卡，按词性分类（名词、动词、形容词）。',
        hasCards: true,
      },
    ],
  },
  {
    id: '7-vidas',
    titleKey: 'shows.7-vidas.name',
    descKey: 'shows.7-vidas.description',
    language: 'es',
    coverEmoji: '🐱',
    accentFrom: 'from-yellow-500',
    accentTo: 'to-amber-600',
    episodes: [
      {
        episodeId: 'S01E01',
        title: 'S01E01 — Piloto',
        description: 'Guille despierta del coma y se reencuentra con sus amigos en Madrid.',
        hasCards: false,
      },
    ],
  },
]

/** Quick lookup by show id */
export const SHOW_MAP: Record<string, ShowDefinition> = Object.fromEntries(
  SHOWS.map((s) => [s.id, s]),
)

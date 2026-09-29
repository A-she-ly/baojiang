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
        episodeId: 'S01E01',
        title: 'S01E01 — The Pilot',
        description: 'Rachel leaves her fiancé and moves in with Monica; Ross reels from his wife leaving him.',
        hasCards: true,
      },
      {
        episodeId: 'S01E01-NOUNS',
        title: 'S01E01 — Noun Classification',
        description: 'Nouns extracted from Friends S01E01 dialogue, each card shows context from the episode.',
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
        episodeId: 'S01E01',
        title: 'S01E01 — Efecto Mariposa',
        description: 'El Profesor recluta a su equipo para el atraco más grande de la historia.',
        hasCards: true,
      },
      {
        episodeId: 'S3E01',
        title: 'S3E01 — 名词分类',
        description: '第三季第一集台词中提取的名词闪卡，每张卡背面展示台词上下文。',
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

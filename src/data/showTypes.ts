export type ShowLanguage = 'en' | 'es'

export interface ShowEpisode {
  episodeId: string     // e.g. "S01E01"
  title: string
  description: string
  hasCards: boolean     // whether flashcard data exists
}

export interface ShowDefinition {
  id: string
  titleKey: string       // i18n key e.g. "shows.friends.name"
  descKey: string        // i18n key e.g. "shows.friends.description"
  language: ShowLanguage
  coverEmoji: string
  accentFrom: string     // tailwind gradient start
  accentTo: string       // tailwind gradient end
  episodes: ShowEpisode[]
}

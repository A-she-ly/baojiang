export interface Flashcard {
  id: string
  episode: string
  scene_id: string
  line_index: number
  character: string
  target_word: string
  ipa: string
  pos: string
  level: 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2'
  vowel_category: string
  tags: string[]
  sentence_cloze: string
  sentence_full: string
  translation: string
  cultural_note: string
  screenshot: string
  frequency_rank: number | null
}

export interface EpisodeMetadata {
  episode: string
  title: string
  title_cn: string
  description: string
  scenes_count: number
  dialogue_lines_count: number
  characters: string[]
  scenes_summary: {
    scene_id: string
    scene_name: string
    lines_count: number
  }[]
}

export interface ScriptLine {
  scene_id: string
  scene_name: string
  line_index: number
  type: 'note' | 'action' | 'dialogue'
  text: string
  character?: string
  direction?: string | null
}

export type SrsRating = 'again' | 'hard' | 'good' | 'easy'

export interface SrsState {
  [cardId: string]: {
    status: 'new' | 'learning' | 'review'
    interval: number // days
    easeFactor: number
    dueAt: number // timestamp ms
    reps: number
    lapses: number
    lastRating?: SrsRating
  }
}

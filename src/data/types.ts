export type PronunciationFocus =
  | 'flap_t'
  | 'vowel_uh'
  | 'y_glide'
  | 'vowel_ih'
  | 'r_colored'
  | 'o_diphthong'
  | 'long_e'
  | 'weak_forms'
  | 'vowel_ah'
  | 'vowel_ae'
  | 'vowel_eh'
  | 'schwa'

export const PRONUNCIATION_FOCUS_LABELS: Record<PronunciationFocus, string> = {
  flap_t: '闪音 /ɾ/',
  vowel_uh: '短元音 /ʌ/',
  y_glide: '滑音 /j/',
  vowel_ih: '短元音 /ɪ/',
  r_colored: '卷舌元音 /ɚ, ɝ/',
  o_diphthong: '双元音 /oʊ/',
  long_e: '长元音 /iː/',
  weak_forms: '弱读与连读',
  vowel_ah: '短元音 /ɑ/',
  vowel_ae: '短元音 /æ/',
  vowel_eh: '短元音 /ɛ/',
  schwa: '弱读 /ə/',
}

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
  pronunciation_focus: PronunciationFocus
  tags: string[]
  sentence_cloze: string
  sentence_full: string
  translation: string  // 目标词中文释义
  sentence_translation?: string  // 整句台词中文翻译
  cultural_note: string
  screenshot: string
  frequency_rank: number | null
  is_example_sentence?: boolean // true = 示例句，非台词
  context_prev?: string | null  // 前一句台词（用于台词卡）
  context_prev_cn?: string | null  // 前一句台词中文翻译
  context_next?: string | null  // 后一句台词（用于台词卡）
  context_next_cn?: string | null  // 后一句台词中文翻译
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

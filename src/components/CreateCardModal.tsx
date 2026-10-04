import { useState, useEffect, useMemo } from 'react'
import type { Flashcard, PronunciationFocus } from '../data/types'
import { PRONUNCIATION_FOCUS_LABELS } from '../data/types'
import { wordToIpa } from '../utils/spanishIpa'

interface CreateCardModalProps {
  selectedText: string
  currentCard: Flashcard
  allCards: Flashcard[]
  onClose: () => void
  onSave: (card: Partial<Flashcard>) => void
}

const POS_OPTIONS = [
  { value: 'n', label: '名词' },
  { value: 'v', label: '动词' },
  { value: 'adj', label: '形容词' },
  { value: 'adv', label: '副词' },
  { value: 'prep', label: '介词' },
  { value: 'conj', label: '连词' },
  { value: 'pron', label: '代词' },
  { value: 'art', label: '冠词' },
  { value: 'interj', label: '感叹词' },
  { value: 'phrase', label: '短语' },
]

const LEVEL_OPTIONS: Flashcard['level'][] = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

const PRON_FOCUS_OPTIONS: PronunciationFocus[] = [
  'rolled_r', 'tapped_r', 'ny_sound', 'll_y',
  'vowel_a', 'vowel_e', 'vowel_i', 'vowel_o', 'vowel_u',
  'diphthong', 'silent_h', 'c_z_distinction', 'j_sound', 'gl_gu',
]

function normalizeForSearch(w: string): string {
  return w.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
}

export default function CreateCardModal({
  selectedText,
  currentCard,
  allCards,
  onClose,
  onSave,
}: CreateCardModalProps) {
  const [targetWord, setTargetWord] = useState(selectedText)
  const [translation, setTranslation] = useState('')
  const [ipa, setIpa] = useState('')
  const [pos, setPos] = useState('n')
  const [level, setLevel] = useState<Flashcard['level']>('B1')
  const [pronFocus, setPronFocus] = useState<PronunciationFocus>('vowel_a')
  const [sentenceFull, setSentenceFull] = useState('')
  const [sentenceTranslation, setSentenceTranslation] = useState('')
  const [useCustomSentence, setUseCustomSentence] = useState(false)
  const [error, setError] = useState('')

  // Find existing sentences containing the target word
  const matchingSentences = useMemo(() => {
    if (!targetWord.trim()) return []
    const norm = normalizeForSearch(targetWord.trim())
    const seen = new Set<string>()
    const results: { sentence: string; translation: string; cardId: string }[] = []

    for (const card of allCards) {
      const sentenceNorm = normalizeForSearch(card.sentence_full)
      if (sentenceNorm.includes(norm) && !seen.has(card.sentence_full)) {
        seen.add(card.sentence_full)
        results.push({
          sentence: card.sentence_full,
          translation: card.sentence_translation || '',
          cardId: card.id,
        })
      }
    }
    return results.slice(0, 10) // Limit to 10 results
  }, [targetWord, allCards])

  // Auto-generate IPA when target word changes
  useEffect(() => {
    if (targetWord.trim()) {
      const generated = wordToIpa(targetWord.trim())
      if (generated && generated !== `/${targetWord.trim().toLowerCase()}/`) {
        setIpa(generated)
      }
    }
  }, [targetWord])

  // Auto-select first matching sentence when word changes
  useEffect(() => {
    if (matchingSentences.length > 0 && !sentenceFull) {
      setSentenceFull(matchingSentences[0].sentence)
      setSentenceTranslation(matchingSentences[0].translation)
    }
  }, [matchingSentences])

  const handleSave = () => {
    if (!targetWord.trim()) {
      setError('请输入目标词')
      return
    }
    if (!translation.trim()) {
      setError('请输入中文释义')
      return
    }
    if (!sentenceFull.trim()) {
      setError('请输入例句')
      return
    }

    const newCard: Partial<Flashcard> = {
      id: `user_${Date.now()}`,
      episode: currentCard.episode,
      scene_id: 'user_created',
      line_index: 0,
      character: currentCard.character,
      target_word: targetWord.trim(),
      ipa: ipa.trim(),
      pos: pos,
      level: level,
      pronunciation_focus: pronFocus,
      tags: ['用户创建'],
      sentence_cloze: sentenceFull.replace(new RegExp(targetWord.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'), '___'),
      sentence_full: sentenceFull,
      translation: translation.trim(),
      sentence_translation: sentenceTranslation,
      cultural_note: '',
      screenshot: '',
      frequency_rank: null,
      is_example_sentence: true,
    }

    onSave(newCard)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-border-light px-6 py-4 flex items-center justify-between z-10">
          <h2 className="text-lg font-semibold text-primary-900">
            ✨ Crear tarjeta / 创建闪卡
          </h2>
          <button
            onClick={onClose}
            className="text-primary-500 hover:text-primary-700 transition-colors text-xl"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-4 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          {/* Target Word */}
          <div>
            <label className="block text-sm font-medium text-primary-700 mb-1">
              Palabra objetivo / 目标词 *
            </label>
            <input
              type="text"
              value={targetWord}
              onChange={(e) => setTargetWord(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-border-light focus:border-accent-500 focus:ring-2 focus:ring-accent-200 outline-none transition-all text-lg font-semibold"
              placeholder="输入西班牙语单词..."
            />
          </div>

          {/* Translation */}
          <div>
            <label className="block text-sm font-medium text-primary-700 mb-1">
              Traducción / 中文释义 *
            </label>
            <input
              type="text"
              value={translation}
              onChange={(e) => setTranslation(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-border-light focus:border-accent-500 focus:ring-2 focus:ring-accent-200 outline-none transition-all"
              placeholder="输入中文释义..."
            />
          </div>

          {/* IPA */}
          <div>
            <label className="block text-sm font-medium text-primary-700 mb-1">
              IPA 音标
            </label>
            <input
              type="text"
              value={ipa}
              onChange={(e) => setIpa(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-border-light focus:border-accent-500 focus:ring-2 focus:ring-accent-200 outline-none transition-all"
              placeholder="/pa.la.βra/"
            />
          </div>

          {/* POS and Level */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-primary-700 mb-1">
                Categoría / 词性
              </label>
              <select
                value={pos}
                onChange={(e) => setPos(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-border-light focus:border-accent-500 focus:ring-2 focus:ring-accent-200 outline-none transition-all"
              >
                {POS_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-primary-700 mb-1">
                Nivel / 难度等级
              </label>
              <select
                value={level}
                onChange={(e) => setLevel(e.target.value as Flashcard['level'])}
                className="w-full px-3 py-2 rounded-lg border border-border-light focus:border-accent-500 focus:ring-2 focus:ring-accent-200 outline-none transition-all"
              >
                {LEVEL_OPTIONS.map((lvl) => (
                  <option key={lvl} value={lvl}>
                    {lvl}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Pronunciation Focus */}
          <div>
            <label className="block text-sm font-medium text-primary-700 mb-1">
              Punto de pronunciación / 发音重点
            </label>
            <select
              value={pronFocus}
              onChange={(e) => setPronFocus(e.target.value as PronunciationFocus)}
              className="w-full px-3 py-2 rounded-lg border border-border-light focus:border-accent-500 focus:ring-2 focus:ring-accent-200 outline-none transition-all"
            >
              {PRON_FOCUS_OPTIONS.map((pf) => (
                <option key={pf} value={pf}>
                  {PRONUNCIATION_FOCUS_LABELS[pf]}
                </option>
              ))}
            </select>
          </div>

          {/* Sentence Selection - Key Feature */}
          <div>
            <label className="block text-sm font-medium text-primary-700 mb-2">
              Oración de ejemplo / 例句 *
            </label>

            {/* Existing sentences from card set */}
            {matchingSentences.length > 0 && !useCustomSentence && (
              <div className="mb-3">
                <div className="text-xs text-primary-500 mb-2 flex items-center gap-1">
                  📖 从已有例句中选择（找到 {matchingSentences.length} 条包含「{targetWord}」的例句）
                </div>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {matchingSentences.map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setSentenceFull(item.sentence)
                        setSentenceTranslation(item.translation)
                      }}
                      className={`w-full text-left p-3 rounded-lg border transition-all text-sm ${
                        sentenceFull === item.sentence
                          ? 'bg-accent-50 border-accent-300 ring-2 ring-accent-200'
                          : 'bg-white border-border-light hover:border-accent-200 hover:bg-accent-50/50'
                      }`}
                    >
                      <div className="font-medium text-primary-800">
                        {item.sentence.split(new RegExp(`(${targetWord.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')).map((part, i) =>
                          part.toLowerCase() === targetWord.toLowerCase() ? (
                            <mark key={i} className="bg-accent-200 px-0.5 rounded font-bold">{part}</mark>
                          ) : (
                            <span key={i}>{part}</span>
                          )
                        )}
                      </div>
                      {item.translation && (
                        <div className="text-xs text-primary-500 mt-1">{item.translation}</div>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Custom sentence input */}
            <div className={`border rounded-lg p-3 ${useCustomSentence ? 'border-accent-300 bg-accent-50/30' : 'border-border-light'}`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-primary-500">
                  {useCustomSentence ? '✏️ 自定义例句' : '或者使用自定义例句'}
                </span>
                <button
                  onClick={() => {
                    setUseCustomSentence(!useCustomSentence)
                    if (!useCustomSentence) setSentenceFull('')
                  }}
                  className="text-xs text-accent-600 hover:text-accent-700 font-medium"
                >
                  {useCustomSentence ? '← 返回选择已有例句' : '自定义例句 →'}
                </button>
              </div>
              {useCustomSentence && (
                <>
                  <textarea
                    value={sentenceFull}
                    onChange={(e) => setSentenceFull(e.target.value)}
                    rows={2}
                    className="w-full px-3 py-2 rounded-lg border border-border-light focus:border-accent-500 focus:ring-2 focus:ring-accent-200 outline-none transition-all resize-none text-sm"
                    placeholder="输入完整例句..."
                  />
                  <input
                    type="text"
                    value={sentenceTranslation}
                    onChange={(e) => setSentenceTranslation(e.target.value)}
                    className="w-full px-3 py-2 mt-2 rounded-lg border border-border-light focus:border-accent-500 focus:ring-2 focus:ring-accent-200 outline-none transition-all text-sm"
                    placeholder="输入例句中文翻译..."
                  />
                </>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-white border-t border-border-light px-6 py-4 flex items-center justify-end gap-3 z-10">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-sm font-medium border border-border-light bg-white text-primary-700 hover:bg-primary-50 transition-all"
          >
            Cancelar / 取消
          </button>
          <button
            onClick={handleSave}
            disabled={!targetWord.trim() || !translation.trim() || !sentenceFull.trim()}
            className="px-4 py-2 rounded-lg text-sm font-medium bg-accent-600 text-white hover:bg-accent-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Guardar / 保存
          </button>
        </div>
      </div>
    </div>
  )
}

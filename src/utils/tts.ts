/**
 * Shared TTS utility
 * - Only plays audio from the TTS API (never browser speechSynthesis)
 * - Tracks consecutive failures; after 3, shows a network error提示
 */

let consecutiveFailures = 0
const MAX_FAILURES = 3
let currentAudio: HTMLAudioElement | null = null

/**
 * Play TTS audio.
 * @param text - text to speak
 * @param lang - 'es' | 'en'
 * @param onPlay - called when audio starts playing
 * @param onEnd - called when audio ends (finish or error)
 * @param onError - called only after 3 consecutive failures
 */
export function playTTS(
  text: string,
  lang: 'es' | 'en',
  onPlay?: () => void,
  onEnd?: () => void,
  onError?: (message: string) => void,
): void {
  const cleanText = text.replace(/\*|\(.*?\)/g, '').trim()
  if (!cleanText) return

  // Stop any currently playing audio
  stopTTS()

  const encoded = encodeURIComponent(cleanText)
  const audio = new Audio(`/api/tts?text=${encoded}&lang=${lang}`)
  currentAudio = audio

  audio.onplay = () => {
    consecutiveFailures = 0 // reset on success
    onPlay?.()
  }
  audio.onended = () => {
    currentAudio = null
    onEnd?.()
  }
  audio.onerror = () => {
    currentAudio = null
    consecutiveFailures++
    onEnd?.()
    if (consecutiveFailures >= MAX_FAILURES) {
      consecutiveFailures = 0
      onError?.('网络连接异常，请稍后再试 / Error de red, inténtelo más tarde')
    }
  }

  audio.play().catch(() => {
    currentAudio = null
    consecutiveFailures++
    onEnd?.()
    if (consecutiveFailures >= MAX_FAILURES) {
      consecutiveFailures = 0
      onError?.('网络连接异常，请稍后再试 / Error de red, inténtelo más tarde')
    }
  })
}

/** Stop current TTS playback */
export function stopTTS() {
  if (currentAudio) {
    currentAudio.pause()
    currentAudio.currentTime = 0
    currentAudio = null
  }
}

/** Reset the failure counter */
export function resetTTSFailures() {
  consecutiveFailures = 0
}

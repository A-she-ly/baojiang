import { create } from 'zustand'
import type { Flashcard, SrsRating, SrsState } from '../data/types'
import { scheduleNext } from '../utils/srs'

const LS_KEYS = {
  srs: 'bjy_srs_v1',
  favorites: 'bjy_favorites_v1',
  disliked: 'bjy_disliked_v1',
  mastered: 'bjy_mastered_v1',
  seen: 'bjy_seen_v1',
  settings: 'bjy_settings_v1',
  view: 'bjy_view_v1',
}

type View =
  | { name: 'home' }
  | { name: 'study'; queueIds: string[] }
  | { name: 'favorites' }

interface Store {
  cards: Flashcard[]
  srs: SrsState
  favorites: Set<string>
  disliked: Set<string>
  mastered: Set<string>
  seen: Set<string>
  view: View
  load: (cards: Flashcard[]) => void
  hydrate: () => void
  setView: (v: View) => void
  rateCard: (id: string, rating: SrsRating) => void
  toggleFavorite: (id: string) => void
  toggleDislike: (id: string) => void
  toggleMastered: (id: string) => void
  markSeen: (id: string) => void
}

function loadLS<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key)
    if (!raw) return fallback
    return JSON.parse(raw) as T
  } catch {
    return fallback
  }
}

export const useStore = create<Store>((set, get) => ({
  cards: [],
  srs: {},
  favorites: new Set(),
  disliked: new Set(),
  mastered: new Set(),
  seen: new Set(),
  view: { name: 'home' },

  load(cards) {
    set({ cards })
  },

  hydrate() {
    const srs = loadLS<SrsState>(LS_KEYS.srs, {})
    const favArr = loadLS<string[]>(LS_KEYS.favorites, [])
    const dislikedArr = loadLS<string[]>(LS_KEYS.disliked, [])
    const masteredArr = loadLS<string[]>(LS_KEYS.mastered, [])
    const seenArr = loadLS<string[]>(LS_KEYS.seen, [])
    const savedView = loadLS<View>(LS_KEYS.view, { name: 'home' as const })
    set({ srs, favorites: new Set(favArr), disliked: new Set(dislikedArr), mastered: new Set(masteredArr), seen: new Set(seenArr), view: savedView })
  },

  setView(view) {
    localStorage.setItem(LS_KEYS.view, JSON.stringify(view))
    set({ view })
  },

  rateCard(id, rating) {
    const prev = get().srs[id]
    const next = scheduleNext(prev, rating)
    const srs = { ...get().srs, [id]: next }
    localStorage.setItem(LS_KEYS.srs, JSON.stringify(srs))
    set({ srs })
  },

  toggleFavorite(id) {
    const fav = new Set(get().favorites)
    if (fav.has(id)) fav.delete(id)
    else fav.add(id)
    localStorage.setItem(LS_KEYS.favorites, JSON.stringify([...fav]))
    set({ favorites: fav })
  },

  toggleDislike(id) {
    const dis = new Set(get().disliked)
    if (dis.has(id)) dis.delete(id)
    else dis.add(id)
    localStorage.setItem(LS_KEYS.disliked, JSON.stringify([...dis]))
    set({ disliked: dis })
  },

  toggleMastered(id) {
    const mas = new Set(get().mastered)
    if (mas.has(id)) mas.delete(id)
    else mas.add(id)
    localStorage.setItem(LS_KEYS.mastered, JSON.stringify([...mas]))
    set({ mastered: mas })
  },

  markSeen(id) {
    const seen = get().seen
    if (seen.has(id)) return
    const next = new Set(seen)
    next.add(id)
    localStorage.setItem(LS_KEYS.seen, JSON.stringify([...next]))
    set({ seen: next })
  },
}))

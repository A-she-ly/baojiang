import { create } from 'zustand'
import type { Flashcard, SrsRating, SrsState } from '../data/types'
import { scheduleNext } from '../utils/srs'

const LS_KEYS = {
  srs: 'bjy_srs_v1',
  favorites: 'bjy_favorites_v1',
  settings: 'bjy_settings_v1',
}

type View =
  | { name: 'home' }
  | { name: 'study'; queueIds: string[] }
  | { name: 'favorites' }

interface Store {
  cards: Flashcard[]
  srs: SrsState
  favorites: Set<string>
  view: View
  load: (cards: Flashcard[]) => void
  hydrate: () => void
  setView: (v: View) => void
  rateCard: (id: string, rating: SrsRating) => void
  toggleFavorite: (id: string) => void
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
  view: { name: 'home' },

  load(cards) {
    set({ cards })
  },

  hydrate() {
    const srs = loadLS<SrsState>(LS_KEYS.srs, {})
    const favArr = loadLS<string[]>(LS_KEYS.favorites, [])
    set({ srs, favorites: new Set(favArr) })
  },

  setView(view) {
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
}))

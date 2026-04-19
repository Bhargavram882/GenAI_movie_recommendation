import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Movie, RecommendationResponse, MovieFilters } from '../types'

interface AppState {
  // Search
  query: string
  setQuery: (q: string) => void

  // Filters
  filters: MovieFilters
  setFilters: (f: MovieFilters) => void
  resetFilters: () => void

  // Results
  results: RecommendationResponse | null
  setResults: (r: RecommendationResponse | null) => void
  isLoading: boolean
  setIsLoading: (v: boolean) => void
  error: string | null
  setError: (e: string | null) => void

  // Selected movie
  selectedMovie: Movie | null
  setSelectedMovie: (m: Movie | null) => void

  // Watch history (persisted)
  watchHistory: string[]
  addToHistory: (movieId: string) => void
  removeFromHistory: (movieId: string) => void
  clearHistory: () => void

  // User
  userId: string
}

const DEFAULT_FILTERS: MovieFilters = {}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      query: '',
      setQuery: (q) => set({ query: q }),

      filters: DEFAULT_FILTERS,
      setFilters: (f) => set({ filters: f }),
      resetFilters: () => set({ filters: DEFAULT_FILTERS }),

      results: null,
      setResults: (r) => set({ results: r }),
      isLoading: false,
      setIsLoading: (v) => set({ isLoading: v }),
      error: null,
      setError: (e) => set({ error: e }),

      selectedMovie: null,
      setSelectedMovie: (m) => set({ selectedMovie: m }),

      watchHistory: [],
      addToHistory: (id) =>
        set((s) => ({
          watchHistory: s.watchHistory.includes(id)
            ? s.watchHistory
            : [id, ...s.watchHistory].slice(0, 50),
        })),
      removeFromHistory: (id) =>
        set((s) => ({ watchHistory: s.watchHistory.filter((i) => i !== id) })),
      clearHistory: () => set({ watchHistory: [] }),

      userId: `user_${Math.random().toString(36).slice(2, 10)}`,
    }),
    {
      name: 'cinemate-store',
      partialize: (s) => ({ watchHistory: s.watchHistory, userId: s.userId }),
    }
  )
)

import { useCallback } from 'react'
import { useAppStore } from '../store/useAppStore'
import { recommendationApi } from '../services/api'
import toast from 'react-hot-toast'

export function useRecommendations() {
  const {
    query, filters, userId, watchHistory,
    setResults, setIsLoading, setError, setQuery,
  } = useAppStore()

  const search = useCallback(async (overrideQuery?: string) => {
    const q = overrideQuery ?? query
    if (!q.trim()) return

    setIsLoading(true)
    setError(null)

    try {
      const result = await recommendationApi.getRecommendations({
        query: q,
        user_id: userId,
        watch_history: watchHistory.slice(0, 20),
        top_n: 12,
        filters: Object.keys(filters).length > 0 ? filters : undefined,
      })
      setResults(result)
      if (overrideQuery) setQuery(overrideQuery)
    } catch (err: any) {
      const msg = err.message || 'Failed to fetch recommendations'
      setError(msg)
      toast.error(msg)
    } finally {
      setIsLoading(false)
    }
  }, [query, filters, userId, watchHistory, setResults, setIsLoading, setError, setQuery])

  return { search }
}

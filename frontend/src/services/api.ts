import axios from 'axios'
import type { RecommendationRequest, RecommendationResponse, Movie, HealthStatus } from '../types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.detail || err.message || 'Unknown error'
    return Promise.reject(new Error(msg))
  }
)

export const recommendationApi = {
  getRecommendations: async (req: RecommendationRequest): Promise<RecommendationResponse> => {
    const { data } = await api.post('/recommendations/', req)
    return data
  },

  getSimilarMovies: async (movieId: string, topN = 10): Promise<Movie[]> => {
    const { data } = await api.post('/recommendations/similar', { movie_id: movieId, top_n: topN })
    return data
  },

  indexMovies: async (movies: object[]): Promise<{ status: string; indexed: number }> => {
    const { data } = await api.post('/recommendations/index', { movies })
    return data
  },
}

export const systemApi = {
  getHealth: async (): Promise<HealthStatus> => {
    const { data } = await axios.get('/health')
    return data
  },

  getStats: async () => {
    const { data } = await api.get('/stats')
    return data
  },
}

export default api

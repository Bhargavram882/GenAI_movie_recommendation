export interface Movie {
  id: string
  title: string
  year?: number
  genres: string[]
  director?: string
  cast: string[]
  overview?: string
  poster_path?: string
  vote_average: number
  popularity: number
  runtime?: number
  score: number
  explanation?: string
  cf_boost?: number
}

export interface QueryAnalysis {
  genres: string[]
  mood: string
  themes: string[]
  era: string
}

export interface RecommendationResponse {
  recommendations: Movie[]
  query_analysis: QueryAnalysis
  total: number
  algorithm: string
  latency_ms?: number
}

export interface RecommendationRequest {
  query: string
  user_id?: string
  watch_history?: string[]
  top_n?: number
  filters?: MovieFilters
}

export interface MovieFilters {
  genres?: string[]
  year_min?: number
  year_max?: number
  language?: string
  min_rating?: number
}

export interface HealthStatus {
  status: string
  version: string
  services: Record<string, string>
  timestamp: string
}

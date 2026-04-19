from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RecommendationRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500, description="Natural language preference query")
    user_id: Optional[str] = Field(None, description="User ID for personalization")
    watch_history: Optional[list[str]] = Field(default_factory=list, description="List of movie IDs the user has watched")
    top_n: int = Field(default=10, ge=1, le=50)
    filters: Optional["MovieFilters"] = None


class MovieFilters(BaseModel):
    genres: Optional[list[str]] = None
    year_min: Optional[int] = Field(None, ge=1900, le=2030)
    year_max: Optional[int] = Field(None, ge=1900, le=2030)
    language: Optional[str] = None
    min_rating: Optional[float] = Field(None, ge=0.0, le=10.0)
    max_runtime: Optional[int] = Field(None, ge=30)


class MovieOut(BaseModel):
    id: str
    title: str
    year: Optional[int] = None
    genres: list[str] = []
    director: Optional[str] = None
    cast: list[str] = []
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    vote_average: float = 0.0
    popularity: float = 0.0
    runtime: Optional[int] = None
    score: float = Field(..., description="Semantic similarity score (0-1)")
    explanation: Optional[str] = Field(None, description="LLM-generated personalized explanation")
    cf_boost: Optional[float] = Field(None, description="Collaborative filtering score boost")


class QueryAnalysis(BaseModel):
    genres: list[str] = []
    mood: str = ""
    themes: list[str] = []
    era: str = ""


class RecommendationResponse(BaseModel):
    recommendations: list[MovieOut]
    query_analysis: QueryAnalysis
    total: int
    algorithm: str = "hybrid_semantic_cf"
    latency_ms: Optional[float] = None


class SimilarMoviesRequest(BaseModel):
    movie_id: str
    top_n: int = Field(default=10, ge=1, le=50)


class IndexMovieRequest(BaseModel):
    movies: list[dict] = Field(..., min_length=1, max_length=500)


class HealthResponse(BaseModel):
    status: str
    version: str
    services: dict
    timestamp: datetime


class StatsResponse(BaseModel):
    total_indexed_movies: int
    pinecone_stats: dict
    cache_healthy: bool

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "CineMate AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # Security
    SECRET_KEY: str = "change-me-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ── Embeddings (FREE — runs locally via sentence-transformers) ──────────
    # Model downloads automatically on first run (~90MB).
    # all-MiniLM-L6-v2  → 384-dim, fast, great quality for semantic search
    # all-mpnet-base-v2  → 768-dim, slower, higher quality (swap if you want)
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSIONS: int = 384          # must match EMBEDDING_MODEL output
    EMBEDDING_DEVICE: str = "cpu"            # set "cuda" if you have a GPU

    # ── LLM for explanations + query parsing (FREE via Groq) ───────────────
    # Groq free tier: 30 req/min, 6000 tokens/min — plenty for this app.
    # Sign up at console.groq.com → API Keys → Create key (free, no card).
    # Supported free models: llama-3.1-8b-instant, gemma2-9b-it, mixtral-8x7b
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"

    # ── Pinecone (FREE starter tier) ────────────────────────────────────────
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "us-east-1"
    PINECONE_INDEX_NAME: str = "cinemate-movies"
    PINECONE_NAMESPACE: str = "movies"

    # ── Redis ────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL_SECONDS: int = 3600

    # ── CORS ─────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60

    # ── Recommendation ────────────────────────────────────────────────────────
    TOP_K_RESULTS: int = 20
    RERANK_TOP_N: int = 10
    MIN_SIMILARITY_SCORE: float = 0.3        # lower threshold for 384-dim model

    # ── TMDB (FREE forever) ───────────────────────────────────────────────────
    TMDB_API_KEY: str = ""
    TMDB_BASE_URL: str = "https://api.themoviedb.org/3"
    TMDB_IMAGE_BASE_URL: str = "https://image.tmdb.org/t/p/w500"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

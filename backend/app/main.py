"""
CineMate AI - GenAI-Powered Movie Recommendation Backend
FastAPI + Pinecone + OpenAI + Redis
"""
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.api import recommendations
from app.services.pinecone_service import pinecone_service
from app.services.cache_service import cache_service
from app.models.schemas import HealthResponse, StatsResponse


limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    try:
        await pinecone_service.initialize()
        logger.info("Pinecone connected")
    except Exception as e:
        logger.warning(f"Pinecone init warning: {e}")

    cache_ok = await cache_service.ping()
    if cache_ok:
        logger.info("Redis cache connected")
    else:
        logger.warning("Redis unavailable — caching disabled")

    yield
    logger.info("Shutting down CineMate AI")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## CineMate AI — GenAI-Powered Movie Recommendation System (100% Free Stack)

### Architecture
- **Semantic Search**: `all-MiniLM-L6-v2` embeddings (local, free) indexed in Pinecone free tier
- **Hybrid Ranking**: Content-based similarity + collaborative filtering from watch history
- **LLM Explanations**: Groq free tier (LLaMA-3.1-8B) for personalized recommendation explanations
- **Caching**: Redis for sub-200ms latency on repeated queries

### Free Services Used
| Service | Purpose | Cost |
|---------|---------|------|
| sentence-transformers | Local embeddings (384-dim) | Free |
| Groq API | LLM query parsing + explanations | Free tier |
| Pinecone | Vector search index (10K+ movies) | Free starter |
| TMDB API | Movie metadata + posters | Free forever |
| Redis | Response caching | Free (self-hosted) |
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(recommendations.router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "CineMate AI API", "docs": "/docs", "version": settings.APP_VERSION}


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check():
    pinecone_ok = pinecone_service._initialized
    cache_ok = await cache_service.ping()
    return HealthResponse(
        status="healthy" if pinecone_ok else "degraded",
        version=settings.APP_VERSION,
        services={
            "pinecone": "connected" if pinecone_ok else "disconnected",
            "redis": "connected" if cache_ok else "disconnected",
            "groq_llm": "configured" if settings.GROQ_API_KEY else "missing_key",
            "embeddings": f"local:{settings.EMBEDDING_MODEL}",
        },
        timestamp=datetime.utcnow(),
    )


@app.get("/api/v1/stats", response_model=StatsResponse, tags=["system"])
async def get_stats():
    pinecone_stats = await pinecone_service.get_stats()
    cache_ok = await cache_service.ping()
    return StatsResponse(
        total_indexed_movies=pinecone_stats.get("total_vectors", 0),
        pinecone_stats=pinecone_stats,
        cache_healthy=cache_ok,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=settings.DEBUG,
    )

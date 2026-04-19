import time
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from loguru import logger

from app.models.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    SimilarMoviesRequest,
    IndexMovieRequest,
    MovieOut,
    QueryAnalysis,
)
from app.services.recommendation_engine import recommendation_engine

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get personalized movie recommendations using hybrid GenAI pipeline:
    - Semantic search via Pinecone vector index (10K+ movies)
    - Collaborative filtering re-ranking based on watch history
    - GPT-4o powered personalized explanations
    
    Sub-200ms latency via Redis caching on repeated queries.
    """
    start = time.perf_counter()
    try:
        result = await recommendation_engine.get_recommendations(
            user_query=request.query,
            user_id=request.user_id,
            watch_history=request.watch_history,
            filters=request.filters.model_dump() if request.filters else None,
            top_n=request.top_n,
        )
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation engine error: {str(e)}")

    latency_ms = (time.perf_counter() - start) * 1000

    return RecommendationResponse(
        recommendations=[MovieOut(**m) for m in result["recommendations"]],
        query_analysis=QueryAnalysis(**result.get("query_analysis", {})),
        total=result["total"],
        algorithm=result.get("algorithm", "hybrid_semantic_cf"),
        latency_ms=round(latency_ms, 2),
    )


@router.post("/similar", response_model=list[MovieOut])
async def get_similar_movies(request: SimilarMoviesRequest):
    """
    Find movies semantically similar to a given movie using its Pinecone vector.
    Uses ANN search for sub-50ms retrieval.
    """
    try:
        movies = await recommendation_engine.get_similar_movies(
            movie_id=request.movie_id,
            top_n=request.top_n,
        )
    except Exception as e:
        logger.error(f"Similar movies error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    if not movies:
        raise HTTPException(status_code=404, detail=f"Movie {request.movie_id} not found in index")

    return [MovieOut(**m) for m in movies]


@router.post("/index")
async def index_movies(request: IndexMovieRequest, background_tasks: BackgroundTasks):
    """
    Batch index movies into Pinecone with OpenAI embeddings.
    Large batches are processed asynchronously.
    """
    if len(request.movies) > 100:
        background_tasks.add_task(recommendation_engine.index_movies, request.movies)
        return {
            "status": "queued",
            "message": f"Indexing {len(request.movies)} movies in background",
        }
    try:
        result = await recommendation_engine.index_movies(request.movies)
        return {"status": "complete", **result}
    except Exception as e:
        logger.error(f"Indexing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

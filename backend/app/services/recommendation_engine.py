"""
Core recommendation engine combining:
1. Semantic vector search via Pinecone (content-based)
2. Collaborative filtering via user behavior signals
3. LLM-powered re-ranking and explanation generation
"""
import asyncio
import numpy as np
from typing import Optional
from loguru import logger

from app.services.openai_service import openai_service
from app.services.pinecone_service import pinecone_service
from app.services.cache_service import cache_service
from app.core.config import settings


class RecommendationEngine:
    """
    Hybrid recommendation pipeline:
      Query → LLM parsing → Embedding → Pinecone ANN search
         → Collaborative filter re-rank → LLM explanation → Response
    """

    async def get_recommendations(
        self,
        user_query: str,
        user_id: Optional[str] = None,
        watch_history: Optional[list[str]] = None,
        filters: Optional[dict] = None,
        top_n: int = 10,
    ) -> dict:
        cache_key = f"recs:{user_id}:{hash(user_query)}:{hash(str(filters))}"
        cached = await cache_service.get(cache_key)
        if cached:
            logger.info(f"Cache hit for user {user_id}")
            return cached

        logger.info(f"Generating recommendations for: '{user_query[:60]}...'")

        # Step 1: Parse + enrich the query with GPT-4o
        parsed = await openai_service.parse_user_query(user_query)
        enriched_query = parsed.get("enriched_query", user_query)
        logger.debug(f"Enriched query: {enriched_query}")

        # Step 2: Generate dense embedding
        query_vector = await openai_service.get_embedding(enriched_query)

        # Step 3: Pinecone ANN search
        pinecone_filter = self._build_pinecone_filter(parsed, filters)
        raw_results = await pinecone_service.query_similar(
            query_vector=query_vector,
            top_k=settings.TOP_K_RESULTS,
            filter_dict=pinecone_filter if pinecone_filter else None,
        )
        logger.info(f"Pinecone returned {len(raw_results)} candidates")

        if not raw_results:
            return {"recommendations": [], "query_analysis": parsed, "total": 0}

        # Step 4: Extract metadata + collaborative filter re-rank
        movies = self._extract_movies(raw_results)
        if user_id and watch_history:
            movies = await self._collaborative_rerank(movies, user_id, watch_history)

        # Step 5: Trim to top_n
        movies = movies[:top_n]

        # Step 6: LLM explanations (async, non-blocking enrichment)
        movies_with_explanations = await openai_service.generate_recommendation_explanation(
            user_preferences=user_query,
            recommended_movies=movies,
            watch_history=watch_history,
        )

        result = {
            "recommendations": movies_with_explanations,
            "query_analysis": {
                "genres": parsed.get("genres", []),
                "mood": parsed.get("mood", ""),
                "themes": parsed.get("themes", []),
                "era": parsed.get("era", ""),
            },
            "total": len(movies_with_explanations),
            "algorithm": "hybrid_semantic_cf",
        }

        await cache_service.set(cache_key, result, ttl=settings.CACHE_TTL_SECONDS)
        return result

    async def get_similar_movies(self, movie_id: str, top_n: int = 10) -> list[dict]:
        """Find movies similar to a given movie by fetching its vector."""
        cache_key = f"similar:{movie_id}:{top_n}"
        cached = await cache_service.get(cache_key)
        if cached:
            return cached

        vectors = await pinecone_service.fetch_by_ids([movie_id])
        if movie_id not in vectors:
            return []

        movie_vector = vectors[movie_id].values
        results = await pinecone_service.query_similar(
            query_vector=movie_vector,
            top_k=top_n + 1,
        )
        # Exclude the query movie itself
        similar = [r for r in results if r["id"] != movie_id][:top_n]
        movies = self._extract_movies(similar)
        await cache_service.set(cache_key, movies, ttl=3600)
        return movies

    async def index_movies(self, movies: list[dict]) -> dict:
        """
        Embed and index a batch of movies into Pinecone.
        Called during data ingestion / backfill jobs.
        """
        logger.info(f"Indexing {len(movies)} movies...")

        embedding_texts = await asyncio.gather(
            *[openai_service.generate_movie_embedding_text(m) for m in movies]
        )

        embeddings = await openai_service.get_batch_embeddings(list(embedding_texts))

        vectors = []
        for movie, embedding in zip(movies, embeddings):
            movie_id = str(movie.get("id", movie.get("tmdb_id")))
            vectors.append(
                {
                    "id": movie_id,
                    "values": embedding,
                    "metadata": {
                        "title": movie.get("title", ""),
                        "year": int(movie.get("year") or 0),
                        "genres": movie.get("genres", []),
                        "director": movie.get("director", ""),
                        "cast": movie.get("cast", [])[:5],
                        "overview": (movie.get("overview", ""))[:500],
                        "poster_path": movie.get("poster_path", ""),
                        "vote_average": movie.get("vote_average", 0.0),
                        "popularity": movie.get("popularity", 0.0),
                        "runtime": movie.get("runtime", 0),
                        "language": movie.get("original_language", "en"),
                        "themes": movie.get("themes", []),
                        "mood": movie.get("mood", ""),
                    },
                }
            )

        count = await pinecone_service.upsert_movies(vectors)
        return {"indexed": count, "total_movies": len(movies)}

    def _extract_movies(self, raw_results: list[dict]) -> list[dict]:
        """Flatten Pinecone results into clean movie dicts."""
        movies = []
        for r in raw_results:
            meta = r.get("metadata", {})
            movies.append(
                {
                    "id": r["id"],
                    "score": round(r["score"], 4),
                    "title": meta.get("title", "Unknown"),
                    "year": meta.get("year", ""),
                    "genres": meta.get("genres", []),
                    "director": meta.get("director", ""),
                    "cast": meta.get("cast", []),
                    "overview": meta.get("overview", ""),
                    "poster_path": meta.get("poster_path", ""),
                    "vote_average": meta.get("vote_average", 0.0),
                    "popularity": meta.get("popularity", 0.0),
                    "runtime": meta.get("runtime", 0),
                    "language": meta.get("language", "en"),
                }
            )
        return movies

    async def _collaborative_rerank(
        self, movies: list[dict], user_id: str, watch_history: list[str]
    ) -> list[dict]:
        """
        Apply lightweight collaborative filtering signal on top of vector scores.
        Boosts movies that share genre/director overlap with watch history.
        """
        # Fetch metadata for watched movies to extract preference signals
        history_vectors = await pinecone_service.fetch_by_ids(watch_history[:20])
        if not history_vectors:
            return movies

        watched_genres: dict[str, float] = {}
        watched_directors: dict[str, float] = {}
        for vid in history_vectors.values():
            meta = vid.metadata or {}
            for g in meta.get("genres", []):
                watched_genres[g] = watched_genres.get(g, 0) + 1
            d = meta.get("director", "")
            if d:
                watched_directors[d] = watched_directors.get(d, 0) + 1

        # Normalize
        total_g = sum(watched_genres.values()) or 1
        total_d = sum(watched_directors.values()) or 1
        for k in watched_genres:
            watched_genres[k] /= total_g
        for k in watched_directors:
            watched_directors[k] /= total_d

        # Re-score
        for movie in movies:
            cf_boost = 0.0
            for g in movie.get("genres", []):
                cf_boost += watched_genres.get(g, 0) * 0.15
            d = movie.get("director", "")
            if d:
                cf_boost += watched_directors.get(d, 0) * 0.10
            movie["score"] = min(1.0, movie["score"] + cf_boost)
            movie["cf_boost"] = round(cf_boost, 4)

        # Re-sort
        movies.sort(key=lambda x: x["score"], reverse=True)
        return movies

    def _build_pinecone_filter(self, parsed: dict, extra_filters: Optional[dict]) -> dict:
        """Build Pinecone metadata filter from parsed query + explicit filters."""
        pf = {}
        if extra_filters:
            if extra_filters.get("genres"):
                pf["genres"] = {"$in": extra_filters["genres"]}
            if extra_filters.get("year_min") or extra_filters.get("year_max"):
                year_filter = {}
                if extra_filters.get("year_min"):
                    year_filter["$gte"] = extra_filters["year_min"]
                if extra_filters.get("year_max"):
                    year_filter["$lte"] = extra_filters["year_max"]
                pf["year"] = year_filter
            if extra_filters.get("language"):
                pf["language"] = {"$eq": extra_filters["language"]}
            if extra_filters.get("min_rating"):
                pf["vote_average"] = {"$gte": extra_filters["min_rating"]}
        return pf


recommendation_engine = RecommendationEngine()

#!/usr/bin/env python3
"""
Seed script: Fetch movies from TMDB API, generate LOCAL embeddings
(sentence-transformers, no API key needed), and bulk upsert into Pinecone.

Cost: $0 — uses only free services (TMDB + local embeddings + Pinecone free tier)

Usage:
    python scripts/seed_pinecone.py --pages 50   # ~1 000 movies, ~2 min
    python scripts/seed_pinecone.py --pages 500  # ~10K movies, ~15 min
"""
import asyncio
import argparse
import httpx
from loguru import logger
import sys
sys.path.insert(0, '.')

from app.core.config import settings
from app.services.recommendation_engine import recommendation_engine


async def fetch_tmdb_movies(pages: int = 50) -> list[dict]:
    """Fetch popular movies from TMDB across multiple pages."""
    movies = []
    async with httpx.AsyncClient() as client:
        for page in range(1, pages + 1):
            try:
                resp = await client.get(
                    f"{settings.TMDB_BASE_URL}/movie/popular",
                    params={"api_key": settings.TMDB_API_KEY, "page": page, "language": "en-US"},
                    timeout=10,
                )
                data = resp.json()
                for m in data.get("results", []):
                    # Fetch full details for genres, runtime, etc
                    detail_resp = await client.get(
                        f"{settings.TMDB_BASE_URL}/movie/{m['id']}",
                        params={"api_key": settings.TMDB_API_KEY, "append_to_response": "credits,keywords"},
                        timeout=10,
                    )
                    detail = detail_resp.json()

                    movies.append({
                        "id": str(m["id"]),
                        "tmdb_id": m["id"],
                        "title": m.get("title", ""),
                        "year": int(m.get("release_date", "0000")[:4]) if m.get("release_date") else None,
                        "overview": m.get("overview", ""),
                        "genres": [g["name"] for g in detail.get("genres", [])],
                        "director": next(
                            (c["name"] for c in detail.get("credits", {}).get("crew", []) if c["job"] == "Director"),
                            ""
                        ),
                        "cast": [c["name"] for c in detail.get("credits", {}).get("cast", [])[:8]],
                        "poster_path": m.get("poster_path", ""),
                        "vote_average": m.get("vote_average", 0.0),
                        "popularity": m.get("popularity", 0.0),
                        "runtime": detail.get("runtime", 0),
                        "original_language": m.get("original_language", "en"),
                        "themes": [k["name"] for k in detail.get("keywords", {}).get("keywords", [])[:10]],
                    })

                if page % 10 == 0:
                    logger.info(f"Fetched {len(movies)} movies (page {page}/{pages})")

            except Exception as e:
                logger.warning(f"Failed page {page}: {e}")
                await asyncio.sleep(1)

    return movies


async def main(pages: int):
    logger.info(f"Starting Pinecone seed — fetching {pages * 20} movies from TMDB")

    if not settings.TMDB_API_KEY:
        logger.error("TMDB_API_KEY not set. Add it to your .env file.")
        return

    movies = await fetch_tmdb_movies(pages)
    logger.info(f"Fetched {len(movies)} movies total")

    # Index in batches of 50 (to stay within OpenAI rate limits)
    batch_size = 50
    total_indexed = 0
    for i in range(0, len(movies), batch_size):
        batch = movies[i:i + batch_size]
        result = await recommendation_engine.index_movies(batch)
        total_indexed += result["indexed"]
        logger.info(f"Progress: {total_indexed}/{len(movies)} indexed")

    logger.success(f"Done! {total_indexed} movies indexed in Pinecone.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=50, help="Number of TMDB pages (20 movies each)")
    args = parser.parse_args()
    asyncio.run(main(args.pages))

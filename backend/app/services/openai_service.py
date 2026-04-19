"""
AI service — 100% free stack:
  • Embeddings  → sentence-transformers (local, no API key, ~90 MB download)
  • LLM         → Groq API (free tier: llama-3.1-8b-instant, no credit card)

Groq free tier limits: 30 req/min · 6 000 tokens/min · 500 000 tokens/day
Sign up: https://console.groq.com → API Keys → Create Key
"""

from __future__ import annotations

import asyncio
import json
import re
from functools import lru_cache
from typing import Optional

import httpx
from loguru import logger

from app.core.config import settings


# ── Sentence-Transformers (lazy-loaded) ────────────────────────────────────

@lru_cache(maxsize=1)
def _load_model():
    from sentence_transformers import SentenceTransformer
    logger.info(f"Loading embedding model '{settings.EMBEDDING_MODEL}' on {settings.EMBEDDING_DEVICE}…")
    model = SentenceTransformer(settings.EMBEDDING_MODEL, device=settings.EMBEDDING_DEVICE)
    logger.info("Embedding model ready.")
    return model


def _embed_texts(texts: list[str]) -> list[list[float]]:
    model = _load_model()
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return [v.tolist() for v in vecs]


# ── Groq LLM client ────────────────────────────────────────────────────────

async def _groq_chat(prompt: str, temperature: float = 0.5) -> str:
    if not settings.GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY not set. Get a free key at https://console.groq.com"
        )
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{settings.GROQ_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": 1500,
            },
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


def _extract_json(text: str):
    text = re.sub(r"```(?:json)?", "", text).strip()
    for pattern in (r"(\[.*\])", r"(\{.*\})"):
        m = re.search(pattern, text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                pass
    raise ValueError(f"No valid JSON found:\n{text[:300]}")


# ── Public service (same interface as old OpenAIService) ───────────────────

class AIService:

    async def get_embedding(self, text: str) -> list[float]:
        clean = text.replace("\n", " ").strip()
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, _embed_texts, [clean])
        return results[0]

    async def get_batch_embeddings(self, texts: list[str]) -> list[list[float]]:
        cleaned = [t.replace("\n", " ").strip() for t in texts]
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _embed_texts, cleaned)

    async def parse_user_query(self, raw_query: str) -> dict:
        prompt = f"""You are a movie recommendation assistant.
Extract structured preference signals from this user input and return ONLY valid JSON.

User input: "{raw_query}"

Return JSON with these fields (omit fields you cannot confidently infer):
{{
  "enriched_query": "a semantically rich sentence describing what the user wants",
  "genres": [],
  "mood": "",
  "era": "",
  "themes": [],
  "similar_to": [],
  "avoid": [],
  "language": "",
  "runtime_preference": ""
}}

Return ONLY the JSON object, no explanation."""
        try:
            raw = await _groq_chat(prompt, temperature=0.2)
            parsed = _extract_json(raw)
            if not isinstance(parsed, dict):
                raise ValueError("Expected dict")
            if not parsed.get("enriched_query"):
                parsed["enriched_query"] = raw_query
            return parsed
        except Exception as e:
            logger.warning(f"Query parsing failed ({e}), using raw query")
            return {"enriched_query": raw_query, "genres": [], "mood": "", "themes": [], "era": ""}

    async def generate_recommendation_explanation(
        self,
        user_preferences: str,
        recommended_movies: list[dict],
        watch_history: Optional[list[str]] = None,
    ) -> list[dict]:
        history_line = ""
        if watch_history:
            history_line = f"Previously enjoyed IDs: {', '.join(watch_history[:8])}.\n"

        movies_summary = json.dumps(
            [{"title": m.get("title"), "year": m.get("year"),
              "genres": m.get("genres", []), "director": m.get("director", ""),
              "score": round(m.get("score", 0), 3)}
             for m in recommended_movies], indent=2)

        prompt = f"""You are CineMate, a knowledgeable film critic.

{history_line}User preference: "{user_preferences}"

Recommended films:
{movies_summary}

For EACH film write a 2-sentence personalized explanation of why it matches this user.
Be specific about genres/themes/directors. Sound like a film-loving friend.

Return ONLY a JSON array:
[{{"title": "Film Title", "explanation": "..."}}]

No extra text."""
        try:
            raw = await _groq_chat(prompt, temperature=0.6)
            items = _extract_json(raw)
            if not isinstance(items, list):
                items = []
        except Exception as e:
            logger.warning(f"Explanation generation failed ({e}), using fallbacks")
            items = []

        explanation_map: dict[str, str] = {}
        for item in items:
            if isinstance(item, dict) and "title" in item:
                explanation_map[item["title"].lower()] = item.get("explanation", "")

        enriched = []
        for movie in recommended_movies:
            key = movie.get("title", "").lower()
            fallback_genre = (movie.get("genres") or ["film"])[0]
            enriched.append({
                **movie,
                "explanation": explanation_map.get(
                    key,
                    f"A strong semantic match for your love of {fallback_genre} cinema.",
                ),
            })
        return enriched

    async def generate_movie_embedding_text(self, movie: dict) -> str:
        parts = [
            movie.get("title", ""),
            f"({movie.get('year')})" if movie.get("year") else "",
            f"Directed by {movie['director']}" if movie.get("director") else "",
            f"Genres: {', '.join(movie.get('genres', []))}" if movie.get("genres") else "",
            f"Starring: {', '.join(movie['cast'][:5])}" if movie.get("cast") else "",
            movie.get("overview", ""),
            f"Themes: {', '.join(movie['themes'])}" if movie.get("themes") else "",
            f"Mood: {movie['mood']}" if movie.get("mood") else "",
        ]
        return " | ".join(p for p in parts if p)


# Singleton — kept as openai_service for backward-compat with existing imports
openai_service = AIService()

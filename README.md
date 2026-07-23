# CineMate AI

A movie recommendation engine that combines semantic search, collaborative filtering, and LLM-generated explanations. Built this to actually understand what someone means by "something like Inception but not as confusing" rather than just matching keywords.

## What it uses

Everything here runs on free tiers, so you can clone it and have it working without pulling out a credit card:

- **sentence-transformers** (`all-MiniLM-L6-v2`) for embeddings, runs locally on CPU
- **Groq** for LLaMA-3.1-8B, used for both parsing queries and writing explanations
- **Pinecone** free starter tier as the vector index (handles 10K+ movies fine)
- **TMDB API** for movie metadata and posters
- **Redis** for caching so repeat queries come back fast

## How it works

A query comes in as plain English. Groq's LLaMA model pulls out the genres, mood, and themes from it. That gets embedded with sentence-transformers and searched against the Pinecone index using cosine similarity. Once we have candidates, we re-rank them based on the user's watch history to bias toward what they've actually liked before. Then Groq writes a short explanation for each pick, something like why it fits what they asked for. Redis caches the whole response so if someone runs a similar query again it comes back in under 200ms instead of round-tripping through two LLM calls.

\```
Query → Groq (parse intent) → embed locally → Pinecone search
      → re-rank by watch history → Groq (write explanations) → cache → frontend
\```

## Stack

Backend is FastAPI on Uvicorn. Frontend is React 18 with Zustand for state and TypeScript throughout. Everything's containerized with Docker Compose for local dev, and deploys to Cloud Run via GCP Cloud Build.

## Getting it running

You'll need three free API keys:

1. **Groq** — console.groq.com, sign up, grab a key from API Keys. No card needed.
2. **Pinecone** — app.pinecone.io, create a free serverless index.
3. **TMDB** — themoviedb.org/settings/api, this one's free indefinitely, not just a trial.

Then:

\```bash
git clone <repo> && cd cinemate
cp backend/.env.example backend/.env
# drop your three keys into .env
docker-compose up --build
\```

Frontend lands on `localhost:3000`, API docs are at `localhost:8000/docs`.

Before you can get recommendations, you need to seed the index:

\```bash
cd backend
pip install -r requirements.txt
python scripts/seed_pinecone.py --pages 50    # ~1K movies, a couple minutes
python scripts/seed_pinecone.py --pages 500   # ~10K movies, more like 15 min
\```

First run downloads the embedding model (~90MB), so that's a one-time wait.

## Using the API

The main endpoint is `POST /api/v1/recommendations/`. Send it a query, optionally a user ID and watch history for personalization, plus any filters:

\```json
{
  "query": "mind-bending sci-fi with unreliable narrators",
  "user_id": "user_abc123",
  "watch_history": ["tt0816692", "tt1375666"],
  "top_n": 10,
  "filters": {
    "genres": ["Science Fiction"],
    "year_min": 2000,
    "min_rating": 7.0
  }
}
\```

You get back a ranked list with similarity scores and a short LLM-written explanation for each one.

There's also `POST /api/v1/recommendations/similar` if you just want movies similar to a specific title, `GET /health` for checking the embedding model loaded correctly, and `GET /api/v1/stats` for Pinecone index stats.

## Switching embedding models

Default is `all-MiniLM-L6-v2` at 384 dimensions, which is fast and good enough for most cases. If you want better quality and don't mind the extra size (~420MB), swap to `all-mpnet-base-v2` at 768 dimensions in `.env`. One catch: if you change this after you've already seeded the index, you have to re-seed. The vector dimensions have to match or Pinecone will reject them.

## Deploying

\```bash
gcloud config set project YOUR_PROJECT_ID
echo -n "$GROQ_API_KEY" | gcloud secrets create groq-api-key --data-file=-
echo -n "$PINECONE_API_KEY" | gcloud secrets create pinecone-api-key --data-file=-
gcloud builds submit --config infrastructure/cloudbuild.yaml
\```

## Tests

\```bash
cd backend && pytest tests/ -v
\```

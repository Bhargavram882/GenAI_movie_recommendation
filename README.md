# CineMate AI — GenAI Movie Recommendation System

> Hybrid semantic search + collaborative filtering + LLM explanations  
> **100% free stack** — no OpenAI required

---

## Free Services Used

| Service | Purpose | Cost |
|---------|---------|------|
| `sentence-transformers` | Local embeddings (runs on your CPU) | **Free** |
| Groq API | LLaMA-3.1-8B for query parsing + explanations | **Free tier** |
| Pinecone | Vector index (10K+ movie vectors) | **Free starter** |
| TMDB API | Movie metadata + poster images | **Free forever** |
| Redis | Response caching | **Free (Docker)** |

---

## Architecture

```
User Query (natural language)
        │
        ▼
  Groq LLaMA-3.1        ← Extracts genres, mood, themes (free API)
        │
        ▼
  sentence-transformers  ← all-MiniLM-L6-v2, 384-dim (runs locally, free)
        │
        ▼
  Pinecone ANN Search    ← Cosine similarity over 10K+ movie vectors (free tier)
        │
        ▼
  CF Re-ranking          ← Boosts results matching user's watch history
        │
        ▼
  Groq LLaMA-3.1        ← Personalized "why you'll love it" explanations (free)
        │
        ▼
  Redis Cache            ← Sub-200ms on repeat queries
        │
        ▼
  React Frontend         ← Cinematic dark UI
```

---

## Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI + Uvicorn |
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` (local) |
| LLM | Groq free tier — LLaMA-3.1-8B-Instant |
| Vector DB | Pinecone serverless (free starter) |
| Cache | Redis |
| Frontend | React 18 + Zustand + TypeScript |
| Containers | Docker + Docker Compose |
| CI/CD | GCP Cloud Build → Cloud Run |
| Movie Data | TMDB API (free) |

---

## Quick Start

### 1. Get your free API keys (5 minutes)

| Key | Where to get it |
|-----|----------------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) → API Keys → Create (free, no card) |
| `PINECONE_API_KEY` | [app.pinecone.io](https://app.pinecone.io) → Create index (free starter) |
| `TMDB_API_KEY` | [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api) (free forever) |

### 2. Configure

```bash
git clone <repo> && cd cinemate
cp backend/.env.example backend/.env
# Fill in your 3 free API keys
```

### 3. Run

```bash
docker-compose up --build
```

- Frontend → http://localhost:3000  
- API docs → http://localhost:8000/docs

### 4. Seed movies into Pinecone

```bash
# First time only — downloads ~90MB embedding model, then indexes movies
cd backend
pip install -r requirements.txt
python scripts/seed_pinecone.py --pages 50    # ~1K movies, fast
python scripts/seed_pinecone.py --pages 500   # ~10K movies, ~15 min
```

---

## API

### `POST /api/v1/recommendations/`

```json
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
```

Returns movies with similarity scores + LLaMA-generated personalized explanations.

### `POST /api/v1/recommendations/similar` — find movies similar to a given ID  
### `GET /health` — service health + embedding model status  
### `GET /api/v1/stats` — Pinecone index stats  

---

## Swap embedding model (optional)

Edit `backend/.env`:

```bash
# Faster, smaller (default)
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSIONS=384

# Better quality, larger (~420 MB)
EMBEDDING_MODEL=all-mpnet-base-v2
EMBEDDING_DIMENSIONS=768
```

> If you change the model after seeding, re-run the seed script — vectors must match dimensions.

---

## Deploy to GCP

```bash
gcloud config set project YOUR_PROJECT_ID
echo -n "$GROQ_API_KEY" | gcloud secrets create groq-api-key --data-file=-
echo -n "$PINECONE_API_KEY" | gcloud secrets create pinecone-api-key --data-file=-
gcloud builds submit --config infrastructure/cloudbuild.yaml
```

---

## Testing

```bash
cd backend && pytest tests/ -v
```

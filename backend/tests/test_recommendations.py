"""
Integration tests for the CineMate AI recommendation API.
Run with: pytest tests/ -v
"""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
import sys
sys.path.insert(0, '.')


@pytest.fixture
def mock_openai():
    with patch('app.services.openai_service.AsyncOpenAI') as mock:
        client = MagicMock()
        mock.return_value = client
        # Mock embedding
        embedding_resp = MagicMock()
        embedding_resp.data = [MagicMock(embedding=[0.1] * 1536, index=0)]
        client.embeddings.create = AsyncMock(return_value=embedding_resp)
        # Mock chat
        chat_resp = MagicMock()
        chat_resp.choices = [MagicMock(message=MagicMock(content='{"enriched_query": "test", "genres": ["Drama"]}'))]
        client.chat.completions.create = AsyncMock(return_value=chat_resp)
        yield client


@pytest.fixture
def mock_pinecone():
    with patch('app.services.pinecone_service.Pinecone') as mock:
        pc = MagicMock()
        mock.return_value = pc
        pc.list_indexes.return_value = [MagicMock(name='cinemate-movies')]
        index = MagicMock()
        pc.Index.return_value = index
        index.describe_index_stats.return_value = MagicMock(
            total_vector_count=10000, dimension=1536, namespaces={}
        )
        index.query.return_value = MagicMock(matches=[
            MagicMock(id='tt0816692', score=0.92, metadata={
                'title': 'Interstellar', 'year': 2014,
                'genres': ['Science Fiction', 'Drama'],
                'director': 'Christopher Nolan',
                'overview': 'A team of explorers travel through a wormhole.',
                'vote_average': 8.6, 'popularity': 95.0,
                'cast': ['Matthew McConaughey', 'Anne Hathaway'],
                'poster_path': '/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg',
                'runtime': 169, 'language': 'en',
            })
        ])
        yield index


@pytest.fixture
def mock_redis():
    with patch('app.services.cache_service.redis') as mock:
        client = AsyncMock()
        mock.from_url.return_value = client
        client.get = AsyncMock(return_value=None)
        client.setex = AsyncMock(return_value=True)
        client.ping = AsyncMock(return_value=True)
        yield client


@pytest.mark.asyncio
async def test_health_endpoint(mock_pinecone, mock_redis):
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        resp = await client.get('/health')
        assert resp.status_code == 200
        data = resp.json()
        assert 'status' in data
        assert 'version' in data


@pytest.mark.asyncio
async def test_recommendations_endpoint(mock_openai, mock_pinecone, mock_redis):
    with patch('app.services.openai_service.openai_service.generate_recommendation_explanation',
               new_callable=AsyncMock) as mock_explain:
        mock_explain.return_value = [{
            'id': 'tt0816692', 'title': 'Interstellar', 'year': 2014,
            'genres': ['Science Fiction', 'Drama'], 'director': 'Christopher Nolan',
            'cast': ['Matthew McConaughey'], 'overview': 'Space film.',
            'poster_path': '/poster.jpg', 'vote_average': 8.6,
            'popularity': 95.0, 'runtime': 169, 'score': 0.92, 'language': 'en',
            'explanation': 'This cerebral sci-fi epic will resonate deeply with you.',
        }]

        from app.main import app
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            resp = await client.post('/api/v1/recommendations/', json={
                'query': 'mind-bending space exploration films',
                'top_n': 5,
            })
            assert resp.status_code == 200
            data = resp.json()
            assert 'recommendations' in data
            assert 'query_analysis' in data
            assert data['total'] >= 0


@pytest.mark.asyncio
async def test_recommendations_validation():
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        # Query too short
        resp = await client.post('/api/v1/recommendations/', json={'query': 'hi'})
        assert resp.status_code == 422

        # Missing query
        resp = await client.post('/api/v1/recommendations/', json={})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_stats_endpoint(mock_pinecone, mock_redis):
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        resp = await client.get('/api/v1/stats')
        assert resp.status_code == 200
        data = resp.json()
        assert 'total_indexed_movies' in data
        assert 'pinecone_stats' in data

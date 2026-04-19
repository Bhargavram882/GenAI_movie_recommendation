"""
Pinecone vector store service for semantic movie retrieval.
Manages the index, upserts, and similarity search operations.
"""
from typing import Optional
from loguru import logger
from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings


class PineconeService:
    def __init__(self):
        self.pc: Optional[Pinecone] = None
        self.index = None
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
        try:
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            existing = [idx.name for idx in self.pc.list_indexes()]
            if settings.PINECONE_INDEX_NAME not in existing:
                logger.info(f"Creating Pinecone index: {settings.PINECONE_INDEX_NAME}")
                self.pc.create_index(
                    name=settings.PINECONE_INDEX_NAME,
                    dimension=settings.EMBEDDING_DIMENSIONS,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.PINECONE_ENVIRONMENT,
                    ),
                )
            self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
            stats = self.index.describe_index_stats()
            logger.info(
                f"Pinecone index ready. Total vectors: {stats.total_vector_count}"
            )
            self._initialized = True
        except Exception as e:
            logger.error(f"Pinecone init failed: {e}")
            raise

    async def upsert_movies(self, vectors: list[dict]) -> int:
        """Batch upsert movie vectors into Pinecone."""
        if not self._initialized:
            await self.initialize()
        batch_size = 100
        total_upserted = 0
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i : i + batch_size]
            self.index.upsert(
                vectors=batch,
                namespace=settings.PINECONE_NAMESPACE,
            )
            total_upserted += len(batch)
        logger.info(f"Upserted {total_upserted} movie vectors")
        return total_upserted

    async def query_similar(
        self,
        query_vector: list[float],
        top_k: int = 20,
        filter_dict: Optional[dict] = None,
        include_metadata: bool = True,
    ) -> list[dict]:
        """Query Pinecone for similar movies by embedding vector."""
        if not self._initialized:
            await self.initialize()
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            namespace=settings.PINECONE_NAMESPACE,
            filter=filter_dict,
            include_metadata=include_metadata,
            include_values=False,
        )
        matches = []
        for match in results.matches:
    # Note: with 384-dim MiniLM, cosine scores are typically 0.2–0.8
            if match.score >= settings.MIN_SIMILARITY_SCORE:
               matches.append(
                   {
                       "id": match.id,
                       "score": match.score,
                       "metadata": match.metadata or {}, 
                   }
                )
        return matches


    async def fetch_by_ids(self, ids: list[str]) -> dict:
        """Fetch specific movie vectors by IDs."""
        if not self._initialized:
            await self.initialize()
        result = self.index.fetch(ids=ids, namespace=settings.PINECONE_NAMESPACE)
        return result.vectors

    async def get_stats(self) -> dict:
        if not self._initialized:
            await self.initialize()
        stats = self.index.describe_index_stats()
        return {
            "total_vectors": stats.total_vector_count,
            "dimension": stats.dimension,
            "namespaces": {
                ns: data.vector_count
                for ns, data in (stats.namespaces or {}).items()
            },
        }

    async def delete_movie(self, movie_id: str):
        if not self._initialized:
            await self.initialize()
        self.index.delete(ids=[movie_id], namespace=settings.PINECONE_NAMESPACE)


pinecone_service = PineconeService()

import os
import uuid
import chromadb
from loguru import logger

from jarvis.config import settings


class LongTermMemory:
    def __init__(self, persist_directory: str = "data/chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self._init_db()

    def _init_db(self):
        os.makedirs(self.persist_directory, exist_ok=True)
        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(
                name="jarvis_memory",
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(f"ChromaDB initialized: {self.collection.count()} memories stored")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def add_memory(self, text: str, metadata: dict | None = None):
        if self.collection is None:
            logger.error("ChromaDB not initialized")
            return

        try:
            doc_id = str(uuid.uuid4())
            meta = metadata or {}
            meta["id"] = doc_id
            self.collection.add(
                documents=[text],
                ids=[doc_id],
                metadatas=[meta],
            )
            logger.info(f"Long-term memory added: '{text[:80]}...'")
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")

    def query(self, query_text: str, n_results: int = 5) -> list[dict]:
        if self.collection is None:
            logger.error("ChromaDB not initialized")
            return []

        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=min(n_results, self.collection.count()),
            )
            memories = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    memories.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else None,
                    })
            return memories
        except Exception as e:
            logger.error(f"Failed to query memory: {e}")
            return []

    def get_all_memories(self, limit: int = 50) -> list[dict]:
        if self.collection is None:
            return []

        try:
            count = min(limit, self.collection.count())
            if count == 0:
                return []
            results = self.collection.get(limit=count)
            memories = []
            for i, doc in enumerate(results["documents"]):
                memories.append({
                    "content": doc,
                    "metadata": results["metadatas"][i] if results["metadatas"] else {},
                })
            return memories
        except Exception as e:
            logger.error(f"Failed to get all memories: {e}")
            return []

    @property
    def memory_count(self) -> int:
        if self.collection is None:
            return 0
        return self.collection.count()

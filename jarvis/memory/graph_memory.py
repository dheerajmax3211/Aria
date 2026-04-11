import threading
from loguru import logger
from mem0 import Memory

from jarvis.config import settings


class GraphMemoryAgent:
    def __init__(self):
        self.m = None
        if not settings.gemini_api_key:
            logger.warning("Gemini API Key missing, Graph Memory degraded to pass-through.")
            return
            
        config = {
            "llm": {
                "provider": "gemini",
                "config": {
                    "api_key": settings.gemini_api_key,
                    "model": settings.fast_cloud_model
                }
            },
            "embedder": {
                "provider": "gemini",
                "config": {
                    "api_key": settings.gemini_api_key,
                    "model": "text-embedding-004"
                }
            },
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": "mem0_entities",
                    "path": "data/mem0_db"
                }
            }
        }
        
        try:
            self.m = Memory.from_config(config)
            logger.info("Mem0 Temporal Memory initialized (Gemini Engine)")
        except Exception as e:
            logger.error(f"Mem0 init failed (Make sure chronadb/mem0 are correctly installed): {e}")
            
    def store_background(self, text: str, user_id: str = "aria_user"):
        """Stores conversation logs or tasks asynchronously into the Knowledge Graph."""
        if not self.m: 
            return
            
        def _job():
            try:
                self.m.add(text, user_id=user_id)
                logger.info("Mem0 knowledge graph silently encoded via Gemini Flash.")
            except Exception as e:
                logger.error(f"Mem0 graph sync failed: {e}")
        
        t = threading.Thread(target=_job, daemon=True)
        t.start()
        
    def recall_timeline(self, query: str) -> str:
        """Query the knowledge graph for temporal histories (e.g. 'What did I do at 3 PM?')."""
        if not self.m: 
            return "Knowledge graph is offline."
            
        try:
            results = self.m.search(query, user_id="aria_user", limit=10)
            
            # Mem0 result structure parses the text/graph metadata
            memories = []
            for res in results:
                # Based on mem0 dict format: could be 'memory' or 'text'
                text_content = res.get("memory", res.get("text", str(res)))
                memories.append(text_content)
                
            return "\n".join(memories) if memories else "No specific graph memories match this timeline."
            
        except Exception as e:
            logger.error(f"Mem0 recall failed: {e}")
            return f"Failed to access temporal memory: {e}"

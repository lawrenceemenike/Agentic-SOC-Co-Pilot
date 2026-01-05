import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, persist_directory: Optional[str] = "./chroma_data", client: Optional[chromadb.ClientAPI] = None):
        if client:
            self.client = client
        elif persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            # Ephemeral client for testing
            self.client = chromadb.Client(Settings(allow_reset=True))
            
        self.collection = self.client.get_or_create_collection("soc_knowledge")
        # Source allowlist - in production this might be in a config file or DB
        self.allowed_sources = {"playbook-ssh", "playbook-phishing", "policy-access-control"}

    def add_document(self, doc_id: str, content: str, metadata: Dict[str, Any]):
        """
        Adds a document to the store.
        """
        # Ensure source is allowed (simple check on doc_id prefix or metadata)
        source = metadata.get("source", "unknown")
        if source not in self.allowed_sources:
            logger.warning(f"Blocked addition of document from unauthorized source: {source}")
            raise ValueError(f"Source {source} is not in the allowlist")

        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def query(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves documents relevant to the query.
        Returns a list of results with metadata and scores.
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results["ids"]:
            for i in range(len(results["ids"][0])):
                metadata = results["metadatas"][0][i]
                # Double check allowlist on retrieval (defense in depth)
                if metadata.get("source") not in self.allowed_sources:
                    continue
                    
                formatted_results.append({
                    "doc_id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": metadata,
                    "score": results["distances"][0][i] if results["distances"] else 0.0
                })
        
        return formatted_results

    def reset(self):
        """
        Resets the database. For testing purposes only.
        """
        self.client.reset()
        self.collection = self.client.get_or_create_collection("soc_knowledge")

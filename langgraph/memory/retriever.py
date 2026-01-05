from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
from langgraph.memory.vector_store import VectorStore
import logging

logger = logging.getLogger(__name__)

class HybridRetriever:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        # In a real system, we'd maintain a corpus for BM25. 
        # For MVP, we might fetch all docs or maintain a separate index.
        # Here we assume we can fetch a small corpus or build it on the fly (inefficient for large scale).
        # Let's assume we have a way to get documents for BM25.
        self.documents = [] # List of text
        self.doc_ids = []
        self.bm25 = None

    def index_documents(self, documents: List[str], doc_ids: List[str]):
        """
        Updates the BM25 index.
        """
        self.documents = documents
        self.doc_ids = doc_ids
        tokenized_corpus = [doc.split(" ") for doc in documents]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def retrieve(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Hybrid retrieval using RRF (Reciprocal Rank Fusion).
        """
        # 1. Vector Search
        vector_results = self.vector_store.query(query, n_results=k)
        
        # 2. Keyword Search (BM25)
        bm25_results = []
        if self.bm25:
            tokenized_query = query.split(" ")
            doc_scores = self.bm25.get_scores(tokenized_query)
            # Get top k indices
            top_n = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:k]
            for i in top_n:
                bm25_results.append({
                    "doc_id": self.doc_ids[i],
                    "score": doc_scores[i],
                    "content": self.documents[i]
                })

        # 3. RRF Fusion
        # Simple RRF: score = 1 / (rank + 60)
        fusion_scores = {}
        
        for rank, res in enumerate(vector_results):
            doc_id = res["doc_id"]
            if doc_id not in fusion_scores:
                fusion_scores[doc_id] = {"score": 0, "content": res["content"], "metadata": res["metadata"]}
            fusion_scores[doc_id]["score"] += 1 / (rank + 60)
            
        for rank, res in enumerate(bm25_results):
            doc_id = res["doc_id"]
            if doc_id not in fusion_scores:
                # We might miss metadata if it's only in BM25 results (need a lookup)
                # For MVP, we skip or assume we have it.
                continue 
            fusion_scores[doc_id]["score"] += 1 / (rank + 60)
            
        # Sort by fusion score
        sorted_results = sorted(fusion_scores.values(), key=lambda x: x["score"], reverse=True)
        return sorted_results[:k]

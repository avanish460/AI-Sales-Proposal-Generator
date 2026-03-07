"""
rag_engine.py  —  FAISS Vector Store + Embedding Engine
Handles: Embed text → Store in FAISS → Similarity search
"""

import os
import pickle
import numpy as np
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

try:
    import faiss
    from sentence_transformers import SentenceTransformer
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("[WARNING] Run: pip install faiss-cpu sentence-transformers")

# ── Config from .env ──────────────────────────────────────────────────────────
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
EMBED_DIM   = 384
INDEX_PATH  = os.getenv("FAISS_INDEX_PATH", "data/faiss.index")
STORE_PATH  = os.getenv("PROPOSAL_STORE_PATH", "data/proposal_store.pkl")
TOP_K       = int(os.getenv("RAG_TOP_K", 3))


class RAGEngine:
    """
    FAISS-powered vector store for proposal retrieval.

    Usage:
        engine = RAGEngine()
        engine.add_proposal(text, metadata)
        results = engine.search("healthcare AI startup", k=2)
    """

    def __init__(self):
        if not RAG_AVAILABLE:
            raise ImportError("Install: pip install faiss-cpu sentence-transformers")

        self.index_path = Path(INDEX_PATH)
        self.store_path = Path(STORE_PATH)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)

        print("[RAG] Loading embedding model...")
        self.model = SentenceTransformer(EMBED_MODEL)

        if self.index_path.exists() and self.store_path.exists():
            print("[RAG] Loading existing FAISS index...")
            self.index = faiss.read_index(str(self.index_path))
            with open(self.store_path, "rb") as f:
                self.store = pickle.load(f)
        else:
            print("[RAG] Creating fresh FAISS index...")
            self.index = faiss.IndexFlatL2(EMBED_DIM)
            self.store = []

        print(f"[RAG] Ready — {len(self.store)} proposals indexed.")

    # ── Embed ─────────────────────────────────────────────────────────────────
    def _embed(self, text: str) -> np.ndarray:
        return self.model.encode(
            [text], convert_to_numpy=True, normalize_embeddings=True
        ).astype("float32")

    # ── Add ───────────────────────────────────────────────────────────────────
    def add_proposal(self, text: str, metadata: Optional[dict] = None) -> int:
        """Embed and store a proposal. Returns its index ID."""
        vec = self._embed(text)
        self.index.add(vec)
        self.store.append({"text": text, "metadata": metadata or {}})
        self._persist()
        idx = len(self.store) - 1
        print(f"[RAG] Stored #{idx} | {metadata}")
        return idx

    # ── Search ────────────────────────────────────────────────────────────────
    def search(self, query: str, k: int = TOP_K,
               filters: Optional[dict] = None) -> list:
        """Return top-k similar proposals with optional metadata filters."""
        if not self.store:
            return []

        k_fetch = min(k * 4, len(self.store))
        k       = min(k, len(self.store))
        qvec    = self._embed(query)
        distances, indices = self.index.search(qvec, k_fetch)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            entry = self.store[idx]
            meta  = entry["metadata"]

            # Optional filtering
            if filters:
                skip = False
                if "industry" in filters:
                    if meta.get("industry", "").lower() != filters["industry"].lower():
                        skip = True
                if "budget_min" in filters and meta.get("budget", 0) < filters["budget_min"]:
                    skip = True
                if "budget_max" in filters and meta.get("budget", 0) > filters["budget_max"]:
                    skip = True
                if skip:
                    continue

            results.append({
                "rank":     len(results) + 1,
                "score":    round(float(1 / (1 + dist)), 3),
                "text":     entry["text"],
                "metadata": meta,
            })
            if len(results) == k:
                break

        return results

    # ── Persist ───────────────────────────────────────────────────────────────
    def _persist(self):
        faiss.write_index(self.index, str(self.index_path))
        with open(self.store_path, "wb") as f:
            pickle.dump(self.store, f)

    def stats(self) -> dict:
        return {
            "total_proposals": len(self.store),
            "embed_model":     EMBED_MODEL,
            "embed_dim":       EMBED_DIM,
            "index_type":      type(self.index).__name__,
        }

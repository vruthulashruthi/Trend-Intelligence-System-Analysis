import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.config import EMBEDDING_MODEL
from backend import database

logger = logging.getLogger(__name__)


class EmbeddingAgent:
    def __init__(self):
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading sentence-transformer model...")
            self._model = SentenceTransformer(EMBEDDING_MODEL)
        return self._model

    def embed_papers(self) -> int:
        papers = database.get_relevant_papers()
        to_embed = [p for p in papers if p["embedding"] is None]
        if not to_embed:
            logger.info("EmbeddingAgent: All papers already embedded")
            return 0
        model = self._get_model()
        texts = [p["title"] + " " + p["abstract"] for p in to_embed]
        logger.info("EmbeddingAgent: Embedding %d papers...", len(texts))
        embeddings = model.encode(texts, batch_size=32, show_progress_bar=False)
        for paper, emb in zip(to_embed, embeddings):
            database.update_paper_embedding(paper["id"], emb.tolist())
        logger.info("EmbeddingAgent: Embedded %d papers", len(to_embed))
        return len(to_embed)

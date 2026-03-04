import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.config import SENTIMENT_MODEL
from backend import database

logger = logging.getLogger(__name__)


class SentimentAgent:
    def __init__(self):
        self._pipeline = None

    def _get_pipeline(self):
        if self._pipeline is None:
            from transformers import pipeline as hf_pipeline
            logger.info("Loading sentiment model...")
            self._pipeline = hf_pipeline(
                "sentiment-analysis",
                model=SENTIMENT_MODEL,
                device=-1,
                truncation=True,
                max_length=512,
            )
        return self._pipeline

    def analyze_sentiment(self, run_id: str) -> dict:
        topics = database.get_topics_for_run(run_id)
        if not topics:
            return {}
        all_papers = database.get_relevant_papers()
        papers_by_topic = {}
        for paper in all_papers:
            tid = paper["topic_id"]
            if tid not in papers_by_topic:
                papers_by_topic[tid] = []
            papers_by_topic[tid].append(paper)
        pipe = self._get_pipeline()
        results = {}
        for topic in topics:
            tid = topic["topic_id"]
            topic_papers = papers_by_topic.get(tid, [])
            if not topic_papers:
                continue
            texts = [p["title"][:200] for p in topic_papers[:10]]
            try:
                sentiments = pipe(texts)
                pos = sum(1 for s in sentiments if s["label"] == "POSITIVE")
                neg = sum(1 for s in sentiments if s["label"] == "NEGATIVE")
                avg_score = sum(s["score"] for s in sentiments) / len(sentiments)
                dominant = "POSITIVE" if pos >= neg else "NEGATIVE"
                database.update_topic_sentiment(run_id, tid, dominant, float(avg_score))
                results[topic["label"]] = {"label": dominant, "score": round(avg_score, 3)}
            except Exception as e:
                logger.warning("Sentiment failed for topic %d: %s", tid, e)
        logger.info("SentimentAgent: Analyzed %d topics", len(results))
        return results

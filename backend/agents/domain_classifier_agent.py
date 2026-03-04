import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.config import CLASSIFIER_MODEL, DOMAIN_LABELS, DOMAIN_THRESHOLD
from backend import database

logger = logging.getLogger(__name__)


class DomainClassifierAgent:
    def __init__(self):
        self._pipeline = None

    def _get_pipeline(self):
        if self._pipeline is None:
            from transformers import pipeline as hf_pipeline
            logger.info("Loading zero-shot classification model...")
            self._pipeline = hf_pipeline(
                "zero-shot-classification",
                model=CLASSIFIER_MODEL,
                device=-1,
            )
        return self._pipeline

    def classify_papers(self) -> int:
        papers = database.get_all_papers()
        unclassified = [
            p for p in papers
            if p["is_relevant"] == 0 and p["domain_score"] == 0.0
        ]
        if not unclassified:
            logger.info("DomainClassifierAgent: No new papers to classify")
            return 0
        pipe = self._get_pipeline()
        classified = 0
        for paper in unclassified:
            text = paper["title"] + ". " + paper["abstract"][:300]
            try:
                result = pipe(text, DOMAIN_LABELS, multi_label=False)
                top_label = result["labels"][0]
                top_score = result["scores"][0]
                is_rel = (top_label == DOMAIN_LABELS[0] and top_score >= DOMAIN_THRESHOLD)
                database.update_paper_relevance(paper["id"], is_rel, float(top_score))
                classified += 1
            except Exception as e:
                logger.warning("Classification failed: %s", e)
        logger.info("DomainClassifierAgent: %d classified", classified)
        return classified

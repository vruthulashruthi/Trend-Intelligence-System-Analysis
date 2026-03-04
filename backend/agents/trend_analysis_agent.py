import logging
import sys
import os
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend import database

logger = logging.getLogger(__name__)


def _similarity(a: str, b: str) -> float:
    a_words = set(a.lower().split(" / "))
    b_words = set(b.lower().split(" / "))
    if not a_words or not b_words:
        return 0.0
    intersection = a_words & b_words
    union = a_words | b_words
    return len(intersection) / len(union)


def _find_best_match(label: str, previous_counts: dict, threshold: float = 0.4):
    best_label = None
    best_score = 0.0
    for prev_label in previous_counts:
        score = _similarity(label, prev_label)
        if score > best_score:
            best_score = score
            best_label = prev_label
    if best_score >= threshold:
        return best_label, best_score
    return None, 0.0


class TrendAnalysisAgent:
    def analyze_trends(self, run_id):
        current_topics = database.get_topics_for_run(run_id)
        if not current_topics:
            logger.warning("TrendAnalysisAgent: No topics for current run")
            return []

        # Get the most recent previous run (not the current one)
        conn = database.get_connection()
        prev_run = conn.execute(
            "SELECT id FROM trend_runs ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        conn.close()

        previous_counts = {}
        if prev_run:
            prev_topics = database.get_topics_for_run(prev_run["id"])
            for t in prev_topics:
                previous_counts[t["label"]] = t["paper_count"]

        results = []
        for topic in current_topics:
            label = topic["label"]
            count = topic["paper_count"]

            matched_label, score = _find_best_match(label, previous_counts)
            prev = previous_counts.get(matched_label, 0) if matched_label else 0

            if prev > 0:
                growth = ((count - prev) / prev) * 100.0
            else:
                growth = 0.0

            logger.info("Topic '%s' matched to '%s' (score=%.2f), prev=%d, now=%d, growth=%.1f%%",
                        label, matched_label, score, prev, count, growth)

            database.insert_topic_trend(label, run_id, count, growth)
            results.append({
                "label": label,
                "paper_count": count,
                "growth_rate": round(growth, 2),
                "keywords": topic["keywords"],
            })

        results.sort(key=lambda x: (x["paper_count"], x["growth_rate"]), reverse=True)
        top5 = results[:5]
        if top5:
            logger.info("TrendAnalysisAgent: Top trend: %s", top5[0]["label"])
        return top5
import logging
import uuid
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend import database
from backend.agents.data_ingestion_agent import DataIngestionAgent
from backend.agents.domain_classifier_agent import DomainClassifierAgent
from backend.agents.embedding_agent import EmbeddingAgent
from backend.agents.topic_model_agent import TopicModelAgent
from backend.agents.trend_analysis_agent import TrendAnalysisAgent
from backend.agents.sentiment_agent import SentimentAgent
from backend.agents.scheduler_agent import SchedulerAgent

logger = logging.getLogger(__name__)

_ingestion_agent = DataIngestionAgent()
_classifier_agent = DomainClassifierAgent()
_embedding_agent = EmbeddingAgent()
_topic_agent = TopicModelAgent()
_trend_agent = TrendAnalysisAgent()
_sentiment_agent = SentimentAgent()
_scheduler_agent = None


def run_pipeline():
    run_id = str(uuid.uuid4())
    logger.info("========== Pipeline Run Started: %s ==========", run_id)

    try:
        fetched = _ingestion_agent.fetch_papers()
        logger.info("Step 1 - Ingestion: %d papers fetched", fetched)

        classified = _classifier_agent.classify_papers()
        logger.info("Step 2 - Classification: %d papers classified", classified)

        embedded = _embedding_agent.embed_papers()
        logger.info("Step 3 - Embedding: %d papers embedded", embedded)

        topic_count = _topic_agent.run_topic_modeling(run_id)
        logger.info("Step 4 - Topic Modeling: %d topics found", topic_count)

        if topic_count > 0:
            trends = _trend_agent.analyze_trends(run_id)
            logger.info("Step 5 - Trend Analysis: %d trending topics", len(trends))

            sentiment_results = _sentiment_agent.analyze_sentiment(run_id)
            logger.info("Step 6 - Sentiment: %d topics analyzed", len(sentiment_results))

            papers = database.get_relevant_papers()
            database.insert_trend_run(run_id, len(papers), topic_count)
            logger.info("Pipeline complete. Run ID: %s", run_id)
            return {"run_id": run_id, "topics": topic_count, "trends": trends}
        else:
            papers = database.get_relevant_papers()
            database.insert_trend_run(run_id, len(papers), 0)
            logger.warning("Pipeline complete but no topics generated.")
            return {"run_id": run_id, "topics": 0, "trends": []}

    except Exception as e:
        logger.error("Pipeline failed: %s", e, exc_info=True)
        return {"run_id": run_id, "error": str(e)}


def start_scheduler():
    global _scheduler_agent
    _scheduler_agent = SchedulerAgent(run_pipeline)
    _scheduler_agent.start()


def stop_scheduler():
    global _scheduler_agent
    if _scheduler_agent:
        _scheduler_agent.stop()

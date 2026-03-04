import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.config import SCHEDULER_INTERVAL_MINUTES

logger = logging.getLogger(__name__)


class SchedulerAgent:
    def __init__(self, pipeline_fn):
        self.pipeline_fn = pipeline_fn
        self._scheduler = None

    def start(self):
        from apscheduler.schedulers.background import BackgroundScheduler
        self._scheduler = BackgroundScheduler()
        self._scheduler.add_job(
            self.pipeline_fn,
            trigger="interval",
            minutes=SCHEDULER_INTERVAL_MINUTES,
            id="pipeline_job",
            max_instances=1,
            coalesce=True,
        )
        self._scheduler.start()
        logger.info(
            "SchedulerAgent: Pipeline scheduled every %d minutes",
            SCHEDULER_INTERVAL_MINUTES,
        )

    def stop(self):
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("SchedulerAgent: Stopped")

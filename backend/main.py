import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend import database
from backend.scheduler import run_pipeline, start_scheduler, stop_scheduler
from backend.config import FASTAPI_HOST, FASTAPI_PORT

app = FastAPI(title="Trend Intelligence API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def startup_event():
    database.init_db()
    logger.info("Database initialized. Running initial pipeline...")
    run_pipeline()
    start_scheduler()
    logger.info("Scheduler started - pipeline runs every 30 minutes")


@app.on_event("shutdown")
def shutdown_event():
    stop_scheduler()


@app.get("/")
def root():
    return {"status": "ok", "service": "Trend Intelligence System"}


@app.get("/api/run-pipeline")
def trigger_pipeline():
    return run_pipeline()


@app.get("/api/latest-run")
def get_latest_run():
    return database.get_latest_run() or {}


@app.get("/api/topics")
def get_topics(limit: int = 20):
    import json
    topics = database.get_latest_topics(limit=limit)
    for t in topics:
        if isinstance(t.get("keywords"), str):
            try:
                t["keywords"] = json.loads(t["keywords"])
            except Exception:
                t["keywords"] = []
    return topics


@app.get("/api/trends")
def get_trends():
    return database.get_topic_trends()


@app.get("/api/papers")
def get_papers(limit: int = 50):
    return database.get_relevant_papers()[:limit]


@app.get("/api/stats")
def get_stats():
    all_papers = database.get_all_papers()
    relevant = [p for p in all_papers if p["is_relevant"] == 1]
    return {
        "total_papers": len(all_papers),
        "relevant_papers": len(relevant),
        "latest_run": database.get_latest_run(),
        "topic_count": len(database.get_latest_topics(limit=100)),
    }


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host=FASTAPI_HOST, port=FASTAPI_PORT, reload=False)

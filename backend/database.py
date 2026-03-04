import sqlite3
import json
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "CREATE TABLE IF NOT EXISTS papers ("
        "id TEXT PRIMARY KEY, title TEXT NOT NULL, abstract TEXT NOT NULL, "
        "published TEXT NOT NULL, fetched_at TEXT NOT NULL, "
        "is_relevant INTEGER DEFAULT 0, domain_score REAL DEFAULT 0.0, "
        "embedding TEXT, topic_id INTEGER DEFAULT -1)"
    )
    c.execute(
        "CREATE TABLE IF NOT EXISTS topics ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, "
        "topic_id INTEGER NOT NULL, label TEXT NOT NULL, keywords TEXT NOT NULL, "
        "paper_count INTEGER DEFAULT 0, sentiment_label TEXT DEFAULT 'NEUTRAL', "
        "sentiment_score REAL DEFAULT 0.0, created_at TEXT NOT NULL)"
    )
    c.execute(
        "CREATE TABLE IF NOT EXISTS trend_runs ("
        "id TEXT PRIMARY KEY, created_at TEXT NOT NULL, "
        "paper_count INTEGER DEFAULT 0, topic_count INTEGER DEFAULT 0)"
    )
    c.execute(
        "CREATE TABLE IF NOT EXISTS topic_trends ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, topic_label TEXT NOT NULL, "
        "run_id TEXT NOT NULL, paper_count INTEGER DEFAULT 0, "
        "growth_rate REAL DEFAULT 0.0, recorded_at TEXT NOT NULL)"
    )
    conn.commit()
    conn.close()


def insert_paper(paper: dict):
    conn = get_connection()
    conn.execute(
        "INSERT OR IGNORE INTO papers (id, title, abstract, published, fetched_at) "
        "VALUES (:id, :title, :abstract, :published, :fetched_at)",
        paper,
    )
    conn.commit()
    conn.close()


def update_paper_relevance(paper_id: str, is_relevant: bool, domain_score: float):
    conn = get_connection()
    conn.execute(
        "UPDATE papers SET is_relevant=?, domain_score=? WHERE id=?",
        (1 if is_relevant else 0, domain_score, paper_id),
    )
    conn.commit()
    conn.close()


def update_paper_embedding(paper_id: str, embedding: list):
    conn = get_connection()
    conn.execute(
        "UPDATE papers SET embedding=? WHERE id=?",
        (json.dumps(embedding), paper_id),
    )
    conn.commit()
    conn.close()


def update_paper_topic(paper_id: str, topic_id: int):
    conn = get_connection()
    conn.execute("UPDATE papers SET topic_id=? WHERE id=?", (topic_id, paper_id))
    conn.commit()
    conn.close()


def get_relevant_papers():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM papers WHERE is_relevant=1").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_papers():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM papers").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def insert_topic(run_id: str, topic_id: int, label: str, keywords: list, paper_count: int):
    conn = get_connection()
    conn.execute(
        "INSERT INTO topics (run_id, topic_id, label, keywords, paper_count, created_at) "
        "VALUES (?,?,?,?,?,?)",
        (run_id, topic_id, label, json.dumps(keywords), paper_count, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def update_topic_sentiment(run_id: str, topic_id: int, sentiment_label: str, sentiment_score: float):
    conn = get_connection()
    conn.execute(
        "UPDATE topics SET sentiment_label=?, sentiment_score=? WHERE run_id=? AND topic_id=?",
        (sentiment_label, sentiment_score, run_id, topic_id),
    )
    conn.commit()
    conn.close()


def insert_trend_run(run_id: str, paper_count: int, topic_count: int):
    conn = get_connection()
    conn.execute(
        "INSERT INTO trend_runs (id, created_at, paper_count, topic_count) VALUES (?,?,?,?)",
        (run_id, datetime.utcnow().isoformat(), paper_count, topic_count),
    )
    conn.commit()
    conn.close()


def insert_topic_trend(topic_label: str, run_id: str, paper_count: int, growth_rate: float):
    conn = get_connection()
    conn.execute(
        "INSERT INTO topic_trends (topic_label, run_id, paper_count, growth_rate, recorded_at) "
        "VALUES (?,?,?,?,?)",
        (topic_label, run_id, paper_count, growth_rate, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_latest_topics(limit: int = 20):
    conn = get_connection()
    latest_run = conn.execute(
        "SELECT id FROM trend_runs ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    if not latest_run:
        conn.close()
        return []
    rows = conn.execute(
        "SELECT * FROM topics WHERE run_id=? AND topic_id != -1 ORDER BY paper_count DESC LIMIT ?",
        (latest_run["id"], limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_topic_trends():
    conn = get_connection()
    rows = conn.execute(
        "SELECT topic_label, paper_count, growth_rate, recorded_at "
        "FROM topic_trends ORDER BY recorded_at DESC, paper_count DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_latest_run():
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM trend_runs ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_topics_for_run(run_id: str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM topics WHERE run_id=? AND topic_id != -1 ORDER BY paper_count DESC",
        (run_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

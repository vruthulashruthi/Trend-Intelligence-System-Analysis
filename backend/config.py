import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "trend_intelligence.db")

ARXIV_CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.NE"]
ARXIV_MAX_RESULTS = 100
ARXIV_BASE_URL = "http://export.arxiv.org/api/query"

SCHEDULER_INTERVAL_MINUTES = 30

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CLASSIFIER_MODEL = "typeform/distilbert-base-uncased-mnli"
SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"

DOMAIN_LABELS = [
    "artificial intelligence and machine learning",
    "unrelated general topic",
]
DOMAIN_THRESHOLD = 0.6

MIN_TOPIC_SIZE = 3
NR_TOPICS = 15

FASTAPI_HOST = "0.0.0.0"
FASTAPI_PORT = int(os.environ.get("PORT", 8000))
import os

REPORT_SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "shruthi242004@gmail.com")
REPORT_SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "gwut glbl gira jtcx")
REPORT_RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL", "kjvarsini14@gmail.com")
REPORT_SEND_TIME = os.environ.get("REPORT_SEND_TIME", "12:00")
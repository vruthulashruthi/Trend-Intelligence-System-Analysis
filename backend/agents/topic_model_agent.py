import json, logging, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.config import MIN_TOPIC_SIZE, NR_TOPICS
from backend import database
logger = logging.getLogger(__name__)

class TopicModelAgent:
    def run_topic_modeling(self, run_id):
        papers = database.get_relevant_papers()
        papers_with_emb = [p for p in papers if p["embedding"] is not None]
        if len(papers_with_emb) < 5:
            logger.warning("Not enough papers")
            return 0
        docs = [p["title"] + " " + p["abstract"] for p in papers_with_emb]
        embeddings = np.array([json.loads(p["embedding"]) for p in papers_with_emb])
        from bertopic import BERTopic
        from sklearn.feature_extraction.text import CountVectorizer
        from umap import UMAP
        from hdbscan import HDBSCAN
        n_docs = len(docs)
        n_neighbors = min(15, max(2, n_docs - 1))
        min_cluster = max(8, min(MIN_TOPIC_SIZE, n_docs // 4))
        umap_model = UMAP(n_neighbors=n_neighbors, n_components=min(5, n_docs-1), min_dist=0.0, metric="cosine", random_state=42)
        hdbscan_model = HDBSCAN(min_cluster_size=min_cluster, metric="euclidean", cluster_selection_method="eom", prediction_data=True)
        vectorizer = CountVectorizer(ngram_range=(1, 2), stop_words="english", min_df=1, max_features=5000)
        nr_topics = min(NR_TOPICS, max(2, n_docs // 5))
        topic_model = BERTopic(umap_model=umap_model, hdbscan_model=hdbscan_model, vectorizer_model=vectorizer, nr_topics=nr_topics, top_n_words=10, verbose=False, calculate_probabilities=False)
        logger.info("TopicModelAgent: Running BERTopic on %d docs", n_docs)
        topics, _ = topic_model.fit_transform(docs, embeddings)
        topic_info = topic_model.get_topic_info()
        topic_count = 0
        for _, row in topic_info.iterrows():
            tid = int(row["Topic"])
            if tid == -1: continue
            count = int(row["Count"])
            keywords_raw = topic_model.get_topic(tid)
            keywords = [kw for kw, _ in keywords_raw[:8]] if keywords_raw else []
            label = self._make_label(keywords)
            database.insert_topic(run_id, tid, label, keywords, count)
            topic_count += 1
        for paper, t_id in zip(papers_with_emb, topics):
            database.update_paper_topic(paper["id"], int(t_id))
        logger.info("TopicModelAgent: Found %d topics", topic_count)
        return topic_count

    def _make_label(self, keywords):
        if not keywords: return "Uncategorized"
        top = [k.replace("_", " ").title() for k in keywords[:3]]
        return " / ".join(top)
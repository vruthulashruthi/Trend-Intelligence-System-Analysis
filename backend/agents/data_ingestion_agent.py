import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.config import ARXIV_BASE_URL, ARXIV_CATEGORIES, ARXIV_MAX_RESULTS
from backend import database

logger = logging.getLogger(__name__)

NS = "http://www.w3.org/2005/Atom"


class DataIngestionAgent:
    def __init__(self):
        self.base_url = ARXIV_BASE_URL
        self.categories = ARXIV_CATEGORIES
        self.max_results = ARXIV_MAX_RESULTS

    def fetch_papers(self) -> int:
        total_new = 0
        for category in self.categories:
            papers = self._fetch_category(category)
            for paper in papers:
                database.insert_paper(paper)
                total_new += 1
        logger.info(f"DataIngestionAgent: Fetched {total_new} papers total")
        return total_new

    def _fetch_category(self, category: str) -> list:
        params = {
            "search_query": f"cat:{category}",
            "start": 0,
            "max_results": self.max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        try:
            resp = requests.get(self.base_url, params=params, timeout=30)
            resp.raise_for_status()
            return self._parse_feed(resp.text)
        except Exception as e:
            logger.error(f"Failed to fetch {category}: {e}")
            return []

    def _parse_feed(self, xml_text: str) -> list:
        root = ET.fromstring(xml_text)
        papers = []
        for entry in root.findall(f"{{{NS}}}entry"):
            try:
                arxiv_id = entry.find(f"{{{NS}}}id").text.strip()
                title = entry.find(f"{{{NS}}}title").text.strip().replace("\n", " ")
                abstract = entry.find(f"{{{NS}}}summary").text.strip().replace("\n", " ")
                published = entry.find(f"{{{NS}}}published").text.strip()
                papers.append({"id": arxiv_id, "title": title, "abstract": abstract, "published": published, "fetched_at": datetime.utcnow().isoformat()})
            except Exception as e:
                logger.warning(f"Failed to parse entry: {e}")
        return papers

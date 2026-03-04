# Autonomous Multi-Agent Tech Trend Intelligence System

A fully automated AI/ML research trend analysis system using multi-agent architecture, BERTopic, and real-time arXiv data.

## Quickstart

### 1. Install dependencies
```bash
pip install -r requirements.txt
```
First install may take 5-10 minutes (PyTorch + HuggingFace models ~1.5 GB).

### 2. Start the backend (from the project root folder)
```bash
python -m backend.main
```

This automatically:
- Initializes SQLite database
- Fetches ~500 papers from arXiv (cs.AI, cs.LG, cs.CL, cs.CV, cs.NE)
- Runs zero-shot classification to filter AI/ML papers
- Generates semantic embeddings (all-MiniLM-L6-v2)
- Runs BERTopic for topic clustering
- Computes sentiment per cluster
- Schedules re-run every 30 minutes

First run takes 3-8 minutes for model downloads.

### 3. Start the Streamlit dashboard (in a new terminal)
```bash
streamlit run ui/app.py
```
Open http://localhost:8501

## Project Structure
```
trend_intelligence_system/
├── backend/
│   ├── main.py                       # FastAPI server
│   ├── scheduler.py                  # Pipeline orchestration
│   ├── database.py                   # SQLite operations
│   ├── config.py                     # Configuration
│   └── agents/
│       ├── data_ingestion_agent.py   # arXiv fetcher
│       ├── domain_classifier_agent.py # Zero-shot classifier
│       ├── embedding_agent.py        # Sentence embeddings
│       ├── topic_model_agent.py      # BERTopic clustering
│       ├── trend_analysis_agent.py   # Growth rate analysis
│       ├── sentiment_agent.py        # Sentiment analysis
│       └── scheduler_agent.py       # APScheduler wrapper
├── ui/
│   └── app.py                       # Streamlit dashboard
├── requirements.txt
└── README.md
```

## API Endpoints
- GET /api/stats         - System statistics
- GET /api/topics        - Latest topic clusters
- GET /api/trends        - Historical trend data
- GET /api/papers        - Relevant papers list
- GET /api/run-pipeline  - Manually trigger pipeline

## Expected Topics (example)
- Transformer / Attention / Language Model - 45 papers
- Reinforcement Learning / Policy / Reward - 38 papers
- Graph Neural Networks / Node Classification - 27 papers
- Diffusion Models / Image Synthesis / Generative - 31 papers
- Federated Learning / Privacy / Distributed - 22 papers

## System Requirements
- Python 3.10+
- Internet access (arXiv API + HuggingFace model downloads)
- ~2 GB disk space for cached model weights
- 4 GB RAM recommended

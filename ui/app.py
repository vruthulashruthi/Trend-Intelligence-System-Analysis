import os
import json
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(
    page_title="TrendScope — AI Research Intelligence",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

/* Hide default streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display:none;}
header {visibility: hidden;}

/* Root vars */
:root {
    --bg: #080b12;
    --surface: #0e1420;
    --surface2: #141c2e;
    --border: #1e2d47;
    --accent: #00d4ff;
    --accent2: #7c3aed;
    --accent3: #10b981;
    --warn: #f59e0b;
    --danger: #ef4444;
    --text: #e2e8f0;
    --muted: #64748b;
    --font-mono: 'Space Mono', monospace;
}

.stApp {
    background: var(--bg);
    color: var(--text);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

/* Page header */
.page-header {
    padding: 2rem 0 1.5rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}
.page-title {
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #fff;
    margin: 0;
    line-height: 1;
}
.page-subtitle {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 0.5rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.accent-dot {
    color: var(--accent);
}

/* KPI Cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}
.kpi-label {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted);
    margin-bottom: 0.6rem;
}
.kpi-value {
    font-size: 2.4rem;
    font-weight: 800;
    color: #fff;
    line-height: 1;
    letter-spacing: -0.04em;
}
.kpi-sub {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    color: var(--muted);
    margin-top: 0.4rem;
}

/* Topic Cards */
.topic-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.4rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
    position: relative;
}
.topic-card:hover {
    border-color: var(--accent);
}
.topic-rank {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    color: var(--accent);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.topic-name {
    font-size: 1.15rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 0.8rem;
    letter-spacing: -0.02em;
}
.topic-meta {
    display: flex;
    gap: 1rem;
    align-items: center;
    flex-wrap: wrap;
}
.badge {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    padding: 0.25rem 0.6rem;
    border-radius: 4px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.badge-papers {
    background: rgba(0, 212, 255, 0.1);
    color: var(--accent);
    border: 1px solid rgba(0, 212, 255, 0.2);
}

.badge-pos {
    background: rgba(16, 185, 129, 0.1);
    color: var(--accent3);
    border: 1px solid rgba(16, 185, 129, 0.2);
}
.badge-neg {
    background: rgba(239, 68, 68, 0.1);
    color: var(--danger);
    border: 1px solid rgba(239, 68, 68, 0.2);
}
.kw-pill {
    display: inline-block;
    font-family: var(--font-mono);
    font-size: 0.6rem;
    padding: 0.2rem 0.5rem;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 4px;
    color: var(--muted);
    margin: 0.15rem;
    letter-spacing: 0.03em;
}

/* Progress bar */
.bar-track {
    background: var(--surface2);
    border-radius: 3px;
    height: 4px;
    margin-top: 0.8rem;
    overflow: hidden;
}
.bar-fill {
    height: 100%;
    border-radius: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}

/* Section headers */
.section-header {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--muted);
    margin-bottom: 1.2rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid var(--border);
}

/* Nav pills */
.nav-pill {
    display: inline-block;
    padding: 0.4rem 1rem;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
    margin-right: 0.5rem;
}

/* Status dot */
.status-live {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--accent3);
    margin-right: 0.4rem;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* Table styling */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

/* Metric overrides */
[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.2rem;
}
[data-testid="stMetricLabel"] {
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted) !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
}

/* Sidebar logo */
.sidebar-logo {
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    color: #fff;
    margin-bottom: 0.2rem;
}
.sidebar-tagline {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* Alert box */
.alert-box {
    background: rgba(0, 212, 255, 0.05);
    border: 1px solid rgba(0, 212, 255, 0.2);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--accent);
}

/* Paper card */
.paper-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
}
.paper-title {
    font-weight: 700;
    font-size: 0.95rem;
    color: #fff;
    margin-bottom: 0.4rem;
    line-height: 1.4;
}
.paper-meta {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    color: var(--muted);
    letter-spacing: 0.05em;
}
.paper-abstract {
    font-size: 0.8rem;
    color: #94a3b8;
    margin-top: 0.6rem;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)


PLOT_THEME = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Space Mono, monospace", color="#94a3b8", size=11),
    margin=dict(l=10, r=10, t=30, b=10),
    colorway=["#00d4ff", "#7c3aed", "#10b981", "#f59e0b", "#ef4444", "#06b6d4", "#8b5cf6"],
)

GRID_STYLE = dict(
    gridcolor="#1e2d47",
    zerolinecolor="#1e2d47",
    linecolor="#1e2d47",
)


def fetch(endpoint, default=None):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.warning(f"Cannot reach backend ({endpoint}): {e}")
        return default if default is not None else {}


def parse_topics(raw):
    out = []
    for t in raw:
        kw = t.get("keywords", [])
        if isinstance(kw, str):
            try:
                kw = json.loads(kw)
            except Exception:
                kw = []
        out.append({**t, "keywords": kw})
    return out


def sentiment_badge(s):
    if s == "POSITIVE":
        return '<span class="badge badge-pos">● Positive</span>'
    elif s == "NEGATIVE":
        return '<span class="badge badge-neg">● Negative</span>'
    return '<span class="badge" style="color:#64748b">● Neutral</span>'


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div class="sidebar-logo">⬡ TrendScope</div>
        <div class="sidebar-tagline">AI Research Intelligence</div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["🏠  Overview", "📊  Topic Explorer", "📄  Papers", "⚙️  System"],
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Pipeline Control</div>', unsafe_allow_html=True)

    if st.button("⟳  Run Pipeline Now", use_container_width=True, type="primary"):
        with st.spinner("Running pipeline..."):
            result = fetch("/api/run-pipeline", {})
        if "error" in result:
            st.error(result["error"])
        else:
            st.success(f"✓ {result.get('topics', 0)} topics discovered")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Live Stats</div>', unsafe_allow_html=True)

    stats = fetch("/api/stats", {})
    latest_run = stats.get("latest_run") or {}

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Papers", stats.get("total_papers", 0))
    with col_b:
        st.metric("Relevant", stats.get("relevant_papers", 0))

    st.metric("Topics Found", stats.get("topic_count", 0))

    if latest_run.get("created_at"):
        ts = latest_run["created_at"][:19].replace("T", " ")
        st.markdown(f"""
            <div style="margin-top:1rem">
                <span class="status-live"></span>
                <span style="font-family:'Space Mono',monospace;font-size:0.65rem;color:#64748b">
                    {ts} UTC
                </span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="alert-box">
            Auto-refresh every<br><strong>30 minutes</strong> via APScheduler
        </div>
    """, unsafe_allow_html=True)


# ── Data ─────────────────────────────────────────────────────────────────────
topics_raw = fetch("/api/topics", [])
topics = parse_topics(topics_raw)
papers_raw = fetch("/api/papers", [])

no_data = not topics


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠  Overview":
    st.markdown("""
        <div class="page-header">
            <div class="page-title">Research Intelligence<span class="accent-dot"> ·</span></div>
            <div class="page-subtitle">Autonomous arXiv trend analysis — cs.AI · cs.LG · cs.CL · cs.CV · cs.NE</div>
        </div>
    """, unsafe_allow_html=True)

    if no_data:
        st.markdown("""
            <div class="alert-box" style="font-size:0.85rem;padding:1.5rem">
                No data yet. Click <strong>Run Pipeline Now</strong> in the sidebar to fetch and analyze papers.
            </div>
        """, unsafe_allow_html=True)
        st.stop()

    # KPI row
    total = stats.get("total_papers", 0)
    relevant = stats.get("relevant_papers", 0)
    n_topics = stats.get("topic_count", 0)
    ratio = round(relevant / total * 100) if total else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Papers Fetched", f"{total:,}")
    with c2:
        st.metric("AI/ML Relevant", f"{relevant:,}", delta=f"{ratio}% of total")
    with c3:
        st.metric("Topics Discovered", n_topics)
    with c4:
        runs_conn = latest_run.get("paper_count", 0)
        st.metric("Last Run Papers", runs_conn)

    st.markdown("<br>", unsafe_allow_html=True)

    # Top topics ranked
    st.markdown('<div class="section-header">Top Research Clusters This Run</div>', unsafe_allow_html=True)

    top_topics = sorted(topics, key=lambda x: x.get("paper_count", 0), reverse=True)
    max_count = top_topics[0]["paper_count"] if top_topics else 1

    for i, topic in enumerate(top_topics[:6]):
        s = topic.get("sentiment_label", "NEUTRAL")
        kws = topic.get("keywords", [])[:5]
        pct = topic["paper_count"] / max_count * 100
        kw_html = "".join([f'<span class="kw-pill">{k}</span>' for k in kws])
        sb = sentiment_badge(s)

        st.markdown(f"""
        <div class="topic-card">
            <div class="topic-rank">#{i+1} cluster</div>
            <div class="topic-name">{topic["label"]}</div>
            <div class="topic-meta">
                <span class="badge badge-papers">{topic["paper_count"]} papers</span>
                {sb}
            </div>
            <div style="margin-top:0.8rem">{kw_html}</div>
            <div class="bar-track">
                <div class="bar-fill" style="width:{pct}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Two charts side by side
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown('<div class="section-header">Paper Distribution by Cluster</div>', unsafe_allow_html=True)
        df = pd.DataFrame(top_topics[:10])
        fig = px.bar(
            df, x="paper_count", y="label", orientation="h",
            color="paper_count", color_continuous_scale=["#1e2d47", "#00d4ff"],
            labels={"paper_count": "Papers", "label": ""},
        )
        fig.update_layout(**PLOT_THEME, height=380, showlegend=False,
                          yaxis={"categoryorder": "total ascending", **GRID_STYLE},
                          xaxis=GRID_STYLE, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-header">Sentiment Breakdown</div>', unsafe_allow_html=True)
        sents = [t for t in topics if t.get("sentiment_label") in ("POSITIVE", "NEGATIVE")]
        if sents:
            pos = sum(1 for t in sents if t["sentiment_label"] == "POSITIVE")
            neg = len(sents) - pos
            fig2 = go.Figure(data=[go.Pie(
                labels=["Positive Tone", "Negative Tone"],
                values=[pos, neg],
                hole=0.55,
                marker=dict(colors=["#10b981", "#ef4444"],
                            line=dict(color="#080b12", width=3)),
                textfont=dict(family="Space Mono", size=10),
            )])
            fig2.update_layout(**PLOT_THEME, height=320,
                               legend=dict(orientation="h", y=-0.1, font=dict(size=10)))
            st.plotly_chart(fig2, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — TOPIC EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊  Topic Explorer":
    st.markdown("""
        <div class="page-header">
            <div class="page-title">Topic Explorer<span class="accent-dot"> ·</span></div>
            <div class="page-subtitle">Deep-dive into each discovered research cluster</div>
        </div>
    """, unsafe_allow_html=True)

    if no_data:
        st.info("No topics yet. Run the pipeline first.")
        st.stop()

    sorted_topics = sorted(topics, key=lambda x: x.get("paper_count", 0), reverse=True)

    # Scatter: paper_count vs sentiment_score
    st.markdown('<div class="section-header">Cluster Map — Size vs Sentiment Confidence</div>', unsafe_allow_html=True)
    df_scatter = pd.DataFrame([{
        "Topic": t["label"],
        "Papers": t["paper_count"],
        "Sentiment Score": t.get("sentiment_score", 0.5),
        "Sentiment": t.get("sentiment_label", "NEUTRAL"),
    } for t in sorted_topics])

    fig_s = px.scatter(
        df_scatter, x="Sentiment Score", y="Papers",
        size="Papers", color="Sentiment",
        hover_name="Topic",
        color_discrete_map={"POSITIVE": "#10b981", "NEGATIVE": "#ef4444", "NEUTRAL": "#64748b"},
        size_max=60,
        labels={"Papers": "Paper Count", "Sentiment Score": "Sentiment Confidence"},
    )
    fig_s.update_layout(**PLOT_THEME, height=380,
                        xaxis={**GRID_STYLE}, yaxis={**GRID_STYLE})
    st.plotly_chart(fig_s, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">All Topic Clusters — Detailed View</div>', unsafe_allow_html=True)

    # Selectable topic detail
    topic_names = [t["label"] for t in sorted_topics]
    selected = st.selectbox("Select a topic to inspect", topic_names, label_visibility="collapsed")
    sel_topic = next((t for t in sorted_topics if t["label"] == selected), None)

    if sel_topic:
        s = sel_topic.get("sentiment_label", "NEUTRAL")
        score = sel_topic.get("sentiment_score", 0.0)
        kws = sel_topic.get("keywords", [])

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Papers in Cluster", sel_topic["paper_count"])
        with c2:
            st.metric("Sentiment", s)
        with c3:
            st.metric("Confidence", f"{score:.3f}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">Keywords extracted by BERTopic</div>', unsafe_allow_html=True)
        kw_html = "".join([
            f'<span class="kw-pill" style="font-size:0.75rem;padding:0.3rem 0.8rem;margin:0.3rem">{k}</span>'
            for k in kws
        ])
        st.markdown(f'<div style="margin-bottom:1.5rem">{kw_html}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Full Keyword Heatmap</div>', unsafe_allow_html=True)

    # Keyword frequency across topics
    all_kw_data = []
    for t in sorted_topics[:8]:
        for i, kw in enumerate(t.get("keywords", [])[:6]):
            all_kw_data.append({
                "Topic": t["label"].split(" / ")[0],
                "Keyword": kw,
                "Rank": 6 - i,
            })
    if all_kw_data:
        df_kw = pd.DataFrame(all_kw_data)
        pivot = df_kw.pivot_table(index="Keyword", columns="Topic", values="Rank", fill_value=0)
        fig_h = px.imshow(
            pivot,
            color_continuous_scale=[[0, "#0e1420"], [0.5, "#1e3a5f"], [1, "#00d4ff"]],
            aspect="auto",
            labels={"color": "Relevance"},
        )
        fig_h.update_layout(**PLOT_THEME, height=420)
        st.plotly_chart(fig_h, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — PAPERS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📄  Papers":
    st.markdown("""
        <div class="page-header">
            <div class="page-title">Paper Library<span class="accent-dot"> ·</span></div>
            <div class="page-subtitle">All AI/ML-relevant papers fetched from arXiv</div>
        </div>
    """, unsafe_allow_html=True)

    if not papers_raw:
        st.info("No papers yet. Run the pipeline first.")
        st.stop()

    # Search + filter
    col_search, col_sort = st.columns([4, 1])
    with col_search:
        query = st.text_input("Search papers", placeholder="Search titles and abstracts...",
                              label_visibility="collapsed")
    with col_sort:
        sort_by = st.selectbox("Sort", ["Newest", "Oldest"], label_visibility="collapsed")

    papers = papers_raw
    if query:
        q = query.lower()
        papers = [p for p in papers if q in p.get("title", "").lower() or q in p.get("abstract", "").lower()]

    if sort_by == "Newest":
        papers = sorted(papers, key=lambda x: x.get("published", ""), reverse=True)
    else:
        papers = sorted(papers, key=lambda x: x.get("published", ""))

    st.markdown(f"""
        <div style="font-family:'Space Mono',monospace;font-size:0.65rem;color:#64748b;
                    margin-bottom:1rem;text-transform:uppercase;letter-spacing:0.1em">
            Showing {len(papers)} papers
        </div>
    """, unsafe_allow_html=True)

    for paper in papers[:50]:
        title = paper.get("title", "Untitled")
        abstract = paper.get("abstract", "")[:220] + "..."
        published = paper.get("published", "")[:10]
        arxiv_id = paper.get("id", "")
        score = paper.get("domain_score", 0.0)
        topic_id = paper.get("topic_id", -1)

        # Build direct arXiv link from the stored ID
        # IDs are stored as full URLs like http://arxiv.org/abs/2401.12345v1
        if arxiv_id.startswith("http"):
            link = arxiv_id
        else:
            link = f"https://arxiv.org/abs/{arxiv_id}"

        topic_label = ""
        if topic_id != -1:
            matched = next((t["label"] for t in topics if t.get("topic_id") == topic_id), "")
            if matched:
                topic_label = f'<span class="kw-pill">{matched.split(" / ")[0]}</span>'

        st.markdown(f"""
        <div class="paper-card">
            <div class="paper-title">
                <a href="{link}" target="_blank" style="color:#fff;text-decoration:none;
                   border-bottom:1px solid #1e2d47;padding-bottom:1px;
                   transition:border-color 0.2s"
                   onmouseover="this.style.borderColor='#00d4ff'"
                   onmouseout="this.style.borderColor='#1e2d47'">
                    {title} ↗
                </a>
            </div>
            <div class="paper-meta">
                arXiv · {published} &nbsp;·&nbsp; relevance: {score:.2f}
                &nbsp;{topic_label}
            </div>
            <div class="paper-abstract">{abstract}</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚙️  System":
    st.markdown("""
        <div class="page-header">
            <div class="page-title">System Status<span class="accent-dot"> ·</span></div>
            <div class="page-subtitle">Agent pipeline diagnostics and configuration</div>
        </div>
    """, unsafe_allow_html=True)

    # Backend health
    try:
        health = requests.get(f"{API_BASE}/", timeout=5).json()
        backend_ok = True
    except Exception:
        backend_ok = False

    c1, c2, c3 = st.columns(3)
    with c1:
        if backend_ok:
            st.success("✓ Backend API — Online")
        else:
            st.error("✗ Backend API — Offline")
    with c2:
        st.info(f"⬡ API Base: {API_BASE}")
    with c3:
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        st.info(f"🕐 Current Time: {now}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Agent Pipeline</div>', unsafe_allow_html=True)

    agents = [
        ("DataIngestionAgent", "Fetches papers from arXiv API (cs.AI, cs.LG, cs.CL, cs.CV, cs.NE)", "arXiv REST API", "Active"),
        ("DomainClassifierAgent", "Zero-shot classification — filters AI/ML relevant papers", "facebook/bart-large-mnli", "Active"),
        ("EmbeddingAgent", "Converts paper text into semantic vector embeddings", "all-MiniLM-L6-v2", "Active"),
        ("TopicModelAgent", "Clusters papers into coherent research topics", "BERTopic + UMAP + HDBSCAN", "Active"),
        ("TrendAnalysisAgent", "Tracks topic paper counts across pipeline runs", "Internal", "Active"),
        ("SentimentAgent", "Scores research tone per topic cluster", "distilbert-base-uncased-finetuned-sst-2-english", "Active"),
        ("SchedulerAgent", "Triggers full pipeline automatically", "APScheduler (30 min interval)", "Active"),
    ]

    for name, desc, model, status in agents:
        st.markdown(f"""
        <div class="topic-card" style="padding:1rem 1.2rem;margin-bottom:0.6rem">
            <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div>
                    <div style="font-weight:700;font-size:0.9rem;color:#fff;margin-bottom:0.3rem">{name}</div>
                    <div style="font-size:0.78rem;color:#94a3b8;margin-bottom:0.4rem">{desc}</div>
                    <span class="kw-pill">{model}</span>
                </div>
                <span class="badge badge-pos" style="margin-left:1rem;white-space:nowrap">● {status}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Configuration</div>', unsafe_allow_html=True)

    cfg = {
        "ARXIV_CATEGORIES": "cs.AI, cs.LG, cs.CL, cs.CV, cs.NE",
        "ARXIV_MAX_RESULTS": "100 per category",
        "SCHEDULER_INTERVAL": "30 minutes",
        "EMBEDDING_MODEL": "all-MiniLM-L6-v2",
        "CLASSIFIER_MODEL": "facebook/bart-large-mnli",
        "SENTIMENT_MODEL": "distilbert-base-uncased-finetuned-sst-2-english",
        "MIN_TOPIC_SIZE": "8",
        "NR_TOPICS": "10",
        "DOMAIN_THRESHOLD": "0.6",
        "DATABASE": "SQLite (local)",
    }
    df_cfg = pd.DataFrame(list(cfg.items()), columns=["Parameter", "Value"])
    st.dataframe(df_cfg, use_container_width=True, hide_index=True)
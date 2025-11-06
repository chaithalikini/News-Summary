from typing import List, Dict
import os
import re
import requests
from collections import Counter
from sentence_transformers import SentenceTransformer, util

# Global caches
_summarizer = None
_sentiment = None
_kw_model = None
_sem_model = None

# Semantic model loader
def _get_semantic_model():
    global _sem_model
    if _sem_model is None:
        _sem_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _sem_model

# Helper functions
def _get_summarizer():
    global _summarizer
    if _summarizer is None:
        from transformers import pipeline
        _summarizer = pipeline("summarization", model="t5-base")
    return _summarizer

def _get_sentiment():
    global _sentiment
    if _sentiment is None:
        from transformers import pipeline
        _sentiment = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment"
        )
    return _sentiment

def _get_kw():
    global _kw_model
    if _kw_model is None:
        from keybert import KeyBERT
        _kw_model = KeyBERT()
    return _kw_model

# News fetching 
def get_news(company: str, limit: int = 10) -> List[Dict]:
    """
    Fetch top recent English news articles and return the top N most relevant for any company.
    """
    try:
        from datetime import datetime, timedelta

        api_key = os.getenv("NEWS_API_KEY") or "YOUR_NEWS_API_KEY"
        if api_key == "YOUR_NEWS_API_KEY":
            raise ValueError("NEWS_API_KEY missing! Please set your NewsAPI key.")

        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={company}&language=en&sortBy=publishedAt&pageSize={limit*3}"
            f"&from={from_date}&to={to_date}&apiKey={api_key}"
        )

        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print("NewsAPI error:", response.text)
            return []

        data = response.json()
        articles = data.get("articles", [])

        # Rank articles by relevance
        ranked_articles = rank_articles_by_relevance(company, articles)

        news = []
        for art in ranked_articles[:limit]:
            title = art.get("title") or "No Title"
            desc = art.get("description") or art.get("content") or ""
            desc = re.sub(r"http\S+", "", desc)
            desc = re.sub(r"[^A-Za-z0-9\s.,'\-]", " ", desc)
            desc = re.sub(r"\s+", " ", desc).strip()
            if not desc:
                desc = f"{title}. More details to follow."

            news.append({
                "Title": title.strip(),
                "Summary": desc.strip(),
                "Sentiment": analyze_sentiment(desc),
                "Topics": extract_topics(desc, company)
            })

        return news

    except Exception as e:
        print("get_news error:", e)
        return []

# Rank articles by semantic relevance
def rank_articles_by_relevance(company: str, articles: List[Dict]) -> List[Dict]:
    """
    Rank articles based on semantic similarity to company name.
    """
    sem_model = _get_semantic_model()
    company_embed = sem_model.encode(company, convert_to_tensor=True)

    scored = []
    for art in articles:
        title = art.get("title", "")
        desc = art.get("description", "")
        content = f"{title}. {desc}".strip()
        art_embed = sem_model.encode(content, convert_to_tensor=True)
        score = util.cos_sim(company_embed, art_embed).item()
        scored.append((score, art))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [art for _, art in scored]

# Summarization
def summarize_text(text: str, title: str = "", max_length=100, min_length=40) -> str:
    if not text:
        return ""
    try:
        summarizer = _get_summarizer()
        text = re.sub(r"(Reuters|BBC|NDTV|The Hindu|Economic Times|LiveMint)+", "", text, flags=re.I)
        text = re.sub(r"\s+", " ", text).strip()
        input_text = f"{title}. {text}" if title and title.lower() not in text.lower() else text
        input_text = input_text[:1000]
        out = summarizer(input_text, max_length=max_length, min_length=min_length, do_sample=False)
        summary = out[0]["summary_text"].strip()
        summary = re.sub(r"\s+([.,!?])", r"\1", summary)
        summary = summary[0].upper() + summary[1:] if summary else summary
        return summary
    except Exception:
        return text[:150] + "..."

# Sentiment Analysis
def analyze_sentiment(text: str) -> str:
    if not text:
        return "Neutral"
    try:
        classifier = _get_sentiment()
        result = classifier(text[:512])[0]
        label = result.get("label", "").lower()
        mapping = {"label_0": "Negative", "label_1": "Neutral", "label_2": "Positive"}
        return mapping.get(label, "Neutral")
    except Exception:
        return "Neutral"

# Topic Extraction
def extract_topics(text: str, company: str = "", top_n=3) -> List[str]:
    if not text:
        return []

    try:
        kw = _get_kw().extract_keywords(
            text,
            keyphrase_ngram_range=(1,2),
            stop_words='english',
            top_n=top_n,
            use_maxsum=True
        )

        clean = []
        for k, _ in kw:
            k_clean = k.title()
            if not re.match(r'^(href|rss|http|amp|www|cbm|ol|read|click|article)$', k.lower()):
                clean.append(k_clean)

        # Ensure company name appears in topics
        if company:
            for t in company.split():
                if t.lower() in text.lower() and t.title() not in clean:
                    clean.insert(0, t.title())

        # Fill if less than top_n
        if len(clean) < top_n:
            tokens = re.findall(r"[A-Za-z]{3,}", text)
            for t in tokens:
                t_title = t.title()
                if t_title not in clean:
                    clean.append(t_title)
                if len(clean) >= top_n:
                    break

        return clean[:top_n]

    except Exception:
        tokens = re.findall(r"[A-Za-z]{3,}", text)
        return [t.title() for t in tokens[:top_n]]


# Comparative Analysis
def comparative_analysis(articles: List[Dict], company: str = "") -> Dict:
    sentiment_dist = {"Positive": 0, "Negative": 0, "Neutral": 0}
    for a in articles:
        sentiment_dist[a.get("Sentiment", "Neutral")] += 1

    topics_all = [set(a.get("Topics", [])) for a in articles]
    flat = [t.lower() for s in topics_all for t in s]
    counts = Counter(flat)
    common = {t.title() for t, c in counts.items() if c >= 2}
    unique_per_article = [[t for t in s if t.lower() not in common] for s in topics_all]

    def detect_focus(topics):
        joined = " ".join(topics).lower()
        if any(k in joined for k in ["revenue", "profit", "sales", "stock", "investor", "earning"]):
            return "Financial"
        if any(k in joined for k in ["launch", "product", "ai", "innovation", "technology", "fabric"]):
            return "Product/Innovation"
        if any(k in joined for k in ["tax", "law", "regulation", "ban", "compliance", "legal"]):
            return "Regulatory"
        if any(k in joined for k in ["ceo", "leadership", "chair", "executive", "founder"]):
            return "Leadership"
        if any(k in joined for k in ["india", "china", "us", "global", "market"]):
            return "Geopolitical"
        return "General"

    focuses = [detect_focus(a.get("Topics", [])) for a in articles]

    coverage = []
    for i in range(len(articles) - 1):
        a1, a2 = articles[i], articles[i + 1]
        t1 = a1["Topics"][0] if a1.get("Topics") else focuses[i]
        t2 = a2["Topics"][0] if a2.get("Topics") else focuses[i+1]
        comp = f"Article {i+1} highlights {t1} issues, whereas Article {i+2} focuses on {t2}."

        s1, s2 = a1.get("Sentiment", "Neutral"), a2.get("Sentiment", "Neutral")
        if s1 == "Positive" and s2 == "Negative":
            imp = "Shift from positive to negative news — mixed perception."
        elif s1 == "Negative" and s2 == "Positive":
            imp = "Shift from negative to positive news — improving outlook."
        elif s1 == s2 == "Positive":
            imp = "Consistent positive coverage — optimism reinforced."
        elif s1 == s2 == "Negative":
            imp = "Consistent negative coverage — concerns persist."
        else:
            imp = "Mixed sentiment — perception varies."

        coverage.append({"Comparison": comp, "Impact": imp})

    pos, neg, neu = sentiment_dist.values()
    total = max(1, pos + neg + neu)
    pos_ratio, neg_ratio = pos / total, neg / total
    company_name = company or (articles[0]['Title'].split()[0] if articles else "The company")

    if pos_ratio > 0.6:
        final_eng = f"Most news about {company_name} is positive. Overall public perception seems optimistic."
    elif neg_ratio > 0.6:
        final_eng = f"Most news about {company_name} is negative. There are notable concerns or challenges being reported."
    elif neu > max(pos, neg):
        final_eng = f"The news about {company_name} is mostly neutral. Public sentiment is calm and factual."
    elif abs(pos - neg) <= 1:
        final_eng = f"The news about {company_name} is mixed. Opinions are divided, and the situation is evolving."
    else:
        final_eng = f"The news about {company_name} is slightly positive. While some issues are mentioned, overall perception is optimistic."

    final_hi = f"कुल {total} समाचारों का विश्लेषण: सकारात्मक {pos}, नकारात्मक {neg}, तटस्थ {neu}।"

    topic_overlap = {"Common Topics": list(common)}
    for i, uniq in enumerate(unique_per_article, 1):
        topic_overlap[f"Unique Topics in Article {i}"] = uniq

    return {
        "Comparative Sentiment Score": {
            "Sentiment Distribution": sentiment_dist,
            "Coverage Differences": coverage,
            "Topic Overlap": topic_overlap
        },
        "Final Sentiment Analysis": final_eng,
        "Hindi Summary": final_hi
    }

# Text-to-Speech (Hindi)
def text_to_speech_hindi(text: str, filename: str = "report.mp3") -> str:
    try:
        from gtts import gTTS
        os.makedirs("outputs/audio", exist_ok=True)
        path = os.path.join("outputs/audio", filename)
        path = path.replace("\\", "/")  # Streamlit compatible
        gTTS(text, lang="hi").save(path)
        return path
    except Exception as e:
        print("TTS error:", e)
        return ""


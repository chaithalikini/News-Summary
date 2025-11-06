from fastapi import FastAPI, Query, HTTPException
from utils import (
    get_news, summarize_text, analyze_sentiment,
    extract_topics, comparative_analysis, text_to_speech_hindi
)

app = FastAPI(title="News Summarizer API")

@app.get("/analyze")
def analyze_news(company: str = Query(..., min_length=1), limit: int = Query(10, ge=1)):
    try:
        # Step 1: Fetch news
        news = get_news(company, limit)
        if not news:
            raise HTTPException(status_code=404, detail="No articles found.")

        # Step 2: Summarize + analyze each article
        for a in news:
            text = a["Summary"]
            a["Summary"] = summarize_text(text, a["Title"])
            a["Sentiment"] = analyze_sentiment(a["Summary"])
            a["Topics"] = extract_topics(a["Summary"], company)

        # Step 3: Comparative + final analysis
        comparative = comparative_analysis(news, company)
        final_sent = comparative["Final Sentiment Analysis"]
        hindi_summary = comparative["Hindi Summary"]

        # Step 4: Generate Hindi TTS
        filename = f"{company.lower().replace(' ', '_')}_report.mp3"
        audio_path = text_to_speech_hindi(hindi_summary, filename)

        # Step 5: Build clean response
        report = {
            "Company": company.title(),
            "Articles": news,
            "Comparative Sentiment Score": comparative["Comparative Sentiment Score"],
            "Final Sentiment Analysis": final_sent,
            "Audio": audio_path
        }

        return report

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

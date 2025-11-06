# 📰 News Summarization and Text-to-Speech Application
Project Overview
This web-based application extracts key information from multiple news articles related to a given company, performs sentiment analysis, conducts comparative analysis, and generates a Hindi text-to-speech (TTS) audio summary. Users can input a company name and receive a structured sentiment report along with an audio output.

**Features**
- 📰 Fetches latest news articles for any company using NewsAPI.
- ✍️ Summarizes articles using a transformer-based summarizer.
- 🙂 Performs sentiment analysis (Positive, Negative, Neutral) per article.
- 🔑 Extracts key topics from each article.
- 📊 Conducts comparative sentiment analysis across multiple articles.
- 🔊 Generates a Hindi TTS audio summarizing the report.
- 🌐 Web-based interface via Streamlit with API-driven architecture

### **File Structure**
```text
news-analyse/
│
├── app.py                  # Streamlit frontend
├── api.py                  # FastAPI backend
├── utils.py                # Utility functions for news, summarization, sentiment, TTS
├── requirements.txt        # Python dependencies
├── outputs/                # Generated audio files
│   └── audio/
└── README.md
---

## Installation & Setup

1. **Clone the repository**
git clone <repository_url>
cd project-root

2. **Install dependencies**
pip install -r requirements.txt

3. **Set up NewsAPI Key**
export NEWS_API_KEY="7a8d61c74ea54b81b238ca71f0699183"

4. **Run the FastAPI backend**
uvicorn api:app --reload --port 8000

5. **Run the Streamlit frontend**
streamlit run app.py

6. Open the browser and enter the company name to get the sentiment report and Hindi audio summary.

## API Documentation
Endpoint: /analyze
Method: GET
Parameters:
a. company (str, required): Name of the company to fetch news for.
b. limit (int, optional): Number of news articles to analyze (default=10, max=20).
**Usage Example (Browser / Postman):** 
GET http://localhost:8000/analyze?company=Tesla&limit=10

**Sample Input & Output**
**Input:**
Enter Company Nmae : Tesla

### **2️⃣ Sample Output (JSON)**

Instead of pasting raw JSON, use a **JSON code block**:

```markdown
### **Sample Output**
```json
{
  "Company": "Tesla",
  "Articles": [
    {
      "Title": "The People Who Will Determine Whether Musk Becomes a Trillionaire",
      "Summary": "The vote could give the world s richest man more money and more control. this week s vote on whether to become a trillionaire could give him more control of his wealth.",
      "Sentiment": "Neutral",
      "Topics": [
        "Control Week",
        "World Richest",
        "Vote"
      ]
    },
    {
      "Title": "Tesla Is Obsessed With Musk’s Pay Package. Musk Is Obsessed With AI",
      "Summary": "Tesla Is Obsessed With Musk’s Pay Package. Employees were compelled to turn over biometric data to develop controversial avatars. xAI is a company focused on winning the artificial-intelligence arms race.",
      "Sentiment": "Neutral",
      "Topics": [
        "Tesla",
        "Turn Biometric",
        "Musk Pay"
      ]
    }
  ],
  "Comparative Sentiment Score": {
    "Sentiment Distribution": {
      "Positive": 0,
      "Negative": 2,
      "Neutral": 8
    },
    "Coverage Differences": [
      {
        "Comparison": "Article 1 highlights Control Week issues, whereas Article 2 focuses on Tesla.",
        "Impact": "Mixed sentiment — perception varies."
      },
      {
        "Comparison": "Article 2 highlights Tesla issues, whereas Article 3 focuses on Tesla.",
        "Impact": "Mixed sentiment — perception varies."
      }
    ],
    "Topic Overlap": {
      "Common Topics": [
        "Tesla",
        "Pay Package"
      ],
      "Unique Topics in Article 1": [
        "Vote",
        "World Richest",
        "Control Week"
      ],
      "Unique Topics in Article 2": [
        "Tesla",
        "Musk Pay",
        "Turn Biometric"
      ]
    }
  },
  "Final Sentiment Analysis": "The news about Tesla is mostly neutral. Public sentiment is calm and factual.",
  "Audio": "outputs/audio/tesla_report.mp3"
}

## Models & Libraries

**Task**	                **Model / Library**
Summarization	        t5-base via HuggingFace Transformers
Sentiment Analysis	  cardiffnlp/twitter-roberta-base-sentiment
Topic Extraction	    KeyBERT
Semantic Ranking	    all-MiniLM-L6-v2 via SentenceTransformers
Hindi Text-to-Speech	gTTS

**Assumptions & Limitations**
Only English news articles are fetched.
NewsAPI free plan limits may restrict the number of requests.
Text-to-Speech is limited to Hindi language only.
Only articles with textual content are considered.
Maximum 20 articles can be analyzed at a time for performance reasons.
    



import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="News Summarizer", layout="wide")
st.title("📰 News Summarization and Text-to-Speech Application")
st.write("Performs sentiment analysis, conducts a comparative analysis, and generates a text-to-speech (TTS) output in Hindi.")

API_URL = os.environ.get("API_URL") or "http://localhost:8000/analyze"

company = st.text_input("Enter Company Name:")

if company:
    with st.spinner("Fetching and analyzing news..."):
        response = requests.get(API_URL, params={"company": company, "limit": 10})
        if response.status_code == 200:
            data = response.json()

            st.markdown(f"### 🧾 Structured Sentiment Report for {company.title()}")
            st.code(json.dumps(data, indent=2, ensure_ascii=False), language="json")

            if data.get("Audio"):
                st.markdown(f"### 🔊 Hindi Audio Summary for {company.title()}")
                st.audio(data["Audio"])
        else:
            st.error(f"Error: {response.text}")

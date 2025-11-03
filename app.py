import streamlit as st
import requests

st.set_page_config(page_title="News Summarization & Hindi TTS", layout="wide")

st.title("News Summarization and Text-to-Speech App")
st.markdown("Enter a company name to fetch related news, analyze sentiment, and generate Hindi audio.")

# Input
company_name = st.text_input("Enter Company Name:", placeholder="e.g., Tesla")

if st.button("Generate Report"):
    if not company_name.strip():
        st.warning("Please enter a company name.")
    else:
        with st.spinner("Fetching news and generating report..."):
            try:
                # Call 
                response=requests.get(f"http://127.0.0.1:8000/analyze?company={company_name}")
                if response.status_code==200:
                    data=response.json()

                    st.subheader(f"Sentiment Report for {data['Company']}")
                    for article in data["Articles"]:
                        st.markdown(f"{article['Title']}")
                        st.write(article["Summary"])
                        st.write(f"Sentiment:{article['Sentiment']}")
                        st.write(f"Topics:{','.join(article['Topics'])}")
                        st.divider()
                    st.audio(data["Audio"], format="audio/mp3")
                else:
                    st.error("Failed to get response from backend")
            except Exception as e:
                st.error(f"Error:{e}")

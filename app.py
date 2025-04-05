import streamlit as st
import pandas as pd
from utils import (
    compute_engagement, 
    get_engagement_string, 
    compute_keyword_engagement, 
    create_persona_tweet
)

st.set_page_config(page_title="Cyberpunk Twitter Persona 🚀", layout="wide")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a page", ["Homepage", "Keyword Engagement", "Persona Tweet"])

# --- Homepage ---
if page == "Homepage":
    st.title("Cyberpunk Twitter Persona Analyzer 🛸")
    
    uploaded_file = st.file_uploader("Upload your tweets CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df = compute_engagement(df)
        
        with st.spinner("Analyzing engagement ..."):
            engagement_summary = get_engagement_string(df)

        st.subheader("Top Tweets")
        st.dataframe(df[['text', 'engagement']].head(10), use_container_width=True)

        st.markdown(f"### 📊 Engagement Analysis:\n{engagement_summary}")

# --- Keyword Engagement ---
elif page == "Keyword Engagement":
    st.title("Keyword Engagement Analysis 🔥")

    uploaded_file = st.file_uploader("Upload your tweets CSV", type="csv", key="keyword_csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df = compute_engagement(df)

        keywords_string = st.text_input("Keywords (comma-separated)")
        
        if st.button("Analyze"):
            if keywords_string:
                df_keywords = compute_keyword_engagement(df, keywords_string)

                st.subheader("Keyword Engagement")
                st.bar_chart(df_keywords.set_index('keyword')[['engagement_true', 'engagement_false']])

                st.table(df_keywords)

# --- Persona Tweet ---
elif page == "Persona Tweet":
    st.title("Generate Persona Tweet 🧠")

    uploaded_file = st.file_uploader("Upload your tweets CSV", type="csv", key="persona_csv")
    topic = st.text_input("Topic (text or URL)")
    
    if uploaded_file and topic:
        df = pd.read_csv(uploaded_file)
        df = compute_engagement(df)

        with st.spinner("Analyzing engagement for persona tweet..."):
            engagement_summary = get_engagement_string(df)

        if st.button("Create Tweet"):
            with st.spinner("Creating tweet..."):
                tweet_html = create_persona_tweet(topic, df, engagement_summary)
                st.markdown(tweet_html, unsafe_allow_html=True)

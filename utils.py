# utils.py
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests
from genai import generate_text, display_tweet
import requests
from bs4 import BeautifulSoup

# Compute engagement

def compute_engagement(df):
    df = df.copy()
    df['engagement'] = df['favorite_count'] / df['view_count']
    df = df.sort_values(by='engagement', ascending=False)
    return df

# AI engagement analysis string

def get_engagement_string(df):
    tweets_summary = df[['text', 'engagement']].head(10).to_dict(orient='records')
    prompt = f"Analyze the following tweets based on their text and engagement, and summarize what drives engagement:\n\n{tweets_summary}\n\nProvide your analysis:"
    engagement_analysis = generate_text(prompt)
    return engagement_analysis

# Keyword engagement analysis

def compute_keyword_engagement(df, keywords_string):
    keywords = [kw.strip().lower() for kw in keywords_string.split(',')]

    results = []
    for keyword in keywords:
        has_keyword = df['text'].str.lower().str.contains(keyword)

        engagement_true = df.loc[has_keyword, 'engagement'].mean()
        engagement_false = df.loc[~has_keyword, 'engagement'].mean()

        # Perform t-test
        t_stat, pvalue = ttest_ind(df.loc[has_keyword, 'engagement'],
                                   df.loc[~has_keyword, 'engagement'],
                                   equal_var=False, nan_policy='omit')

        results.append({
            'keyword': keyword,
            'pvalue': pvalue,
            'engagement_true': engagement_true,
            'engagement_false': engagement_false
        })

    df_results = pd.DataFrame(results)

    # Benjamini-Hochberg correction
    corrected = multipletests(df_results['pvalue'], method='fdr_bh')
    df_results['pvalue_bh'] = corrected[1]

    return df_results[['keyword', 'pvalue_bh', 'engagement_false', 'engagement_true']]

# Persona tweet generation

def create_persona_tweet(topic, df, engagement_analysis_string):
    if topic.startswith('http://') or topic.startswith('https://'):
        response = requests.get(topic)
        soup = BeautifulSoup(response.text, 'html.parser')
        topic_content = soup.get_text()
    else:
        topic_content = topic

    prompt = (
        f"You are emulating a Twitter persona. Based on the following analysis of tweet engagement: {engagement_analysis_string}\n\n"
        f"Here are some example tweets and their engagements: {df[['text', 'engagement']].head(10).to_dict(orient='records')}\n\n"
        f"Create an engaging tweet about the following topic or content:\n\n{topic_content}\n\nTweet:"
    )

    tweet_text = generate_text(prompt)
    tweet_html = display_tweet(tweet_text)

    return tweet_html

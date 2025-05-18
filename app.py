import streamlit as st
import pandas as pd
from sentiment_model import classify_sentiment
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud

st.set_page_config(page_title="Citizen Feedback", layout="wide")

# Load data
df = pd.read_csv("sample_posts.csv")
feedback_data = []

st.markdown("<h1 style='color:#014F86'>AI-Powered Citizen Feedback Platform</h1>", unsafe_allow_html=True)

# Filter by category
categories = df['category'].unique()
selected_category = st.sidebar.selectbox("Filter by Category", options=["All"] + list(categories))

if selected_category != "All":
    df = df[df["category"] == selected_category]

st.sidebar.markdown("**Made with love for Nigeria**")

# Loop through posts
for i, row in df.iterrows():
    st.markdown(f"<h3 style='color:#2A9D8F'>{row['title']}</h3>", unsafe_allow_html=True)
    st.image(row['image_url'], width=500)
    st.write(row['description'])

    col1, col2 = st.columns(2)
    with col1:
        sentiment = st.radio("React", ["Positive", "Neutral", "Negative"], key=f"sentiment_{i}")
    with col2:
        suggestion = st.text_area("Suggestion", key=f"suggestion_{i}")

    if st.button("Submit", key=f"submit_{i}"):
        classified_sent = classify_sentiment(suggestion)
        feedback_data.append({
            "title": row["title"],
            "sentiment": sentiment,
            "suggestion": suggestion,
            "analyzed_sentiment": classified_sent
        })
        st.success(f"Feedback recorded. Sentiment: {classified_sent}")

# Show analytics if there’s data
if feedback_data:
    st.markdown("## Feedback Analytics")

    feedback_df = pd.DataFrame(feedback_data)

    # Sentiment count chart
    counts = Counter(feedback_df['sentiment'])
    st.subheader("Sentiment Summary")
    fig, ax = plt.subplots()
    ax.bar(counts.keys(), counts.values(), color=['green', 'gray', 'red'])
    ax.set_ylabel("Count")
    st.pyplot(fig)

    # Word cloud from suggestions
    all_text = " ".join(feedback_df["suggestion"].dropna())
    if all_text.strip():
        st.subheader("Word Cloud from Suggestions")
        wordcloud = WordCloud(width=800, height=300, background_color='white').generate(all_text)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

    # Download feedback summary
    st.download_button("Download Feedback Summary", feedback_df.to_csv(index=False).encode('utf-8'), "feedback_summary.csv", "text/csv")

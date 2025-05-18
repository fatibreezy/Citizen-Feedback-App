import streamlit as st
import pandas as pd
from textblob import TextBlob
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import re

st.set_page_config(page_title="Citizen Feedback Platform", layout="wide")

# Load post data
df = pd.read_csv("sample_posts.csv")

# Initialize feedback storage
if 'feedback_data' not in st.session_state:
    st.session_state.feedback_data = []

st.title("AI-Powered Citizen Feedback Platform")
st.markdown("Provide your reaction and suggestions on each government post. Analysis is updated below each one.")

# Function to clean and prepare wordcloud text
def clean_text(text):
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    text = re.sub(r'\@w+|\#','', text)
    text = re.sub(r'[^A-Za-z\s]', '', text)
    text = text.lower()
    return text

# Display each post with feedback
for i, row in df.iterrows():
    st.markdown(f"### {row['title']}")
    st.image(row['image_url'], use_container_width=True)
    st.write(row['description'])

    col1, col2 = st.columns(2)
    with col1:
        reaction = st.radio("Quick Reaction", ["Positive", "Neutral", "Negative"], key=f"reaction_{i}")
    with col2:
        suggestion = st.text_area("Your Suggestion", key=f"suggestion_{i}")

    if st.button("Submit Feedback", key=f"submit_{i}"):
        sentiment = "None"
        if suggestion.strip():
            polarity = TextBlob(suggestion).sentiment.polarity
            if polarity > 0.2:
                sentiment = "Positive"
            elif polarity < -0.2:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"

        feedback_entry = {
            "Post Title": row["title"],
            "Category": row["category"],
            "Reaction": reaction,
            "Suggestion": suggestion,
            "Analyzed Sentiment": sentiment
        }
        st.session_state.feedback_data.append(feedback_entry)
        st.success("Feedback recorded successfully.")

    # Pull feedback for this post only
    post_feedback = [f for f in st.session_state.feedback_data if f["Post Title"] == row["title"]]
    if post_feedback:
        post_df = pd.DataFrame(post_feedback)

        # Reaction Summary Chart
        st.markdown("#### Reaction Summary")
        react_counts = post_df["Reaction"].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.bar(react_counts.index, react_counts.values, color=['green', 'gray', 'red'])
        ax1.set_ylabel("Count")
        st.pyplot(fig1)

        # Sentiment Summary Chart
        st.markdown("#### Sentiment Summary from Suggestions")
        sent_counts = post_df["Analyzed Sentiment"].value_counts()
        fig2, ax2 = plt.subplots()
        ax2.bar(sent_counts.index, sent_counts.values, color=['green', 'gray', 'red'])
        ax2.set_ylabel("Count")
        st.pyplot(fig2)

        # Word Cloud from Suggestions
        combined_text = " ".join([clean_text(t) for t in post_df["Suggestion"] if t.strip()])
        if combined_text:
            st.markdown("#### Word Cloud of Suggestions")
            wc = WordCloud(width=800, height=300, stopwords=STOPWORDS, background_color="white").generate(combined_text)
            fig3, ax3 = plt.subplots(figsize=(10, 4))
            ax3.imshow(wc, interpolation='bilinear')
            ax3.axis('off')
            st.pyplot(fig3)

        # Show all suggestions
        st.markdown("#### Suggestions Table")
        st.dataframe(post_df[["Suggestion", "Analyzed Sentiment"]])

        # Download button
        csv_data = post_df.to_csv(index=False).encode('utf-8')
        st.download_button(f"Download Feedback for {row['title']}", csv_data, f"{row['title']}_feedback.csv", "text/csv")

    st.markdown("---")

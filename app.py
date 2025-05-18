import streamlit as st
import pandas as pd
from textblob import TextBlob
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud

st.set_page_config(page_title="Citizen Feedback Platform", layout="wide")

# Load posts
df = pd.read_csv("sample_posts.csv")

# Temporary session state to collect feedback
if 'feedback_data' not in st.session_state:
    st.session_state.feedback_data = []

st.title("AI-Powered Citizen Feedback Platform")

# Filter
categories = df['category'].unique()
selected_category = st.sidebar.selectbox("Filter by Category", ["All"] + list(categories))
if selected_category != "All":
    df = df[df['category'] == selected_category]

# Display posts
st.subheader("Recent Government Posts")
for i, row in df.iterrows():
    st.markdown(f"### {row['title']}")
    st.image(row['image_url'], use_column_width=True)
    st.write(row['description'])

    col1, col2 = st.columns(2)
    with col1:
        reaction = st.radio("Quick Reaction", ["Positive", "Neutral", "Negative"], key=f"react_{i}")
    with col2:
        suggestion = st.text_area("Enter Suggestion", key=f"suggestion_{i}")

    if st.button("Submit", key=f"submit_{i}"):
        sentiment = "None"
        if suggestion.strip() != "":
            blob = TextBlob(suggestion)
            polarity = blob.sentiment.polarity
            if polarity > 0.2:
                sentiment = "Positive"
            elif polarity < -0.2:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"

        feedback = {
            "Post Title": row['title'],
            "Category": row['category'],
            "Reaction": reaction,
            "Suggestion": suggestion,
            "Analyzed Sentiment": sentiment
        }
        st.session_state.feedback_data.append(feedback)
        st.success("Feedback submitted successfully!")

# Show analytics if any feedback is recorded
if len(st.session_state.feedback_data) > 0:
    feedback_df = pd.DataFrame(st.session_state.feedback_data)
    st.markdown("---")
    st.subheader("Feedback Analytics")

    # Sentiment chart (overall)
    sentiment_counts = feedback_df["Analyzed Sentiment"].value_counts()
    st.markdown("**Suggestion Sentiment Distribution**")
    fig1, ax1 = plt.subplots()
    ax1.bar(sentiment_counts.index, sentiment_counts.values, color=['green', 'gray', 'red'])
    ax1.set_ylabel("Count")
    st.pyplot(fig1)

    # Wordcloud from suggestions
    suggestions_text = " ".join(feedback_df["Suggestion"].dropna().astype(str))
    if suggestions_text.strip():
        st.subheader("Word Cloud of Suggestions")
        wordcloud = WordCloud(width=800, height=300, background_color='white').generate(suggestions_text)
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        ax2.imshow(wordcloud, interpolation='bilinear')
        ax2.axis('off')
        st.pyplot(fig2)

    # Per-post summary (optional feature)
    st.subheader("Per-Post Feedback Table")
    st.dataframe(feedback_df)

    # Download button
    csv_data = feedback_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Feedback Summary", csv_data, "feedback_summary.csv", "text/csv")

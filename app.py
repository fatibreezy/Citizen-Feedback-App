import streamlit as st
import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt

st.set_page_config(page_title="Citizen Feedback Platform", layout="wide")

# Load posts
df = pd.read_csv("sample_posts.csv")

# Initialize feedback stores
if 'post_feedback' not in st.session_state:
    st.session_state.post_feedback = {}

if 'general_notes' not in st.session_state:
    st.session_state.general_notes = []

st.title("AI-Powered Citizen Feedback Platform")
st.markdown("React to official updates or write directly to the government.")

# === GENERAL NOTE TO GOVERNMENT SECTION ===
st.markdown("## Write a Note to the Government")
general_col1, general_col2 = st.columns([3, 1])
with general_col1:
    general_note = st.text_area("What's on your mind?", placeholder="Your message to the government...")
with general_col2:
    if st.button("Submit Note"):
        if general_note.strip():
            polarity = TextBlob(general_note).sentiment.polarity
            sentiment = (
                "Positive" if polarity > 0.2 else
                "Negative" if polarity < -0.2 else
                "Neutral"
            )
            st.session_state.general_notes.append({
                "Note": general_note,
                "Sentiment": sentiment
            })
            st.success("Note submitted!")

if st.session_state.general_notes:
    st.markdown("### Notes Summary")
    gen_df = pd.DataFrame(st.session_state.general_notes)
    sentiment_summary = gen_df["Sentiment"].value_counts().reset_index()
    sentiment_summary.columns = ["Sentiment", "Count"]
    st.dataframe(sentiment_summary)

    csv_gen = gen_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download General Notes", csv_gen, "general_notes.csv", "text/csv")

st.markdown("---")

# === GOVERNMENT POSTS SECTION ===
st.subheader("React to Government Updates")

for i, row in df.iterrows():
    st.markdown(f"### {row['title']}")
    st.image(row['image_url'], use_container_width=True)
    st.write(row['description'])

    # Initialize feedback store per post
    if row['title'] not in st.session_state.post_feedback:
        st.session_state.post_feedback[row['title']] = []

    col1, col2 = st.columns(2)
    with col1:
        reaction = st.radio("Reaction", ["Positive", "Neutral", "Negative"], key=f"react_{i}")
    with col2:
        comment = st.text_area("Your Comment", key=f"comment_{i}")

    if st.button("Submit", key=f"submit_{i}"):
        sentiment = "None"
        if comment.strip():
            polarity = TextBlob(comment).sentiment.polarity
            sentiment = (
                "Positive" if polarity > 0.2 else
                "Negative" if polarity < -0.2 else
                "Neutral"
            )

        entry = {
            "Reaction": reaction,
            "Comment": comment,
            "Analyzed Sentiment": sentiment
        }
        st.session_state.post_feedback[row['title']].append(entry)
        st.success("Feedback submitted!")

    # === SUMMARY TABLE PER POST ===
    feedback_list = st.session_state.post_feedback[row['title']]
    if feedback_list:
        st.markdown("#### Summary of Feedback for This Post")

        fb_df = pd.DataFrame(feedback_list)
        sentiment_counts = fb_df["Analyzed Sentiment"].value_counts().reset_index()
        sentiment_counts.columns = ["Sentiment", "Count"]
        st.dataframe(sentiment_counts)

        csv_fb = fb_df.to_csv(index=False).encode('utf-8')
        st.download_button(f"Download Feedback for {row['title']}", csv_fb, f"{row['title']}_feedback.csv", "text/csv")

    st.markdown("---")

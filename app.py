import streamlit as st
import pandas as pd
from textblob import TextBlob

st.set_page_config(page_title="Citizen Feedback Platform", layout="wide")

# Load posts
df = pd.read_csv("sample_posts.csv")

# Initialize feedback store
if 'post_feedback' not in st.session_state:
    st.session_state.post_feedback = {}

if 'general_notes' not in st.session_state:
    st.session_state.general_notes = []

# Sidebar Navigation
st.sidebar.title("Navigate")
option = st.sidebar.radio("Go to:", ["Write a Note to Government", "View & React to Government Posts"])

# === GENERAL NOTES PAGE ===
if option == "Write a Note to Government":
    st.title("Write a Note to the Government")
    st.markdown("This section allows you to submit general comments, praise, or concerns unrelated to any specific post.")

    general_note = st.text_area("Your Note", placeholder="Type your message to the government here...")

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
        st.markdown("### Summary of All General Notes")
        gen_df = pd.DataFrame(st.session_state.general_notes)
        sentiment_summary = gen_df["Sentiment"].value_counts().reset_index()
        sentiment_summary.columns = ["Sentiment", "Count"]
        st.dataframe(sentiment_summary)

        csv_gen = gen_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download General Notes", csv_gen, "general_notes.csv", "text/csv")

# === POST REACTIONS PAGE ===
elif option == "View & React to Government Posts":
    st.title("React to Government Updates")
    st.markdown("Give your reaction or comment on each update from public institutions.")

    for i, row in df.iterrows():
        st.markdown(f"### {row['title']}")
        st.image(row['image_url'], use_container_width=True)
        st.write(row['description'])

        if row['title'] not in st.session_state.post_feedback:
            st.session_state.post_feedback[row['title']] = []

        col1, col2 = st.columns(2)
        with col1:
            reaction = st.radio("React (Optional)", ["Positive", "Neutral", "Negative"], key=f"react_{i}", index=1)
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
                "Analyzed Sentiment": sentiment if comment.strip() else ""
            }
            st.session_state.post_feedback[row['title']].append(entry)
            st.success("Feedback submitted!")

        feedback_list = st.session_state.post_feedback[row['title']]
        if feedback_list:
            st.markdown("#### Summary of Feedback for This Post")
            fb_df = pd.DataFrame(feedback_list)

            if "Reaction" in fb_df and fb_df["Reaction"].any():
                st.markdown("**Reaction Counts:**")
                react_counts = fb_df["Reaction"].value_counts().reset_index()
                react_counts.columns = ["Reaction Type", "Count"]
                st.dataframe(react_counts)

            if "Analyzed Sentiment" in fb_df and fb_df["Analyzed Sentiment"].any():
                st.markdown("**Comment Sentiment Summary:**")
                sentiment_counts = fb_df["Analyzed Sentiment"].value_counts().reset_index()
                sentiment_counts.columns = ["Sentiment", "Count"]
                st.dataframe(sentiment_counts)

            csv_fb = fb_df.to_csv(index=False).encode('utf-8')
            st.download_button(f"Download Feedback for {row['title']}", csv_fb, f"{row['title']}_feedback.csv", "text/csv")

        st.markdown("---")

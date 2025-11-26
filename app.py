"""
app.py: A simple Streamlit web application to visualize YouTube engagement analytics and suggest content topics for maximum engagement.

This mini-app allows users to upload a CSV file containing metrics for their YouTube videos (as exported from the ingestion and analysis pipeline) and provides:
- A display of the top-performing videos by engagement score.
- Classification of each content item as a short or regular video based on duration.
- Suggested topics based on tags from the highest-engagement videos.

Usage:
1. Use the ingestion script (ingestion/yt_data_ingest.py) to fetch recent videos and their statistics from the YouTube Data API and export them to CSV.
2. Use the analysis script (analysis/engagement_analysis.py) to compute engagement scores and generate a cleaned CSV containing video metrics and tags.
3. Run this Streamlit app and upload the resulting CSV file:

    streamlit run app.py

The app will process the uploaded file and display analytics and recommendations.
"""

import pandas as pd
import streamlit as st

# Import functions from the analysis module. These functions should already exist in analysis/engagement_analysis.py
from analysis.engagement_analysis import compute_engagement_score, classify_content_type, suggest_content_topics

def main() -> None:
    """Run the Streamlit web app."""
    st.set_page_config(page_title="YouTube Engagement Optimizer", layout="centered")
    st.title("YouTube Engagement Optimizer")
    st.write(
        "Upload a CSV file containing metrics for your YouTube videos (views, likes, comments, shares, watch time, duration, and tags) to analyze engagement and receive topic suggestions."
    )

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])  # pragma: no mutate
    if uploaded_file is not None:
        # Read CSV into DataFrame
        df = pd.read_csv(uploaded_file)

        # Ensure necessary columns exist
        required_columns = {"video_id", "title", "duration", "views", "likes", "comments", "shares", "watch_time_hours", "tags"}
        missing = required_columns - set(df.columns)
        if missing:
            st.error(f"Missing required columns: {', '.join(sorted(missing))}.")
            return

        # Classify content type
        df["content_type"] = df["duration"].apply(classify_content_type)

        # Compute engagement score for each row
        df["engagement_score"] = df.apply(
            lambda row: compute_engagement_score(
                views=row["views"],
                likes=row["likes"],
                comments=row["comments"],
                shares=row["shares"],
                watch_time=row["watch_time_hours"],
                duration=row["duration"],
            ),
            axis=1,
        )

        # Display top 10 videos by engagement score
        top_n = st.slider("Number of top videos to display", min_value=5, max_value=20, value=10)
        top_videos = df.sort_values(by="engagement_score", ascending=False).head(top_n)

        st.subheader("Top Performing Videos")
        st.dataframe(top_videos[["video_id", "title", "content_type", "engagement_score"]])

        # Suggest content topics based on tags in top videos
        try:
            suggestions = suggest_content_topics(df, top_n=5)
            st.subheader("Suggested Topics for Future Content")
            st.write(", ".join(suggestions))
        except Exception:
            st.info("Could not generate suggestions because tag parsing failed or no tags available.")
    else:
        st.info("Please upload a CSV file to begin analysis.")


if __name__ == "__main__":
    main()

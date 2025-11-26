"""
Module for analyzing YouTube videos and shorts to determine high engagement and suggest content strategies.

This module defines classes and functions to load data from various sources (YouTube API, CSV exports), compute engagement metrics,
classify content as video or short, analyze trends across topics and durations, and generate recommendations for new content.

It is designed to be part of a larger data engineering project with streaming and batch pipelines.
"""

from dataclasses import dataclass
from typing import List, Tuple
import pandas as pd

@dataclass
class VideoRecord:
    video_id: str
    title: str
    publish_date: pd.Timestamp
    duration_sec: int
    views: int
    likes: int
    comments: int
    shares: int
    average_view_duration_sec: float
    tags: List[str]

def compute_engagement_score(row: pd.Series) -> float:
    """
    Compute a composite engagement score based on likes, comments, shares, and average view duration relative to duration.
    """
    like_weight = 1.0
    comment_weight = 1.5
    share_weight = 2.0
    watch_ratio_weight = 3.0
    watch_ratio = row["average_view_duration_sec"] / max(row["duration_sec"], 1)
    return (
        like_weight * row["likes"] +
        comment_weight * row["comments"] +
        share_weight * row["shares"] +
        watch_ratio_weight * watch_ratio * row["views"]
    )

def classify_content_type(duration_sec: int) -> str:
    """
    Classify content as 'short' if less than 60 seconds, otherwise 'video'.
    """
    return "short" if duration_sec < 60 else "video"

def analyze_engagement(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add engagement score and content type, then sort by score descending.
    """
    df = df.copy()
    df["content_type"] = df["duration_sec"].apply(classify_content_type)
    df["engagement_score"] = df.apply(compute_engagement_score, axis=1)
    return df.sort_values("engagement_score", ascending=False)

def suggest_topics(df: pd.DataFrame, top_n: int = 5) -> List[Tuple[str, int]]:
    """
    Suggest topics based on tags from top performing videos.
    """
    top_df = df.head(50)
    tag_counts = {}
    for tags in top_df["tags"]:
        for tag in tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_tags[:top_n]

def load_data(path: str) -> pd.DataFrame:
    """
    Load video data from a CSV or parquet file.
    """
    if path.endswith(".parquet"):
        df = pd.read_parquet(path)
    else:
        df = pd.read_csv(path)
    # Ensure tags column is lists
    if df["tags"].dtype == object:
        df["tags"] = df["tags"].apply(lambda x: eval(x) if isinstance(x, str) else x)
    return df

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Analyze YouTube engagement metrics and suggest content topics.")
    parser.add_argument("--input-path", required=True, help="Path to CSV or parquet file containing video metrics.")
    args = parser.parse_args()
    df = load_data(args.input_path)
    analysis_df = analyze_engagement(df)
    print("Top 10 videos by engagement:")
    print(analysis_df.head(10)[["video_id", "title", "engagement_score", "content_type"]])
    topics = suggest_topics(analysis_df, top_n=5)
    print("Suggested topics based on top performers:")
    for tag, count in topics:
        print(f"{tag}: {count}")

if __name__ == "__main__":
    main()

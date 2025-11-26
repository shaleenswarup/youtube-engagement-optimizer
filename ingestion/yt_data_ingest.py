"""
Module for ingesting YouTube data from the YouTube Data API.

This script fetches metadata and statistics for recent videos uploaded by a given channel and writes them to a CSV file.  
It can be orchestrated as part of a data pipeline to provide fresh inputs for downstream analytics.
"""

from typing import List, Dict
import os

try:
    from googleapiclient.discovery import build
except ImportError:
    build = None  # type: ignore

import pandas as pd

def get_youtube_client(api_key: str):
    """Create a YouTube Data API client using the provided API key."""
    if build is None:
        raise ImportError("googleapiclient is required for YouTube ingestion. Install via `pip install google-api-python-client`." )
    return build("youtube", "v3", developerKey=api_key)

def fetch_channel_videos(youtube, channel_id: str, max_results: int = 50) -> List[Dict]:
    """Fetch recent video metadata for a channel."""
    videos: List[Dict] = []
    request = youtube.search().list(
        part="id,snippet",
        channelId=channel_id,
        maxResults=max_results,
        type="video",
        order="date",
    )
    response = request.execute()
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        videos.append({
            "video_id": video_id,
            "title": snippet.get("title"),
            "published_at": snippet.get("publishedAt"),
        })
    return videos

def fetch_video_stats(youtube, video_ids: List[str]) -> List[Dict]:
    """Fetch statistics for a list of video IDs."""
    stats: List[Dict] = []
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i : i + 50]
        request = youtube.videos().list(
            part="statistics,contentDetails",
            id=",".join(batch_ids),
        )
        response = request.execute()
        for item in response.get("items", []):
            vid = item["id"]
            content_details = item.get("contentDetails", {})
            statistics = item.get("statistics", {})
            stats.append({
                "video_id": vid,
                "duration_iso": content_details.get("duration"),
                "views": int(statistics.get("viewCount", 0)),
                "likes": int(statistics.get("likeCount", 0)),
                "comments": int(statistics.get("commentCount", 0)),
            })
    return stats

def main() -> None:
    """Command-line interface for fetching YouTube channel data."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch YouTube channel video metadata and statistics and write them to a CSV file."
    )
    parser.add_argument("--channel-id", required=True, help="YouTube channel ID to fetch videos from.")
    parser.add_argument(
        "--output-path",
        default="videos.csv",
        help="Path to save output CSV file with video metadata and stats.",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=50,
        help="Number of recent videos to fetch (max 50 per API call).",
    )
    args = parser.parse_args()

    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "YOUTUBE_API_KEY environment variable must be set to use the YouTube Data API."
        )

    youtube = get_youtube_client(api_key)
    videos = fetch_channel_videos(youtube, args.channel_id, max_results=args.max_results)
    video_ids = [v["video_id"] for v in videos]
    stats = fetch_video_stats(youtube, video_ids)
    df_videos = pd.DataFrame(videos)
    df_stats = pd.DataFrame(stats)
    df = pd.merge(df_videos, df_stats, on="video_id", how="left")
    df.to_csv(args.output_path, index=False)
    print(f"Fetched {len(df)} videos and saved to {args.output_path}")

if __name__ == "__main__":
    main()

"""
YouTube channel scraper using Apify API.
Extracts video titles and subtitles/transcripts from a YouTube channel.
"""

import os
from typing import List, Dict, Optional
from apify_client import ApifyClient


class YouTubeScraper:
    """Handles scraping YouTube channel videos using Apify."""

    def __init__(self, api_token: str):
        """
        Initialize the YouTube scraper.

        Args:
            api_token: Apify API token
        """
        self.client = ApifyClient(api_token)

    def scrape_channel(
        self,
        channel_url: str,
        max_videos: int = 10
    ) -> List[Dict[str, str]]:
        """
        Scrape videos from a YouTube channel.

        Args:
            channel_url: URL of the YouTube channel
            max_videos: Maximum number of videos to scrape (from newest)

        Returns:
            List of dictionaries containing video data (title, url, transcript)
        """
        print(f"\n🔍 Scraping channel: {channel_url}")
        print(f"📊 Fetching up to {max_videos} videos...")

        # Configure the Apify actor run
        run_input = {
            "startUrls": [{"url": channel_url}],
            "maxResults": max_videos,
            "searchType": "channel",
            "includeSubtitles": True,  # Include subtitles/transcripts
        }

        # Run the actor and wait for it to finish
        print("⏳ Running Apify scraper...")
        run = self.client.actor("streamers/youtube-scraper").call(run_input=run_input)

        # Fetch results from the dataset
        videos = []
        print("📥 Fetching results...")

        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            video_data = {
                "title": item.get("title", "Untitled"),
                "url": item.get("url", ""),
                "video_id": item.get("id", ""),
                "transcript": self._extract_transcript(item),
                "description": item.get("description", ""),
                "duration": item.get("duration", ""),
                "views": item.get("viewCount", 0),
            }

            # Only add videos that have transcripts
            if video_data["transcript"]:
                videos.append(video_data)
                print(f"  ✓ {video_data['title'][:60]}...")
            else:
                print(f"  ⊗ {video_data['title'][:60]}... (no transcript)")

        print(f"\n✅ Successfully scraped {len(videos)} videos with transcripts")
        return videos

    def _extract_transcript(self, item: Dict) -> str:
        """
        Extract transcript/subtitles from video item.

        Args:
            item: Video data item from Apify

        Returns:
            Transcript text or empty string if not available
        """
        # Try to get subtitles from the item
        subtitles = item.get("subtitles", [])

        if not subtitles:
            return ""

        # Combine all subtitle text
        transcript_parts = []
        for subtitle in subtitles:
            if isinstance(subtitle, dict):
                text = subtitle.get("text", "")
                if text:
                    transcript_parts.append(text)
            elif isinstance(subtitle, str):
                transcript_parts.append(subtitle)

        return " ".join(transcript_parts).strip()


def test_scraper():
    """Test function for the YouTube scraper."""
    api_token = os.getenv("APIFY_API_TOKEN")

    if not api_token:
        print("Error: APIFY_API_TOKEN not set")
        return

    scraper = YouTubeScraper(api_token)

    # Test with a popular channel
    channel_url = "https://www.youtube.com/@mkbhd"
    videos = scraper.scrape_channel(channel_url, max_videos=3)

    print(f"\nFound {len(videos)} videos:")
    for video in videos:
        print(f"\nTitle: {video['title']}")
        print(f"URL: {video['url']}")
        print(f"Transcript length: {len(video['transcript'])} characters")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    test_scraper()

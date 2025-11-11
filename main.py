#!/usr/bin/env python3
"""
YouTube Channel RAG Tool
------------------------
A tool to scrape YouTube channel videos, extract transcripts,
and enable AI-powered chat using Gemini API File Search.

Usage:
    python main.py
"""

import os
import sys
from dotenv import load_dotenv

from youtube_scraper import YouTubeScraper
from file_manager import FileManager
from gemini_rag import GeminiRAG
from chat_interface import ChatInterface


def print_banner():
    """Print application banner."""
    print("\n" + "=" * 80)
    print("🎬 YouTube Channel RAG Tool")
    print("=" * 80)
    print("\nBuild a chatbot for any YouTube channel using AI-powered search!")
    print("=" * 80 + "\n")


def get_user_input():
    """
    Get channel URL and video count from user.

    Returns:
        Tuple of (channel_url, max_videos, channel_name)
    """
    print("📋 Setup")
    print("-" * 80)

    # Get channel URL
    while True:
        channel_url = input("\n🔗 Enter YouTube Channel URL: ").strip()

        if not channel_url:
            print("❌ URL cannot be empty. Please try again.")
            continue

        if "youtube.com" not in channel_url and "youtu.be" not in channel_url:
            print("❌ Invalid URL. Please enter a valid YouTube channel URL.")
            continue

        break

    # Get number of videos
    while True:
        try:
            max_videos_input = input("\n📊 How many videos to process (default: 10): ").strip()

            if not max_videos_input:
                max_videos = 10
                break

            max_videos = int(max_videos_input)

            if max_videos < 1:
                print("❌ Please enter a positive number.")
                continue

            if max_videos > 50:
                print("⚠️  Warning: Processing many videos may take a while and incur API costs.")
                confirm = input("   Continue? (y/n): ").strip().lower()
                if confirm != 'y':
                    continue

            break

        except ValueError:
            print("❌ Invalid number. Please enter a valid integer.")

    # Extract channel name from URL
    channel_name = channel_url.split('/')[-1].replace('@', '')

    print("\n" + "=" * 80)
    print(f"✅ Configuration:")
    print(f"   Channel: {channel_name}")
    print(f"   Videos to process: {max_videos}")
    print("=" * 80)

    return channel_url, max_videos, channel_name


def validate_environment():
    """
    Validate that required environment variables are set.

    Returns:
        Tuple of (apify_token, gemini_key) or None if validation fails
    """
    load_dotenv()

    apify_token = os.getenv("APIFY_API_TOKEN")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not apify_token:
        print("\n❌ Error: APIFY_API_TOKEN not found in environment variables")
        print("\n📝 Please:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Apify API token from https://console.apify.com/account/integrations")
        print("   3. Run the script again")
        return None

    if not gemini_key:
        print("\n❌ Error: GEMINI_API_KEY not found in environment variables")
        print("\n📝 Please:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Gemini API key from https://aistudio.google.com/app/apikey")
        print("   3. Run the script again")
        return None

    return apify_token, gemini_key


def main():
    """Main application entry point."""
    try:
        # Print banner
        print_banner()

        # Validate environment
        env_vars = validate_environment()
        if not env_vars:
            sys.exit(1)

        apify_token, gemini_key = env_vars

        # Get user input
        channel_url, max_videos, channel_name = get_user_input()

        # Step 1: Scrape YouTube channel
        print("\n" + "=" * 80)
        print("STEP 1: Scraping YouTube Channel")
        print("=" * 80)

        scraper = YouTubeScraper(apify_token)
        videos = scraper.scrape_channel(channel_url, max_videos)

        if not videos:
            print("\n❌ No videos with transcripts found. Exiting.")
            sys.exit(1)

        # Step 2: Create transcript files
        print("\n" + "=" * 80)
        print("STEP 2: Creating Transcript Files")
        print("=" * 80)

        file_manager = FileManager()
        file_paths = file_manager.create_transcript_files(videos)

        # Step 3: Upload to Gemini and setup RAG
        print("\n" + "=" * 80)
        print("STEP 3: Setting up Gemini File Search")
        print("=" * 80)

        rag = GeminiRAG(gemini_key)
        rag.upload_files(file_paths)

        # Step 4: Start chat interface
        print("\n" + "=" * 80)
        print("STEP 4: Starting Chat Interface")
        print("=" * 80)

        chat = ChatInterface(rag, channel_name)
        chat.start()

        # Cleanup
        print("\n" + "=" * 80)
        print("CLEANUP")
        print("=" * 80)

        cleanup = input("\n🗑️  Delete uploaded files from Gemini API? (y/n): ").strip().lower()
        if cleanup == 'y':
            rag.cleanup()

        cleanup_local = input("🗑️  Delete local transcript files? (y/n): ").strip().lower()
        if cleanup_local == 'y':
            file_manager.clear_files()

        print("\n✅ Done! Thank you for using YouTube Channel RAG Tool!")
        print("=" * 80 + "\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Exiting...")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

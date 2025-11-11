"""
File manager for creating and managing transcript files.
"""

import os
import re
from typing import List, Dict
from pathlib import Path


class FileManager:
    """Manages transcript file creation and storage."""

    def __init__(self, base_dir: str = "transcripts"):
        """
        Initialize the file manager.

        Args:
            base_dir: Base directory for storing transcript files
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    def create_transcript_files(self, videos: List[Dict[str, str]]) -> List[str]:
        """
        Create individual transcript files for each video.

        Args:
            videos: List of video dictionaries with title, url, and transcript

        Returns:
            List of file paths created
        """
        print(f"\n📝 Creating transcript files in '{self.base_dir}'...")

        file_paths = []

        for i, video in enumerate(videos, 1):
            # Create safe filename from video title
            filename = self._sanitize_filename(video["title"])
            file_path = self.base_dir / f"{i:03d}_{filename}.txt"

            # Create file content with metadata
            content = self._format_transcript(video)

            # Write to file
            file_path.write_text(content, encoding="utf-8")
            file_paths.append(str(file_path))

            print(f"  ✓ Created: {file_path.name}")

        print(f"\n✅ Created {len(file_paths)} transcript files")
        return file_paths

    def _sanitize_filename(self, title: str) -> str:
        """
        Convert video title to safe filename.

        Args:
            title: Video title

        Returns:
            Sanitized filename (without extension)
        """
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', title)
        # Replace spaces and special chars with underscores
        filename = re.sub(r'\s+', '_', filename)
        # Limit length
        filename = filename[:100]
        # Remove trailing dots and underscores
        filename = filename.rstrip('._')

        return filename or "video"

    def _format_transcript(self, video: Dict[str, str]) -> str:
        """
        Format video data into a structured transcript file.

        Args:
            video: Video dictionary

        Returns:
            Formatted transcript content
        """
        lines = [
            "=" * 80,
            f"VIDEO: {video['title']}",
            "=" * 80,
            f"URL: {video['url']}",
            f"Video ID: {video['video_id']}",
            f"Duration: {video.get('duration', 'N/A')}",
            f"Views: {video.get('views', 'N/A'):,}",
            "=" * 80,
            "",
            "DESCRIPTION:",
            video.get('description', 'No description available'),
            "",
            "=" * 80,
            "",
            "TRANSCRIPT:",
            video['transcript'],
            "",
            "=" * 80,
        ]

        return "\n".join(lines)

    def get_all_files(self) -> List[str]:
        """
        Get all transcript file paths.

        Returns:
            List of file paths
        """
        return [str(f) for f in self.base_dir.glob("*.txt")]

    def clear_files(self):
        """Remove all transcript files."""
        for file_path in self.base_dir.glob("*.txt"):
            file_path.unlink()

        print(f"🗑️  Cleared all files from '{self.base_dir}'")


def test_file_manager():
    """Test the file manager."""
    # Sample video data
    videos = [
        {
            "title": "Test Video #1: How to Build RAG",
            "url": "https://youtube.com/watch?v=test1",
            "video_id": "test1",
            "transcript": "This is a test transcript for video 1.",
            "description": "A test video",
            "duration": "10:30",
            "views": 1000,
        },
        {
            "title": "Test Video #2: AI/ML Basics",
            "url": "https://youtube.com/watch?v=test2",
            "video_id": "test2",
            "transcript": "This is a test transcript for video 2.",
            "description": "Another test video",
            "duration": "15:45",
            "views": 2000,
        }
    ]

    manager = FileManager()
    file_paths = manager.create_transcript_files(videos)

    print(f"\nCreated files:")
    for path in file_paths:
        print(f"  - {path}")


if __name__ == "__main__":
    test_file_manager()

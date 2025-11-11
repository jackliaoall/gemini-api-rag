"""
Gemini API File Search integration for RAG functionality.
Uses the new google.genai SDK (not the legacy google.generativeai).
"""

import os
import time
from typing import List, Dict
from google import genai
from google.genai import types


class GeminiRAG:
    """Handles Gemini API File Search for retrieval-augmented generation."""

    def __init__(self, api_key: str):
        """
        Initialize the Gemini RAG system.

        Args:
            api_key: Google Gemini API key
        """
        self.client = genai.Client(api_key=api_key)
        self.file_search_store = None
        self.uploaded_files = []

    def upload_files(self, file_paths: List[str]) -> List[str]:
        """
        Upload transcript files to Gemini API File Search store.

        Args:
            file_paths: List of file paths to upload

        Returns:
            List of uploaded file names
        """
        print(f"\n☁️  Setting up File Search store...")

        # Create file search store
        try:
            self.file_search_store = self.client.file_search_stores.create(
                config={'display_name': 'YouTube Transcripts RAG Store'}
            )
            print(f"✅ File Search store created: {self.file_search_store.name}")
        except Exception as e:
            print(f"❌ Error creating file search store: {e}")
            return []

        print(f"\n☁️  Uploading {len(file_paths)} files...")

        uploaded_names = []

        for file_path in file_paths:
            try:
                filename = os.path.basename(file_path)
                print(f"  ⏳ Uploading: {filename}...", end=" ", flush=True)

                # Upload file to file search store
                operation = self.client.file_search_stores.upload_to_file_search_store(
                    file=file_path,
                    file_search_store_name=self.file_search_store.name,
                    config={'display_name': filename}
                )

                # Wait for operation to complete
                while not operation.done:
                    time.sleep(2)
                    operation = self.client.operations.get(operation)

                if hasattr(operation, 'error') and operation.error:
                    print(f"❌ Failed: {operation.error}")
                    continue

                self.uploaded_files.append(filename)
                uploaded_names.append(filename)
                print(f"✓")

            except Exception as e:
                print(f"❌ Error: {e}")

        print(f"\n✅ Successfully uploaded {len(uploaded_names)} files")
        return uploaded_names

    def query(self, question: str, temperature: float = 0.7) -> Dict:
        """
        Query the RAG system with a question.

        Args:
            question: User's question
            temperature: Model temperature (0.0-1.0)

        Returns:
            Dictionary with response and citations
        """
        if not self.file_search_store:
            raise ValueError("File search store not initialized. Call upload_files() first.")

        try:
            # Generate response with file search
            # Use simplified syntax without types.Tool wrapper
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",  # File Search requires Gemini 2.0+
                contents=question,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    tools=[
                        types.FileSearch(
                            file_search_store_names=[self.file_search_store.name]
                        )
                    ]
                )
            )

            # Extract text and citations
            answer_text = response.text if hasattr(response, 'text') else str(response)

            result = {
                "answer": answer_text,
                "citations": self._extract_citations(response),
            }

            return result

        except Exception as e:
            return {
                "answer": f"Error generating response: {str(e)}",
                "citations": []
            }

    def _extract_citations(self, response) -> List[Dict]:
        """
        Extract citations from the response.

        Args:
            response: Gemini API response

        Returns:
            List of citation dictionaries
        """
        citations = []

        try:
            # Try to extract grounding metadata
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'grounding_metadata'):
                        metadata = candidate.grounding_metadata

                        # Extract grounding chunks
                        if hasattr(metadata, 'grounding_chunks'):
                            for chunk in metadata.grounding_chunks:
                                citation = {
                                    "text": getattr(chunk, 'text', ''),
                                    "source": getattr(chunk, 'source', 'Unknown'),
                                }
                                if citation["text"]:
                                    citations.append(citation)

                        # Extract search entry points
                        if hasattr(metadata, 'search_entry_point'):
                            entry = metadata.search_entry_point
                            if hasattr(entry, 'rendered_content'):
                                citations.append({
                                    "text": entry.rendered_content[:200] + "...",
                                    "source": "File Search"
                                })
        except Exception as e:
            print(f"⚠️  Warning: Could not extract citations: {e}")

        return citations

    def cleanup(self):
        """Delete file search store and all uploaded files."""
        if not self.file_search_store:
            print("⚠️  No file search store to clean up")
            return

        print("\n🗑️  Cleaning up file search store...")

        try:
            self.client.file_search_stores.delete(
                name=self.file_search_store.name
            )
            print(f"✅ Deleted file search store: {self.file_search_store.name}")
            self.file_search_store = None
            self.uploaded_files = []
        except Exception as e:
            print(f"❌ Error deleting file search store: {e}")

    def list_files(self):
        """List all uploaded files."""
        if not self.uploaded_files:
            print("\n📁 No files uploaded yet")
            return

        print(f"\n📁 Uploaded files ({len(self.uploaded_files)}):")
        for filename in self.uploaded_files:
            print(f"  - {filename}")


def test_gemini_rag():
    """Test the Gemini RAG functionality."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Error: GEMINI_API_KEY not set")
        return

    # Create a test file
    test_file = "test_transcript.txt"
    with open(test_file, "w") as f:
        f.write("""
        This is a test transcript about artificial intelligence.
        AI and machine learning are transforming how we interact with technology.
        Large language models like GPT and Gemini can understand and generate human-like text.
        The future of AI includes better reasoning, multimodal capabilities, and more efficient training.
        """)

    rag = GeminiRAG(api_key)

    try:
        # Upload files
        rag.upload_files([test_file])

        # List files
        rag.list_files()

        # Query
        print("\n💬 Testing query...")
        result = rag.query("What topics are covered in this transcript?")
        print(f"\n🤖 Answer:\n{result['answer']}")

        if result['citations']:
            print(f"\n📚 Citations ({len(result['citations'])}):")
            for i, citation in enumerate(result['citations'], 1):
                print(f"  [{i}] {citation.get('text', '')[:100]}...")

    finally:
        # Cleanup
        rag.cleanup()
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"🗑️  Deleted test file: {test_file}")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    test_gemini_rag()

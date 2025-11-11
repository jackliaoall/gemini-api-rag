"""
Gemini API File Search integration for RAG functionality.
"""

import os
from typing import List, Optional
import google.generativeai as genai
from google.generativeai import caching
import time


class GeminiRAG:
    """Handles Gemini API File Search for retrieval-augmented generation."""

    def __init__(self, api_key: str):
        """
        Initialize the Gemini RAG system.

        Args:
            api_key: Google Gemini API key
        """
        genai.configure(api_key=api_key)
        self.uploaded_files = []
        self.model = None

    def upload_files(self, file_paths: List[str]) -> List[str]:
        """
        Upload transcript files to Gemini API.

        Args:
            file_paths: List of file paths to upload

        Returns:
            List of uploaded file URIs
        """
        print(f"\n☁️  Uploading {len(file_paths)} files to Gemini API...")

        uploaded_uris = []

        for file_path in file_paths:
            try:
                # Upload file
                print(f"  ⏳ Uploading: {os.path.basename(file_path)}...", end=" ")

                uploaded_file = genai.upload_file(file_path)

                # Wait for file to be processed
                while uploaded_file.state.name == "PROCESSING":
                    time.sleep(1)
                    uploaded_file = genai.get_file(uploaded_file.name)

                if uploaded_file.state.name == "FAILED":
                    print(f"❌ Failed")
                    continue

                self.uploaded_files.append(uploaded_file)
                uploaded_uris.append(uploaded_file.uri)
                print(f"✓")

            except Exception as e:
                print(f"❌ Error: {e}")

        print(f"\n✅ Successfully uploaded {len(uploaded_uris)} files")
        return uploaded_uris

    def create_model_with_files(self, model_name: str = "gemini-1.5-flash-8b"):
        """
        Create a Gemini model configured with uploaded files for File Search.

        Args:
            model_name: Name of the Gemini model to use
        """
        if not self.uploaded_files:
            raise ValueError("No files uploaded. Call upload_files() first.")

        print(f"\n🤖 Creating model with File Search enabled...")

        # Create model with File Search tool
        self.model = genai.GenerativeModel(
            model_name=model_name,
            tools=[
                genai.protos.Tool(
                    file_search=genai.protos.FileSearchTool()
                )
            ]
        )

        print(f"✅ Model '{model_name}' ready with {len(self.uploaded_files)} files")

    def query(self, question: str, temperature: float = 0.7) -> dict:
        """
        Query the RAG system with a question.

        Args:
            question: User's question
            temperature: Model temperature (0.0-1.0)

        Returns:
            Dictionary with response and citations
        """
        if not self.model:
            raise ValueError("Model not initialized. Call create_model_with_files() first.")

        try:
            # Generate response with file search
            response = self.model.generate_content(
                question,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                ),
                tools=[
                    genai.protos.Tool(
                        file_search=genai.protos.FileSearchTool(
                            file_ids=[f.name for f in self.uploaded_files]
                        )
                    )
                ]
            )

            # Extract text and citations
            result = {
                "answer": response.text,
                "citations": self._extract_citations(response),
            }

            return result

        except Exception as e:
            return {
                "answer": f"Error generating response: {str(e)}",
                "citations": []
            }

    def _extract_citations(self, response) -> List[dict]:
        """
        Extract citations from the response.

        Args:
            response: Gemini API response

        Returns:
            List of citation dictionaries
        """
        citations = []

        # Check if response has grounding metadata
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]

            if hasattr(candidate, 'grounding_metadata'):
                metadata = candidate.grounding_metadata

                if hasattr(metadata, 'grounding_chunks'):
                    for chunk in metadata.grounding_chunks:
                        citation = {
                            "text": getattr(chunk, 'text', ''),
                            "source": getattr(chunk, 'source', 'Unknown'),
                        }
                        citations.append(citation)

        return citations

    def cleanup(self):
        """Delete uploaded files from Gemini API."""
        print("\n🗑️  Cleaning up uploaded files...")

        for uploaded_file in self.uploaded_files:
            try:
                genai.delete_file(uploaded_file.name)
                print(f"  ✓ Deleted: {uploaded_file.display_name}")
            except Exception as e:
                print(f"  ❌ Error deleting {uploaded_file.display_name}: {e}")

        self.uploaded_files = []
        print("✅ Cleanup complete")

    def list_files(self):
        """List all uploaded files."""
        print("\n📁 Uploaded files:")
        for f in self.uploaded_files:
            print(f"  - {f.display_name} ({f.uri})")


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
        """)

    rag = GeminiRAG(api_key)

    try:
        # Upload files
        rag.upload_files([test_file])

        # Create model
        rag.create_model_with_files()

        # Query
        result = rag.query("What is this transcript about?")
        print(f"\nAnswer: {result['answer']}")

        if result['citations']:
            print("\nCitations:")
            for citation in result['citations']:
                print(f"  - {citation}")

    finally:
        # Cleanup
        rag.cleanup()
        os.remove(test_file)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    test_gemini_rag()

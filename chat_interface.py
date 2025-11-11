"""
Interactive chat interface for querying YouTube video transcripts.
"""

from typing import Optional
from gemini_rag import GeminiRAG


class ChatInterface:
    """Interactive chat interface for RAG queries."""

    def __init__(self, rag: GeminiRAG, channel_name: str = "YouTube Channel"):
        """
        Initialize the chat interface.

        Args:
            rag: GeminiRAG instance with uploaded files
            channel_name: Name of the YouTube channel for display
        """
        self.rag = rag
        self.channel_name = channel_name
        self.history = []

    def start(self):
        """Start the interactive chat session."""
        self._print_welcome()

        while True:
            try:
                # Get user input
                question = input("\n💬 You: ").strip()

                # Check for exit commands
                if question.lower() in ["exit", "quit", "q", "bye"]:
                    self._print_goodbye()
                    break

                # Skip empty questions
                if not question:
                    continue

                # Special commands
                if question.lower() == "help":
                    self._print_help()
                    continue

                if question.lower() == "history":
                    self._print_history()
                    continue

                if question.lower() == "clear":
                    self.history = []
                    print("✅ History cleared")
                    continue

                # Query the RAG system
                print("\n🤔 Thinking...", end=" ", flush=True)
                result = self.rag.query(question)
                print("\r", end="")  # Clear the "Thinking..." message

                # Display response
                self._display_response(result)

                # Save to history
                self.history.append({
                    "question": question,
                    "answer": result["answer"],
                    "citations": result.get("citations", [])
                })

            except KeyboardInterrupt:
                print("\n")
                self._print_goodbye()
                break

            except Exception as e:
                print(f"\n❌ Error: {e}")

    def _print_welcome(self):
        """Print welcome message."""
        print("\n" + "=" * 80)
        print(f"🎬 YouTube Channel RAG Chat - {self.channel_name}")
        print("=" * 80)
        print("\nWelcome! Ask me anything about the videos from this channel.")
        print("\nCommands:")
        print("  - Type 'help' for help")
        print("  - Type 'history' to see conversation history")
        print("  - Type 'clear' to clear history")
        print("  - Type 'exit', 'quit', or 'q' to exit")
        print("\n" + "=" * 80)

    def _print_goodbye(self):
        """Print goodbye message."""
        print("\n" + "=" * 80)
        print("👋 Thanks for chatting! Goodbye!")
        print("=" * 80)

    def _print_help(self):
        """Print help information."""
        print("\n" + "=" * 80)
        print("📖 HELP")
        print("=" * 80)
        print("\nThis is a RAG (Retrieval-Augmented Generation) chatbot.")
        print("It uses the video transcripts from the YouTube channel to answer your questions.")
        print("\nTips:")
        print("  - Ask specific questions about topics covered in the videos")
        print("  - Request summaries or explanations")
        print("  - Ask for comparisons between different videos")
        print("  - Citations show which parts of the transcripts were used")
        print("\nCommands:")
        print("  - help     : Show this help message")
        print("  - history  : View conversation history")
        print("  - clear    : Clear conversation history")
        print("  - exit/quit: Exit the chat")
        print("=" * 80)

    def _print_history(self):
        """Print conversation history."""
        if not self.history:
            print("\n📝 No conversation history yet.")
            return

        print("\n" + "=" * 80)
        print("📝 CONVERSATION HISTORY")
        print("=" * 80)

        for i, entry in enumerate(self.history, 1):
            print(f"\n[{i}] You: {entry['question']}")
            print(f"    Bot: {entry['answer'][:200]}...")

        print("\n" + "=" * 80)

    def _display_response(self, result: dict):
        """
        Display the response from the RAG system.

        Args:
            result: Dictionary with 'answer' and 'citations'
        """
        print(f"\n🤖 Assistant:\n")
        print(result["answer"])

        # Display citations if available
        citations = result.get("citations", [])
        if citations:
            print(f"\n📚 Sources ({len(citations)} citations):")
            for i, citation in enumerate(citations, 1):
                source = citation.get("source", "Unknown")
                text = citation.get("text", "")
                if text:
                    print(f"  [{i}] {text[:100]}...")
                else:
                    print(f"  [{i}] {source}")


def test_chat_interface():
    """Test the chat interface with mock data."""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set")
        return

    # Create a test file
    test_file = "test_chat_transcript.txt"
    with open(test_file, "w") as f:
        f.write("""
        Video: Introduction to Machine Learning

        In this video, we discuss the basics of machine learning.
        Machine learning is a subset of artificial intelligence that enables
        computers to learn from data without being explicitly programmed.

        We cover three main types:
        1. Supervised Learning - learning from labeled data
        2. Unsupervised Learning - finding patterns in unlabeled data
        3. Reinforcement Learning - learning through trial and error
        """)

    rag = GeminiRAG(api_key)

    try:
        print("Setting up test environment...")
        rag.upload_files([test_file])
        rag.create_model_with_files()

        # Start chat
        chat = ChatInterface(rag, "Test Channel")
        chat.start()

    finally:
        rag.cleanup()
        os.remove(test_file)


if __name__ == "__main__":
    test_chat_interface()

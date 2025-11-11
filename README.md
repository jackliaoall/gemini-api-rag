# YouTube Channel RAG Tool

Build an AI-powered chatbot for any YouTube channel using Retrieval-Augmented Generation (RAG).

This tool scrapes video transcripts from a YouTube channel using Apify, stores them in Gemini API File Search, and provides an interactive chat interface to ask questions about the videos.

## Features

- **YouTube Scraping**: Extract video titles and subtitles from any YouTube channel
- **Automatic Indexing**: Upload transcripts to Gemini API with automatic chunking and embedding
- **RAG Chat**: Ask questions and get answers based on actual video content
- **Citations**: See which parts of the transcripts were used to generate answers
- **Interactive CLI**: Simple command-line interface for easy interaction

## Prerequisites

- Python 3.9 or higher (required for google-genai SDK)
- [Apify API Token](https://console.apify.com/account/integrations)
- [Google Gemini API Key](https://aistudio.google.com/app/apikey)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd gemini-api-rag
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

**Important:** This project uses the new `google-genai` SDK (not the legacy `google-generativeai`). File Search is only available in the new SDK, which requires Python 3.9+.

3. Set up environment variables:
```bash
cp .env.example .env
```

4. Edit `.env` and add your API keys:
```
APIFY_API_TOKEN=your_apify_api_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

## Usage

Run the main application:

```bash
python main.py
```

The application will guide you through:

1. **Enter YouTube Channel URL**: Provide the URL of any YouTube channel
   - Example: `https://www.youtube.com/@mkbhd`

2. **Specify Video Count**: Choose how many videos to process (from newest to oldest)
   - Default: 10 videos
   - Warning: Processing many videos may take time and incur API costs

3. **Wait for Processing**:
   - Videos are scraped and transcripts extracted
   - Files are created and uploaded to Gemini API
   - RAG system is initialized

4. **Chat Interface**: Ask questions about the channel's videos
   - Ask about specific topics covered in videos
   - Request summaries or explanations
   - Compare information across multiple videos

## Example Interaction

```
🔗 Enter YouTube Channel URL: https://www.youtube.com/@mkbhd
📊 How many videos to process: 5

[Scraping and processing...]

💬 You: What topics are covered in these videos?
🤖 Assistant: Based on the transcripts, the videos cover...

💬 You: Tell me about the smartphone reviews
🤖 Assistant: The channel has reviewed several smartphones...

Commands:
  - help     : Show help message
  - history  : View conversation history
  - clear    : Clear history
  - exit/quit: Exit chat
```

## Project Structure

```
gemini-api-rag/
├── main.py               # Main entry point
├── youtube_scraper.py    # Apify YouTube scraping
├── file_manager.py       # Transcript file management
├── gemini_rag.py         # Gemini API File Search integration
├── chat_interface.py     # Interactive chat interface
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
├── .gitignore           # Git ignore file
└── README.md            # This file
```

## How It Works

1. **Scraping**: Uses Apify's YouTube Scraper actor to extract video metadata and subtitles
2. **File Creation**: Creates individual text files for each video with title, description, and transcript
3. **Upload to Gemini**: Uploads files to Gemini API which handles:
   - Automatic text chunking
   - Semantic embedding generation
   - Vector search indexing
4. **RAG Chat**: Uses Gemini's File Search tool to:
   - Retrieve relevant transcript segments
   - Generate contextual answers
   - Provide citations to source material

## API Costs

### Apify
- Free tier includes limited runs
- See [Apify Pricing](https://apify.com/pricing) for details

### Gemini API
- File uploads and storage: **FREE**
- Embedding generation (one-time): **$0.15 per 1M tokens**
- Chat queries: Standard Gemini API pricing
- See [Gemini Pricing](https://ai.google.dev/pricing) for details

## Limitations

- Only works with videos that have subtitles/captions
- Maximum file size limits apply (check Gemini API docs)
- Some channels may have restrictions on scraping
- Processing many videos can take time

## Troubleshooting

### No videos found
- Ensure the channel URL is correct
- Check if videos have subtitles/captions enabled
- Try increasing the number of videos to process

### API errors
- Verify your API keys are correct in `.env`
- Check API rate limits and quotas
- Ensure you have credits in your Apify account

### Upload failures
- Check your internet connection
- Verify file sizes are within limits
- Review Gemini API status

## Development

### Running Tests

Each module includes a test function:

```bash
# Test YouTube scraper
python youtube_scraper.py

# Test file manager
python file_manager.py

# Test Gemini RAG
python gemini_rag.py

# Test chat interface
python chat_interface.py
```

### Environment Variables

Required variables in `.env`:
- `APIFY_API_TOKEN`: Your Apify API token
- `GEMINI_API_KEY`: Your Google Gemini API key

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - feel free to use this project for any purpose.

## Acknowledgments

- [Apify](https://apify.com/) for YouTube scraping capabilities
- [Google Gemini](https://ai.google.dev/) for File Search and RAG functionality

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation:
   - [Apify YouTube Scraper](https://apify.com/streamers/youtube-scraper)
   - [Gemini File Search](https://ai.google.dev/gemini-api/docs/file-search)
3. Open an issue in this repository

# Pymavi

Python SDK for the Mavi Video AI Platform. This SDK provides a simple and intuitive interface to interact with the Mavi API for video processing, search, and analysis.

## Installation

```bash
pip install pymavi
```

## Quick Start

```python
from pymavi import MaviClient

# Initialize the client
client = MaviClient(api_key="your_api_key")

# Upload a video
response = client.upload_video(
    video_path="path/to/video.mp4",
    callback_uri="https://your-callback-url.com/webhook"
)

# Search for videos
results = client.search_video("find me videos with cars")

# Chat with videos
response = client.chat_with_videos(
    video_nos=["video_id_1", "video_id_2"],
    message="What's happening in these videos?",
    stream=True
)
```

## Features

- Video upload and management
- Natural language video search
- Key clip extraction
- AI-powered video chat
- Comprehensive error handling
- Type hints and documentation

## API Reference

### MaviClient

The main client class for interacting with the Mavi API.

#### Methods

- `upload_video(video_path: str, callback_uri: Optional[str] = None) -> Dict[str, Any]`
- `search_video_metadata(start_time: Optional[int] = None, end_time: Optional[int] = None, video_status: str = "PARSE", range_bucket: int = 1, num_results: int = 10) -> Dict[str, Any]`
- `search_video(search_query: str) -> Dict[str, Any]`
- `search_key_clip(search_query: str, video_ids: Optional[List[str]] = None) -> Dict[str, Any]`
- `chat_with_videos(video_nos: List[str], message: str, history: Optional[List[Dict[str, str]]] = None, stream: bool = False) -> Union[str, Dict[str, Any]]`
- `delete_video(video_ids: List[str]) -> Dict[str, Any]`

### Exceptions

- `MaviError`: Base exception for all Pymavi-related errors
- `MaviAuthenticationError`: Raised when there are authentication-related errors
- `MaviAPIError`: Raised when the API returns an error response
- `MaviValidationError`: Raised when there are validation errors in the input parameters

## Development

1. Clone the repository
2. Install development dependencies: `pip install -e ".[dev]"`
3. Run tests: `pytest`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

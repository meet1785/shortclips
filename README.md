# Short Clips AI 🎬

A free AI-powered tool that converts long videos into viral 15-60 second clips using Python, FastAPI, and MoviePy. Process videos locally with zero paid APIs!

## Features 🚀

- **Video Download**: Download videos from YouTube and other platforms using yt-dlp
- **AI Transcription**: Automatic speech-to-text with OpenAI Whisper
- **Scene Detection**: Intelligent scene detection using PySceneDetect
- **AI Content Analysis**: Find key moments and generate viral titles using Google Gemini Pro
- **Video Processing**: Professional editing with MoviePy and FFmpeg
- **Text Overlays**: Attention-grabbing text hooks for the first 3 seconds
- **Cinematic Effects**: Smooth zoom effects for engagement
- **Background Music**: Copyright-free music from Freesound API
- **9:16 Format**: Perfect vertical video for TikTok, Reels, and Shorts
- **Thumbnails**: Auto-generated thumbnails for each clip
- **Viral Titles**: AI-generated engaging titles

## Tech Stack 💻

- **Backend**: FastAPI
- **Video Processing**: MoviePy, FFmpeg
- **Video Download**: yt-dlp
- **Transcription**: OpenAI Whisper
- **Scene Detection**: PySceneDetect
- **AI Analysis**: Google Gemini Pro (Free API)
- **Music**: Freesound API (Free)
- **Language**: Python 3.8+

## Installation 🔧

### Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system

#### Install FFmpeg:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

### Setup

1. Clone the repository:
```bash
git clone https://github.com/meet1785/shortclips.git
cd shortclips
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
- **GEMINI_API_KEY**: Get free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **FREESOUND_API_KEY** (optional): Get free API key from [Freesound](https://freesound.org/apiv2/apply/)

## Usage 📖

### Start the Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Access interactive API docs at: `http://localhost:8000/docs`

### Process a Video URL

```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=YOUR_VIDEO_ID",
    "num_clips": 3,
    "add_music": true,
    "add_zoom": true
  }'
```

### Upload and Process Local Video

```bash
curl -X POST "http://localhost:8000/process-local" \
  -F "file=@/path/to/your/video.mp4" \
  -F "num_clips=3"
```

### Python Example

```python
import requests

# Process a YouTube video
response = requests.post(
    "http://localhost:8000/process",
    json={
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "num_clips": 3,
        "add_music": True,
        "add_zoom": True
    }
)

results = response.json()
print(f"Generated {len(results['clips'])} clips!")

for clip in results['clips']:
    print(f"Clip: {clip['video_path']}")
    print(f"Title: {clip['title']}")
    print(f"Hook: {clip['text_hook']}")
```

## API Endpoints 🌐

### `POST /process`
Process a video URL and generate clips.

**Request Body:**
```json
{
  "video_url": "https://youtube.com/watch?v=...",
  "num_clips": 3,
  "add_music": true,
  "add_zoom": true
}
```

### `POST /process-local`
Upload and process a local video file.

**Form Data:**
- `file`: Video file
- `num_clips`: Number of clips (default: 3)
- `add_music`: Add background music (default: true)
- `add_zoom`: Add zoom effects (default: true)

### `GET /video-info?video_url=...`
Get video information without downloading.

### `GET /clips`
List all generated clips.

### `GET /clips/{clip_name}`
Download a specific clip.

### `GET /thumbnails/{thumbnail_name}`
Download a specific thumbnail.

### `DELETE /clips/{clip_name}`
Delete a clip and its thumbnail.

## Configuration ⚙️

Edit `.env` to customize settings:

```env
# API Keys
GEMINI_API_KEY=your_gemini_api_key
FREESOUND_API_KEY=your_freesound_api_key

# Server
HOST=0.0.0.0
PORT=8000

# Video Processing
MIN_CLIP_DURATION=15
MAX_CLIP_DURATION=60
TARGET_ASPECT_RATIO=9:16
OUTPUT_RESOLUTION=1080x1920
```

## Output Files 📁

Generated clips are saved in the `outputs/` directory:
- `clip_1.mp4` - First generated clip
- `clip_1_thumb.jpg` - Thumbnail for first clip
- `clip_2.mp4` - Second generated clip
- etc.

## Project Structure 📂

```
shortclips/
├── main.py                 # FastAPI application
├── orchestrator.py         # Main processing pipeline
├── video_downloader.py     # Video download (yt-dlp)
├── audio_transcriber.py    # Audio transcription (Whisper)
├── scene_detector.py       # Scene detection (PySceneDetect)
├── content_analyzer.py     # AI analysis (Gemini Pro)
├── music_manager.py        # Music management (Freesound)
├── video_processor.py      # Video processing (MoviePy)
├── config.py               # Configuration
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## How It Works 🔍

1. **Download**: Video is downloaded using yt-dlp
2. **Transcribe**: Audio is transcribed with Whisper for precise timestamps
3. **Detect**: Scenes are detected using PySceneDetect
4. **Analyze**: Gemini Pro AI analyzes content to find viral moments
5. **Select**: Best segments are selected based on AI analysis and scene boundaries
6. **Generate**: For each clip:
   - AI generates a viral title
   - AI creates a text hook
   - Video is cropped to 9:16 format
   - Zoom effects are applied
   - Text overlay is added
   - Background music is mixed in
   - Thumbnail is generated
7. **Export**: Final clips are saved as ready-to-upload MP4 files

## Performance Tips 🚄

- Use `base` Whisper model for faster processing (default)
- Use `small` or `medium` for better accuracy (slower)
- Disable zoom effects for faster processing
- Skip music if Freesound API is not configured
- Process shorter videos for quicker results

## Troubleshooting 🔧

### FFmpeg Not Found
Install FFmpeg and ensure it's in your system PATH.

### Whisper Model Download
First run will download Whisper model (~140MB for base model).

### Memory Issues
For large videos, consider:
- Using a smaller Whisper model
- Processing shorter segments
- Increasing system RAM

### API Key Errors
Ensure your `.env` file has valid API keys:
- Gemini Pro: [Get free key](https://makersuite.google.com/app/apikey)
- Freesound: [Get free key](https://freesound.org/apiv2/apply/)

## Inspired By 🌟

- [faceless.io](https://faceless.io) - AI video automation
- [OpusClip](https://opus.pro) - AI video clipping

## License 📄

MIT License - See LICENSE file for details

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## Roadmap 🗺️

- [ ] Web UI for easier interaction
- [ ] Batch processing multiple videos
- [ ] Custom text styles and animations
- [ ] More video effects (slow-mo, speed-up)
- [ ] Social media auto-posting
- [ ] Multi-language support
- [ ] GPU acceleration
- [ ] Docker deployment

## Support 💬

For issues and questions, please open an issue on GitHub.

---

Made with ❤️ using free and open-source tools
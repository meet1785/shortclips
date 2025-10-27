# Quick Start Guide

## 1. Prerequisites

- Python 3.8 or higher
- FFmpeg
- Git (for cloning the repository)

### Install FFmpeg

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
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract and add to PATH

Verify installation:
```bash
ffmpeg -version
```

## 2. Installation

Clone the repository:
```bash
git clone https://github.com/meet1785/shortclips.git
cd shortclips
```

Create virtual environment:
```bash
python -m venv venv
```

Activate virtual environment:
```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

This will install:
- FastAPI & Uvicorn (API server)
- yt-dlp (video downloading)
- OpenAI Whisper (transcription)
- PySceneDetect (scene detection)
- MoviePy (video editing)
- Google Generative AI (AI analysis)
- And other required libraries

**Note:** First run will download Whisper model (~140MB for base model).

## 3. Configuration

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

### Get Gemini API Key (Required)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key and add to `.env`:
   ```
   GEMINI_API_KEY=your_key_here
   ```

### Get Freesound API Key (Optional)
1. Visit [Freesound API](https://freesound.org/apiv2/apply/)
2. Create account and apply for API key
3. Add to `.env`:
   ```
   FREESOUND_API_KEY=your_key_here
   ```

Note: Freesound is optional. Without it, clips won't have background music.

## 4. First Run

Test your setup:
```bash
python demo.py
```

This checks if all dependencies are installed correctly.

## 5. Usage

### Option A: Command Line

Process a YouTube video:
```bash
python cli.py "https://www.youtube.com/watch?v=YOUR_VIDEO_ID" -n 3
```

Process a local video:
```bash
python cli.py /path/to/video.mp4 -n 3
```

### Option B: API Server

Start the server:
```bash
python main.py
```

Visit: http://localhost:8000/docs

Use the interactive API documentation to:
- Process videos from URLs
- Upload and process local videos
- Download generated clips

### Option C: Python Module

```python
from orchestrator import ClipOrchestrator

orchestrator = ClipOrchestrator()

results = orchestrator.process_video(
    video_url="https://www.youtube.com/watch?v=...",
    num_clips=3
)

for clip in results['clips']:
    print(f"Generated: {clip['video_path']}")
```

## 6. First Video Processing

Example with a short YouTube video:

```bash
python cli.py "https://www.youtube.com/watch?v=jNQXAC9IVRw" -n 2
```

This will:
1. Download the video
2. Transcribe audio with Whisper
3. Detect scene changes
4. Analyze content with Gemini AI
5. Generate 2 viral clips
6. Add text hooks and effects
7. Save to `outputs/` directory

Processing time depends on video length:
- 5-minute video: ~3-5 minutes
- 15-minute video: ~10-15 minutes
- 30-minute video: ~20-30 minutes

## 7. View Results

Generated clips are in the `outputs/` directory:
```
outputs/
├── clip_1.mp4          # First clip
├── clip_1_thumb.jpg    # Thumbnail
├── clip_2.mp4          # Second clip
├── clip_2_thumb.jpg    # Thumbnail
└── ...
```

Each clip is:
- 15-60 seconds long
- 9:16 vertical format (1080x1920)
- Ready to upload to TikTok/Reels/Shorts
- Includes text hook, effects, and music (if enabled)

## 8. Troubleshooting

### "ModuleNotFoundError"
Solution: Activate virtual environment and reinstall:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### "FFmpeg not found"
Solution: Install FFmpeg and ensure it's in PATH

### "GEMINI_API_KEY not configured"
Solution: Add your API key to `.env` file

### "Out of memory"
Solutions:
- Process shorter videos
- Use smaller Whisper model (edit `orchestrator.py` line 20)
- Close other applications

### "Video download failed"
Solutions:
- Check internet connection
- Verify video URL is accessible
- Try a different video
- Update yt-dlp: `pip install --upgrade yt-dlp`

### Processing is slow
Tips:
- Use `base` Whisper model (default, fastest)
- Disable zoom effects: `--no-zoom`
- Disable music: `--no-music`
- Process shorter videos

## 9. Next Steps

- Read [EXAMPLES.md](EXAMPLES.md) for more usage examples
- Explore the API at http://localhost:8000/docs
- Customize settings in `.env`
- Integrate into your workflow

## 10. Common Workflows

### Content Creator Workflow
```bash
# 1. Download and process video
python cli.py "https://youtube.com/watch?v=..." -n 5

# 2. Review generated clips in outputs/

# 3. Upload best clips to social media
```

### Batch Processing
```bash
# Process multiple videos
python cli.py "video1_url" -n 3
python cli.py "video2_url" -n 3
python cli.py "video3_url" -n 3
```

### API Integration
Use the FastAPI server to integrate with your own applications:
1. Start server: `python main.py`
2. Make HTTP requests from your app
3. Download generated clips programmatically

## Need Help?

- Check [README.md](README.md) for detailed information
- See [EXAMPLES.md](EXAMPLES.md) for code examples
- Open an issue on GitHub for bugs/questions

Happy clipping! 🎬✨

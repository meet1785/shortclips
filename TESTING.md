# Testing Guide

## Manual Testing

### Prerequisites
1. Install all dependencies: `pip install -r requirements.txt`
2. Install FFmpeg
3. Set up API keys in `.env`

### Test 1: Basic Setup Verification

```bash
python demo.py
```

**Expected Output:**
- All dependencies checked ✓
- FFmpeg found ✓
- API keys configured ✓
- Directories created ✓

### Test 2: Configuration Loading

```bash
python -c "from config import settings; print(f'Config loaded: Port={settings.port}')"
```

**Expected Output:**
```
Config loaded: Port=8000
```

### Test 3: Video Downloader

Create a test file `test_downloader.py`:

```python
from video_downloader import VideoDownloader

downloader = VideoDownloader()

# Test getting video info
info = downloader.get_video_info("https://www.youtube.com/watch?v=jNQXAC9IVRw")
print(f"Title: {info['title']}")
print(f"Duration: {info['duration']}s")
```

Run:
```bash
python test_downloader.py
```

### Test 4: API Server

Start the server:
```bash
python main.py
```

Test endpoints:
```bash
# Health check
curl http://localhost:8000/health

# Get video info
curl "http://localhost:8000/video-info?video_url=https://www.youtube.com/watch?v=jNQXAC9IVRw"
```

### Test 5: CLI Processing

Test with a short video:

```bash
python cli.py "https://www.youtube.com/watch?v=jNQXAC9IVRw" -n 2 --no-music
```

**Expected:**
- Video downloads
- Transcription completes
- Scenes detected
- 2 clips generated in `outputs/`

### Test 6: Full Pipeline

Test complete processing with all features:

```bash
python cli.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -n 3
```

**Expected Output:**
- Downloads video ✓
- Transcribes audio ✓
- Detects scenes ✓
- Analyzes content ✓
- Downloads music (if API key set) ✓
- Generates 3 clips ✓
- Creates thumbnails ✓

### Test 7: Local Video Processing

Test with a local file:

```bash
python cli.py /path/to/video.mp4 -n 2
```

## Component Testing

### Test Audio Transcriber

```python
from audio_transcriber import AudioTranscriber

transcriber = AudioTranscriber(model_size="base")
result = transcriber.transcribe("/path/to/video.mp4")

print(f"Transcript: {result['text'][:200]}...")
print(f"Segments: {len(result['segments'])}")
print(f"Language: {result['language']}")
```

### Test Scene Detector

```python
from scene_detector import SceneDetector

detector = SceneDetector(threshold=27.0)
scenes = detector.detect_scenes("/path/to/video.mp4")

for scene in scenes[:5]:
    print(f"Scene {scene['scene_number']}: {scene['start']:.1f}s - {scene['end']:.1f}s")
```

### Test Content Analyzer

```python
from content_analyzer import ContentAnalyzer

analyzer = ContentAnalyzer()

# Test viral title generation
title = analyzer.generate_viral_title("Amazing discovery in science")
print(f"Title: {title}")

# Test text hook generation
hook = analyzer.generate_text_hook("You won't believe this")
print(f"Hook: {hook}")
```

### Test Music Manager

```python
from music_manager import MusicManager

manager = MusicManager()

# Search for music
tracks = manager.search_music("upbeat", duration_range=(20, 40))
print(f"Found {len(tracks)} tracks")

# Get default music
music_path = manager.get_default_music()
if music_path:
    print(f"Downloaded: {music_path}")
```

### Test Video Processor

```python
from video_processor import VideoProcessor

processor = VideoProcessor()

result = processor.create_clip(
    video_path="/path/to/video.mp4",
    start_time=10.0,
    end_time=40.0,
    output_name="test_clip",
    text_hook="Watch This!",
    add_zoom=True
)

if result['success']:
    print(f"Clip created: {result['video_path']}")
    print(f"Thumbnail: {result['thumbnail_path']}")
else:
    print(f"Error: {result['error']}")
```

## API Testing

### Using cURL

```bash
# Process a video
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
    "num_clips": 2,
    "add_music": false,
    "add_zoom": true
  }'

# List clips
curl http://localhost:8000/clips

# Download a clip
curl http://localhost:8000/clips/clip_1.mp4 -o downloaded_clip.mp4
```

### Using Python Requests

```python
import requests

# Start server first: python main.py

# Process video
response = requests.post(
    "http://localhost:8000/process",
    json={
        "video_url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
        "num_clips": 2,
        "add_music": False,
        "add_zoom": True
    }
)

results = response.json()

if results['success']:
    print(f"Generated {len(results['clips'])} clips")
    for clip in results['clips']:
        print(f"- {clip['video_path']}")
else:
    print(f"Errors: {results['errors']}")
```

## Docker Testing

### Build and Run

```bash
# Build image
docker build -t shortclips-ai .

# Run container
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -v $(pwd)/outputs:/app/outputs \
  shortclips-ai
```

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Performance Testing

### Measure Processing Time

```python
import time
from orchestrator import ClipOrchestrator

orchestrator = ClipOrchestrator()

start = time.time()
results = orchestrator.process_video(
    video_url="https://www.youtube.com/watch?v=...",
    num_clips=3
)
end = time.time()

print(f"Processing time: {end - start:.1f} seconds")
print(f"Clips generated: {len(results['clips'])}")
```

### Test Different Video Lengths

| Video Length | Expected Time | Notes |
|--------------|---------------|-------|
| 2-5 min      | 2-4 min       | Fast |
| 10-15 min    | 8-12 min      | Medium |
| 30+ min      | 20-40 min     | Slow |

## Error Testing

### Test Missing API Key

```bash
# Remove API key
export GEMINI_API_KEY=""

# Try to process
python cli.py "https://youtube.com/watch?v=..." -n 2
```

**Expected:** Error message about missing API key

### Test Invalid Video URL

```bash
python cli.py "https://invalid-url.com/video" -n 2
```

**Expected:** Error message about video download failure

### Test Unsupported File

```bash
python cli.py /path/to/text-file.txt -n 2
```

**Expected:** Error message about invalid video file

## Common Issues

### Issue: Whisper Model Download Fails

**Solution:**
```bash
# Pre-download model
python -c "import whisper; whisper.load_model('base')"
```

### Issue: Out of Memory

**Solution:**
- Use smaller Whisper model
- Process shorter videos
- Close other applications

### Issue: FFmpeg Not Found

**Solution:**
```bash
# Ubuntu
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Verify
ffmpeg -version
```

### Issue: Slow Processing

**Solutions:**
- Use `base` instead of `large` Whisper model
- Disable zoom: `--no-zoom`
- Disable music: `--no-music`
- Process shorter segments

## Automated Testing (Future)

### Unit Tests Structure

```python
# tests/test_downloader.py
import unittest
from video_downloader import VideoDownloader

class TestVideoDownloader(unittest.TestCase):
    def test_get_info(self):
        downloader = VideoDownloader()
        info = downloader.get_video_info("test_url")
        self.assertIsNotNone(info)

# Run tests
python -m unittest discover tests/
```

### Integration Tests

```python
# tests/test_integration.py
import unittest
from orchestrator import ClipOrchestrator

class TestIntegration(unittest.TestCase):
    def test_full_pipeline(self):
        orchestrator = ClipOrchestrator()
        results = orchestrator.process_video(
            "test_video_url",
            num_clips=1
        )
        self.assertTrue(results['success'])
        self.assertEqual(len(results['clips']), 1)
```

## Continuous Testing

### GitHub Actions

The `.github/workflows/ci.yml` file runs tests on:
- Every push to main/develop
- Every pull request

### Manual CI Run

```bash
# Install dependencies
pip install -r requirements.txt

# Check syntax
python -m py_compile *.py

# Run tests (when implemented)
python -m unittest discover tests/
```

## Validation Checklist

Before considering the tool production-ready:

- [ ] All dependencies install correctly
- [ ] FFmpeg is detected
- [ ] Configuration loads properly
- [ ] Video download works
- [ ] Transcription completes
- [ ] Scene detection works
- [ ] AI analysis generates results
- [ ] Video processing creates clips
- [ ] Clips are in 9:16 format
- [ ] Text overlays appear
- [ ] Zoom effects work
- [ ] Background music mixes properly
- [ ] Thumbnails generate
- [ ] API server starts
- [ ] All endpoints respond
- [ ] CLI processes videos
- [ ] Error handling works
- [ ] Documentation is clear

## Test Videos

Recommended test videos (short, public domain):

1. **Short (2-3 min)**: Quick tests
   - Nature documentaries
   - TED-Ed animations

2. **Medium (10-15 min)**: Full tests
   - Educational content
   - Tech reviews

3. **Long (30+ min)**: Stress tests
   - Podcasts
   - Interviews

## Reporting Issues

When reporting issues, include:

1. Python version: `python --version`
2. OS: Linux/macOS/Windows
3. FFmpeg version: `ffmpeg -version`
4. Error messages (full traceback)
5. Video URL or length
6. Configuration (.env settings)
7. Steps to reproduce

## Next Steps

After basic testing:

1. Test with various video types
2. Test error scenarios
3. Measure performance
4. Optimize bottlenecks
5. Add automated tests
6. Set up CI/CD
7. Deploy to production

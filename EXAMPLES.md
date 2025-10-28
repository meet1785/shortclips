# Examples

## Using the CLI

### Process a YouTube Video

```bash
python cli.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -n 3
```

### Process a Local Video

```bash
python cli.py /path/to/video.mp4 -n 5
```

### Process Without Music

```bash
python cli.py "https://youtube.com/watch?v=..." --no-music
```

### Process Without Zoom Effects

```bash
python cli.py "https://youtube.com/watch?v=..." --no-zoom
```

## Using the API

### Start the Server

```bash
python main.py
```

### Process a Video (Python)

```python
import requests

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

if results['success']:
    for clip in results['clips']:
        print(f"Generated: {clip['video_path']}")
        print(f"Title: {clip['title']}")
        print(f"Hook: {clip['text_hook']}")
```

### Upload a Local Video (Python)

```python
import requests

with open("video.mp4", "rb") as f:
    response = requests.post(
        "http://localhost:8000/process-local",
        files={"file": f},
        data={
            "num_clips": 3,
            "add_music": True,
            "add_zoom": True
        }
    )

results = response.json()
print(f"Generated {len(results['clips'])} clips!")
```

### Using cURL

```bash
# Process a YouTube video
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "num_clips": 3,
    "add_music": true,
    "add_zoom": true
  }'

# Upload and process a local video
curl -X POST "http://localhost:8000/process-local" \
  -F "file=@video.mp4" \
  -F "num_clips=3" \
  -F "add_music=true" \
  -F "add_zoom=true"

# List all generated clips
curl "http://localhost:8000/clips"

# Download a clip
curl "http://localhost:8000/clips/clip_1.mp4" -o my_clip.mp4
```

## Using as a Python Module

```python
from orchestrator import ClipOrchestrator

# Initialize
orchestrator = ClipOrchestrator()

# Process a YouTube video
results = orchestrator.process_video(
    video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    num_clips=3,
    add_music=True,
    add_zoom=True
)

# Process a local video
results = orchestrator.process_local_video(
    video_path="/path/to/video.mp4",
    num_clips=3,
    add_music=True,
    add_zoom=True
)

# Check results
if results['success']:
    print(f"Original title: {results['original_title']}")
    print(f"Generated {len(results['clips'])} clips")
    
    for clip in results['clips']:
        print(f"\nClip: {clip['video_path']}")
        print(f"Title: {clip['title']}")
        print(f"Hook: {clip['text_hook']}")
        print(f"Duration: {clip['duration']:.1f}s")
else:
    print("Failed:", results['errors'])
```

## Advanced Usage

### Custom Transcription Model

```python
from audio_transcriber import AudioTranscriber

# Use larger model for better accuracy
transcriber = AudioTranscriber(model_size="medium")
transcript_data = transcriber.transcribe("video.mp4")

print(transcript_data['text'])
print(f"Language: {transcript_data['language']}")
```

### Custom Scene Detection

```python
from scene_detector import SceneDetector

# Use more sensitive threshold
detector = SceneDetector(threshold=20.0)
scenes = detector.detect_scenes("video.mp4")

for scene in scenes:
    print(f"Scene {scene['scene_number']}: {scene['start']:.1f}s - {scene['end']:.1f}s")
```

### AI Content Analysis

```python
from content_analyzer import ContentAnalyzer

analyzer = ContentAnalyzer()

# Analyze transcript
analysis = analyzer.analyze_transcript(
    transcript="Your video transcript here...",
    video_title="My Video Title"
)

print(analysis['analysis'])

# Generate viral titles
title = analyzer.generate_viral_title("Clip content...")
print(f"Suggested title: {title}")

# Generate text hook
hook = analyzer.generate_text_hook("Clip content...")
print(f"Text hook: {hook}")
```

### Custom Video Processing

```python
from video_processor import VideoProcessor

processor = VideoProcessor()

# Create a single clip
result = processor.create_clip(
    video_path="video.mp4",
    start_time=10.0,
    end_time=40.0,
    output_name="my_clip",
    text_hook="Watch this!",
    add_zoom=True,
    music_path="background.mp3"
)

print(f"Clip saved: {result['video_path']}")
print(f"Thumbnail: {result['thumbnail_path']}")
```

## Tips for Best Results

1. **Choose engaging source videos**
   - Educational content with clear structure
   - Entertainment with high-energy moments
   - Storytelling with emotional peaks

2. **Optimize clip count**
   - 3-5 clips for 10-30 minute videos
   - 1-2 clips for 2-5 minute videos
   - More clips = more processing time

3. **Use appropriate models**
   - `base` Whisper model: Fast, good quality (default)
   - `small` Whisper model: Better accuracy, slower
   - `medium` Whisper model: Best accuracy, slowest

4. **Music selection**
   - Enable music for entertainment content
   - Disable for educational/professional content
   - Music volume is automatically balanced

5. **Text hooks**
   - AI generates attention-grabbing hooks
   - Displayed for first 3 seconds
   - Bold white text with black outline

6. **Zoom effects**
   - Adds cinematic feel
   - Subtle zoom in/out during clip
   - Disable for static content (slides, etc.)

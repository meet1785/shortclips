# Architecture Overview

## System Design

Short Clips AI follows a modular pipeline architecture where each component handles a specific part of the video-to-clips transformation process.

```
┌─────────────────┐
│  Video Input    │  (URL or File)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Video Downloader│  (yt-dlp)
└────────┬────────┘
         │
         ▼
    ┌────────────────────────────────────┐
    │                                    │
    ▼                                    ▼
┌─────────────────┐              ┌──────────────┐
│Audio Transcriber│              │Scene Detector│
│   (Whisper)     │              │(PySceneDetect)│
└────────┬────────┘              └──────┬───────┘
         │                              │
         └──────────────┬───────────────┘
                        ▼
                ┌───────────────┐
                │Content Analyzer│
                │  (Gemini Pro) │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │ Key Moments   │
                │  Selection    │
                └───────┬───────┘
                        │
         ┌──────────────┴──────────────┐
         │                             │
         ▼                             ▼
┌─────────────────┐           ┌───────────────┐
│ Music Manager   │           │Video Processor│
│  (Freesound)    │           │   (MoviePy)   │
└────────┬────────┘           └───────┬───────┘
         │                            │
         └──────────────┬─────────────┘
                        ▼
                ┌───────────────┐
                │  Final Clips  │
                │  + Thumbnails │
                └───────────────┘
```

## Component Details

### 1. Video Downloader (`video_downloader.py`)

**Purpose:** Download videos from YouTube and other platforms.

**Technology:** yt-dlp

**Key Functions:**
- `download(url)`: Download video from URL
- `get_video_info(url)`: Get metadata without downloading

**Output:** Local video file + metadata

### 2. Audio Transcriber (`audio_transcriber.py`)

**Purpose:** Convert speech to text with precise timestamps.

**Technology:** OpenAI Whisper

**Key Functions:**
- `transcribe(video_path)`: Full transcription with word timestamps
- `extract_audio(video_path)`: Extract audio track
- `get_segments_in_range()`: Get transcript for specific time range

**Output:** Transcript with timestamps

**Models Available:**
- `tiny`: Fastest, lowest quality
- `base`: Default, good balance (recommended)
- `small`: Better accuracy, slower
- `medium`: High accuracy, slow
- `large`: Best accuracy, very slow

### 3. Scene Detector (`scene_detector.py`)

**Purpose:** Identify scene changes and natural cut points.

**Technology:** PySceneDetect

**Key Functions:**
- `detect_scenes(video_path)`: Find all scene changes
- `get_natural_cut_points()`: Suggest clip boundaries
- `find_scenes_in_range()`: Get scenes in time range

**Output:** List of scenes with start/end times

**Configuration:**
- `threshold`: Sensitivity (default: 27.0)
  - Lower = more sensitive = more scenes
  - Higher = less sensitive = fewer scenes

### 4. Content Analyzer (`content_analyzer.py`)

**Purpose:** AI-powered content analysis to find viral moments.

**Technology:** Google Gemini Pro

**Key Functions:**
- `analyze_transcript()`: Overall content analysis
- `find_key_moments()`: Identify most engaging segments
- `generate_viral_title()`: Create attention-grabbing title
- `generate_text_hook()`: Create 3-second text overlay

**Output:** AI suggestions for clips and titles

**Prompting Strategy:**
- Structured prompts for consistent output
- Context-aware analysis
- Viral content heuristics

### 5. Music Manager (`music_manager.py`)

**Purpose:** Add copyright-free background music.

**Technology:** Freesound API

**Key Functions:**
- `search_music()`: Find suitable music
- `download_music()`: Download music file
- `get_default_music()`: Get default track
- `search_by_mood()`: Find music by mood

**Output:** Background music file

**Features:**
- Free, copyright-free music
- Filtered by duration
- Mood-based selection

### 6. Video Processor (`video_processor.py`)

**Purpose:** Edit and export final clips.

**Technology:** MoviePy + FFmpeg

**Key Functions:**
- `create_clip()`: Main clip creation
- `_convert_to_vertical()`: Convert to 9:16
- `_add_zoom_effect()`: Cinematic zoom
- `_add_text_overlay()`: Add text hooks
- `_add_background_music()`: Mix audio
- `_generate_thumbnail()`: Create thumbnail

**Output:** Final MP4 clip + thumbnail

**Processing Pipeline:**
1. Extract segment from video
2. Convert to 9:16 aspect ratio
3. Apply zoom effect (optional)
4. Add text overlay (first 3 seconds)
5. Mix background music
6. Export as MP4 (H.264)
7. Generate thumbnail

### 7. Orchestrator (`orchestrator.py`)

**Purpose:** Coordinate entire pipeline.

**Key Functions:**
- `process_video()`: Process URL
- `process_local_video()`: Process file
- `_find_best_segments()`: Select clip segments
- `_adjust_to_scenes()`: Align to scene boundaries

**Flow:**
1. Download or load video
2. Parallel: Transcribe + Detect scenes
3. Analyze content with AI
4. Select best segments
5. Download music (if enabled)
6. Generate each clip
7. Return results

### 8. FastAPI Application (`main.py`)

**Purpose:** REST API server.

**Endpoints:**
- `POST /process`: Process video URL
- `POST /process-local`: Upload and process
- `GET /video-info`: Get video metadata
- `GET /clips`: List generated clips
- `GET /clips/{name}`: Download clip
- `GET /thumbnails/{name}`: Download thumbnail
- `DELETE /clips/{name}`: Delete clip

**Features:**
- Async processing
- CORS enabled
- Interactive docs at `/docs`

### 9. CLI (`cli.py`)

**Purpose:** Command-line interface.

**Usage:**
```bash
python cli.py [URL_OR_FILE] [OPTIONS]
```

**Options:**
- `-n, --num-clips`: Number of clips
- `--no-music`: Disable music
- `--no-zoom`: Disable zoom

## Data Flow

### Input
```
Video URL or File
↓
Video Downloader / Local File
↓
MP4 Video File
```

### Processing
```
MP4 Video
├─→ Audio Extraction → Whisper → Transcript with Timestamps
├─→ Scene Analysis → PySceneDetect → Scene Boundaries
└─→ Combined Analysis
    ↓
    AI Analysis (Gemini Pro)
    ↓
    Key Moments Selection
    ↓
    Video Processing (MoviePy)
    ├─→ 9:16 Conversion
    ├─→ Zoom Effects
    ├─→ Text Overlays
    └─→ Music Mixing
    ↓
    FFmpeg Encoding
```

### Output
```
Final Clips
├─→ clip_1.mp4 (9:16, H.264, AAC)
├─→ clip_1_thumb.jpg
├─→ clip_2.mp4
├─→ clip_2_thumb.jpg
└─→ ...
```

## Configuration

### Environment Variables (`.env`)
- `GEMINI_API_KEY`: Required for AI analysis
- `FREESOUND_API_KEY`: Optional for music
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `MIN_CLIP_DURATION`: Minimum seconds (default: 15)
- `MAX_CLIP_DURATION`: Maximum seconds (default: 60)

### Directory Structure
```
shortclips/
├── downloads/     # Downloaded videos
├── outputs/       # Generated clips
├── temp/          # Temporary files
└── models/        # Whisper model cache
```

## Performance Considerations

### Bottlenecks
1. **Whisper Transcription**: CPU-intensive
   - Solution: Use smaller model or GPU
2. **Video Encoding**: I/O and CPU intensive
   - Solution: Use hardware encoding if available
3. **Scene Detection**: CPU-intensive for long videos
   - Solution: Adjust threshold or sample frames

### Optimization Tips
1. Use `base` Whisper model (default)
2. Process videos in parallel (separate sessions)
3. Cache transcriptions and scene data
4. Use hardware acceleration for FFmpeg
5. Limit clip count for faster results

### Resource Usage
- **Memory**: ~2-4GB per video
- **CPU**: 100% during processing
- **Disk**: 2-3x video size (temporary files)
- **Network**: Only for download and API calls

## Scaling

### Horizontal Scaling
- Run multiple instances
- Use message queue (Celery, RabbitMQ)
- Distribute video processing

### Vertical Scaling
- Add more CPU cores
- Increase RAM
- Use GPU for Whisper
- Use SSD for faster I/O

## Security

### API Keys
- Never commit API keys
- Use environment variables
- Rotate keys regularly

### File Upload
- Validate file types
- Limit file size
- Scan for malware
- Clean up temp files

### Rate Limiting
- Implement per-IP limits
- Use API key authentication
- Monitor usage

## Testing

### Unit Tests
- Test each component independently
- Mock external dependencies
- Use sample videos

### Integration Tests
- Test full pipeline
- Verify output quality
- Check error handling

### Performance Tests
- Measure processing time
- Monitor resource usage
- Test with various video lengths

## Future Enhancements

1. **GPU Acceleration**: CUDA support for Whisper
2. **Batch Processing**: Multiple videos at once
3. **Custom Effects**: More video effects
4. **Auto-posting**: Social media integration
5. **Web UI**: Browser-based interface
6. **Caching**: Cache transcriptions and analyses
7. **Quality Presets**: Fast/balanced/quality modes
8. **Multi-language**: Support more languages
9. **Advanced AI**: Better moment detection
10. **Analytics**: Track clip performance

## Dependencies

### Core
- Python 3.8+
- FFmpeg

### Python Packages
- fastapi: Web framework
- uvicorn: ASGI server
- yt-dlp: Video downloading
- openai-whisper: Transcription
- PySceneDetect: Scene detection
- moviepy: Video editing
- google-generativeai: AI analysis
- Pillow: Image processing

### System
- ffmpeg: Video encoding
- ffprobe: Video analysis

## License

MIT License - See LICENSE file

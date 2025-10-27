"""
Short Clips AI - Convert long videos into viral short clips.

A free AI-powered tool using Python, FastAPI, MoviePy, Whisper,
PySceneDetect, and Gemini Pro.
"""

__version__ = "1.0.0"
__author__ = "Short Clips AI Contributors"

# Import main components when used as a package
try:
    from orchestrator import ClipOrchestrator
    from video_downloader import VideoDownloader
    from audio_transcriber import AudioTranscriber
    from scene_detector import SceneDetector
    from content_analyzer import ContentAnalyzer
    from music_manager import MusicManager
    from video_processor import VideoProcessor

    __all__ = [
        'ClipOrchestrator',
        'VideoDownloader',
        'AudioTranscriber',
        'SceneDetector',
        'ContentAnalyzer',
        'MusicManager',
        'VideoProcessor',
    ]
except ImportError:
    # When dependencies are not installed yet
    pass

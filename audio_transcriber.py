"""
Audio transcription module using OpenAI Whisper.
Transcribes audio with timestamps for precise clip extraction.
"""

import os
import whisper
from typing import List, Dict
from moviepy.editor import VideoFileClip
from config import settings


class AudioTranscriber:
    """Transcribes audio using Whisper model."""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize transcriber with Whisper model.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        print(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
        
    def extract_audio(self, video_path: str) -> str:
        """
        Extract audio from video file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Path to extracted audio file
        """
        audio_path = os.path.join(settings.temp_dir, "temp_audio.wav")
        
        try:
            video = VideoFileClip(video_path)
            video.audio.write_audiofile(audio_path, verbose=False, logger=None)
            video.close()
            return audio_path
        except Exception as e:
            raise Exception(f"Failed to extract audio: {str(e)}")
    
    def transcribe(self, video_path: str) -> Dict:
        """
        Transcribe video audio with timestamps.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary containing full text and segments with timestamps
        """
        # Extract audio from video
        audio_path = self.extract_audio(video_path)
        
        try:
            # Transcribe with word-level timestamps
            result = self.model.transcribe(
                audio_path,
                word_timestamps=True,
                verbose=False
            )
            
            # Clean up temp audio
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            # Format segments
            segments = []
            for segment in result['segments']:
                segments.append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].strip(),
                })
            
            return {
                'text': result['text'],
                'segments': segments,
                'language': result.get('language', 'en'),
            }
        except Exception as e:
            # Clean up temp audio on error
            if os.path.exists(audio_path):
                os.remove(audio_path)
            raise Exception(f"Failed to transcribe audio: {str(e)}")
    
    def get_segments_in_range(self, segments: List[Dict], 
                               start_time: float, end_time: float) -> List[Dict]:
        """
        Get transcript segments within a time range.
        
        Args:
            segments: List of transcript segments
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            List of segments within the time range
        """
        return [
            seg for seg in segments 
            if seg['start'] >= start_time and seg['end'] <= end_time
        ]

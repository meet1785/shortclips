"""
Video processor using MoviePy and FFmpeg.
Creates viral clips with effects, text overlays, and music.
"""

import os
from typing import Dict, List, Optional, Tuple
from moviepy.editor import (
    VideoFileClip, TextClip, CompositeVideoClip, 
    AudioFileClip, concatenate_videoclips
)
from moviepy.video.fx import all as vfx
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from config import settings


class VideoProcessor:
    """Processes videos to create viral short clips."""
    
    def __init__(self):
        self.output_dir = settings.outputs_dir
        self.temp_dir = settings.temp_dir
        
    def create_clip(self, 
                    video_path: str,
                    start_time: float,
                    end_time: float,
                    output_name: str,
                    text_hook: Optional[str] = None,
                    add_zoom: bool = True,
                    music_path: Optional[str] = None,
                    aspect_ratio: str = "9:16") -> Dict[str, str]:
        """
        Create a viral clip from video segment.
        
        Args:
            video_path: Path to source video
            start_time: Start time in seconds
            end_time: End time in seconds
            output_name: Name for output file
            text_hook: Text overlay for first few seconds
            add_zoom: Whether to add cinematic zoom effect
            music_path: Path to background music
            aspect_ratio: Target aspect ratio (9:16 for vertical)
            
        Returns:
            Dictionary with output paths and metadata
        """
        try:
            # Load video segment
            video = VideoFileClip(video_path).subclip(start_time, end_time)
            
            # Convert to 9:16 aspect ratio
            video = self._convert_to_vertical(video)
            
            # Add cinematic zoom effect
            if add_zoom:
                video = self._add_zoom_effect(video)
            
            # Add text hook overlay
            if text_hook:
                video = self._add_text_overlay(video, text_hook, duration=3)
            
            # Add background music
            if music_path and os.path.exists(music_path):
                video = self._add_background_music(video, music_path)
            
            # Generate output path
            output_path = os.path.join(self.output_dir, f"{output_name}.mp4")
            
            # Export video
            video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium',
                threads=4,
                logger=None
            )
            
            # Generate thumbnail
            thumbnail_path = self._generate_thumbnail(video, output_name)
            
            # Clean up
            video.close()
            
            return {
                'video_path': output_path,
                'thumbnail_path': thumbnail_path,
                'duration': end_time - start_time,
                'success': True,
            }
            
        except Exception as e:
            return {
                'video_path': '',
                'thumbnail_path': '',
                'duration': 0,
                'success': False,
                'error': str(e),
            }
    
    def _convert_to_vertical(self, video: VideoFileClip) -> VideoFileClip:
        """
        Convert video to 9:16 vertical format.
        
        Args:
            video: Source video clip
            
        Returns:
            Resized vertical video
        """
        target_width = 1080
        target_height = 1920
        
        # Calculate scaling to fit height while maintaining aspect ratio
        scale = target_height / video.h
        
        # Resize video
        video_resized = video.resize(height=target_height)
        
        # Crop to center if wider than target
        if video_resized.w > target_width:
            x_center = video_resized.w / 2
            x1 = x_center - target_width / 2
            video_resized = video_resized.crop(x1=x1, width=target_width)
        
        # Add padding if narrower than target
        elif video_resized.w < target_width:
            # Create black background
            from moviepy.editor import ColorClip
            background = ColorClip(
                size=(target_width, target_height),
                color=(0, 0, 0),
                duration=video.duration
            )
            
            # Center video on background
            x_offset = (target_width - video_resized.w) / 2
            video_resized = CompositeVideoClip([
                background,
                video_resized.set_position(('center', 'center'))
            ])
        
        return video_resized
    
    def _add_zoom_effect(self, video: VideoFileClip, 
                         zoom_factor: float = 1.15) -> VideoFileClip:
        """
        Add cinematic zoom effect to video.
        
        Args:
            video: Source video clip
            zoom_factor: Maximum zoom level
            
        Returns:
            Video with zoom effect
        """
        duration = video.duration
        
        def zoom_in_out(get_frame, t):
            """Apply zoom effect based on time."""
            frame = get_frame(t)
            
            # Calculate zoom (zoom in first half, zoom out second half)
            progress = t / duration
            if progress < 0.5:
                current_zoom = 1 + (zoom_factor - 1) * (progress * 2)
            else:
                current_zoom = zoom_factor - (zoom_factor - 1) * ((progress - 0.5) * 2)
            
            # Apply zoom
            h, w = frame.shape[:2]
            new_h, new_w = int(h * current_zoom), int(w * current_zoom)
            
            # Resize and crop to original size
            from scipy.ndimage import zoom as scipy_zoom
            if current_zoom > 1:
                zoomed = scipy_zoom(frame, (current_zoom, current_zoom, 1))
                # Crop to center
                start_h = (zoomed.shape[0] - h) // 2
                start_w = (zoomed.shape[1] - w) // 2
                return zoomed[start_h:start_h+h, start_w:start_w+w]
            
            return frame
        
        # Apply the zoom effect
        return video.fl(zoom_in_out)
    
    def _add_text_overlay(self, video: VideoFileClip, 
                          text: str, 
                          duration: float = 3) -> VideoFileClip:
        """
        Add text overlay to video.
        
        Args:
            video: Source video clip
            text: Text to overlay
            duration: Duration of text display in seconds
            
        Returns:
            Video with text overlay
        """
        try:
            # Create text clip
            txt_clip = TextClip(
                text,
                fontsize=70,
                color='white',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=3,
                method='caption',
                size=(video.w - 100, None),
                align='center'
            )
            
            # Position at top center
            txt_clip = txt_clip.set_position(('center', 100))
            txt_clip = txt_clip.set_duration(min(duration, video.duration))
            
            # Add fade in/out
            txt_clip = txt_clip.crossfadein(0.5).crossfadeout(0.5)
            
            # Composite with video
            return CompositeVideoClip([video, txt_clip])
            
        except Exception as e:
            print(f"Failed to add text overlay: {str(e)}")
            return video
    
    def _add_background_music(self, video: VideoFileClip, 
                               music_path: str,
                               volume: float = 0.3) -> VideoFileClip:
        """
        Add background music to video.
        
        Args:
            video: Source video clip
            music_path: Path to music file
            volume: Music volume (0.0 to 1.0)
            
        Returns:
            Video with background music
        """
        try:
            # Load music
            music = AudioFileClip(music_path)
            
            # Loop or trim music to match video duration
            if music.duration < video.duration:
                # Loop music
                loops = int(video.duration / music.duration) + 1
                music = concatenate_videoclips([music] * loops)
            
            music = music.subclip(0, video.duration)
            
            # Reduce volume
            music = music.volumex(volume)
            
            # Mix with original audio if exists
            if video.audio:
                from moviepy.audio.AudioClip import CompositeAudioClip
                final_audio = CompositeAudioClip([video.audio, music])
            else:
                final_audio = music
            
            return video.set_audio(final_audio)
            
        except Exception as e:
            print(f"Failed to add background music: {str(e)}")
            return video
    
    def _generate_thumbnail(self, video: VideoFileClip, 
                            output_name: str) -> str:
        """
        Generate thumbnail from video.
        
        Args:
            video: Source video clip
            output_name: Base name for thumbnail file
            
        Returns:
            Path to thumbnail image
        """
        try:
            # Get frame from middle of video
            t = video.duration / 2
            frame = video.get_frame(t)
            
            # Convert to PIL Image
            img = Image.fromarray(frame)
            
            # Save thumbnail
            thumbnail_path = os.path.join(self.output_dir, f"{output_name}_thumb.jpg")
            img.save(thumbnail_path, quality=90)
            
            return thumbnail_path
            
        except Exception as e:
            print(f"Failed to generate thumbnail: {str(e)}")
            return ""
    
    def create_multiple_clips(self, 
                              video_path: str,
                              segments: List[Dict],
                              base_name: str,
                              **kwargs) -> List[Dict]:
        """
        Create multiple clips from a video.
        
        Args:
            video_path: Path to source video
            segments: List of segments with start/end times
            base_name: Base name for output files
            **kwargs: Additional arguments for create_clip
            
        Returns:
            List of results for each clip
        """
        results = []
        
        for i, segment in enumerate(segments):
            output_name = f"{base_name}_clip_{i+1}"
            
            result = self.create_clip(
                video_path=video_path,
                start_time=segment['start'],
                end_time=segment['end'],
                output_name=output_name,
                **kwargs
            )
            
            result['segment_index'] = i
            results.append(result)
        
        return results

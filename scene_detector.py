"""
Scene detection module using PySceneDetect.
Detects scene changes and potential clip boundaries.
"""

from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector
from typing import List, Dict


class SceneDetector:
    """Detects scenes and cuts in videos."""
    
    def __init__(self, threshold: float = 27.0):
        """
        Initialize scene detector.
        
        Args:
            threshold: Content detection threshold (lower = more sensitive)
        """
        self.threshold = threshold
        
    def detect_scenes(self, video_path: str) -> List[Dict]:
        """
        Detect scene changes in video.
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of scenes with start and end times
        """
        try:
            # Open video
            video = open_video(video_path)
            scene_manager = SceneManager()
            
            # Add content detector
            scene_manager.add_detector(
                ContentDetector(threshold=self.threshold)
            )
            
            # Detect scenes
            scene_manager.detect_scenes(video)
            scene_list = scene_manager.get_scene_list()
            
            # Convert to simple format
            scenes = []
            for i, scene in enumerate(scene_list):
                start_time = scene[0].get_seconds()
                end_time = scene[1].get_seconds()
                
                scenes.append({
                    'scene_number': i + 1,
                    'start': start_time,
                    'end': end_time,
                    'duration': end_time - start_time,
                })
            
            return scenes
            
        except Exception as e:
            raise Exception(f"Failed to detect scenes: {str(e)}")
    
    def find_scenes_in_range(self, scenes: List[Dict], 
                             start_time: float, end_time: float) -> List[Dict]:
        """
        Find scenes that overlap with a time range.
        
        Args:
            scenes: List of detected scenes
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            List of scenes within the range
        """
        return [
            scene for scene in scenes
            if (scene['start'] <= end_time and scene['end'] >= start_time)
        ]
    
    def get_natural_cut_points(self, scenes: List[Dict], 
                                min_duration: float = 15,
                                max_duration: float = 60) -> List[Dict]:
        """
        Get natural cut points for creating clips based on scene boundaries.
        
        Args:
            scenes: List of detected scenes
            min_duration: Minimum clip duration in seconds
            max_duration: Maximum clip duration in seconds
            
        Returns:
            List of potential clip segments
        """
        clips = []
        current_start = 0
        current_duration = 0
        
        for scene in scenes:
            scene_duration = scene['duration']
            
            # If adding this scene exceeds max duration, create a clip
            if current_duration + scene_duration > max_duration:
                if current_duration >= min_duration:
                    clips.append({
                        'start': current_start,
                        'end': scene['start'],
                        'duration': current_duration,
                    })
                current_start = scene['start']
                current_duration = scene_duration
            else:
                current_duration += scene_duration
        
        # Add remaining clip if it meets minimum duration
        if current_duration >= min_duration and scenes:
            clips.append({
                'start': current_start,
                'end': scenes[-1]['end'],
                'duration': current_duration,
            })
        
        return clips

"""
Main orchestrator for the video clip generation pipeline.
Coordinates all components to create viral clips.
"""

import os
from typing import Dict, List, Optional
from video_downloader import VideoDownloader
from audio_transcriber import AudioTranscriber
from scene_detector import SceneDetector
from content_analyzer import ContentAnalyzer
from music_manager import MusicManager
from video_processor import VideoProcessor
from config import settings


class ClipOrchestrator:
    """Orchestrates the entire clip creation pipeline."""
    
    def __init__(self):
        """Initialize all components."""
        self.downloader = VideoDownloader()
        self.transcriber = AudioTranscriber(model_size="base")
        self.scene_detector = SceneDetector()
        self.content_analyzer = ContentAnalyzer()
        self.music_manager = MusicManager()
        self.video_processor = VideoProcessor()
        
    def process_video(self, 
                      video_url: str,
                      num_clips: int = 3,
                      add_music: bool = True,
                      add_zoom: bool = True) -> Dict:
        """
        Process a video URL and create viral clips.
        
        Args:
            video_url: URL of the video to process
            num_clips: Number of clips to generate
            add_music: Whether to add background music
            add_zoom: Whether to add cinematic zoom effects
            
        Returns:
            Dictionary containing results and generated clips
        """
        results = {
            'success': False,
            'clips': [],
            'errors': [],
        }
        
        try:
            # Step 1: Download video
            print("Step 1: Downloading video...")
            download_info = self.downloader.download(video_url)
            video_path = download_info['filepath']
            video_title = download_info['title']
            
            print(f"Downloaded: {video_title}")
            
            # Step 2: Transcribe audio
            print("Step 2: Transcribing audio...")
            transcript_data = self.transcriber.transcribe(video_path)
            transcript = transcript_data['text']
            segments = transcript_data['segments']
            
            print(f"Transcribed {len(segments)} segments")
            
            # Step 3: Detect scenes
            print("Step 3: Detecting scenes...")
            scenes = self.scene_detector.detect_scenes(video_path)
            
            print(f"Detected {len(scenes)} scenes")
            
            # Step 4: Analyze content with AI
            print("Step 4: Analyzing content with AI...")
            analysis = self.content_analyzer.analyze_transcript(transcript, video_title)
            
            print("AI analysis complete")
            
            # Step 5: Find key moments
            print("Step 5: Finding key moments...")
            clip_segments = self._find_best_segments(
                scenes=scenes,
                segments=segments,
                num_clips=num_clips
            )
            
            print(f"Identified {len(clip_segments)} key moments")
            
            # Step 6: Get background music
            music_path = None
            if add_music and settings.freesound_api_key:
                print("Step 6: Getting background music...")
                music_path = self.music_manager.get_default_music()
                if music_path:
                    print(f"Music downloaded: {music_path}")
            
            # Step 7: Generate clips
            print("Step 7: Generating clips...")
            for i, segment in enumerate(clip_segments[:num_clips]):
                print(f"Creating clip {i+1}/{num_clips}...")
                
                # Generate text hook using AI
                clip_text = self._get_clip_text(segments, segment['start'], segment['end'])
                text_hook = self.content_analyzer.generate_text_hook(clip_text)
                
                # Generate viral title
                viral_title = self.content_analyzer.generate_viral_title(clip_text)
                
                # Create clip
                clip_result = self.video_processor.create_clip(
                    video_path=video_path,
                    start_time=segment['start'],
                    end_time=segment['end'],
                    output_name=f"clip_{i+1}",
                    text_hook=text_hook,
                    add_zoom=add_zoom,
                    music_path=music_path
                )
                
                if clip_result['success']:
                    clip_result['title'] = viral_title
                    clip_result['text_hook'] = text_hook
                    results['clips'].append(clip_result)
                    print(f"Clip {i+1} created successfully")
                else:
                    results['errors'].append(clip_result.get('error', 'Unknown error'))
            
            results['success'] = len(results['clips']) > 0
            results['original_title'] = video_title
            results['analysis'] = analysis.get('analysis', '')
            
            # Clean up
            if os.path.exists(video_path):
                print("Cleaning up downloaded video...")
                # Optionally remove downloaded video to save space
                # os.remove(video_path)
            
            return results
            
        except Exception as e:
            results['errors'].append(str(e))
            return results
    
    def _find_best_segments(self, 
                            scenes: List[Dict],
                            segments: List[Dict],
                            num_clips: int = 3) -> List[Dict]:
        """
        Find the best segments for clips based on scenes and transcript.
        
        Args:
            scenes: Detected scene changes
            segments: Transcript segments
            num_clips: Number of clips to find
            
        Returns:
            List of segment dictionaries with start/end times
        """
        min_duration = settings.min_clip_duration
        max_duration = settings.max_clip_duration
        
        # Get natural cut points from scene detection
        potential_clips = self.scene_detector.get_natural_cut_points(
            scenes, 
            min_duration=min_duration,
            max_duration=max_duration
        )
        
        # If not enough clips, create evenly spaced segments
        if len(potential_clips) < num_clips and scenes:
            total_duration = scenes[-1]['end']
            interval = total_duration / (num_clips + 1)
            
            potential_clips = []
            for i in range(num_clips):
                start = interval * (i + 0.5)
                end = min(start + max_duration, total_duration)
                
                # Adjust to scene boundaries
                start, end = self._adjust_to_scenes(start, end, scenes)
                
                if end - start >= min_duration:
                    potential_clips.append({
                        'start': start,
                        'end': end,
                        'duration': end - start,
                    })
        
        return potential_clips[:num_clips]
    
    def _adjust_to_scenes(self, start: float, end: float, 
                          scenes: List[Dict]) -> tuple:
        """Adjust segment boundaries to scene cuts."""
        # Find nearest scene boundaries
        for scene in scenes:
            if abs(scene['start'] - start) < 2:
                start = scene['start']
            if abs(scene['end'] - end) < 2:
                end = scene['end']
        
        return start, end
    
    def _get_clip_text(self, segments: List[Dict], 
                       start: float, end: float) -> str:
        """Get transcript text for a specific clip."""
        clip_segments = [
            seg for seg in segments
            if seg['start'] >= start and seg['end'] <= end
        ]
        return " ".join([seg['text'] for seg in clip_segments])
    
    def process_local_video(self,
                            video_path: str,
                            num_clips: int = 3,
                            add_music: bool = True,
                            add_zoom: bool = True) -> Dict:
        """
        Process a local video file.
        
        Args:
            video_path: Path to local video file
            num_clips: Number of clips to generate
            add_music: Whether to add background music
            add_zoom: Whether to add cinematic zoom effects
            
        Returns:
            Dictionary containing results and generated clips
        """
        results = {
            'success': False,
            'clips': [],
            'errors': [],
        }
        
        try:
            # Get video title from filename
            video_title = os.path.splitext(os.path.basename(video_path))[0]
            
            # Step 1: Transcribe audio
            print("Step 1: Transcribing audio...")
            transcript_data = self.transcriber.transcribe(video_path)
            transcript = transcript_data['text']
            segments = transcript_data['segments']
            
            print(f"Transcribed {len(segments)} segments")
            
            # Step 2: Detect scenes
            print("Step 2: Detecting scenes...")
            scenes = self.scene_detector.detect_scenes(video_path)
            
            print(f"Detected {len(scenes)} scenes")
            
            # Step 3: Analyze content with AI
            print("Step 3: Analyzing content with AI...")
            analysis = self.content_analyzer.analyze_transcript(transcript, video_title)
            
            print("AI analysis complete")
            
            # Step 4: Find key moments
            print("Step 4: Finding key moments...")
            clip_segments = self._find_best_segments(
                scenes=scenes,
                segments=segments,
                num_clips=num_clips
            )
            
            print(f"Identified {len(clip_segments)} key moments")
            
            # Step 5: Get background music
            music_path = None
            if add_music and settings.freesound_api_key:
                print("Step 5: Getting background music...")
                music_path = self.music_manager.get_default_music()
                if music_path:
                    print(f"Music downloaded: {music_path}")
            
            # Step 6: Generate clips
            print("Step 6: Generating clips...")
            for i, segment in enumerate(clip_segments[:num_clips]):
                print(f"Creating clip {i+1}/{num_clips}...")
                
                # Generate text hook using AI
                clip_text = self._get_clip_text(segments, segment['start'], segment['end'])
                text_hook = self.content_analyzer.generate_text_hook(clip_text)
                
                # Generate viral title
                viral_title = self.content_analyzer.generate_viral_title(clip_text)
                
                # Create clip
                clip_result = self.video_processor.create_clip(
                    video_path=video_path,
                    start_time=segment['start'],
                    end_time=segment['end'],
                    output_name=f"clip_{i+1}",
                    text_hook=text_hook,
                    add_zoom=add_zoom,
                    music_path=music_path
                )
                
                if clip_result['success']:
                    clip_result['title'] = viral_title
                    clip_result['text_hook'] = text_hook
                    results['clips'].append(clip_result)
                    print(f"Clip {i+1} created successfully")
                else:
                    results['errors'].append(clip_result.get('error', 'Unknown error'))
            
            results['success'] = len(results['clips']) > 0
            results['original_title'] = video_title
            results['analysis'] = analysis.get('analysis', '')
            
            return results
            
        except Exception as e:
            results['errors'].append(str(e))
            return results

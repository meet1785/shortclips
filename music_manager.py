"""
Music manager for adding copyright-free background music using Freesound API.
"""

import os
import requests
from typing import List, Dict, Optional
from config import settings


class MusicManager:
    """Manages copyright-free music from Freesound."""
    
    def __init__(self):
        """Initialize Freesound API client."""
        self.api_key = settings.freesound_api_key
        self.base_url = "https://freesound.org/apiv2"
        
    def search_music(self, query: str = "background music", 
                     duration_range: tuple = (15, 120),
                     limit: int = 10) -> List[Dict]:
        """
        Search for copyright-free music on Freesound.
        
        Args:
            query: Search query
            duration_range: (min_duration, max_duration) in seconds
            limit: Maximum number of results
            
        Returns:
            List of music tracks with metadata
        """
        if not self.api_key:
            return []
        
        params = {
            'query': query,
            'token': self.api_key,
            'filter': f'duration:[{duration_range[0]} TO {duration_range[1]}]',
            'fields': 'id,name,duration,url,previews,license',
            'page_size': limit,
        }
        
        try:
            response = requests.get(f"{self.base_url}/search/text/", params=params)
            response.raise_for_status()
            data = response.json()
            
            return data.get('results', [])
        except Exception as e:
            print(f"Failed to search music: {str(e)}")
            return []
    
    def download_music(self, sound_id: int, output_path: str) -> bool:
        """
        Download music file from Freesound.
        
        Args:
            sound_id: Freesound sound ID
            output_path: Path to save the music file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.api_key:
            return False
        
        try:
            # Get sound details
            response = requests.get(
                f"{self.base_url}/sounds/{sound_id}/",
                params={'token': self.api_key}
            )
            response.raise_for_status()
            sound_data = response.json()
            
            # Download preview (high quality)
            preview_url = sound_data['previews']['preview-hq-mp3']
            
            audio_response = requests.get(preview_url)
            audio_response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(audio_response.content)
            
            return True
        except Exception as e:
            print(f"Failed to download music: {str(e)}")
            return False
    
    def get_default_music(self) -> Optional[str]:
        """
        Get a default background music track.
        
        Returns:
            Path to downloaded music or None
        """
        # Search for upbeat background music
        tracks = self.search_music("upbeat instrumental", duration_range=(30, 180), limit=5)
        
        if not tracks:
            return None
        
        # Download first suitable track
        for track in tracks:
            output_path = os.path.join(settings.temp_dir, f"music_{track['id']}.mp3")
            
            if self.download_music(track['id'], output_path):
                return output_path
        
        return None
    
    def search_by_mood(self, mood: str = "upbeat", 
                       duration: int = 30) -> Optional[str]:
        """
        Search and download music by mood.
        
        Args:
            mood: Mood/style of music (upbeat, calm, energetic, etc.)
            duration: Approximate duration needed
            
        Returns:
            Path to downloaded music or None
        """
        query = f"{mood} instrumental music"
        tracks = self.search_music(
            query, 
            duration_range=(duration - 10, duration + 30),
            limit=5
        )
        
        if not tracks:
            return None
        
        # Download first track
        if tracks:
            output_path = os.path.join(settings.temp_dir, f"music_{tracks[0]['id']}.mp3")
            if self.download_music(tracks[0]['id'], output_path):
                return output_path
        
        return None

"""
Video downloader module using yt-dlp.
Downloads videos from YouTube and other platforms.
"""

import os
import yt_dlp
from typing import Dict, Optional
from config import settings


class VideoDownloader:
    """Downloads videos using yt-dlp."""
    
    def __init__(self):
        self.download_dir = settings.downloads_dir
        
    def download(self, url: str, output_filename: Optional[str] = None) -> Dict[str, str]:
        """
        Download video from URL.
        
        Args:
            url: Video URL (YouTube, etc.)
            output_filename: Optional custom filename
            
        Returns:
            Dictionary containing video path and metadata
        """
        if not output_filename:
            output_filename = "%(title)s.%(ext)s"
            
        output_path = os.path.join(self.download_dir, output_filename)
        
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_path,
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'merge_output_format': 'mp4',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Get the actual downloaded file path
                if 'requested_downloads' in info:
                    filepath = info['requested_downloads'][0]['filepath']
                else:
                    filepath = ydl.prepare_filename(info)
                
                return {
                    'filepath': filepath,
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'description': info.get('description', ''),
                    'uploader': info.get('uploader', 'Unknown'),
                }
        except Exception as e:
            raise Exception(f"Failed to download video: {str(e)}")
    
    def get_video_info(self, url: str) -> Dict:
        """Get video information without downloading."""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                }
        except Exception as e:
            raise Exception(f"Failed to get video info: {str(e)}")

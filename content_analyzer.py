"""
AI content analyzer using Google Gemini Pro.
Identifies key moments and generates viral titles/captions.
"""

import google.generativeai as genai
from typing import List, Dict, Optional
from config import settings


class ContentAnalyzer:
    """Analyzes video content using Gemini Pro to find viral moments."""
    
    def __init__(self):
        """Initialize Gemini Pro API."""
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not set in environment")
        
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def analyze_transcript(self, transcript: str, video_title: str = "") -> Dict:
        """
        Analyze transcript to find key moments for viral clips.
        
        Args:
            transcript: Full video transcript
            video_title: Original video title
            
        Returns:
            Analysis with key moments and suggestions
        """
        prompt = f"""Analyze this video transcript and identify the most engaging moments for creating viral short-form clips (15-60 seconds).

Video Title: {video_title}

Transcript:
{transcript}

Please provide:
1. Top 3-5 key moments that would make great short clips (with approximate timestamp references if mentioned)
2. Why each moment is engaging (hook, emotional impact, educational value, etc.)
3. Suggested viral titles for each clip (attention-grabbing, curiosity-inducing)
4. Suggested text hooks/captions for each clip (first 3 seconds overlay text)

Format your response as structured data that can be parsed."""

        try:
            response = self.model.generate_content(prompt)
            return {
                'analysis': response.text,
                'success': True,
            }
        except Exception as e:
            return {
                'analysis': '',
                'success': False,
                'error': str(e),
            }
    
    def find_key_moments(self, segments: List[Dict], 
                         min_duration: int = 15,
                         max_duration: int = 60) -> List[Dict]:
        """
        Find key moments in transcript segments based on content.
        
        Args:
            segments: List of transcript segments with timestamps
            min_duration: Minimum clip duration
            max_duration: Maximum clip duration
            
        Returns:
            List of suggested clip segments
        """
        # Combine segments into chunks
        full_text = " ".join([seg['text'] for seg in segments])
        
        prompt = f"""Given this video transcript, identify the exact time ranges for the top 3-5 most engaging moments suitable for 15-60 second clips.

Transcript with timestamps:
{self._format_segments(segments)}

For each key moment, provide:
1. Start time (in seconds)
2. End time (in seconds) - ensure duration is between {min_duration} and {max_duration} seconds
3. Brief description of why this moment is engaging
4. Suggested viral title
5. Text hook (3-5 words for overlay)

Respond in a structured format."""

        try:
            response = self.model.generate_content(prompt)
            
            # Parse response (simplified - in production, use more robust parsing)
            return {
                'suggestions': response.text,
                'success': True,
            }
        except Exception as e:
            return {
                'suggestions': '',
                'success': False,
                'error': str(e),
            }
    
    def generate_viral_title(self, clip_context: str) -> str:
        """
        Generate a viral title for a clip.
        
        Args:
            clip_context: Context/content of the clip
            
        Returns:
            Viral title suggestion
        """
        prompt = f"""Generate 3 viral, attention-grabbing titles for this video clip content:

{clip_context}

Make them:
- Curiosity-inducing
- Emotional or shocking
- Under 60 characters
- Suitable for TikTok/YouTube Shorts/Instagram Reels

Provide 3 options, one per line."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return "Amazing Video Clip"
    
    def generate_text_hook(self, clip_context: str) -> str:
        """
        Generate a text hook for the first 3 seconds of a clip.
        
        Args:
            clip_context: Context/content of the clip
            
        Returns:
            Short text hook (3-7 words)
        """
        prompt = f"""Generate a short, attention-grabbing text hook (3-7 words) for the first 3 seconds of this clip:

{clip_context}

Make it:
- Ultra-short and punchy
- Creates curiosity
- Makes viewer want to keep watching

Provide only the hook text, nothing else."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return "Watch this..."
    
    def _format_segments(self, segments: List[Dict]) -> str:
        """Format segments with timestamps for prompt."""
        formatted = []
        for seg in segments:
            formatted.append(f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")
        return "\n".join(formatted)

"""
FastAPI application for the Short Clips AI tool.
Provides REST API endpoints for video processing.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
import os
import uvicorn
from pathlib import Path
from orchestrator import ClipOrchestrator
from config import settings


def safe_join_path(base_dir: str, filename: str) -> str:
    """
    Safely join paths and prevent directory traversal attacks.
    
    Args:
        base_dir: Base directory path
        filename: Filename to join
        
    Returns:
        Safe joined path
        
    Raises:
        HTTPException: If path traversal is detected
    """
    # Resolve the base directory to absolute path
    base = Path(base_dir).resolve()
    
    # Remove any path components and use only the filename
    safe_filename = os.path.basename(filename)
    
    # Join and resolve the full path
    full_path = (base / safe_filename).resolve()
    
    # Ensure the resolved path is within the base directory
    try:
        full_path.relative_to(base)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    return str(full_path)


# Initialize FastAPI app
app = FastAPI(
    title="Short Clips AI",
    description="AI-powered tool to convert long videos into viral short clips",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = ClipOrchestrator()

# Store processing jobs
processing_jobs = {}


# Request models
class VideoProcessRequest(BaseModel):
    """Request model for processing a video URL."""
    video_url: HttpUrl
    num_clips: int = 3
    add_music: bool = True
    add_zoom: bool = True


class VideoInfoRequest(BaseModel):
    """Request model for getting video info."""
    video_url: HttpUrl


# Response models
class ClipInfo(BaseModel):
    """Information about a generated clip."""
    video_path: str
    thumbnail_path: str
    duration: float
    title: str
    text_hook: str


class ProcessResponse(BaseModel):
    """Response model for video processing."""
    success: bool
    clips: List[dict]
    original_title: Optional[str] = None
    analysis: Optional[str] = None
    errors: List[str] = []


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Short Clips AI",
        "version": "1.0.0",
        "description": "Convert long videos into viral short clips",
        "endpoints": {
            "POST /process": "Process a video URL",
            "POST /process-local": "Process a local video file",
            "GET /video-info": "Get video information",
            "GET /clips/{clip_id}": "Download a generated clip",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "gemini_api_configured": bool(settings.gemini_api_key),
        "freesound_api_configured": bool(settings.freesound_api_key),
    }


@app.post("/process", response_model=ProcessResponse)
async def process_video(request: VideoProcessRequest, background_tasks: BackgroundTasks):
    """
    Process a video URL and generate viral clips.
    
    Args:
        request: Video processing request
        background_tasks: FastAPI background tasks
        
    Returns:
        Processing results with generated clips
    """
    try:
        # Validate Gemini API key
        if not settings.gemini_api_key:
            raise HTTPException(
                status_code=400,
                detail="GEMINI_API_KEY not configured. Please set it in .env file."
            )
        
        # Process video
        results = orchestrator.process_video(
            video_url=str(request.video_url),
            num_clips=request.num_clips,
            add_music=request.add_music,
            add_zoom=request.add_zoom
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-local")
async def process_local_video(
    file: UploadFile = File(...),
    num_clips: int = 3,
    add_music: bool = True,
    add_zoom: bool = True
):
    """
    Process a locally uploaded video file.
    
    Args:
        file: Uploaded video file
        num_clips: Number of clips to generate
        add_music: Whether to add background music
        add_zoom: Whether to add cinematic zoom effects
        
    Returns:
        Processing results with generated clips
    """
    try:
        # Validate Gemini API key
        if not settings.gemini_api_key:
            raise HTTPException(
                status_code=400,
                detail="GEMINI_API_KEY not configured. Please set it in .env file."
            )
        
        # Save uploaded file
        file_path = os.path.join(settings.downloads_dir, file.filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process video
        results = orchestrator.process_local_video(
            video_path=file_path,
            num_clips=num_clips,
            add_music=add_music,
            add_zoom=add_zoom
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/video-info")
async def get_video_info(video_url: str):
    """
    Get information about a video without downloading it.
    
    Args:
        video_url: URL of the video
        
    Returns:
        Video metadata
    """
    try:
        info = orchestrator.downloader.get_video_info(video_url)
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/clips/{clip_name}")
async def download_clip(clip_name: str):
    """
    Download a generated clip.
    
    Args:
        clip_name: Name of the clip file
        
    Returns:
        Video file
    """
    # Use safe path joining to prevent directory traversal
    clip_path = safe_join_path(settings.outputs_dir, clip_name)
    
    if not os.path.exists(clip_path):
        raise HTTPException(status_code=404, detail="Clip not found")
    
    # Ensure it's a file and has correct extension
    if not os.path.isfile(clip_path) or not clip_name.endswith('.mp4'):
        raise HTTPException(status_code=400, detail="Invalid clip file")
    
    return FileResponse(
        clip_path,
        media_type="video/mp4",
        filename=os.path.basename(clip_path)
    )


@app.get("/thumbnails/{thumbnail_name}")
async def download_thumbnail(thumbnail_name: str):
    """
    Download a generated thumbnail.
    
    Args:
        thumbnail_name: Name of the thumbnail file
        
    Returns:
        Image file
    """
    # Use safe path joining to prevent directory traversal
    thumbnail_path = safe_join_path(settings.outputs_dir, thumbnail_name)
    
    if not os.path.exists(thumbnail_path):
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    # Ensure it's a file and has correct extension
    if not os.path.isfile(thumbnail_path) or not thumbnail_name.endswith('.jpg'):
        raise HTTPException(status_code=400, detail="Invalid thumbnail file")
    
    return FileResponse(
        thumbnail_path,
        media_type="image/jpeg",
        filename=os.path.basename(thumbnail_path)
    )


@app.delete("/clips/{clip_name}")
async def delete_clip(clip_name: str):
    """
    Delete a generated clip and its thumbnail.
    
    Args:
        clip_name: Name of the clip file
        
    Returns:
        Success message
    """
    # Use safe path joining to prevent directory traversal
    clip_path = safe_join_path(settings.outputs_dir, clip_name)
    
    # Ensure it's a valid MP4 file
    if not clip_name.endswith('.mp4'):
        raise HTTPException(status_code=400, detail="Invalid clip name")
    
    if os.path.exists(clip_path) and os.path.isfile(clip_path):
        os.remove(clip_path)
        
        # Also remove thumbnail
        thumbnail_name = clip_name.replace(".mp4", "_thumb.jpg")
        thumbnail_path = safe_join_path(settings.outputs_dir, thumbnail_name)
        if os.path.exists(thumbnail_path) and os.path.isfile(thumbnail_path):
            os.remove(thumbnail_path)
        
        return {"message": "Clip deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Clip not found")


@app.get("/clips")
async def list_clips():
    """
    List all generated clips.
    
    Returns:
        List of clip files
    """
    try:
        clips = []
        for filename in os.listdir(settings.outputs_dir):
            if filename.endswith(".mp4"):
                file_path = os.path.join(settings.outputs_dir, filename)
                thumbnail_name = filename.replace(".mp4", "_thumb.jpg")
                
                clips.append({
                    "name": filename,
                    "size": os.path.getsize(file_path),
                    "thumbnail": thumbnail_name if os.path.exists(
                        os.path.join(settings.outputs_dir, thumbnail_name)
                    ) else None,
                })
        
        return {"clips": clips}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def start_server():
    """Start the FastAPI server."""
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )


if __name__ == "__main__":
    start_server()

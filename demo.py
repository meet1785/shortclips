#!/usr/bin/env python3
"""
Demo script to test the Short Clips AI functionality.
This script demonstrates basic usage without needing API keys.
"""

import os


def print_banner():
    """Print welcome banner."""
    print("=" * 70)
    print(" " * 20 + "SHORT CLIPS AI DEMO")
    print("=" * 70)
    print()


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    dependencies = {
        "fastapi": "FastAPI",
        "yt_dlp": "yt-dlp",
        "whisper": "OpenAI Whisper",
        "scenedetect": "PySceneDetect",
        "moviepy": "MoviePy",
        "google.generativeai": "Google Generative AI",
        "PIL": "Pillow",
    }
    
    missing = []
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - MISSING")
            missing.append(name)
    
    if missing:
        print("\n⚠️  Missing dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nInstall with: pip install -r requirements.txt")
        return False
    
    print("\n✓ All dependencies installed!\n")
    return True


def check_ffmpeg():
    """Check if FFmpeg is installed."""
    print("Checking FFmpeg...")
    
    import subprocess
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"  ✓ {version}\n")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("  ✗ FFmpeg not found!")
    print("\nPlease install FFmpeg:")
    print("  Ubuntu/Debian: sudo apt install ffmpeg")
    print("  macOS: brew install ffmpeg")
    print("  Windows: Download from ffmpeg.org\n")
    return False


def check_config():
    """Check configuration."""
    print("Checking configuration...")
    
    from config import settings
    
    issues = []
    
    if not settings.gemini_api_key:
        issues.append("GEMINI_API_KEY not set")
        print("  ⚠️  GEMINI_API_KEY not configured")
        print("     Get free API key: https://makersuite.google.com/app/apikey")
    else:
        print("  ✓ GEMINI_API_KEY configured")
    
    if not settings.freesound_api_key:
        print("  ⚠️  FREESOUND_API_KEY not configured (optional)")
        print("     Background music will be disabled")
        print("     Get free API key: https://freesound.org/apiv2/apply/")
    else:
        print("  ✓ FREESOUND_API_KEY configured")
    
    # Check directories
    for dir_name in [settings.downloads_dir, settings.outputs_dir, 
                     settings.temp_dir, settings.models_dir]:
        if os.path.exists(dir_name):
            print(f"  ✓ Directory '{dir_name}' exists")
        else:
            print(f"  ⚠️  Directory '{dir_name}' will be created")
    
    print()
    return len(issues) == 0


def show_usage():
    """Show usage examples."""
    print("Usage Examples:")
    print("=" * 70)
    print()
    print("1. CLI Usage:")
    print("   python cli.py 'https://youtube.com/watch?v=...' -n 3")
    print()
    print("2. API Server:")
    print("   python main.py")
    print("   Then visit: http://localhost:8000/docs")
    print()
    print("3. Python Module:")
    print("   from orchestrator import ClipOrchestrator")
    print("   orchestrator = ClipOrchestrator()")
    print("   results = orchestrator.process_video('https://...')")
    print()
    print("For more examples, see EXAMPLES.md")
    print("=" * 70)
    print()


def main():
    """Main demo function."""
    print_banner()
    
    # Check everything
    deps_ok = check_dependencies()
    ffmpeg_ok = check_ffmpeg()
    config_ok = check_config()
    
    if deps_ok and ffmpeg_ok:
        print("✅ System is ready to process videos!")
        print()
        
        if not config_ok:
            print("⚠️  Note: Some API keys are missing.")
            print("   You can still test with your own API keys.")
        
        print()
        show_usage()
    else:
        print("❌ Please fix the issues above before running.")
        print()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

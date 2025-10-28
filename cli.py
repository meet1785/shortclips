#!/usr/bin/env python3
"""
Command-line interface for Short Clips AI.
Process videos from the command line without starting the server.
"""

import argparse
import sys
from orchestrator import ClipOrchestrator
from config import settings


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Short Clips AI - Convert long videos into viral short clips"
    )
    
    parser.add_argument(
        "video",
        help="Video URL (YouTube, etc.) or path to local video file"
    )
    
    parser.add_argument(
        "-n", "--num-clips",
        type=int,
        default=3,
        help="Number of clips to generate (default: 3)"
    )
    
    parser.add_argument(
        "--no-music",
        action="store_true",
        help="Don't add background music"
    )
    
    parser.add_argument(
        "--no-zoom",
        action="store_true",
        help="Don't add cinematic zoom effects"
    )
    
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Custom output directory"
    )
    
    args = parser.parse_args()
    
    # Check if Gemini API key is set
    if not settings.gemini_api_key:
        print("ERROR: GEMINI_API_KEY not set!")
        print("Please set it in .env file or environment variables.")
        print("Get a free API key from: https://makersuite.google.com/app/apikey")
        sys.exit(1)
    
    # Initialize orchestrator
    print("Initializing Short Clips AI...")
    orchestrator = ClipOrchestrator()
    
    # Determine if video is URL or local file
    import os
    is_local = os.path.isfile(args.video)
    
    print(f"\nProcessing {'local video' if is_local else 'video from URL'}...")
    print(f"Video: {args.video}")
    print(f"Generating {args.num_clips} clips")
    print(f"Background music: {'No' if args.no_music else 'Yes'}")
    print(f"Cinematic zoom: {'No' if args.no_zoom else 'Yes'}")
    print()
    
    try:
        # Process video
        if is_local:
            results = orchestrator.process_local_video(
                video_path=args.video,
                num_clips=args.num_clips,
                add_music=not args.no_music,
                add_zoom=not args.no_zoom
            )
        else:
            results = orchestrator.process_video(
                video_url=args.video,
                num_clips=args.num_clips,
                add_music=not args.no_music,
                add_zoom=not args.no_zoom
            )
        
        # Display results
        if results['success']:
            print("\n" + "="*60)
            print("✅ SUCCESS! Generated clips:")
            print("="*60)
            
            for i, clip in enumerate(results['clips'], 1):
                print(f"\nClip {i}:")
                print(f"  📹 Video: {clip['video_path']}")
                print(f"  🖼️  Thumbnail: {clip['thumbnail_path']}")
                print(f"  ⏱️  Duration: {clip['duration']:.1f}s")
                print(f"  📝 Title: {clip.get('title', 'N/A')}")
                print(f"  🎯 Hook: {clip.get('text_hook', 'N/A')}")
            
            print(f"\n📁 All clips saved to: {settings.outputs_dir}/")
            print("\n🎉 Ready to upload to TikTok, Reels, or Shorts!")
            
            if results.get('analysis'):
                print("\n" + "="*60)
                print("📊 AI Analysis:")
                print("="*60)
                print(results['analysis'][:500] + "..." if len(results['analysis']) > 500 else results['analysis'])
        
        else:
            print("\n❌ ERROR: Failed to generate clips")
            if results['errors']:
                print("Errors:")
                for error in results['errors']:
                    print(f"  - {error}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

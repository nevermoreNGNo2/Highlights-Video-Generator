import os
import subprocess
import logging
import tempfile
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_simple_highlight_intro(output_path, width=1280, height=720):
    """
    Create an extremely simple HIGHLIGHTS intro screen - standalone utility
    
    Args:
        output_path: Where to save the intro video
        width: Video width
        height: Video height
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Creating simple highlight intro at {output_path}")
        
        # Create a very basic HIGHLIGHTS text video
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c=black:s={width}x{height}:d=2",
            "-vf", f"drawtext=text=HIGHLIGHTS:fontcolor=white:fontsize=96:x=(w-text_w)/2:y=(h-text_h)/2",
            "-c:v", "libx264",
            "-t", "2",
            output_path
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr.decode('utf-8')}")
            return False
            
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            logger.info(f"Successfully created intro at {output_path}")
            return True
        else:
            logger.error(f"Failed to create intro or file too small")
            return False
    
    except Exception as e:
        logger.error(f"Error in create_simple_highlight_intro: {str(e)}")
        return False

# Direct testing function
if __name__ == "__main__":
    # Test the intro creator directly
    test_output = os.path.join(tempfile.gettempdir(), "test_intro.mp4")
    success = create_simple_highlight_intro(test_output)
    print(f"Intro creation {'succeeded' if success else 'failed'}")
    print(f"Output path: {test_output}")
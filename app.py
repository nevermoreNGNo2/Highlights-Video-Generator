import streamlit as st
import tempfile
import os
import time
from pathlib import Path
import logging
import subprocess
from datetime import datetime

# Import modules
from modules.scene_detector import SceneDetector
from modules.audio_analyzer import AudioAnalyzer
from modules.action_recognizer import ActionRecognizer
from modules.highlight_creator import HighlightCreator
from modules.video_editor import VideoEditor
from utils.helpers import get_video_info, format_time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="Video Highlight Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

def downscale_video(input_path, output_path, width=640, height=360):
    """Downscale video using FFmpeg to speed up processing"""
    cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-vf', f'scale={width}:{height}',
        '-c:a', 'copy', output_path
    ]
    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0

def main():
    st.title("🎬 Automatic Video Highlight Generator")
    st.markdown("""
    Upload a video and let AI create a highlight reel by detecting key moments.
    The system uses scene detection, audio analysis, and action recognition.
    """)

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload a video file", 
        type=["mp4", "mov", "avi", "mkv", "webm"],
        help="Maximum upload size depends on your Streamlit server configuration"
    )
    
    if uploaded_file:
        # Save uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Video preview
        with st.expander("Preview Original Video", expanded=True):
            st.video(temp_path)
            video_info = get_video_info(temp_path)
            if video_info:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Duration", video_info.get('duration_formatted', 'Unknown'))
                with col2:
                    st.metric("Resolution", f"{video_info.get('width', 0)}×{video_info.get('height', 0)}")
                with col3:
                    st.metric("FPS", f"{video_info.get('fps', 0):.1f}")
        
        # Process button
        if st.button("Generate Highlights", type="primary", use_container_width=True):
            progress_container = st.container()
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
                results_area = st.container()
            
            start_time = time.time()
            
            try:
                progress_bar.progress(0.1)
                
                # Create processing objects
                scene_detector = SceneDetector(threshold=0.5)  # Default sensitivity
                audio_analyzer = AudioAnalyzer(sensitivity=0.5)
                action_recognizer = ActionRecognizer(confidence_threshold=0.5)
                highlight_creator = HighlightCreator()
                video_editor = VideoEditor()
                
                # Detect scenes
                # Detect scenes (optimized)
                # Detect scenes
                status_text.text("Detecting scene changes...")
                scenes = scene_detector.detect_scenes(temp_path)
                progress_bar.progress(0.25)

                
                # Analyze audio
                status_text.text("Analyzing audio for exciting moments...")
                audio_highlights = audio_analyzer.find_exciting_moments(temp_path)
                progress_bar.progress(0.5)
                
                # Detect actions
                status_text.text("Recognizing important actions...")
                action_highlights = action_recognizer.detect_actions(temp_path)
                progress_bar.progress(0.75)
                
                # Create highlights (use default logic)
                status_text.text("Selecting highlight segments...")
                video_duration = float(video_info.get('duration', 0)) if video_info else 0
                target_duration = min(60, video_duration * 0.3) if video_duration else 60
                highlights = highlight_creator.create_highlights(
                    video_path=temp_path,
                    scenes=scenes,
                    audio_highlights=audio_highlights,
                    action_highlights=action_highlights,
                    target_duration=target_duration
                )
                
                # Always use simple concatenation
                status_text.text("Creating highlight video (simple concatenation)...")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join("output", f"highlights_{timestamp}.mp4")
                output_path = video_editor.create_highlight_video(
                    video_path=temp_path,
                    highlights=highlights,
                    transition_type="None",  # Always simple concatenation
                    output_dir="output",
                    add_intro=False,         # No intro
                    resolution="original"    # Keep original resolution
                )
                
                progress_bar.progress(1.0)
                processing_time = time.time() - start_time
                
                # Display results
                with results_area:
                    if output_path and os.path.exists(output_path):
                        st.success(f"🎉 Highlight video created successfully in {processing_time:.1f} seconds!")
                        st.subheader("Highlight Video")
                        st.video(output_path)
                        with open(output_path, "rb") as file:
                            filename = f"highlight_{Path(uploaded_file.name).stem}.mp4"
                            st.download_button(
                                label="⬇️ Download Highlight Video",
                                data=file,
                                file_name=filename,
                                mime="video/mp4",
                                use_container_width=True
                            )
                        st.subheader("Highlight Statistics")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Scenes Detected", len(scenes) if scenes else 0)
                        with col2:
                            st.metric("Audio Highlights", len(audio_highlights) if audio_highlights else 0)
                        with col3:
                            st.metric("Action Segments", len(action_highlights) if action_highlights else 0)
                    else:
                        st.error("Failed to create highlight video. Check if FFmpeg is installed.")
                    
            except Exception as e:
                st.error(f"Error generating highlights: {str(e)}")
                logger.exception("Error in highlight generation")

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("output", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    
    main()
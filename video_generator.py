"""Simple Video Generator using MoviePy and GTTS.

Generates educational videos with text overlays and narration.
"""
import os
from pathlib import Path
from moviepy.editor import (
    TextClip, ColorClip, CompositeVideoClip, 
    concatenate_videoclips, AudioFileClip, ImageClip
)
from moviepy.config import change_settings
from gtts import gTTS
import tempfile
import subprocess
import numpy as np
from PIL import Image, ImageDraw

# Configure ImageMagick path for MoviePy
try:
    # Find ImageMagick convert binary
    result = subprocess.run(['which', 'convert'], capture_output=True, text=True)
    if result.returncode == 0:
        convert_path = result.stdout.strip()
        change_settings({"IMAGEMAGICK_BINARY": convert_path})
except Exception as e:
    print(f"Warning: Could not configure ImageMagick: {e}")
    pass

class VideoGenerator:
    def __init__(self, output_dir="generated_videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def create_simple_visual(self, scene_number, duration, size=(400, 300)):
        """Create simple animated visual (circles, arrows, boxes) for educational content."""
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Different visuals for different scenes
        colors = [(100, 200, 255), (255, 150, 100), (150, 255, 150), (255, 200, 150)]
        color = colors[scene_number % len(colors)]
        
        if scene_number % 4 == 0:
            # Draw circle (concept/topic)
            draw.ellipse([50, 50, 350, 250], fill=color + (180,), outline=color + (255,), width=5)
        elif scene_number % 4 == 1:
            # Draw rectangles (steps/process)
            for i in range(3):
                y = 50 + i * 80
                draw.rectangle([50, y, 350, y + 60], fill=color + (180,), outline=color + (255,), width=4)
        elif scene_number % 4 == 2:
            # Draw arrows (flow/connection)
            draw.polygon([(200, 50), (350, 150), (200, 250), (250, 150)], fill=color + (180,), outline=color + (255,))
        else:
            # Draw grid/network
            for i in range(4):
                for j in range(3):
                    x, y = 50 + i * 100, 50 + j * 80
                    draw.ellipse([x, y, x + 60, y + 60], fill=color + (180,), outline=color + (255,), width=3)
        
        # Convert to numpy array
        return np.array(img)
        
    def generate_video(self, scenes, topic, video_id):
        """
        Generate video from scenes
        
        Args:
            scenes: List of scene dicts with narration_text, title, visual_description
            topic: Video topic name
            video_id: Unique video identifier
            
        Returns:
            Path to generated video file
        """
        try:
            clips = []
            temp_audio_files = []
            
            # Generate each scene
            for idx, scene in enumerate(scenes):
                narration = scene.get('narration_text', '')
                title = scene.get('title', f'Scene {idx + 1}')
                visual_desc = scene.get('visual_description', '')
                
                # Generate audio from narration
                audio_path = tempfile.mktemp(suffix='.mp3')
                temp_audio_files.append(audio_path)
                
                tts = gTTS(text=narration, lang='en', slow=False)
                tts.save(audio_path)
                
                # Load audio to get duration
                audio = AudioFileClip(audio_path)
                duration = audio.duration
                
                # Create background
                bg = ColorClip(
                    size=(1280, 720),
                    color=(45, 55, 72),  # Dark blue-gray
                    duration=duration
                )
                
                # Create title text
                title_clip = TextClip(
                    title,
                    fontsize=60,
                    color='white',
                    font='Arial-Bold',
                    method='caption',
                    size=(1100, None)
                ).set_position(('center', 100)).set_duration(duration)
                
                # Create narration text (subtitle-like)
                narration_clip = TextClip(
                    narration,
                    fontsize=28,
                    color='white',
                    font='Arial',
                    method='caption',
                    size=(900, None),
                    align='center'
                ).set_position(('center', 500)).set_duration(duration)
                
                # Create simple visual animation
                visual_img = self.create_simple_visual(idx, duration)
                visual_clip = ImageClip(visual_img).set_duration(duration).set_position((50, 200))
                
                # Composite all elements with visual
                scene_clip = CompositeVideoClip([
                    bg, visual_clip, title_clip, narration_clip
                ]).set_audio(audio)
                
                clips.append(scene_clip)
            
            # Concatenate all scenes
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Output path
            output_path = self.output_dir / f"{video_id}.mp4"
            
            # Write video file
            final_video.write_videofile(
                str(output_path),
                fps=24,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=tempfile.mktemp(suffix='.m4a'),
                remove_temp=True,
                logger=None  # Suppress moviepy logs
            )
            
            # Cleanup
            final_video.close()
            for audio_file in temp_audio_files:
                if os.path.exists(audio_file):
                    os.remove(audio_file)
            
            return str(output_path)
            
        except Exception as e:
            # Cleanup on error
            for audio_file in temp_audio_files:
                if os.path.exists(audio_file):
                    try:
                        os.remove(audio_file)
                    except:
                        pass
            raise e
    
    def create_intro_video(self, topic, duration=3):
        """Create a simple intro scene"""
        bg = ColorClip(size=(1280, 720), color=(45, 55, 72), duration=duration)
        
        title = TextClip(
            topic,
            fontsize=80,
            color='white',
            font='Arial-Bold',
            method='caption',
            size=(1100, None)
        ).set_position('center').set_duration(duration)
        
        subtitle = TextClip(
            "Educational Video",
            fontsize=40,
            color='#60A5FA',
            font='Arial',
        ).set_position(('center', 450)).set_duration(duration)
        
        return CompositeVideoClip([bg, title, subtitle])

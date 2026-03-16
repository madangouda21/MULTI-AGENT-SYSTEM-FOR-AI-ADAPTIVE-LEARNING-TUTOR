"""
3Blue1Brown Complete Video Generator
Generates ALL 4 sections for creating professional math videos:
1. Voiceover Script (with [PAUSE] and [EMPHASIS] markers)
2. Animation Storyboard (scene-by-scene descriptions)
3. Manim Code (runnable Python)
4. Voice Generation Prompt (for OpenAI TTS/ElevenLabs)
"""
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from openai import OpenAI
from dataclasses import dataclass


@dataclass
class VideoPackage:
    """Complete video generation package with all 4 sections."""
    topic: str
    voiceover_script: str
    animation_storyboard: str
    manim_code: str
    voice_prompt: str
    
    def to_string(self) -> str:
        """Return formatted string with all 4 sections."""
        return f"""
========================
SECTION 1: VOICEOVER SCRIPT
========================
{self.voiceover_script}

========================
SECTION 2: ANIMATION STORYBOARD
========================
{self.animation_storyboard}

========================
SECTION 3: MANIM CODE
========================
{self.manim_code}

========================
SECTION 4: VOICE GENERATION PROMPT
========================
{self.voice_prompt}
"""


class ThreeBlueOneBrownGenerator:
    """
    Complete 3Blue1Brown-style video generator.
    Creates professional educational content with natural narration.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.output_dir = Path("generated_videos")
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_complete_package(self, topic: str) -> VideoPackage:
        """
        Generate complete 3Blue1Brown-style video package.
        
        Args:
            topic: The math/science topic to explain
            
        Returns:
            VideoPackage with all 4 sections
        """
        print(f"\n🎬 Generating complete 3Blue1Brown package for: {topic}")
        print("=" * 60)
        
        # Generate all sections using GPT-4
        prompt = self._build_generation_prompt(topic)
        
        print("📝 Generating all 4 sections...")
        response = self.client.chat.completions.create(
            model="gpt-4o",  # Use GPT-4 for best quality
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        content = response.choices[0].message.content
        
        # Parse the 4 sections
        sections = self._parse_sections(content)
        
        print("✅ All sections generated!")
        
        return VideoPackage(
            topic=topic,
            voiceover_script=sections.get("voiceover", ""),
            animation_storyboard=sections.get("storyboard", ""),
            manim_code=sections.get("manim", ""),
            voice_prompt=sections.get("voice", "")
        )
    
    def _get_system_prompt(self) -> str:
        """System prompt for 3Blue1Brown style generation."""
        return """You are an educator, animator, and Python developer inspired by 3Blue1Brown.

STYLE RULES:
- Intuitive and visual-first explanations
- Friendly, curious, calm tone
- Short sentences for narration
- Minimal formalism
- Assume the viewer is smart but unfamiliar
- Pacing matters more than rigor

You must generate EXACTLY 4 sections, no more, no less.
Do NOT add any extra commentary or text outside the sections."""

    def _build_generation_prompt(self, topic: str) -> str:
        """Build the generation prompt for a topic."""
        return f"""Create a complete 3Blue1Brown-style math video package for:

TOPIC: "{topic}"

OUTPUT MUST HAVE EXACTLY 4 SECTIONS.
DO NOT ADD ANY EXTRA TEXT.

========================
SECTION 1: VOICEOVER SCRIPT
========================
- Conversational and warm
- Written exactly as it should be spoken
- Include [PAUSE] markers for natural breaks
- Include [EMPHASIS] markers for key points
- 2-3 minutes long when spoken

========================
SECTION 2: ANIMATION STORYBOARD
========================
- Scene-by-scene description
- Each scene explains:
  * What appears on screen
  * What moves or transforms
  * Why the visual helps understanding
- No code in this section
- Be specific about colors, positions, and animations

========================
SECTION 3: MANIM CODE
========================
- Manim Community Edition
- Python only
- 1920x1080 resolution
- One Scene class per major concept
- Use these Manim objects: Axes, MathTex, Dot, Arrow, Circle, Line, VGroup
- Use these animations: Write, FadeIn, FadeOut, Transform, Create, MoveAlongPath
- Use self.wait() where [PAUSE] appears in script
- Clean, runnable code
- Use 3Blue1Brown colors: BLUE_C, PURPLE_B, YELLOW, GREEN_C
- Background color: "#1e1e2e" (dark blue)

========================
SECTION 4: VOICE GENERATION PROMPT
========================
- A prompt suitable for OpenAI TTS or ElevenLabs
- Describe the voice style clearly:
  * Warm and curious
  * Calm, not rushed
  * Like explaining to a friend
  * Emphasize wonder and discovery
- Include the full voiceover script text
- Specify pacing instructions"""

    def _parse_sections(self, content: str) -> Dict[str, str]:
        """Parse the 4 sections from the generated content."""
        sections = {
            "voiceover": "",
            "storyboard": "",
            "manim": "",
            "voice": ""
        }
        
        # Split by section headers
        if "SECTION 1" in content and "SECTION 2" in content:
            parts = content.split("SECTION 1: VOICEOVER SCRIPT")
            if len(parts) > 1:
                remaining = parts[1]
                
                # Extract voiceover
                if "SECTION 2" in remaining:
                    voiceover_parts = remaining.split("SECTION 2")
                    sections["voiceover"] = voiceover_parts[0].strip().strip("=").strip()
                    remaining = "SECTION 2" + voiceover_parts[1]
                
                # Extract storyboard
                if "SECTION 3" in remaining:
                    storyboard_parts = remaining.split("SECTION 3")
                    sections["storyboard"] = storyboard_parts[0].replace("SECTION 2: ANIMATION STORYBOARD", "").strip().strip("=").strip()
                    remaining = "SECTION 3" + storyboard_parts[1]
                
                # Extract manim code
                if "SECTION 4" in remaining:
                    manim_parts = remaining.split("SECTION 4")
                    manim_text = manim_parts[0].replace("SECTION 3: MANIM CODE", "").strip().strip("=").strip()
                    # Extract code block if present
                    if "```python" in manim_text:
                        manim_text = manim_text.split("```python")[1].split("```")[0]
                    elif "```" in manim_text:
                        manim_text = manim_text.split("```")[1].split("```")[0]
                    sections["manim"] = manim_text.strip()
                    remaining = "SECTION 4" + manim_parts[1]
                
                # Extract voice prompt
                sections["voice"] = remaining.replace("SECTION 4: VOICE GENERATION PROMPT", "").strip().strip("=").strip()
        
        return sections
    
    def generate_audio(self, script: str, output_path: str, voice: str = "nova") -> str:
        """
        Generate natural TTS audio using OpenAI.
        
        Args:
            script: The voiceover script (can include [PAUSE] markers)
            output_path: Where to save the audio
            voice: OpenAI voice (nova, shimmer, alloy, echo, onyx, fable)
        """
        # Clean script - remove markers for TTS
        clean_script = script.replace("[PAUSE]", "...").replace("[EMPHASIS]", "")
        
        print(f"🎙️ Generating natural voice with '{voice}'...")
        
        response = self.client.audio.speech.create(
            model="tts-1-hd",
            voice=voice,
            input=clean_script,
            speed=0.95  # Slightly slower for educational clarity
        )
        
        response.stream_to_file(output_path)
        print(f"✅ Audio saved: {output_path}")
        return output_path
    
    def render_manim(self, manim_code: str, output_name: str) -> Optional[str]:
        """
        Render Manim code to video.
        
        Args:
            manim_code: The Manim Python code
            output_name: Name for the output video
            
        Returns:
            Path to rendered video or None if failed
        """
        print("🎨 Rendering Manim animation...")
        
        # Write code to temp file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        temp_file.write(manim_code)
        temp_file.close()
        
        try:
            # Find scene class name
            scene_name = "EducationalScene"
            for line in manim_code.split('\n'):
                if line.strip().startswith("class ") and "(Scene)" in line:
                    scene_name = line.split("class ")[1].split("(")[0].strip()
                    break
            
            # Render with Manim
            cmd = [
                "manim", "render",
                "-qh",  # High quality 1080p
                "--fps", "60",
                temp_file.name,
                scene_name
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Find output file
                media_dir = Path("media/videos")
                if media_dir.exists():
                    for video in media_dir.rglob("*.mp4"):
                        if scene_name in video.name:
                            print(f"✅ Video rendered: {video}")
                            return str(video)
            else:
                print(f"⚠️ Manim error: {result.stderr[:200]}")
                return None
                
        except Exception as e:
            print(f"⚠️ Rendering failed: {e}")
            return None
        finally:
            os.unlink(temp_file.name)
        
        return None
    
    def create_full_video(self, topic: str, voice: str = "nova") -> Dict:
        """
        Complete pipeline: Generate package, render video, create audio.
        
        Args:
            topic: The topic to explain
            voice: TTS voice to use
            
        Returns:
            Dict with all outputs and file paths
        """
        # Step 1: Generate complete package
        package = self.generate_complete_package(topic)
        
        # Step 2: Save the package
        output_dir = self.output_dir / topic.lower().replace(" ", "_")
        output_dir.mkdir(exist_ok=True)
        
        # Save all sections to files
        (output_dir / "voiceover_script.txt").write_text(package.voiceover_script)
        (output_dir / "storyboard.txt").write_text(package.animation_storyboard)
        (output_dir / "manim_code.py").write_text(package.manim_code)
        (output_dir / "voice_prompt.txt").write_text(package.voice_prompt)
        (output_dir / "complete_package.txt").write_text(package.to_string())
        
        print(f"\n📁 Saved all sections to: {output_dir}")
        
        # Step 3: Generate audio
        audio_path = str(output_dir / "narration.mp3")
        self.generate_audio(package.voiceover_script, audio_path, voice)
        
        # Step 4: Render Manim (optional - may fail if Manim not installed)
        video_path = self.render_manim(package.manim_code, topic)
        
        return {
            "topic": topic,
            "package": package,
            "output_dir": str(output_dir),
            "audio_path": audio_path,
            "video_path": video_path,
            "files": {
                "voiceover": str(output_dir / "voiceover_script.txt"),
                "storyboard": str(output_dir / "storyboard.txt"),
                "manim_code": str(output_dir / "manim_code.py"),
                "voice_prompt": str(output_dir / "voice_prompt.txt"),
                "complete": str(output_dir / "complete_package.txt")
            }
        }


def generate_3b1b_video(topic: str, voice: str = "nova") -> Dict:
    """
    Convenience function to generate a complete 3Blue1Brown-style video.
    
    Args:
        topic: The math/science topic to explain
        voice: TTS voice (nova, shimmer recommended for teacher-like)
        
    Returns:
        Dict with all generated content and file paths
    """
    generator = ThreeBlueOneBrownGenerator()
    return generator.create_full_video(topic, voice)


# Example usage
if __name__ == "__main__":
    # Example: Generate a video about the Pythagorean Theorem
    result = generate_3b1b_video(
        topic="The Pythagorean Theorem",
        voice="nova"  # Warm, teacher-like voice
    )
    
    print("\n" + "=" * 60)
    print("🎉 GENERATION COMPLETE!")
    print("=" * 60)
    print(f"\n📁 Output directory: {result['output_dir']}")
    print(f"🎙️ Audio file: {result['audio_path']}")
    if result['video_path']:
        print(f"🎬 Video file: {result['video_path']}")
    print("\n📄 Generated files:")
    for name, path in result['files'].items():
        print(f"   - {name}: {path}")
    
    print("\n📝 Complete Package Preview:")
    print(result['package'].to_string()[:2000] + "...")

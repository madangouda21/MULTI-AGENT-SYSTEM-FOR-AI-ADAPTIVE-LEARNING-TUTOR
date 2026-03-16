"""
Professional 3Blue1Brown-Style Video Generator
Uses Manim for animations + OpenAI TTS for human-like narration
"""
import os
import subprocess
import tempfile
import json
from pathlib import Path
from openai import OpenAI
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
import textwrap


class ProfessionalVideoGenerator:
    """
    Creates flawless educational videos like 3Blue1Brown.
    - Manim Community Edition for smooth mathematical animations
    - OpenAI TTS for natural, teacher-like narration
    """
    
    def __init__(self, output_dir="generated_videos", voice="alloy"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # OpenAI voices: alloy, echo, fable, onyx, nova, shimmer
        # 'nova' and 'shimmer' sound most teacher-like
        self.voice = voice
        
    def generate_tts_audio(self, text: str, output_path: str) -> str:
        """
        Generate natural human-like speech using OpenAI TTS.
        Much smoother than gTTS - sounds like a real teacher.
        """
        response = self.client.audio.speech.create(
            model="tts-1-hd",  # High definition for best quality
            voice=self.voice,  # Natural teacher-like voice
            input=text,
            speed=0.95  # Slightly slower for educational clarity
        )
        response.stream_to_file(output_path)
        return output_path
    
    def create_manim_scene_file(self, scene_config: dict, scene_index: int) -> str:
        """
        Generate a Manim Python scene file for the animation.
        """
        scene_type = scene_config.get('visual_type', 'equation')
        params = scene_config.get('visual_params', {})
        title = scene_config.get('title', 'Lesson')
        
        # Generate Manim code based on scene type
        manim_code = self._get_manim_code(scene_type, params, title)
        
        # Write to temp file
        temp_file = tempfile.mktemp(suffix='.py')
        with open(temp_file, 'w') as f:
            f.write(manim_code)
        
        return temp_file
    
    def _get_manim_code(self, scene_type: str, params: dict, title: str) -> str:
        """Generate Manim scene code for different visualization types."""
        
        base_imports = '''
from manim import *

class EducationalScene(Scene):
    def construct(self):
        # 3Blue1Brown color scheme
        self.camera.background_color = "#1e1e2e"
        
'''
        
        if scene_type == 'equation':
            equation = params.get('equation', r'f(x) = x^2')
            return base_imports + f'''
        # Title with animation
        title = Text("{title}", font_size=48, color=PURPLE_B)
        title.to_edge(UP)
        self.play(Write(title), run_time=1.5)
        self.wait(0.5)
        
        # Main equation with beautiful animation
        equation = MathTex(r"{equation}", font_size=72, color=BLUE_C)
        self.play(Write(equation), run_time=2)
        self.wait(0.5)
        
        # Add elegant box around equation
        box = SurroundingRectangle(equation, color=PURPLE_B, buff=0.3)
        self.play(Create(box), run_time=1)
        self.wait(1)
        
        # Subtle emphasis animation
        self.play(equation.animate.scale(1.1), run_time=0.5)
        self.play(equation.animate.scale(1/1.1), run_time=0.5)
        self.wait(1)
'''

        elif scene_type == 'graph':
            func_str = params.get('function', 'lambda x: x**2')
            label = params.get('label', 'f(x) = x^2')
            return base_imports + f'''
        # Title
        title = Text("{title}", font_size=48, color=PURPLE_B)
        title.to_edge(UP)
        self.play(Write(title), run_time=1)
        
        # Create axes with 3b1b style
        axes = Axes(
            x_range=[-5, 5, 1],
            y_range=[-2, 10, 2],
            x_length=8,
            y_length=5,
            axis_config={{"color": BLUE_C, "include_tip": True}},
            tips=True
        )
        axes_labels = axes.get_axis_labels(x_label="x", y_label="y")
        
        # Animate axes creation
        self.play(Create(axes), Write(axes_labels), run_time=2)
        
        # Draw function graph smoothly
        graph = axes.plot({func_str}, color=PURPLE_B, stroke_width=4)
        graph_label = MathTex(r"{label}", color=PURPLE_B).next_to(graph, UR)
        
        self.play(Create(graph), run_time=3)
        self.play(Write(graph_label), run_time=1)
        
        # Add moving dot tracing the curve
        dot = Dot(color=YELLOW).move_to(axes.c2p(-4, 16))
        self.play(Create(dot))
        self.play(MoveAlongPath(dot, graph), run_time=3)
        
        self.wait(1)
'''

        elif scene_type == 'tree':
            values = params.get('values', [4, 2, 6, 1, 3, 5, 7])
            return base_imports + f'''
        # Title
        title = Text("{title}", font_size=48, color=PURPLE_B)
        title.to_edge(UP)
        self.play(Write(title), run_time=1)
        
        values = {values}
        
        # Create tree nodes
        nodes = {{}}
        positions = {{
            0: UP * 1.5,
            1: UP * 1.5 + LEFT * 3 + DOWN * 2,
            2: UP * 1.5 + RIGHT * 3 + DOWN * 2,
            3: UP * 1.5 + LEFT * 4.5 + DOWN * 4,
            4: UP * 1.5 + LEFT * 1.5 + DOWN * 4,
            5: UP * 1.5 + RIGHT * 1.5 + DOWN * 4,
            6: UP * 1.5 + RIGHT * 4.5 + DOWN * 4,
        }}
        
        # Draw nodes one by one with animation
        for i, val in enumerate(values[:7]):
            if i in positions:
                circle = Circle(radius=0.5, color=PURPLE_B, fill_opacity=0.8)
                circle.move_to(positions[i])
                text = Text(str(val), font_size=32, color=WHITE).move_to(positions[i])
                nodes[i] = VGroup(circle, text)
                self.play(Create(circle), Write(text), run_time=0.5)
        
        # Draw edges
        edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
        for parent, child in edges:
            if parent in nodes and child in nodes:
                line = Line(
                    positions[parent] + DOWN * 0.5,
                    positions[child] + UP * 0.5,
                    color=BLUE_C
                )
                self.play(Create(line), run_time=0.3)
        
        self.wait(2)
'''

        elif scene_type == 'array':
            arr = params.get('array', [64, 34, 25, 12, 22, 11, 90])
            return base_imports + f'''
        # Title
        title = Text("{title}", font_size=48, color=PURPLE_B)
        title.to_edge(UP)
        self.play(Write(title), run_time=1)
        
        arr = {arr}
        
        # Create array visualization
        squares = VGroup()
        texts = VGroup()
        
        for i, val in enumerate(arr):
            sq = Square(side_length=1, color=PURPLE_B, fill_opacity=0.7)
            sq.move_to(RIGHT * (i - len(arr)/2 + 0.5) * 1.2)
            txt = Text(str(val), font_size=28, color=WHITE)
            txt.move_to(sq.get_center())
            squares.add(sq)
            texts.add(txt)
        
        # Animate array appearing
        for sq, txt in zip(squares, texts):
            self.play(Create(sq), Write(txt), run_time=0.3)
        
        # Add index labels
        indices = VGroup()
        for i in range(len(arr)):
            idx = Text(f"[{{i}}]", font_size=20, color=BLUE_C)
            idx.next_to(squares[i], DOWN)
            indices.add(idx)
        
        self.play(Write(indices), run_time=1)
        self.wait(2)
'''

        elif scene_type == 'algorithm':
            steps = params.get('steps', ['Initialize', 'Compare', 'Swap', 'Repeat'])
            return base_imports + f'''
        # Title
        title = Text("{title}", font_size=48, color=PURPLE_B)
        title.to_edge(UP)
        self.play(Write(title), run_time=1)
        
        steps = {steps}
        
        # Create step boxes
        step_group = VGroup()
        for i, step in enumerate(steps):
            box = RoundedRectangle(
                width=5, height=0.8, 
                corner_radius=0.2,
                color=PURPLE_B, 
                fill_opacity=0.7
            )
            box.move_to(DOWN * i * 1.2)
            txt = Text(step, font_size=28, color=WHITE)
            txt.move_to(box.get_center())
            step_group.add(VGroup(box, txt))
        
        step_group.center()
        
        # Animate steps appearing one by one
        arrows = VGroup()
        for i, step in enumerate(step_group):
            self.play(Create(step[0]), Write(step[1]), run_time=0.5)
            if i < len(step_group) - 1:
                arrow = Arrow(
                    step.get_bottom(),
                    step_group[i+1].get_top(),
                    color=BLUE_C,
                    buff=0.1
                )
                arrows.add(arrow)
                self.play(Create(arrow), run_time=0.3)
        
        self.wait(2)
'''

        elif scene_type == 'matrix':
            matrix_vals = params.get('matrix', [[1, 2], [3, 4]])
            return base_imports + f'''
        # Title
        title = Text("{title}", font_size=48, color=PURPLE_B)
        title.to_edge(UP)
        self.play(Write(title), run_time=1)
        
        # Create matrix with Manim
        matrix = Matrix(
            {matrix_vals},
            left_bracket="[",
            right_bracket="]",
            element_to_mobject_config={{"color": WHITE}}
        ).scale(1.5)
        
        # Animate matrix appearing
        self.play(Write(matrix), run_time=2)
        
        # Highlight elements with color wave
        for i, entry in enumerate(matrix.get_entries()):
            self.play(
                entry.animate.set_color(YELLOW),
                run_time=0.3
            )
            self.play(
                entry.animate.set_color(WHITE),
                run_time=0.2
            )
        
        # Add brackets emphasis
        brackets = VGroup(matrix.get_brackets())
        self.play(brackets.animate.set_color(PURPLE_B), run_time=0.5)
        
        self.wait(2)
'''

        else:  # Default: text explanation
            return base_imports + f'''
        # Title with elegant animation
        title = Text("{title}", font_size=56, color=PURPLE_B)
        title.to_edge(UP)
        self.play(Write(title), run_time=2)
        
        # Decorative line under title
        line = Line(LEFT * 4, RIGHT * 4, color=BLUE_C)
        line.next_to(title, DOWN, buff=0.3)
        self.play(Create(line), run_time=1)
        
        # Key point text
        point = Text("Key Concept", font_size=40, color=WHITE)
        point.move_to(ORIGIN)
        self.play(FadeIn(point, shift=UP), run_time=1.5)
        
        self.wait(2)
'''

    def render_manim_scene(self, scene_file: str, output_name: str) -> str:
        """Render Manim scene to video file."""
        output_path = self.output_dir / f"{output_name}_scene.mp4"
        
        # Run Manim CLI to render - use simpler command that works more reliably
        # Find scene class name from file
        scene_class = "EducationalScene"
        try:
            with open(scene_file, 'r') as f:
                content = f.read()
                for line in content.split('\n'):
                    if 'class' in line and 'Scene' in line:
                        parts = line.strip().split('class')
                        if len(parts) > 1:
                            scene_class = parts[1].split('(')[0].strip()
                            break
        except:
            pass
        
        # Run Manim render
        cmd = [
            "manim", "render",
            "-qh",  # High quality (1080p)
            "--format", "mp4",
            scene_file,
            scene_class
        ]
        
        try:
            print(f"   🎨 Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=str(self.output_dir))
            
            if result.returncode != 0:
                print(f"   ⚠️ Manim stderr: {result.stderr[:500]}")
                # Try with lower quality as fallback
                cmd[2] = "-ql"  # Low quality as fallback
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=180, cwd=str(self.output_dir))
                if result.returncode != 0:
                    raise RuntimeError(f"Manim rendering failed: {result.stderr[:500]}")
            
            # Find the actual output file (Manim puts it in media/videos folder)
            # Check both current dir and project root
            search_paths = [
                Path("media/videos"),
                self.output_dir / "media/videos",
                Path.cwd() / "media/videos",
                self.output_dir
            ]
            
            video_file = None
            for search_dir in search_paths:
                if search_dir.exists():
                    for vid_file in search_dir.rglob("*.mp4"):
                        if scene_class in vid_file.name or "EducationalScene" in vid_file.name:
                            video_file = vid_file
                            # Copy to output_dir for easier access
                            target = self.output_dir / f"{output_name}_scene.mp4"
                            if str(vid_file) != str(target):
                                import shutil
                                shutil.copy2(vid_file, target)
                                video_file = target
                            print(f"   ✅ Found video: {video_file}")
                            break
                    if video_file:
                        break
            
            if not video_file or not video_file.exists():
                raise RuntimeError(f"Could not find rendered video file for {scene_class}")
            
            return str(video_file)
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Manim rendering timed out (>5 minutes)")
        except Exception as e:
            raise RuntimeError(f"Manim rendering error: {str(e)}")
        finally:
            # Don't cleanup scene file yet - might need for debugging
            pass

    def generate_video(self, scenes: list, topic: str, video_id: str) -> str:
        """
        Generate a complete educational video with Manim animations
        and OpenAI TTS narration.
        
        Args:
            scenes: List of scene configurations
            topic: Video topic/title
            video_id: Unique identifier for output file
        
        Returns:
            Path to final video file
        """
        print(f"\n🎬 Generating professional video: {topic}")
        print("=" * 50)
        
        final_clips = []
        temp_files = []
        
        try:
            for idx, scene in enumerate(scenes):
                print(f"\n📍 Processing Scene {idx + 1}/{len(scenes)}")
                
                title = scene.get('title', f'Scene {idx + 1}')
                narration = scene.get('narration_text', '')
                
                # Step 1: Generate natural TTS audio
                print(f"   🎙️ Generating natural narration...")
                audio_path = tempfile.mktemp(suffix='.mp3')
                temp_files.append(audio_path)
                self.generate_tts_audio(narration, audio_path)
                audio_clip = AudioFileClip(audio_path)
                audio_duration = audio_clip.duration
                
                # Step 2: Generate Manim animation
                print(f"   🎨 Creating Manim animation...")
                scene_file = self.create_manim_scene_file(scene, idx)
                temp_files.append(scene_file)
                
                try:
                    video_path = self.render_manim_scene(scene_file, f"{video_id}_scene_{idx}")
                    video_clip = VideoFileClip(video_path)
                    
                    # Adjust video duration to match audio
                    if video_clip.duration < audio_duration:
                        # Loop or extend video to match audio
                        video_clip = video_clip.loop(duration=audio_duration)
                    elif video_clip.duration > audio_duration:
                        # Trim video to match audio
                        video_clip = video_clip.subclip(0, audio_duration)
                    
                    # Combine video with audio
                    final_scene = video_clip.set_audio(audio_clip)
                    final_clips.append(final_scene)
                    
                except Exception as e:
                    print(f"   ⚠️ Manim failed ({str(e)}), using fallback visualization...")
                    # Fallback to matplotlib-based visual (still uses OpenAI TTS)
                    try:
                        fallback_clip = self._create_fallback_scene(scene, audio_clip)
                        final_clips.append(fallback_clip)
                    except Exception as fallback_error:
                        print(f"   ❌ Fallback also failed: {fallback_error}")
                        # Last resort: simple colored background with text
                        from moviepy.editor import ColorClip, TextClip, CompositeVideoClip
                        duration = audio_clip.duration
                        bg = ColorClip(size=(1920, 1080), color=(30, 30, 46), duration=duration)
                        title_text = scene.get('title', 'Lesson')
                        title_clip = TextClip(title_text, fontsize=60, color='#bd93f9', 
                                             font='Arial-Bold', size=(1600, None), method='caption'
                                            ).set_position('center').set_duration(duration)
                        final_clips.append(CompositeVideoClip([bg, title_clip]).set_audio(audio_clip))
            
            # Concatenate all scenes
            if not final_clips:
                raise RuntimeError("No video clips were generated")
            
            print(f"\n🔗 Combining {len(final_clips)} scenes...")
            
            # Ensure all clips have the same size
            target_size = final_clips[0].size
            for i, clip in enumerate(final_clips):
                if clip.size != target_size:
                    print(f"   Resizing clip {i+1} to match target size...")
                    final_clips[i] = clip.resize(target_size)
            
            final_video = concatenate_videoclips(final_clips, method="compose")
            
            # Output
            output_path = self.output_dir / f"{video_id}.mp4"
            print(f"📹 Rendering final video to {output_path}...")
            print(f"   Video duration: {final_video.duration:.2f}s")
            print(f"   Video size: {final_video.size}")
            
            try:
                final_video.write_videofile(
                    str(output_path),
                    fps=60,
                    codec='libx264',
                    audio_codec='aac',
                    bitrate="8000k",  # High quality
                    preset='medium',
                    logger=None,
                    threads=4  # Use multiple threads for faster encoding
                )
            except Exception as write_error:
                # Try with lower quality if high quality fails
                print(f"   ⚠️ High quality encoding failed, trying standard quality...")
                final_video.write_videofile(
                    str(output_path),
                    fps=30,
                    codec='libx264',
                    audio_codec='aac',
                    logger=None
                )
            
            # Cleanup clips to free memory
            final_video.close()
            for clip in final_clips:
                clip.close()
            
            # Verify file was created
            if not output_path.exists():
                raise RuntimeError(f"Video file was not created at {output_path}")
            
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"\n✅ Video generated successfully: {output_path}")
            print(f"   File size: {file_size_mb:.2f} MB")
            return str(output_path)
            
        finally:
            # Cleanup temp files
            for f in temp_files:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except:
                        pass

    def _create_fallback_scene(self, scene: dict, audio_clip):
        """Create a fallback scene using matplotlib if Manim fails.
        Still uses OpenAI TTS for natural voice - just different visuals."""
        from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, ImageClip
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from io import BytesIO
        from PIL import Image
        import numpy as np
        
        duration = audio_clip.duration
        title = scene.get('title', 'Lesson')
        visual_type = scene.get('visual_type', 'text')
        params = scene.get('visual_params', {})
        narration = scene.get('narration_text', '')
        
        # Create matplotlib visualization
        fig, ax = plt.subplots(figsize=(16, 9), facecolor='#1e1e2e')
        ax.set_facecolor('#1e1e2e')
        
        if visual_type == 'equation':
            ax.axis('off')
            equation = params.get('equation', r'$f(x) = x^2$')
            ax.text(0.5, 0.5, f'${equation}$', fontsize=60, color='#bd93f9',
                   ha='center', va='center', transform=ax.transAxes)
            ax.text(0.5, 0.85, title, fontsize=36, color='#cba6f7',
                   ha='center', va='center', transform=ax.transAxes)
        
        elif visual_type == 'graph':
            x = np.linspace(-5, 5, 200)
            func_str = params.get('function', 'lambda x: x**2')
            try:
                y = eval(func_str)(x) if 'lambda' in func_str else eval(func_str, {"x": x, "np": np})
                ax.plot(x, y, color='#bd93f9', linewidth=4)
                ax.grid(True, alpha=0.3, color='#f8f8f2')
                ax.axhline(0, color='#f8f8f2', linewidth=1, alpha=0.5)
                ax.axvline(0, color='#f8f8f2', linewidth=1, alpha=0.5)
                ax.tick_params(colors='#f8f8f2', labelsize=14)
                ax.set_title(title, fontsize=28, color='#cba6f7', pad=20)
            except:
                ax.axis('off')
                ax.text(0.5, 0.5, title, fontsize=48, color='#bd93f9', ha='center', va='center')
        
        elif visual_type == 'tree':
            ax.axis('off')
            values = params.get('values', [4, 2, 6, 1, 3, 5, 7])
            positions = [(0.5, 0.85), (0.3, 0.55), (0.7, 0.55), 
                        (0.15, 0.25), (0.35, 0.25), (0.55, 0.25), (0.85, 0.25)]
            # Draw edges
            edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
            for parent, child in edges:
                if parent < len(values) and child < len(values):
                    ax.plot([positions[parent][0], positions[child][0]],
                           [positions[parent][1], positions[child][1]], 'w-', linewidth=2, alpha=0.6)
            # Draw nodes
            for i, (val, pos) in enumerate(zip(values[:7], positions[:len(values)])):
                circle = plt.Circle(pos, 0.06, color='#bd93f9', transform=ax.transAxes)
                ax.add_patch(circle)
                ax.text(pos[0], pos[1], str(val), fontsize=18, color='white',
                       ha='center', va='center', transform=ax.transAxes, weight='bold')
            ax.text(0.5, 0.98, title, fontsize=28, color='#cba6f7',
                   ha='center', va='top', transform=ax.transAxes)
        
        elif visual_type == 'array':
            ax.axis('off')
            arr = params.get('array', [64, 34, 25, 12, 22])
            n = len(arr)
            for i, val in enumerate(arr):
                x_pos = 0.1 + (i / n) * 0.8
                rect = plt.Rectangle((x_pos, 0.35), 0.8/n - 0.02, 0.3, 
                                     facecolor='#bd93f9', edgecolor='white', linewidth=2,
                                     transform=ax.transAxes)
                ax.add_patch(rect)
                ax.text(x_pos + 0.4/n - 0.01, 0.5, str(val), fontsize=22, color='white',
                       ha='center', va='center', transform=ax.transAxes, weight='bold')
                ax.text(x_pos + 0.4/n - 0.01, 0.28, f'[{i}]', fontsize=14, color='#89dceb',
                       ha='center', va='center', transform=ax.transAxes)
            ax.text(0.5, 0.85, title, fontsize=32, color='#cba6f7',
                   ha='center', va='center', transform=ax.transAxes)
        
        else:  # Default text
            ax.axis('off')
            ax.text(0.5, 0.6, title, fontsize=48, color='#bd93f9',
                   ha='center', va='center', transform=ax.transAxes, weight='bold')
            # Add decorative line
            ax.axhline(y=0.45, xmin=0.2, xmax=0.8, color='#89dceb', linewidth=3)
        
        # Add narration as subtitle at bottom
        wrapped_text = '\n'.join([narration[i:i+80] for i in range(0, len(narration), 80)][:2])
        ax.text(0.5, 0.08, wrapped_text, fontsize=16, color='white',
               ha='center', va='center', transform=ax.transAxes, alpha=0.9,
               bbox=dict(boxstyle='round', facecolor='#1e1e2e', edgecolor='#bd93f9', alpha=0.8))
        
        # Save to image
        buf = BytesIO()
        plt.savefig(buf, format='png', facecolor='#1e1e2e', dpi=120, bbox_inches='tight')
        buf.seek(0)
        img = Image.open(buf)
        plt.close(fig)
        
        # Resize to 1920x1080
        img = img.resize((1920, 1080), Image.Resampling.LANCZOS)
        img_array = np.array(img)
        
        # Create video clip from image
        visual_clip = ImageClip(img_array).set_duration(duration)
        
        return visual_clip.set_audio(audio_clip)


def generate_educational_video(topic: str, scenes: list, video_id: str, voice: str = "nova") -> str:
    """
    Convenience function to generate a professional educational video.
    
    Args:
        topic: The main topic/title
        scenes: List of scene configs with narration_text, visual_type, visual_params
        video_id: Unique video identifier
        voice: OpenAI TTS voice (alloy, echo, fable, onyx, nova, shimmer)
               'nova' and 'shimmer' sound most teacher-like
    
    Returns:
        Path to generated video
    """
    generator = ProfessionalVideoGenerator(voice=voice)
    return generator.generate_video(scenes, topic, video_id)


# Example usage
if __name__ == "__main__":
    # Test video generation
    test_scenes = [
        {
            "title": "Introduction to Binary Search Trees",
            "narration_text": "A Binary Search Tree, or BST, is a fundamental data structure in computer science. It maintains a special ordering property where, for every node, all values in the left subtree are smaller, and all values in the right subtree are larger.",
            "visual_type": "tree",
            "visual_params": {"values": [8, 4, 12, 2, 6, 10, 14]}
        },
        {
            "title": "The Quadratic Function",
            "narration_text": "The quadratic function f of x equals x squared creates a beautiful parabola. Notice how the curve is symmetric around the y-axis, and it has a minimum value at x equals zero.",
            "visual_type": "graph",
            "visual_params": {"function": "lambda x: x**2", "label": "f(x) = x^2"}
        },
        {
            "title": "Array Visualization",
            "narration_text": "Here we have an array of integers. In programming, arrays store elements in contiguous memory locations, allowing for efficient access using indices.",
            "visual_type": "array",
            "visual_params": {"array": [64, 34, 25, 12, 22, 11, 90]}
        }
    ]
    
    video_path = generate_educational_video(
        topic="Data Structures & Algorithms",
        scenes=test_scenes,
        video_id="test_video",
        voice="nova"  # Teacher-like voice
    )
    print(f"Generated: {video_path}")

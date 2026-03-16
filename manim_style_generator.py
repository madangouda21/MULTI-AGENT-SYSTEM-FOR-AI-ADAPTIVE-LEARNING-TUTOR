"""
3Blue1Brown-Style Video Generator (Simplified)
Creates mathematical animations using MoviePy with LaTeX rendering
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
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO

# Configure ImageMagick
try:
    result = subprocess.run(['which', 'convert'], capture_output=True, text=True)
    if result.returncode == 0:
        convert_path = result.stdout.strip()
        change_settings({"IMAGEMAGICK_BINARY": convert_path})
except Exception as e:
    print(f"Warning: Could not configure ImageMagick: {e}")


class ManipStyleVideoGenerator:
    """
    Generates educational videos with mathematical animations
    inspired by 3Blue1Brown's style.
    """
    
    def __init__(self, output_dir="generated_videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.colors = {
            'background': (40, 42, 54),      # Dark blue-gray
            'primary': (189, 147, 249),      # Purple (3b1b signature)
            'secondary': (80, 250, 123),     # Green
            'accent': (255, 121, 198),       # Pink
            'text': (248, 248, 242)          # White-ish
        }
    
    def create_mathematical_visual(self, scene_type, params, size=(1280, 720)):
        """
        Create mathematical visualizations for different scene types.
        
        Scene Types:
        - 'equation': Render LaTeX-style equation
        - 'graph': Plot mathematical function
        - 'tree': Binary tree visualization
        - 'array': Array/list visualization
        - 'histogram': Bar chart/histogram
        - 'network': Graph/network diagram
        - 'matrix': Matrix visualization
        - 'flowchart': Simple flowchart
        - 'animation': Animated transformation
        """
        fig, ax = plt.subplots(figsize=(16, 9), facecolor='#282a36')
        ax.set_facecolor('#282a36')
        ax.axis('off')
        
        if scene_type == 'equation':
            # Render mathematical equation
            equation = params.get('equation', r'$f(x) = x^2$')
            ax.text(0.5, 0.5, equation, 
                   fontsize=80, 
                   color='#bd93f9',
                   ha='center', 
                   va='center',
                   transform=ax.transAxes,
                   usetex=False)
        
        elif scene_type == 'graph':
            # Plot function
            x = np.linspace(-10, 10, 400)
            func_str = params.get('function', 'x**2')
            try:
                y = eval(func_str, {"x": x, "np": np, "sin": np.sin, "cos": np.cos, "exp": np.exp, "log": np.log})
                ax.plot(x, y, color='#bd93f9', linewidth=4, label=f'y = {func_str}')
                ax.grid(True, alpha=0.2, color='#f8f8f2')
                ax.axhline(0, color='#f8f8f2', linewidth=1, alpha=0.5)
                ax.axvline(0, color='#f8f8f2', linewidth=1, alpha=0.5)
                ax.legend(fontsize=20, facecolor='#44475a', edgecolor='#bd93f9')
                ax.tick_params(colors='#f8f8f2', labelsize=16)
            except:
                ax.text(0.5, 0.5, 'Invalid function', 
                       fontsize=40, color='#ff79c6', ha='center', va='center')
        
        elif scene_type == 'tree':
            # Binary tree visualization
            self._draw_binary_tree(ax, params)
        
        elif scene_type == 'array':
            # Array visualization
            arr = params.get('array', [1, 2, 3, 4, 5])
            colors_arr = [self.colors['primary']] * len(arr)
            highlight = params.get('highlight', -1)
            if 0 <= highlight < len(arr):
                colors_arr[highlight] = self.colors['accent']
            
            bars = ax.barh(range(len(arr)), arr, 
                          color=['#bd93f9' if i != highlight else '#ff79c6' for i in range(len(arr))],
                          edgecolor='#f8f8f2', linewidth=2)
            
            for i, (bar, val) in enumerate(zip(bars, arr)):
                ax.text(bar.get_width()/2, bar.get_y() + bar.get_height()/2, 
                       str(val), ha='center', va='center', 
                       color='#282a36', fontsize=24, weight='bold')
            
            ax.set_yticks(range(len(arr)))
            ax.set_yticklabels([f'[{i}]' for i in range(len(arr))], fontsize=18, color='#f8f8f2')
            ax.tick_params(colors='#f8f8f2')
        
        elif scene_type == 'histogram':
            # Histogram/bar chart
            data = params.get('data', [3, 7, 2, 9, 5, 8, 1])
            labels = params.get('labels', [f'Item {i+1}' for i in range(len(data))])
            bars = ax.bar(range(len(data)), data, color='#bd93f9', edgecolor='#f8f8f2', linewidth=2)
            
            for bar, val in zip(bars, data):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{val}', ha='center', va='bottom', color='#f8f8f2', fontsize=20, weight='bold')
            
            ax.set_xticks(range(len(data)))
            ax.set_xticklabels(labels, fontsize=16, color='#f8f8f2', rotation=45, ha='right')
            ax.tick_params(colors='#f8f8f2', labelsize=16)
            ax.spines['bottom'].set_color('#f8f8f2')
            ax.spines['left'].set_color('#f8f8f2')
        
        elif scene_type == 'network':
            # Network/graph diagram
            nodes = params.get('nodes', ['A', 'B', 'C', 'D'])
            raw_edges = params.get('edges', [(0, 1), (0, 2), (1, 3), (2, 3)])

            # Normalize edges to (i, j) integer pairs and ignore malformed entries
            edges = []
            for e in raw_edges:
                try:
                    # Expect list/tuple with at least 2 elements
                    if isinstance(e, (list, tuple)) and len(e) >= 2:
                        i = int(e[0])
                        j = int(e[1])
                        edges.append((i, j))
                except Exception:
                    # Skip any bad edge definitions
                    continue
            
            # Simple circular layout
            n = len(nodes)
            angles = np.linspace(0, 2*np.pi, n, endpoint=False)
            x_pos = 3 * np.cos(angles)
            y_pos = 3 * np.sin(angles)
            
            # Draw edges
            for i, j in edges:
                if 0 <= i < n and 0 <= j < n:
                    ax.plot([x_pos[i], x_pos[j]], [y_pos[i], y_pos[j]], 
                           color='#50fa7b', linewidth=3, alpha=0.6)
            
            # Draw nodes
            for i, (x, y, label) in enumerate(zip(x_pos, y_pos, nodes)):
                circle = plt.Circle((x, y), 0.5, color='#bd93f9', ec='#f8f8f2', linewidth=3)
                ax.add_patch(circle)
                ax.text(x, y, str(label), ha='center', va='center', 
                       color='#282a36', fontsize=24, weight='bold')
            
            ax.set_xlim(-4, 4)
            ax.set_ylim(-4, 4)
            ax.set_aspect('equal')
        
        elif scene_type == 'matrix':
            # Matrix visualization
            matrix = params.get('matrix', [[1, 2, 3], [4, 5, 6], [7, 8, 9]])
            matrix = np.array(matrix)
            
            # Create color-coded matrix
            im = ax.imshow(matrix, cmap='viridis', aspect='auto')
            
            # Add text annotations
            for i in range(matrix.shape[0]):
                for j in range(matrix.shape[1]):
                    text = ax.text(j, i, f'{matrix[i, j]}',
                                 ha="center", va="center", color="white",
                                 fontsize=28, weight='bold')
            
            ax.set_xticks(range(matrix.shape[1]))
            ax.set_yticks(range(matrix.shape[0]))
            ax.tick_params(colors='#f8f8f2', labelsize=16)
            ax.set_xlabel('Columns', color='#f8f8f2', fontsize=20)
            ax.set_ylabel('Rows', color='#f8f8f2', fontsize=20)
        
        elif scene_type == 'flowchart':
            # Simple flowchart
            steps = params.get('steps', ['Start', 'Process', 'Decision', 'End'])
            
            y_positions = np.linspace(5, 1, len(steps))
            
            for i, (step, y) in enumerate(zip(steps, y_positions)):
                # Draw box
                if 'decision' in step.lower() or '?' in step:
                    # Diamond for decision
                    diamond = plt.Polygon([(0, y+0.3), (0.8, y), (0, y-0.3), (-0.8, y)],
                                        color='#ff79c6', ec='#f8f8f2', linewidth=2)
                    ax.add_patch(diamond)
                else:
                    # Rectangle for process
                    rect = plt.Rectangle((-0.8, y-0.25), 1.6, 0.5,
                                       color='#bd93f9', ec='#f8f8f2', linewidth=2)
                    ax.add_patch(rect)
                
                ax.text(0, y, step, ha='center', va='center',
                       color='#282a36', fontsize=18, weight='bold')
                
                # Draw arrow to next step
                if i < len(steps) - 1:
                    ax.arrow(0, y-0.4, 0, -0.4, head_width=0.2, head_length=0.1,
                           fc='#50fa7b', ec='#50fa7b', linewidth=2)
            
            ax.set_xlim(-2, 2)
            ax.set_ylim(0, 6)
        
        # Save to image
        buf = BytesIO()
        plt.savefig(buf, format='png', facecolor='#282a36', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img = Image.open(buf)
        plt.close(fig)
        
        # Resize to target size
        img = img.resize(size, Image.Resampling.LANCZOS)
        return np.array(img)
    
    def _draw_binary_tree(self, ax, params):
        """Draw a binary tree structure"""
        values = params.get('values', [4, 2, 6, 1, 3, 5, 7])
        
        # Simple binary tree layout
        def draw_node(x, y, value, level=0):
            circle = plt.Circle((x, y), 0.5, color='#bd93f9', ec='#f8f8f2', linewidth=2)
            ax.add_patch(circle)
            ax.text(x, y, str(value), ha='center', va='center', 
                   color='#282a36', fontsize=20, weight='bold')
        
        # Root
        if len(values) > 0:
            draw_node(0, 5, values[0])
        if len(values) > 1:
            ax.plot([-2, 0], [3, 4.5], color='#f8f8f2', linewidth=2)
            draw_node(-2, 3, values[1])
        if len(values) > 2:
            ax.plot([2, 0], [3, 4.5], color='#f8f8f2', linewidth=2)
            draw_node(2, 3, values[2])
        if len(values) > 3:
            ax.plot([-3, -2], [1, 2.5], color='#f8f8f2', linewidth=2)
            draw_node(-3, 1, values[3])
        if len(values) > 4:
            ax.plot([-1, -2], [1, 2.5], color='#f8f8f2', linewidth=2)
            draw_node(-1, 1, values[4])
        if len(values) > 5:
            ax.plot([1, 2], [1, 2.5], color='#f8f8f2', linewidth=2)
            draw_node(1, 1, values[5])
        if len(values) > 6:
            ax.plot([3, 2], [1, 2.5], color='#f8f8f2', linewidth=2)
            draw_node(3, 1, values[6])
        
        ax.set_xlim(-4, 4)
        ax.set_ylim(0, 6)
    
    def generate_video(self, scenes, topic, video_id):
        """
        Generate video with mathematical animations.
        
        scenes format:
        [
            {
                "scene_number": 1,
                "title": "Binary Search Tree",
                "narration_text": "A BST maintains order property.",
                "visual_type": "tree",
                "visual_params": {"values": [4, 2, 6, 1, 3, 5, 7]}
            }
        ]
        """
        try:
            clips = []
            temp_audio_files = []
            
            for idx, scene in enumerate(scenes):
                title = scene.get('title', f'Scene {idx+1}')
                narration = scene.get('narration_text', '')
                visual_type = scene.get('visual_type', 'equation')
                visual_params = scene.get('visual_params', {})
                
                # Generate TTS audio
                audio_path = tempfile.mktemp(suffix='.mp3')
                temp_audio_files.append(audio_path)
                tts = gTTS(text=narration, lang='en', slow=False)
                tts.save(audio_path)
                
                # Load audio
                audio = AudioFileClip(audio_path)
                duration = max(audio.duration, 3.0)  # Minimum 3 seconds
                
                # Create background
                bg = ColorClip(
                    size=(1280, 720),
                    color=self.colors['background'],
                    duration=duration
                )
                
                # Create mathematical visual
                visual_img = self.create_mathematical_visual(visual_type, visual_params)
                visual_clip = ImageClip(visual_img).set_duration(duration).set_position('center')
                
                # Create title overlay (top)
                title_clip = TextClip(
                    title,
                    fontsize=48,
                    color='#bd93f9',
                    font='Arial-Bold',
                    method='caption',
                    size=(1100, None)
                ).set_position(('center', 30)).set_duration(duration)
                
                # Create narration subtitle (bottom)
                narration_clip = TextClip(
                    narration,
                    fontsize=24,
                    color='#f8f8f2',
                    font='Arial',
                    method='caption',
                    size=(1000, None),
                    align='center',
                    bg_color='rgba(40, 42, 54, 0.8)'
                ).set_position(('center', 650)).set_duration(duration)
                
                # Composite
                scene_clip = CompositeVideoClip([
                    bg, visual_clip, title_clip, narration_clip
                ]).set_audio(audio)
                
                clips.append(scene_clip)
            
            # Concatenate scenes
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Output path
            output_path = self.output_dir / f"{video_id}.mp4"
            
            # Render video
            final_video.write_videofile(
                str(output_path),
                fps=24,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=tempfile.mktemp(suffix='.m4a'),
                remove_temp=True,
                logger=None
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

"""
AI Adaptive Learning Tutor - Simplified FastAPI Backend
Works without heavy ML dependencies
"""
import os
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
import PyPDF2
import io
from video_generator import VideoGenerator
import asyncio
from concurrent.futures import ThreadPoolExecutor
from agents import MasterOrchestrator
from manim_style_generator import ManipStyleVideoGenerator

# Try to import professional generator (Manim + OpenAI TTS)
try:
    from professional_video_generator import ProfessionalVideoGenerator
    pro_video_gen = ProfessionalVideoGenerator(voice="nova")  # Teacher-like voice
    HAS_PRO_VIDEO = True
except (ImportError, Exception) as e:
    print(f"⚠️ Professional video generator not available: {e}")
    HAS_PRO_VIDEO = False
    pro_video_gen = None

# Initialize FastAPI app
app = FastAPI(
    title="AI Adaptive Learning Tutor",
    description="An adaptive AI tutoring system",
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

# Serve static files (favicon, etc.)
frontend_path = Path(__file__).parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize video generators
video_gen = VideoGenerator(output_dir="generated_videos")
manim_gen = ManipStyleVideoGenerator(output_dir="generated_videos")
executor = ThreadPoolExecutor(max_workers=2)

# Initialize Multi-Agent System
mas_orchestrator = MasterOrchestrator()

# Simple in-memory storage
knowledge_base = []
chat_histories = {}

# Request/Response Models
class AskRequest(BaseModel):
    question: str
    student_id: Optional[str] = None
    subject: Optional[str] = "General"
    session_id: Optional[str] = "default"

class QuizRequest(BaseModel):
    topic: str
    difficulty: str = "beginner"
    num_questions: int = 3

class ContentIngestionRequest(BaseModel):
    content: str
    subject: str
    topic: str
    difficulty: str = "beginner"

class VideoRequest(BaseModel):
    topic: str
    subject: str = "Computer Science"
    difficulty_level: str = "beginner"
    duration_minutes: int = 3
    professional_mode: bool = True  # Use Manim + OpenAI TTS
    voice: str = "nova"  # OpenAI TTS voice: alloy, echo, fable, onyx, nova, shimmer


# Health check
@app.get("/")
async def root():
    return {"status": "healthy", "service": "AI Adaptive Learning Tutor"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Tutoring endpoint
@app.post("/tutor/ask")
async def ask_tutor(request: AskRequest):
    """Ask the AI tutor a question."""
    try:
        # Get chat history
        session_id = request.session_id or "default"
        history = chat_histories.get(session_id, [])
        
        # Build context from knowledge base
        context = ""
        if knowledge_base:
            relevant = [k for k in knowledge_base if request.subject.lower() in k.get('subject', '').lower() or 'uploaded document' in k.get('subject', '').lower()]
            if relevant:
                context = "\n\nRelevant information:\n" + "\n".join([k['content'][:500] for k in relevant[:3]])
        
        # Special handling for materials session - restrict to uploaded content only
        if session_id == "materials_session":
            if not knowledge_base:
                return {
                    "answer": "⚠️ **No materials uploaded yet!**\n\nPlease upload study materials first in the 'Upload Document' or 'Paste Text' tabs.\n\n💡 **Tip:** For general questions, use the **Learn** page instead.",
                    "session_id": session_id
                }
            
            # Check relevance with minimal API call
            question_lower = request.question.lower()
            content_preview = context[:200].lower() if context else ""
            
            # Simple keyword overlap check first (no API call)
            question_words = set(question_lower.split())
            content_words = set(content_preview.split())
            common_words = question_words & content_words - {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
            
            if len(common_words) < 2 and len(question) > 20:
                # Only if clearly unrelated, make API call to verify
                check_prompt = f"Question: {request.question}\nContent: {content[:150]}\nIs question about content? Answer YES or NO only."
                check = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": check_prompt}],
                    temperature=0,
                    max_tokens=5
                )
                
                if "no" in check.choices[0].message.content.lower():
                    return {
                        "answer": f"🔍 **Question not related to uploaded materials**\n\nYour question: *\"{request.question}\"*\n\n❌ This doesn't match your uploaded study materials.\n\n**Options:**\n- 📚 Ask about your uploaded materials\n- 🎓 Use **Learn** page for general questions\n- 📖 Upload relevant materials first",
                        "session_id": session_id
                    }
        
        # Build messages
        messages = [
            {
                "role": "system",
                "content": f"""You are an expert AI tutor helping students learn {request.subject}.
                
Teaching Guidelines:
1. **Format responses clearly** with:
   - Main concepts in **bold**
   - Key points as numbered or bulleted lists
   - Clear section headings
   - Code examples in ```code blocks``` when relevant

2. **Keep it concise** - be comprehensive but avoid unnecessary verbosity

3. **End each response** with interactive options:
   📚 Want me to summarize this?
   🔍 Need more details on any part?
   💡 Want a real-world example?
   ✅ Ready for practice questions?

4. **Use analogies** and real-world examples to explain complex concepts

5. Break down complex topics into digestible parts
6. Provide positive reinforcement
{context}"""
            }
        ]
        
        # Add history
        for msg in history[-10:]:
            messages.append(msg)
        
        # Add current question
        messages.append({"role": "user", "content": request.question})
        
        # Call OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        
        # Update history
        history.append({"role": "user", "content": request.question})
        history.append({"role": "assistant", "content": answer})
        chat_histories[session_id] = history[-20:]  # Keep last 20 messages
        
        return {"answer": answer, "session_id": session_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Quiz endpoint
@app.post("/quiz/generate")
async def generate_quiz(request: QuizRequest):
    """Generate quiz questions."""
    try:
        prompt = f"""Generate {request.num_questions} multiple choice quiz questions about {request.topic} at {request.difficulty} level.

Format as JSON array:
[
    {{
        "question": "Question text?",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer": 0,
        "explanation": "Why this is correct"
    }}
]

Only output the JSON array, nothing else."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        import json
        content = response.choices[0].message.content
        # Clean up the response
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        questions = json.loads(content.strip())
        return {"topic": request.topic, "questions": questions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Content ingestion
@app.post("/content/ingest")
async def ingest_content(request: ContentIngestionRequest):
    """Ingest educational content."""
    try:
        knowledge_base.append({
            "content": request.content,
            "subject": request.subject,
            "topic": request.topic,
            "difficulty": request.difficulty
        })
        return {"status": "ingested", "chunks": 1}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# File upload endpoint
@app.post("/content/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document (PDF or text)."""
    try:
        # Read file content
        content = await file.read()
        
        # Extract text based on file type
        text = ""
        if file.filename.endswith('.pdf'):
            # Process PDF
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        else:
            # Process text file
            text = content.decode('utf-8')
        
        # Add to knowledge base (in-memory storage)
        knowledge_base.append({
            "content": text,
            "subject": "Uploaded Document",
            "topic": file.filename,
            "difficulty": "general"
        })
        
        # Calculate chunks (split by paragraphs)
        chunks = len([p for p in text.split('\n\n') if p.strip()])
        
        return {
            "status": "uploaded",
            "filename": file.filename,
            "chunks": max(1, chunks),
            "total_documents": len(knowledge_base),
            "message": f"Document stored in memory. You can now ask questions about '{file.filename}' in the Learn page!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get knowledge base status
@app.get("/content/status")
async def get_knowledge_status():
    """Get current knowledge base status."""
    documents = []
    for idx, item in enumerate(knowledge_base):
        documents.append({
            "id": idx,
            "topic": item.get("topic", "Unknown"),
            "subject": item.get("subject", "Unknown"),
            "content_length": len(item.get("content", "")),
            "preview": item.get("content", "")[:200] + "..."
        })
    
    return {
        "total_documents": len(knowledge_base),
        "documents": documents
    }


# Video generation with actual video rendering
@app.post("/video/generate")
async def generate_video(request: VideoRequest):
    """Generate video script and render actual video.
    
    Professional mode: Uses Manim animations + OpenAI TTS (natural voice)
    Standard mode: Uses matplotlib + gTTS
    """
    try:
        # Step 1: Generate enhanced script with visual types
        prompt = f"""Create an educational video script about {request.topic} for {request.difficulty_level} level.

IMPORTANT: Create a TEACHER-STYLE explanation with clear narration.
- Create exactly 2-3 scenes
- Write narration as if you're a teacher explaining to a student
- Each narration: 2-3 natural sentences that flow smoothly when spoken
- Title: MAX 5 words
- Specify visual_type for each scene:
  * "equation" - for mathematical formulas
  * "graph" - for plotting functions
  * "tree" - for tree structures  
  * "array" - for array/list visualization
  * "histogram" - for bar charts/statistics
  * "network" - for graph theory/networks
  * "matrix" - for matrix operations
  * "algorithm" - for step-by-step algorithm visualization

Narration Style Guidelines:
- Use conversational, teacher-like language
- Say "Let's look at..." "Notice how..." "This is important because..."
- Pause naturally between concepts
- Make it engaging and easy to follow

Format as JSON:
[
  {{
    "scene_number": 1,
    "title": "Topic Name",
    "narration_text": "Let me explain this concept to you. Notice how this works in practice.",
    "visual_type": "equation",
    "visual_params": {{"equation": "f(x) = x^2"}}
  }}
]

Examples of visual_params:
- equation: {{"equation": "E = mc^2"}}
- graph: {{"function": "lambda x: x**2", "label": "f(x) = x²"}}
- tree: {{"values": [4, 2, 6, 1, 3, 5, 7]}}
- array: {{"array": [64, 34, 25, 12, 22]}}
- algorithm: {{"steps": ["Initialize", "Compare elements", "Swap if needed", "Repeat"]}}
- matrix: {{"matrix": [[1, 2], [3, 4]]}}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        import json
        script_content = response.choices[0].message.content
        
        # Clean JSON formatting
        script_content = script_content.strip()
        if script_content.startswith("```json"):
            script_content = script_content[7:]
        if script_content.startswith("```"):
            script_content = script_content[3:]
        if script_content.endswith("```"):
            script_content = script_content[:-3]
        
        try:
            scenes = json.loads(script_content.strip())
        except:
            scenes = [
                {
                    "scene_number": 1, 
                    "title": request.topic,
                    "narration_text": script_content[:200]
                }
            ]
        
        video_id = "video_" + str(abs(hash(request.topic + str(len(scenes)))))[:8]
        
        # Step 2: Choose generator based on mode
        use_professional = request.professional_mode and HAS_PRO_VIDEO and pro_video_gen is not None
        
        if use_professional:
            # Professional mode: Manim + OpenAI TTS (natural voice)
            print(f"🎬 Using Professional Mode (Manim + OpenAI TTS voice: {request.voice})")
            if hasattr(pro_video_gen, 'voice'):
                pro_video_gen.voice = request.voice
            generator = pro_video_gen
        else:
            # Standard mode: Check if topic needs mathematical visualization
            math_topics = ['equation', 'graph', 'tree', 'array', 'algorithm', 'math', 'calculus', 
                          'algebra', 'statistics', 'network', 'matrix', 'flowchart', 'histogram',
                          'sorting', 'data structure', 'binary', 'linear', 'geometry']
            use_manim_style = any(keyword in request.topic.lower() or keyword in request.subject.lower() 
                                for keyword in math_topics)
            generator = manim_gen if use_manim_style else video_gen
        
        # Step 3: Generate actual video (run in background)
        try:
            loop = asyncio.get_event_loop()
            video_path = await loop.run_in_executor(
                executor,
                generator.generate_video,
                scenes,
                request.topic,
                video_id
            )

            # Ensure video_path is a string and file exists
            video_path_str = str(video_path) if video_path else None
            video_file = Path(video_path_str) if video_path_str else None

            # Verify file exists
            if video_file and video_file.exists():
                # Ensure it's in generated_videos directory for serving
                output_dir = Path("generated_videos")
                output_dir.mkdir(exist_ok=True)
                target_path = output_dir / f"{video_id}.mp4"

                # Copy if needed
                if video_file != target_path:
                    import shutil
                    shutil.copy2(video_file, target_path)
                    video_path_str = str(target_path)

                return {
                    "id": video_id,
                    "topic": request.topic,
                    "scenes": scenes,
                    "duration_seconds": request.duration_minutes * 60,
                    "status": "completed",
                    "video_path": video_path_str,
                    "download_url": f"/video/{video_id}/download",
                    "message": (
                        f"Video generated successfully! {len(scenes)} scenes rendered."
                        + (" (Professional Mode: Manim + Natural Voice)" if use_professional else "")
                    ),
                }
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Video generation completed but file not found at {video_path_str}",
                )
        except Exception as video_error:
            import traceback
            error_detail = f"Video generation failed: {str(video_error)}"
            print(f"\n❌ {error_detail}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=error_detail)
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Video generation error: {str(e)}")


# Download generated video
@app.get("/video/{video_id}/download")
async def download_video(video_id: str):
    """Download a generated video."""
    # Try multiple possible paths
    possible_paths = [
        Path("generated_videos") / f"{video_id}.mp4",
        Path("generated_videos") / f"video_{video_id}.mp4",
        Path(video_id + ".mp4"),  # Full path provided
    ]
    
    # Also check in media directories (Manim output)
    if video_id.startswith("video_"):
        video_id_only = video_id[6:]  # Remove "video_" prefix
        possible_paths.append(Path("generated_videos") / f"{video_id_only}.mp4")
    
    video_path = None
    for path in possible_paths:
        if path.exists():
            video_path = path
            break
    
    if not video_path or not video_path.exists():
        # Try to find any video with this id in generated_videos
        generated_dir = Path("generated_videos")
        if generated_dir.exists():
            for vid_file in generated_dir.glob(f"*{video_id}*.mp4"):
                video_path = vid_file
                break
        
        if not video_path or not video_path.exists():
            raise HTTPException(status_code=404, detail=f"Video not found: {video_id}")
    
    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        filename=f"{video_id}.mp4"
    )


# Initialize sample content
@app.post("/content/initialize-samples")
async def initialize_samples():
    """Add sample educational content."""
    samples = [
        {
            "content": "Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
            "subject": "Computer Science",
            "topic": "Python Basics",
            "difficulty": "beginner"
        },
        {
            "content": "A binary search tree (BST) is a data structure where each node has at most two children. The left subtree contains only nodes with values less than the parent, and the right subtree only nodes with values greater.",
            "subject": "Computer Science", 
            "topic": "Data Structures",
            "difficulty": "intermediate"
        },
        {
            "content": "Quadratic equations are polynomial equations of degree 2. The general form is ax² + bx + c = 0. Solutions can be found using the quadratic formula: x = (-b ± √(b²-4ac)) / 2a",
            "subject": "Mathematics",
            "topic": "Algebra",
            "difficulty": "beginner"
        }
    ]
    
    for sample in samples:
        knowledge_base.append(sample)
    
    return {"status": "initialized", "chunks": len(samples)}


# Multi-Agent System Endpoint
@app.post("/mas/learn")
async def mas_learn(request: AskRequest):
    """
    Multi-Agent System endpoint - Uses specialized agents to create comprehensive learning experience.
    
    This endpoint demonstrates a true Multi-Agent System architecture with:
    - Designer Agent: Creates structured learning plan
    - Generator Agent: Generates detailed educational content
    - Assessment Agent: Creates practice quizzes
    - Master Orchestrator: Coordinates workflow using LangGraph
    """
    try:
        # Build context from knowledge base
        context = ""
        if knowledge_base:
            relevant = [k for k in knowledge_base if request.subject.lower() in k.get('subject', '').lower()]
            if relevant:
                context = "\n\n".join([k['content'][:400] for k in relevant[:2]])
        
        # Run multi-agent workflow
        result = mas_orchestrator.run(
            question=request.question,
            subject=request.subject,
            difficulty="beginner",  # Can be made dynamic
            context=context
        )
        
        # Format comprehensive response
        comprehensive_answer = f"""## 📋 Learning Plan
{result['learning_plan']}

---

## 📚 Educational Content
{result['content']}

---

## ✅ Practice Assessment
Quiz questions have been generated to test your understanding.
"""
        
        return {
            "answer": comprehensive_answer,
            "learning_plan": result['learning_plan'],
            "content": result['content'],
            "assessment": result['assessment'],
            "session_id": request.session_id,
            "workflow": "multi-agent-system",
            "agents_used": ["designer", "generator", "assessor"]
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# 3Blue1Brown Complete Video Generation
class ThreeB1BRequest(BaseModel):
    topic: str
    voice: str = "nova"  # nova, shimmer, alloy, echo, onyx, fable


@app.post("/video/3b1b-complete")
async def generate_3b1b_complete(request: ThreeB1BRequest):
    """
    Generate a COMPLETE 3Blue1Brown-style video package with all 4 sections:
    1. Voiceover Script (with [PAUSE] and [EMPHASIS] markers)
    2. Animation Storyboard (scene-by-scene descriptions)
    3. Manim Code (runnable Python)
    4. Voice Generation Prompt (for OpenAI TTS)
    """
    try:
        from threeblueonebrown_generator import ThreeBlueOneBrownGenerator
        
        generator = ThreeBlueOneBrownGenerator()
        
        # Generate complete package
        package = generator.generate_complete_package(request.topic)
        
        # Generate audio
        output_dir = Path("generated_videos") / request.topic.lower().replace(" ", "_")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        audio_path = str(output_dir / "narration.mp3")
        generator.generate_audio(package.voiceover_script, audio_path, request.voice)
        
        # Save files
        (output_dir / "complete_package.txt").write_text(package.to_string())
        (output_dir / "manim_code.py").write_text(package.manim_code)
        
        return {
            "topic": request.topic,
            "voice": request.voice,
            "sections": {
                "voiceover_script": package.voiceover_script,
                "animation_storyboard": package.animation_storyboard,
                "manim_code": package.manim_code,
                "voice_prompt": package.voice_prompt
            },
            "audio_url": f"/static/{request.topic.lower().replace(' ', '_')}/narration.mp3",
            "download_url": f"/video/3b1b/{request.topic.lower().replace(' ', '_')}/download",
            "message": "Complete 3Blue1Brown video package generated with all 4 sections!"
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/video/3b1b/{topic_slug}/download")
async def download_3b1b_audio(topic_slug: str):
    """Download the generated narration audio."""
    audio_path = Path("generated_videos") / topic_slug / "narration.mp3"
    
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio not found")
    
    return FileResponse(
        path=str(audio_path),
        media_type="audio/mpeg",
        filename=f"{topic_slug}_narration.mp3"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

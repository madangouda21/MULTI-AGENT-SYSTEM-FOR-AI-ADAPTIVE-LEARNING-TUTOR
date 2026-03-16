# OpenAI API Usage Guide

## Your API Key Configuration

Your OpenAI API key is now configured in the `.env` file:
- **Key**: `OPENAI_API_KEY`
- **Model**: `gpt-4o-mini` (cost-effective, fast, intelligent)
- **Location**: `/Users/kartikhiremath/Desktop/Gen_AI/Project/.env`

---

## Features That Use Your OpenAI API Key

### 1. **AI Tutor (📚 Learn Page)**
**What it does:**
- Answers student questions with context from uploaded materials
- Adapts responses based on student learning style and difficulty level
- Uses RAG (Retrieval-Augmented Generation) to provide accurate, contextual answers

**API Calls:**
- **When**: Every time a student asks a question in "AI Tutor (full answer)" mode
- **Model**: gpt-4o-mini
- **Approximate tokens**: 500-2000 tokens per question (depending on context and response length)
- **Cost**: ~$0.0001-0.0006 per question

**How to save credits:**
- Switch to "Resource-first (save credits)" mode for Computer Science topics
- This provides curated links (GeeksforGeeks, CP-Algorithms, etc.) instead of API calls

---

### 2. **Quiz Generator (📝 Quiz Page)**
**What it does:**
- Generates multiple-choice questions based on topics
- Creates explanations for correct answers
- Uses RAG to pull relevant educational context

**API Calls:**
- **When**: When you click "Generate Quiz"
- **Model**: gpt-4o-mini
- **Approximate tokens**: 300-800 tokens per question
- **Cost**: ~$0.0001-0.0003 per question

**Example:** Generating 3 quiz questions = ~1500 tokens = ~$0.0004

---

### 3. **Concept Explainer**
**What it does:**
- Provides detailed explanations of specific concepts
- Structures explanations with examples and key takeaways

**API Calls:**
- **When**: Used internally by the tutor pipeline for detailed explanations
- **Model**: gpt-4o-mini
- **Approximate tokens**: 400-1000 tokens
- **Cost**: ~$0.0001-0.0003 per explanation

---

### 4. **Video Script Generator (🎬 Video Generator)**
**What it does:**
- Creates scene-by-scene scripts for educational videos
- Determines animation types (equations, graphs, bullet points, etc.)
- Writes narration text for each scene

**API Calls:**
- **When**: When you click "Generate Video"
- **Model**: gpt-4o-mini
- **Approximate tokens**: 1000-3000 tokens per video script (5-8 scenes)
- **Cost**: ~$0.0003-0.0009 per video

**Note:** Video generation also uses:
- **Edge-TTS**: Free text-to-speech (no API cost)
- **MoviePy**: Local video rendering (no API cost)

---

## Features That DO NOT Use Your API Key

### 1. **RAG System (Vector Search)**
- Uses local HuggingFace embeddings (`all-MiniLM-L6-v2`)
- ChromaDB vector storage is local
- **No API calls** for document retrieval

### 2. **Study Materials Upload (📥 Materials)**
- Document processing and chunking is local
- Vector embeddings are generated locally
- **No API calls** for ingestion

### 3. **Student Profiles & Adaptive Engine**
- Learning progress tracking is local
- Difficulty adjustments are algorithmic
- **No API calls**

### 4. **Voice Narration (TTS)**
- Uses Edge-TTS (Microsoft's free service)
- **No OpenAI API calls**

### 5. **Video Rendering**
- MoviePy for video generation (local)
- Manim for animations (local, optional)
- **No API calls**

---

## Estimated Monthly Costs (Based on Usage)

### Light Usage (10 students, 5 questions/day each)
- **Daily**: 50 questions × $0.0003 = **$0.015/day**
- **Monthly**: **~$0.45/month**

### Moderate Usage (50 students, 10 questions/day each)
- **Daily**: 500 questions × $0.0003 = **$0.15/day**
- **Monthly**: **~$4.50/month**

### Heavy Usage (100 students, 20 questions/day, 5 quizzes/week)
- **Daily questions**: 2000 × $0.0003 = **$0.60/day**
- **Weekly quizzes**: 500 × 3 questions × $0.0002 = **$0.30/week**
- **Monthly**: **~$19/month**

---

## How to Monitor Your Usage

### OpenAI Dashboard
1. Visit: https://platform.openai.com/usage
2. Log in with your OpenAI account
3. View real-time usage and costs
4. Set up billing alerts

### In-App Recommendations
The app is designed to minimize API costs:

1. **Resource-first mode**: Provides curated CS resources instead of LLM calls
2. **Selective video recommendations**: Only suggests videos for visual topics
3. **Local embeddings**: RAG uses local models, not OpenAI embeddings
4. **Smart caching**: LangChain memory reduces redundant API calls

---

## Tips to Reduce API Costs

1. **Use Resource-first mode** for Computer Science topics
2. **Upload comprehensive materials** - better RAG context = more efficient responses
3. **Batch quiz generation** - generate multiple questions at once
4. **Use sample content** - initialize with built-in educational content
5. **Monitor usage** - check OpenAI dashboard regularly

---

## Current Configuration

```env
OPENAI_API_KEY=sk-proj-mzmw-OvdOoQNBjtn...  # Your key (redacted)
LLM_MODEL=gpt-4o-mini                        # Cost-effective model
TEMPERATURE=0.7                               # Balanced creativity
```

**Model Details:**
- **gpt-4o-mini**: $0.150 per 1M input tokens, $0.600 per 1M output tokens
- Fast, intelligent, cost-effective
- Perfect for educational use cases

---

## Need Help?

If you notice unexpected API usage:
1. Check the OpenAI usage dashboard
2. Review recent chat history in the app
3. Consider switching to "Resource-first" mode for high-traffic topics
4. Adjust temperature or model in `.env` if needed

**Questions?** Open the Settings page in the app for system status and configuration tips.

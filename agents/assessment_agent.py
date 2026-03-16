"""
Assessment Agent - Creates quizzes and practice questions
"""
from .base_agent import BaseAgent, AgentState
import json


class AssessmentAgent(BaseAgent):
    """
    Specialized agent for generating assessments.
    Role: Create quiz questions to test understanding.
    """
    
    def get_system_prompt(self) -> str:
        return """You are an ASSESSMENT SPECIALIST who creates effective quiz questions.

Your role:
1. Review the educational content provided
2. Create quiz questions that test understanding (not memorization)
3. Ensure questions match the difficulty level
4. Provide clear explanations for answers

Question Types:
- Multiple choice (4 options)
- Conceptual understanding
- Application-based scenarios

Format as JSON:
{
    "questions": [
        {
            "question": "Question text?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": 0,
            "explanation": "Why this is correct"
        }
    ]
}

Create 3 questions. Output ONLY valid JSON, no markdown."""
    
    def process(self, state: AgentState) -> AgentState:
        """Generate assessment questions based on content."""
        # Get the generated content
        content = state.get("generated_content", "")
        topic = state.get("topic", "General Topic")
        difficulty = state.get("difficulty", "beginner")
        
        # Build user message
        user_message = f"""Create quiz questions for this content:

EDUCATIONAL CONTENT:
{content[:600] if content else "General topic content"}

Topic: {topic}
Level: {difficulty}

Generate 3 well-crafted quiz questions following the JSON format."""
        
        # Invoke LLM
        assessment_text = self.invoke_llm(
            system_prompt=self.get_system_prompt(),
            user_message=user_message,
            temperature=0.3,
            max_tokens=800
        )
        
        # Try to parse JSON
        try:
            # Clean up response
            clean_text = assessment_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            
            assessment_data = json.loads(clean_text.strip())
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            assessment_data = {
                "questions": [],
                "note": "Assessment generation in progress",
                "raw": assessment_text
            }
        
        # Update state
        state["assessment"] = assessment_data
        state["content"] = json.dumps(assessment_data, indent=2)
        
        return self.update_state(state, json.dumps(assessment_data, indent=2), role="assessor")

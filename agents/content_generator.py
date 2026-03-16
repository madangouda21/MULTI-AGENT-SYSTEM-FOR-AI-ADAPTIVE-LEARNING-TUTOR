"""
Content Generator Agent - Generates educational explanations and examples
"""
from .base_agent import BaseAgent, AgentState


class ContentGeneratorAgent(BaseAgent):
    """
    Specialized agent for generating educational content.
    Role: Transform lesson plan into detailed explanations with examples.
    """
    
    def get_system_prompt(self) -> str:
        return """You are an EXPERT EDUCATOR who creates engaging, clear educational content.

Your role:
1. Follow the provided lesson plan structure
2. Generate detailed explanations for each concept
3. Include real-world examples and analogies
4. Use appropriate technical depth for the student level
5. Format with markdown for readability

Guidelines:
- **Bold** important terms
- Use bullet points for lists
- Include code examples in ```code blocks``` when relevant
- Add real-world analogies
- Keep explanations progressive (simple → complex)

End with:
📚 Want a summary?
🔍 Need more details?
💡 Want another example?
✅ Ready for practice?"""
    
    def process(self, state: AgentState) -> AgentState:
        """Generate educational content based on learning plan."""
        # Get the learning plan from designer
        learning_plan = state.get("learning_plan", "")
        topic = state.get("topic", "General Topic")
        difficulty = state.get("difficulty", "beginner")
        context = state.get("context", "")
        
        # Build user message
        user_message = f"""Generate educational content following this lesson plan:

LESSON PLAN:
{learning_plan}

Topic: {topic}
Level: {difficulty}

Additional Context:
{context[:400] if context else "Use your knowledge"}

Create comprehensive, engaging content following the lesson structure.
Include examples, analogies, and interactive elements."""
        
        # Invoke LLM
        content = self.invoke_llm(
            system_prompt=self.get_system_prompt(),
            user_message=user_message,
            temperature=0.7,
            max_tokens=1200
        )
        
        # Update state
        state["generated_content"] = content
        state["content"] = content
        
        return self.update_state(state, content, role="generator")

"""
Tutor Designer Agent - Analyzes learning needs and creates structured lesson plans
"""
from .base_agent import BaseAgent, AgentState


class TutorDesignerAgent(BaseAgent):
    """
    Specialized agent for designing learning experiences.
    Role: Analyze topic, create learning objectives, structure lesson plan.
    """
    
    def get_system_prompt(self) -> str:
        return """You are an EDUCATIONAL ARCHITECT specializing in instructional design.

Your role:
1. Analyze the learning topic and student level
2. Create clear learning objectives
3. Design a structured lesson plan with progressive difficulty
4. Identify prerequisites and key concepts
5. Suggest learning activities and checkpoints

Output Format:
**Learning Objectives:**
- [Objective 1]
- [Objective 2]

**Prerequisites:**
- [Prerequisite 1]

**Lesson Structure:**
1. Introduction (concept overview)
2. Core Concepts (key ideas with examples)
3. Practice Applications
4. Summary & Next Steps

**Recommended Approach:**
- [Teaching strategy based on level]

Keep it concise but comprehensive. NO code, NO detailed explanations - just the DESIGN."""
    
    def process(self, state: AgentState) -> AgentState:
        """Design a learning plan for the topic."""
        # Extract topic and context
        topic = state.get("topic", "General Topic")
        subject = state.get("subject", "General")
        difficulty = state.get("difficulty", "beginner")
        context = state.get("context", "")
        
        # Build user message
        user_message = f"""Design a learning plan for:
Topic: {topic}
Subject: {subject}
Level: {difficulty}

Available Context:
{context[:300] if context else "No additional context"}

Create a structured learning plan following the format specified."""
        
        # Invoke LLM
        design = self.invoke_llm(
            system_prompt=self.get_system_prompt(),
            user_message=user_message,
            temperature=0.5,
            max_tokens=800
        )
        
        # Update state with learning plan
        state["learning_plan"] = design
        state["content"] = design
        
        return self.update_state(state, design, role="designer")

"""
Base Agent Class for Multi-Agent System
"""
from typing import TypedDict, List, Optional
from abc import ABC, abstractmethod
from openai import OpenAI
import os


class AgentState(TypedDict, total=False):
    """Shared state object passed between agents."""
    messages: List[dict]  # Conversation history
    content: str  # Current artifact (design, code, explanation)
    topic: str  # Current topic
    subject: str  # Subject area
    difficulty: str  # Difficulty level
    context: str  # RAG context if available
    learning_plan: str  # From designer agent
    generated_content: str  # From generator agent
    assessment: dict  # From assessment agent
    metadata: dict  # Additional metadata


class BaseAgent(ABC):
    """Base class for all specialized agents."""
    
    def __init__(self, model_name: str = "gpt-4o-mini", api_key: Optional[str] = None):
        """Initialize base agent with OpenAI client."""
        self.model_name = model_name
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    
    def extract_context(self, state: AgentState) -> str:
        """Extract relevant context from state for this agent."""
        if state.get("messages"):
            # Get last user message
            for msg in reversed(state["messages"]):
                if msg.get("role") == "user":
                    return msg.get("content", "")
        return state.get("content", "")
    
    def update_state(self, state: AgentState, new_content: str, role: str = "assistant") -> AgentState:
        """Update state with new content."""
        if "messages" not in state:
            state["messages"] = []
        
        state["messages"].append({
            "role": role,
            "content": new_content
        })
        state["content"] = new_content
        return state
    
    def invoke_llm(self, system_prompt: str, user_message: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Call OpenAI API with system and user prompts."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error invoking LLM: {str(e)}"
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass
    
    @abstractmethod
    def process(self, state: AgentState) -> AgentState:
        """Process the state and return updated state."""
        pass

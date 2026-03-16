"""
Master Orchestrator - Coordinates all agents using LangGraph
"""
from typing import Optional
from langgraph.graph import StateGraph, END
from .base_agent import AgentState
from .tutor_designer import TutorDesignerAgent
from .content_generator import ContentGeneratorAgent
from .assessment_agent import AssessmentAgent


class MasterOrchestrator:
    """
    Master agent that orchestrates the multi-agent workflow using LangGraph.
    
    Workflow:
    1. User Question → Designer Agent (creates learning plan)
    2. Learning Plan → Generator Agent (creates content)
    3. Content → Assessment Agent (creates quiz)
    4. Return comprehensive response
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize all agents and build the workflow graph."""
        # Initialize specialized agents
        self.designer = TutorDesignerAgent(api_key=api_key)
        self.generator = ContentGeneratorAgent(api_key=api_key)
        self.assessor = AssessmentAgent(api_key=api_key)
        
        # Build the LangGraph workflow
        self.workflow = self._create_workflow()
    
    def _design_step(self, state: AgentState) -> AgentState:
        """Execute designer agent."""
        print("🎨 Designer Agent: Creating learning plan...")
        return self.designer.process(state)
    
    def _generate_step(self, state: AgentState) -> AgentState:
        """Execute content generator agent."""
        print("📝 Generator Agent: Creating educational content...")
        return self.generator.process(state)
    
    def _assess_step(self, state: AgentState) -> AgentState:
        """Execute assessment agent."""
        print("✅ Assessment Agent: Generating quiz questions...")
        return self.assessor.process(state)
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow with sequential agent execution."""
        # Create state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent
        workflow.add_node("design", self._design_step)
        workflow.add_node("generate", self._generate_step)
        workflow.add_node("assess", self._assess_step)
        
        # Define sequential flow
        workflow.set_entry_point("design")
        workflow.add_edge("design", "generate")
        workflow.add_edge("generate", "assess")
        workflow.add_edge("assess", END)
        
        # Compile the workflow
        return workflow.compile()
    
    def run(
        self,
        question: str,
        subject: str = "General",
        difficulty: str = "beginner",
        context: str = ""
    ) -> dict:
        """
        Execute the multi-agent workflow.
        
        Args:
            question: The learning question/topic
            subject: Subject area
            difficulty: Difficulty level (beginner/intermediate/advanced/expert)
            context: Optional RAG context
        
        Returns:
            dict: Complete response with learning plan, content, and assessment
        """
        # Initialize state
        initial_state: AgentState = {
            "messages": [{"role": "user", "content": question}],
            "content": question,
            "topic": question,
            "subject": subject,
            "difficulty": difficulty,
            "context": context,
            "metadata": {
                "workflow": "multi-agent",
                "agents": ["designer", "generator", "assessor"]
            }
        }
        
        # Execute workflow
        print("\n" + "="*60)
        print("🤖 Multi-Agent System Activated")
        print("="*60)
        
        final_state = self.workflow.invoke(initial_state)
        
        print("="*60)
        print("✨ Multi-Agent Processing Complete\n")
        
        # Extract results
        return {
            "learning_plan": final_state.get("learning_plan", ""),
            "content": final_state.get("generated_content", ""),
            "assessment": final_state.get("assessment", {}),
            "full_conversation": final_state.get("messages", []),
            "metadata": final_state.get("metadata", {})
        }
    
    def run_partial(
        self,
        question: str,
        agents: list = None,
        subject: str = "General",
        difficulty: str = "beginner",
        context: str = ""
    ) -> dict:
        """
        Run only specific agents (for flexibility).
        
        Args:
            question: The learning question/topic
            agents: List of agent names to run (e.g., ['design', 'generate'])
            subject: Subject area
            difficulty: Difficulty level
            context: Optional RAG context
        
        Returns:
            dict: Partial results based on selected agents
        """
        if agents is None:
            agents = ["design", "generate"]
        
        initial_state: AgentState = {
            "messages": [{"role": "user", "content": question}],
            "content": question,
            "topic": question,
            "subject": subject,
            "difficulty": difficulty,
            "context": context,
            "metadata": {"workflow": "partial", "agents": agents}
        }
        
        result = {}
        current_state = initial_state
        
        # Execute agents sequentially
        if "design" in agents:
            current_state = self.designer.process(current_state)
            result["learning_plan"] = current_state.get("learning_plan", "")
        
        if "generate" in agents:
            current_state = self.generator.process(current_state)
            result["content"] = current_state.get("generated_content", "")
        
        if "assess" in agents:
            current_state = self.assessor.process(current_state)
            result["assessment"] = current_state.get("assessment", {})
        
        return result

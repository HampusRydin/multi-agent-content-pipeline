from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from agents.researcher import ResearchAgent
from agents.writer import WriterAgent
from agents.fact_checker import FactCheckerAgent
from agents.polisher import PolisherAgent


class WorkflowState(TypedDict):
    topic: str
    target_length: Annotated[int, "Target length for the content"]
    style: Annotated[str, "Writing style"]
    research_data: Annotated[dict, "Research findings"]
    draft_content: Annotated[str, "Initial draft"]
    fact_checked_content: Annotated[str, "Content after fact checking"]
    final_content: Annotated[str, "Final polished content"]
    metadata: Annotated[dict, "Additional metadata"]


def create_workflow():
    """
    Create and compile the LangGraph workflow for the multi-agent content pipeline.
    """
    # Initialize agents
    researcher = ResearchAgent()
    writer = WriterAgent()
    fact_checker = FactCheckerAgent()
    polisher = PolisherAgent()
    
    # Create the graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("research", researcher.run)
    workflow.add_node("write", writer.run)
    workflow.add_node("fact_check", fact_checker.run)
    workflow.add_node("polish", polisher.run)
    
    # Define the flow
    workflow.set_entry_point("research")
    workflow.add_edge("research", "write")
    workflow.add_edge("write", "fact_check")
    workflow.add_edge("fact_check", "polish")
    workflow.add_edge("polish", END)
    
    # Compile the graph
    return workflow.compile()


def create_workflow_async():
    """
    Create an async version of the workflow.
    """
    # Initialize agents
    researcher = ResearchAgent()
    writer = WriterAgent()
    fact_checker = FactCheckerAgent()
    polisher = PolisherAgent()
    
    # Create the graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("research", researcher.run_async)
    workflow.add_node("write", writer.run_async)
    workflow.add_node("fact_check", fact_checker.run_async)
    workflow.add_node("polish", polisher.run_async)
    
    # Define the flow
    workflow.set_entry_point("research")
    workflow.add_edge("research", "write")
    workflow.add_edge("write", "fact_check")
    workflow.add_edge("fact_check", "polish")
    workflow.add_edge("polish", END)
    
    # Compile the graph
    return workflow.compile()


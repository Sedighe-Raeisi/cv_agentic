from langgraph.graph import END, StateGraph

from src.agent.nodes import enrich_cv_node, fetch_github_node, validate_cv_node
from src.agent.state import AgentState


def should_continue(state: AgentState) -> str:
    """Conditional Edge: Directs to END if validated or if max retries exceeded."""
    if state.get("validation_passed", False) or state.get("revision_count", 0) >= 3:
        return "end"
    return "enrich"

def build_cv_agent():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("fetch_github", fetch_github_node)
    workflow.add_node("enrich_cv", enrich_cv_node)
    workflow.add_node("validate_cv", validate_cv_node)

    # Set Entry Point
    workflow.set_entry_point("fetch_github")

    # Connect Edges
    workflow.add_edge("fetch_github", "enrich_cv")
    workflow.add_edge("enrich_cv", "validate_cv")

    # Add Conditional Routing (Validation Loop)
    workflow.add_conditional_edges(
        "validate_cv",
        should_continue,
        {
            "end": END,
            "enrich": "enrich_cv"
        }
    )

    return workflow.compile()
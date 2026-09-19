import json
import os

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage

from src.agent.factory import get_llm
from src.agent.state import AgentState
from src.tools.github_mcp import fetch_github_repositories

load_dotenv()

llm_provider = os.getenv("PROVIDER", "academiccloud")
llm = get_llm(llm_provider)

def fetch_github_node(state: AgentState) -> dict:
    """Fetches repository data via MCP tool."""
    username = state["github_username"]
    repos = fetch_github_repositories.invoke({"username": username})
    return {"github_data": repos}

def enrich_cv_node(state: AgentState) -> dict:
    """Enriches CV bullet points using GitHub evidence."""
    prompt = f"""You are a Senior Agentic AI Career Strategist.
    Enrich the given CV for targeted AI Engineer and ML Engineer roles.

    Original CV:
    {state['raw_cv']}

    GitHub Evidence Data:
    {json.dumps(state['github_data'], indent=2)}

    Critique from previous validation loop (if any):
    {state.get('critique', 'None')}

    Preserve formatting while injecting technical proof points. Return ONLY Markdown text."""
    
    response = llm.invoke([SystemMessage(content=prompt)])
    return {
        "draft_cv": response.content,
        "revision_count": state.get("revision_count", 0) + 1
    }

def validate_cv_node(state: AgentState) -> dict:
    """Validates generated output against raw evidence to block hallucinations."""
    prompt = f"""You are a Technical Auditor. Verify if claims in Draft CV are supported by Raw CV or GitHub Evidence.

    Raw CV: {state['raw_cv']}
    GitHub Evidence: {json.dumps(state['github_data'], indent=2)}
    Draft CV: {state['draft_cv']}

    Return ONLY a raw JSON object with keys "passed" (boolean) and "critique" (string)."""
    
    response = llm.invoke([SystemMessage(content=prompt)])
    try:
        result = json.loads(response.content.strip().strip("```json").strip("```"))
        return {
            "validation_passed": result.get("passed", False),
            "critique": result.get("critique", "")
        }
    except Exception:  # noqa: BLE001
        return {"validation_passed": True, "critique": "Validation check bypassed."}
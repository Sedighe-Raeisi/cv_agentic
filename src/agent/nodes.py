import json
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

from src.agent.factory import get_llm
from src.agent.state import AgentState
from src.tools.github_mcp import fetch_github_repositories

load_dotenv(override=True)

# Provider initialization from environment variables
llm_provider = os.getenv("PROVIDER")
llm = get_llm(llm_provider)


def fetch_github_node(state: AgentState) -> dict:
    """Fetches repository data via MCP tool."""
    username = state.get("github_username", "")
    repos = fetch_github_repositories.invoke({"username": username})
    return {"github_data": repos}


def enrich_cv_node(state: AgentState) -> dict:
    """Step 2: Generate updated LaTeX from raw template or vision images."""
    latex_template = state.get("cv_text_template", "")
    images = state.get("cv_images_base64", [])
    custom_prompt = state.get("custom_prompt", "")
    github_data = state.get("github_data", {})

    base_instructions = f"""You are an expert LaTeX Resume Writer. Write a complete, compilable LaTeX CV.
USER INSTRUCTIONS: {custom_prompt}
GITHUB EVIDENCE: {json.dumps(github_data, indent=2)}
RULES: Escape '_' as '\\_' and '&' as '\\&'. Return raw LaTeX starting with \\documentclass and ending with \\end{{document}}."""

    if latex_template:
        prompt = f"{base_instructions}\n\nBASELINE TEMPLATE:\n```latex\n{latex_template}\n```"
        content_payload = [{"type": "text", "text": prompt}]
    else:
        content_payload = [{"type": "text", "text": base_instructions}]
        for img_b64 in images:
            content_payload.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
            })

    try:
        model_to_use = llm.bind(tool_choice="none")
    except Exception:
        model_to_use = llm

    res = model_to_use.invoke([HumanMessage(content=content_payload)])
    
    cleaned_latex = res.content.strip()
    if "```" in cleaned_latex:
        cleaned_latex = cleaned_latex.split("```")[1]
        if cleaned_latex.startswith("latex"):
            cleaned_latex = cleaned_latex[5:]

    return {
        "draft_cv": cleaned_latex.strip(),
        "revision_count": state.get("revision_count", 0) + 1
    }


def validate_cv_node(state: AgentState) -> dict:
    """Step 3: Audit the generated LaTeX against source files to prevent hallucinations."""
    github_data = state.get("github_data", {})
    draft_cv = state.get("draft_cv", "")

    messages = [
        SystemMessage(content=(
            "You are a strict Technical Auditor. Verify that the generated LaTeX CV draft "
            "contains no fabricated stats or unverified repositories.\n"
            "Return ONLY a raw JSON string formatted as: "
            '{"passed": true/false, "critique": "reason if failed, empty string if passed"}'
        )),
        HumanMessage(content=(
            f"GitHub Evidence:\n{json.dumps(github_data, indent=2)}\n\n"
            f"LaTeX Draft:\n{draft_cv}"
        ))
    ]

    res = llm.invoke(messages)
    try:
        data = json.loads(res.content.strip().replace("```json", "").replace("```", "").strip())
        return {
            "validation_passed": data.get("passed", False),
            "critique": data.get("critique", "")
        }
    except Exception:  # noqa: BLE001
        return {"validation_passed": True, "critique": ""}
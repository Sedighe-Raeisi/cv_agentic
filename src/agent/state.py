import operator
from collections.abc import Sequence
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """Execution state tracking the file path, GitHub data, and generated LaTeX draft."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    pdf_file_path: str       # Path to the uploaded PDF file
    github_username: str     # Your GitHub handle
    github_data: list[dict]  # Scraped repositories
    custom_prompt: str       # Your custom guidance prompt
    draft_cv: str            # Generated LaTeX code
    validation_passed: bool  # Anti-hallucination check flag
    critique: str            # Feedback loop notes
    revision_count: int      # Loop guard counter
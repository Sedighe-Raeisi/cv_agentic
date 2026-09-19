import operator
from collections.abc import Sequence
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """Execution state for the CV Enhancement Agent."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    raw_cv: str
    github_username: str
    github_data: list[dict]
    draft_cv: str
    validation_passed: bool
    critique: str
    revision_count: int
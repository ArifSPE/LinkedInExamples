from __future__ import annotations

import operator
from typing import Annotated

from typing_extensions import Literal, TypedDict


class PlannerState(TypedDict):
    goal: str
    plan: list[str]
    completed_steps: list[str]
    final_answer: str
    history: list[str]


class RouterState(TypedDict):
    request: str
    route: str
    result: str
    history: list[str]


class TravelState(TypedDict):
    destination: str
    flights: str
    hotels: str
    weather: str
    summary: str
    history: list[str]


class ReflectionState(TypedDict):
    topic: str
    draft: str
    critique: str
    revision_count: int
    history: list[str]


class CollaborationState(TypedDict):
    topic: str
    research_notes: str
    outline: str
    draft: str
    history: list[str]


class ApprovalState(TypedDict):
    request: str
    draft_action: str
    approved: bool
    reviewer: str
    outcome: str
    history: list[str]


class StatefulAgentState(TypedDict):
    request: str
    status: Literal["new", "researching", "drafting", "review", "done"]
    notes: str
    draft: str
    final_answer: str
    history: list[str]


class AggregationState(TypedDict):
    user_request: str
    results: Annotated[list[dict], operator.add]
    history: Annotated[list[str], operator.add]
    final_answer: str
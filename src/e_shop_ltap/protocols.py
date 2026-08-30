"""Interfaces. Orchestration and the CLI depend on these and on nothing concrete."""

from __future__ import annotations

from typing import Protocol

from .models import Answer, CostLine, Job, LatencyStage, Recommendation


class InventoryRepository(Protocol):
    """Where the scenario's facts come from. Swap CSV for a scheduler API without touching callers."""

    def load_jobs(self) -> tuple[Job, ...]: ...

    def load_latency_stages(self) -> tuple[LatencyStage, ...]: ...

    def load_cost_lines(self) -> tuple[CostLine, ...]: ...

    def load_answers(self) -> tuple[Answer, ...]: ...


class RetirementRule(Protocol):
    """One reading of the inventory. A new reading is a new class, not an edit to the service."""

    label: str

    def is_retired_by_ltap(self, job: Job) -> bool: ...


class DecisionPolicy(Protocol):
    """Turns the five answers into a commitment level."""

    def recommend(self, answers: tuple[Answer, ...]) -> Recommendation: ...

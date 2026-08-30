"""Orchestration only. It knows the protocols and the order of operations, nothing else."""

from __future__ import annotations

from collections.abc import Sequence

from .decision import FiveQuestionPolicy
from .lag_model import build_paths
from .models import (
    CostComparison,
    InventoryReading,
    Job,
    ReadingComparison,
    ScenarioReport,
)
from .protocols import DecisionPolicy, InventoryRepository, RetirementRule


def _read(rule: RetirementRule, jobs: Sequence[Job]) -> InventoryReading:
    retired = tuple(j for j in jobs if rule.is_retired_by_ltap(j))
    kept = tuple(j for j in jobs if j not in retired)
    return InventoryReading(label=rule.label, retired=retired, kept=kept)


def _compare(governed: InventoryReading, other: InventoryReading) -> ReadingComparison:
    return ReadingComparison(
        reading=other,
        count_matches=other.retired_count == governed.retired_count,
        set_matches=other.retired_ids == governed.retired_ids,
        wrongly_retired=tuple(j for j in other.retired if j.job_id not in governed.retired_ids),
        wrongly_kept=tuple(j for j in governed.retired if j.job_id not in other.retired_ids),
    )


class ScenarioService:
    """Runs the governed reading, the naive readings, the lag paths, the cost and the decision."""

    def __init__(
        self,
        repository: InventoryRepository,
        governed_rule: RetirementRule,
        naive_rules: Sequence[RetirementRule],
        policy: DecisionPolicy | None = None,
    ) -> None:
        self._repository = repository
        self._governed_rule = governed_rule
        self._naive_rules = tuple(naive_rules)
        self._policy = policy or FiveQuestionPolicy()

    def build_report(self) -> ScenarioReport:
        jobs = self._repository.load_jobs()
        governed = _read(self._governed_rule, jobs)
        comparisons = tuple(_compare(governed, _read(rule, jobs)) for rule in self._naive_rules)

        return ScenarioReport(
            governed=governed,
            comparisons=comparisons,
            latency_paths=build_paths(self._repository.load_latency_stages()),
            cost=CostComparison(lines=self._repository.load_cost_lines()),
            recommendation=self._policy.recommend(self._repository.load_answers()),
        )

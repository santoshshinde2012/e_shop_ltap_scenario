"""Value objects. Every number the article quotes is reported through one of these."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TransformKind(StrEnum):
    """What a scheduled job does to the data that passes through it.

    ``COPY`` and ``COMPARE`` change nothing about meaning: one moves rows between stores,
    the other proves the two stores still agree. The rest earn their place.
    """

    COPY = "copy"
    COMPARE = "compare"
    DERIVE = "derive"
    AGGREGATE = "aggregate"
    VALIDATE = "validate"

    @property
    def changes_meaning(self) -> bool:
        return self not in (TransformKind.COPY, TransformKind.COMPARE)


@dataclass(frozen=True)
class Job:
    """One scheduled job, described by what it observably does — not by what it is called."""

    job_id: str
    name: str
    schedule: str
    source: str
    target: str
    transform_kind: TransformKind
    external_input: bool
    downstream: tuple[str, ...]


@dataclass(frozen=True)
class InventoryReading:
    """One reading of the same inventory: which jobs this rule says LTAP retires."""

    label: str
    retired: tuple[Job, ...]
    kept: tuple[Job, ...]

    @property
    def retired_ids(self) -> frozenset[str]:
        return frozenset(j.job_id for j in self.retired)

    @property
    def retired_count(self) -> int:
        return len(self.retired)

    @property
    def total(self) -> int:
        return len(self.retired) + len(self.kept)


@dataclass(frozen=True)
class ReadingComparison:
    """A reading held against the governed one — the two ways a reading can be wrong."""

    reading: InventoryReading
    count_matches: bool
    set_matches: bool
    wrongly_retired: tuple[Job, ...]
    wrongly_kept: tuple[Job, ...]

    @property
    def agrees(self) -> bool:
        return self.count_matches and self.set_matches


@dataclass(frozen=True)
class LatencyStage:
    """One contributor to end-to-end staleness, in seconds at p95."""

    path: str
    stage: str
    p95_seconds: float
    note: str


@dataclass(frozen=True)
class LatencyPath:
    """A full path from a committed write to the read that acts on it."""

    name: str
    stages: tuple[LatencyStage, ...]

    @property
    def p95_seconds(self) -> float:
        return round(sum(s.p95_seconds for s in self.stages), 3)

    @property
    def dominant_stage(self) -> LatencyStage:
        return max(self.stages, key=lambda s: s.p95_seconds)


@dataclass(frozen=True)
class CostLine:
    """One monthly line item, and whether retiring the sync tier removes it."""

    line_item: str
    monthly_usd: int
    retired_by_ltap: bool
    note: str


@dataclass(frozen=True)
class CostComparison:
    """What the sync tier costs, what replaces it, and the difference."""

    lines: tuple[CostLine, ...]

    @property
    def sync_tier_monthly(self) -> int:
        return sum(line.monthly_usd for line in self.lines if line.retired_by_ltap)

    @property
    def replacement_monthly(self) -> int:
        return sum(line.monthly_usd for line in self.lines if not line.retired_by_ltap)

    @property
    def net_monthly_saving(self) -> int:
        return self.sync_tier_monthly - self.replacement_monthly


@dataclass(frozen=True)
class Answer:
    """One answer in the five-question walk, with the evidence that backs it."""

    question_id: str
    question: str
    answer: bool
    evidence: str


@dataclass(frozen=True)
class Recommendation:
    """The commitment level the answers add up to, and the conditions attached to it."""

    level: str
    reasons: tuple[str, ...]
    brakes: tuple[str, ...]
    prerequisites: tuple[str, ...]


@dataclass(frozen=True)
class ScenarioReport:
    """Everything the CLI prints: the readings, the lag paths, the cost, the recommendation."""

    governed: InventoryReading
    comparisons: tuple[ReadingComparison, ...]
    latency_paths: tuple[LatencyPath, ...]
    cost: CostComparison
    recommendation: Recommendation

    @property
    def every_naive_reading_is_wrong(self) -> bool:
        return all(not c.agrees for c in self.comparisons)

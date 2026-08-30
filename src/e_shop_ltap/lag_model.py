"""Build the end-to-end staleness paths from the measured stages."""

from __future__ import annotations

from collections import defaultdict

from .models import LatencyPath, LatencyStage
from .schema import ANALYTICAL_PATH, FEATURE_PATH, PATH_TITLES, TWO_COPY_PATH

PATH_ORDER = (TWO_COPY_PATH, FEATURE_PATH, ANALYTICAL_PATH)


def build_paths(stages: tuple[LatencyStage, ...]) -> tuple[LatencyPath, ...]:
    """Group stages into paths, in the order the report reads best."""
    grouped: dict[str, list[LatencyStage]] = defaultdict(list)
    for stage in stages:
        grouped[stage.path].append(stage)

    ordered = [p for p in PATH_ORDER if p in grouped]
    ordered += sorted(p for p in grouped if p not in PATH_ORDER)
    return tuple(
        LatencyPath(name=PATH_TITLES.get(path, path), stages=tuple(grouped[path])) for path in ordered
    )


def speedup(before: LatencyPath, after: LatencyPath) -> float:
    """How many times faster ``after`` is. Returns 0.0 rather than dividing by zero."""
    if after.p95_seconds <= 0:
        return 0.0
    return round(before.p95_seconds / after.p95_seconds, 1)

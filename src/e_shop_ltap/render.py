"""Turn the report into the two shapes people want: something to read, something to pipe."""

from __future__ import annotations

from typing import Any

from .lag_model import speedup
from .models import InventoryReading, LatencyPath, ReadingComparison, ScenarioReport

WIDTH = 62


def _job_lines(reading: InventoryReading) -> list[str]:
    return [f"    {j.job_id}  {j.name}" for j in reading.retired]


def _minutes(seconds: float) -> str:
    return f" ({seconds / 60:.1f} min)" if seconds >= 60 else ""


def _governed_block(reading: InventoryReading) -> list[str]:
    lines = [reading.label, f"  Retires {reading.retired_count} of {reading.total}:"]
    lines += _job_lines(reading)
    lines.append(f"  Keeps {len(reading.kept)} — ingestion, transforms, quality tests, features, reporting.")
    return lines


def _comparison_block(comparison: ReadingComparison) -> list[str]:
    reading = comparison.reading
    if comparison.agrees:
        verdict = "agrees with the second-copy rule"
    elif comparison.count_matches:
        verdict = "right count, wrong list"
    else:
        verdict = "wrong count"

    lines = [reading.label, f"  Retires {reading.retired_count} of {reading.total} — {verdict}."]
    for job in comparison.wrongly_retired[:3]:
        lines.append(f"    would retire  {job.job_id}  {job.name}")
    if len(comparison.wrongly_retired) > 3:
        lines.append(f"    ... and {len(comparison.wrongly_retired) - 3} more that keep the data trustworthy")
    for job in comparison.wrongly_kept:
        lines.append(f"    would keep    {job.job_id}  {job.name}")
    return lines


def _latency_block(paths: tuple[LatencyPath, ...]) -> list[str]:
    lines = ["--- Staleness from committed write to the read that acts on it (p95) ---"]
    for path in paths:
        lines.append(f"  {path.name}")
        lines.append(f"    {path.p95_seconds:>8.1f} s{_minutes(path.p95_seconds)}")
        lines.append(f"    dominated by: {path.dominant_stage.stage} ({path.dominant_stage.p95_seconds:g} s)")
    if len(paths) >= 3:
        today, feature, analytical = paths[0], paths[1], paths[2]
        lines.append(
            f"  Feature path {speedup(today, feature):g}x faster; "
            f"analytical path {speedup(today, analytical):g}x faster."
        )
        lines.append(
            "  Neither is zero. The flush interval is still there; it is no longer yours to operate."
        )
    return lines


def _money(amount: int) -> str:
    """``-$5,200`` rather than ``$-5,200``."""
    return f"-${abs(amount):,}" if amount < 0 else f"${amount:,}"


def _cost_block(report: ScenarioReport) -> list[str]:
    cost = report.cost
    totals = (
        ("Sync tier retired", cost.sync_tier_monthly, ""),
        ("Less what replaces it (estimate)", -cost.replacement_monthly, ""),
        ("Net, to be confirmed by the pilot bill", cost.net_monthly_saving, ""),
    )
    labels = [line.line_item for line in cost.lines] + [t[0] for t in totals]
    width = max(len(label) for label in labels)

    lines = ["--- Sync tier, monthly ---"]
    for line in cost.lines:
        marker = "retired" if line.retired_by_ltap else "replaces"
        lines.append(f"  {line.line_item:<{width}}  {_money(line.monthly_usd):>9}  ({marker})")
    lines.append("  " + "-" * (width + 11))
    for label, amount, _ in totals:
        lines.append(f"  {label:<{width}}  {_money(amount):>9}")
    return lines


def _decision_block(report: ScenarioReport) -> list[str]:
    rec = report.recommendation
    lines = ["--- Decision ---", f"  Level: {rec.level}"]
    lines += [f"    because {reason}" for reason in rec.reasons]
    lines += [f"    brake:  {brake}" for brake in rec.brakes]
    lines += [f"    first:  {prerequisite}" for prerequisite in rec.prerequisites]
    return lines


def render_text(report: ScenarioReport) -> str:
    """The human report — this is what the article quotes."""
    blocks: list[list[str]] = [
        ["=== E-Shop — what LTAP actually retires ===", ""],
        _governed_block(report.governed),
        [""],
    ]
    for comparison in report.comparisons:
        blocks.append(_comparison_block(comparison))
        blocks.append([""])
    blocks += [_latency_block(report.latency_paths), [""]]
    blocks += [_cost_block(report), [""]]
    blocks += [_decision_block(report)]
    return "\n".join(line for block in blocks for line in block)


def to_dict(report: ScenarioReport) -> dict[str, Any]:
    """The same report as JSON, for a pipeline or a spreadsheet."""
    return {
        "governed": {
            "label": report.governed.label,
            "retired": [{"job_id": j.job_id, "name": j.name} for j in report.governed.retired],
            "retired_count": report.governed.retired_count,
            "kept_count": len(report.governed.kept),
            "total": report.governed.total,
        },
        "naive_readings": [
            {
                "label": c.reading.label,
                "retired_count": c.reading.retired_count,
                "count_matches": c.count_matches,
                "set_matches": c.set_matches,
                "wrongly_retired": [j.job_id for j in c.wrongly_retired],
                "wrongly_kept": [j.job_id for j in c.wrongly_kept],
            }
            for c in report.comparisons
        ],
        "latency_paths": [
            {
                "name": p.name,
                "p95_seconds": p.p95_seconds,
                "dominant_stage": p.dominant_stage.stage,
                "stages": [{"stage": s.stage, "p95_seconds": s.p95_seconds} for s in p.stages],
            }
            for p in report.latency_paths
        ],
        "cost": {
            "sync_tier_monthly_usd": report.cost.sync_tier_monthly,
            "replacement_monthly_usd": report.cost.replacement_monthly,
            "net_monthly_saving_usd": report.cost.net_monthly_saving,
        },
        "recommendation": {
            "level": report.recommendation.level,
            "reasons": list(report.recommendation.reasons),
            "brakes": list(report.recommendation.brakes),
            "prerequisites": list(report.recommendation.prerequisites),
        },
    }

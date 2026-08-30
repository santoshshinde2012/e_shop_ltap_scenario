"""The one place that reads files. Everything downstream takes frozen dataclasses."""

from __future__ import annotations

import csv
from pathlib import Path

from .models import Answer, CostLine, Job, LatencyStage, TransformKind
from .schema import ANSWERS_CSV, COST_CSV, JOBS_CSV, LATENCY_CSV


def _as_bool(value: str) -> bool:
    return value.strip().lower() in ("true", "yes", "1")


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class CsvInventoryRepository:
    """Reads the E-Shop scenario from the packaged CSVs.

    Point it at your own directory to run the same rules over your own inventory:
    ``CsvInventoryRepository(Path("~/my-platform").expanduser())``.
    """

    def __init__(self, data_dir: Path | None = None) -> None:
        self._jobs_csv = data_dir / JOBS_CSV.name if data_dir else JOBS_CSV
        self._latency_csv = data_dir / LATENCY_CSV.name if data_dir else LATENCY_CSV
        self._cost_csv = data_dir / COST_CSV.name if data_dir else COST_CSV
        self._answers_csv = data_dir / ANSWERS_CSV.name if data_dir else ANSWERS_CSV

    def load_jobs(self) -> tuple[Job, ...]:
        return tuple(
            Job(
                job_id=row["job_id"],
                name=row["name"],
                schedule=row["schedule"],
                source=row["source"],
                target=row["target"],
                transform_kind=TransformKind(row["transform_kind"]),
                external_input=_as_bool(row["external_input"]),
                downstream=tuple(d for d in row["downstream"].split(";") if d),
            )
            for row in _rows(self._jobs_csv)
        )

    def load_latency_stages(self) -> tuple[LatencyStage, ...]:
        return tuple(
            LatencyStage(
                path=row["path"],
                stage=row["stage"],
                p95_seconds=float(row["p95_seconds"]),
                note=row["note"],
            )
            for row in _rows(self._latency_csv)
        )

    def load_cost_lines(self) -> tuple[CostLine, ...]:
        return tuple(
            CostLine(
                line_item=row["line_item"],
                monthly_usd=int(row["monthly_usd"]),
                retired_by_ltap=_as_bool(row["retired_by_ltap"]),
                note=row["note"],
            )
            for row in _rows(self._cost_csv)
        )

    def load_answers(self) -> tuple[Answer, ...]:
        return tuple(
            Answer(
                question_id=row["question_id"],
                question=row["question"],
                answer=_as_bool(row["answer"]),
                evidence=row["evidence"],
            )
            for row in _rows(self._answers_csv)
        )

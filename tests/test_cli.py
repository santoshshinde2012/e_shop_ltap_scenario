"""The CLI contract: exit code, JSON shape, and a run over someone else's inventory."""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from e_shop_ltap.cli import build_service, main, run
from e_shop_ltap.models import Job, ScenarioReport, TransformKind
from e_shop_ltap.rules import SecondCopyRule
from e_shop_ltap.schema import DATA_DIR


def test_exit_code_is_zero_when_the_thesis_holds(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    assert "Retires 3 of 12" in capsys.readouterr().out


def test_json_output_is_machine_readable(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["governed"]["retired_count"] == 3
    assert payload["cost"]["net_monthly_saving_usd"] == 12_800
    assert payload["recommendation"]["level"] == "pilot"
    assert [r["retired_count"] for r in payload["naive_readings"]] == [12, 3]


def test_it_runs_over_your_own_inventory(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Copy the CSVs, drop the reconciliation job, and the count follows the data."""
    for csv_file in DATA_DIR.glob("*.csv"):
        (tmp_path / csv_file.name).write_text(csv_file.read_text(encoding="utf-8"), encoding="utf-8")

    jobs = tmp_path / "jobs.csv"
    kept = [line for line in jobs.read_text().splitlines() if not line.startswith("J03,")]
    jobs.write_text("\n".join(kept) + "\n", encoding="utf-8")

    assert main(["--data-dir", str(tmp_path)]) == 0
    assert "Retires 2 of 11" in capsys.readouterr().out


def test_a_fake_service_still_drives_the_exit_code(capsys: pytest.CaptureFixture[str]) -> None:
    """``run`` depends on the report shape, not on how the report was built."""

    real = build_service().build_report()
    nothing_retired = dataclasses.replace(
        real,
        governed=dataclasses.replace(real.governed, retired=()),
        comparisons=(),
    )

    class FrozenService:
        def build_report(self) -> ScenarioReport:
            return nothing_retired

    assert run(FrozenService(), as_json=True) == 1  # type: ignore[arg-type]
    assert json.loads(capsys.readouterr().out)["governed"]["retired_count"] == 0


def test_a_new_rule_is_a_new_class_not_an_edit() -> None:
    """Open/closed: the rule protocol is two members wide."""
    rule = SecondCopyRule()
    ingest = Job(
        job_id="JX",
        name="Partner returns feed",
        schedule="daily",
        source="sftp",
        target="delta_bronze",
        transform_kind=TransformKind.COPY,
        external_input=True,
        downstream=(),
    )
    assert rule.is_retired_by_ltap(ingest) is False

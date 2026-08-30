"""CLI and composition root — the only module that knows which concrete classes exist.

``e-shop-ltap`` prints the inventory three ways, the staleness paths, the sync-tier cost and
the decision the answers add up to. Exit code 0 only when the governed reading retires at
least one job and every naive reading disagrees with it — the article's claim, as a check.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .decision import FiveQuestionPolicy
from .inventory_service import ScenarioService
from .render import render_text, to_dict
from .repository import CsvInventoryRepository
from .rules import EndOfPipelinesRule, NameKeywordRule, SecondCopyRule


def build_service(data_dir: Path | None = None) -> ScenarioService:
    """Wire the concretes. Everything above this line depends on protocols only."""
    return ScenarioService(
        repository=CsvInventoryRepository(data_dir),
        governed_rule=SecondCopyRule(),
        naive_rules=(EndOfPipelinesRule(), NameKeywordRule()),
        policy=FiveQuestionPolicy(),
    )


def run(service: ScenarioService, *, as_json: bool = False) -> int:
    """Run the scenario and turn the result into an exit code."""
    report = service.build_report()
    print(json.dumps(to_dict(report), indent=2) if as_json else render_text(report))
    thesis_holds = report.governed.retired_count > 0 and report.every_naive_reading_is_wrong
    return 0 if thesis_holds else 1


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="e-shop-ltap",
        description="Count what LTAP actually retires from a pipeline inventory, three ways.",
        epilog="Point --data-dir at a copy of the CSVs to run the same rules over your own jobs.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="directory holding jobs.csv, latency_budget.csv, sync_cost.csv and "
        "decision_answers.csv (default: the packaged E-Shop scenario)",
    )
    parser.add_argument("--json", action="store_true", help="print the JSON report only")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    return run(build_service(args.data_dir), as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())

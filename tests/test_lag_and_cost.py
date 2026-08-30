"""The staleness budget and the money, both quoted in the article."""

from __future__ import annotations

import pytest

from e_shop_ltap.lag_model import speedup
from e_shop_ltap.models import ScenarioReport


def test_todays_path_is_eight_minutes_at_p95(report: ScenarioReport) -> None:
    today = report.latency_paths[0]
    assert today.p95_seconds == pytest.approx(480.0)
    assert today.p95_seconds / 60 == pytest.approx(8.0)


def test_the_merge_window_dominates_todays_lag(report: ScenarioReport) -> None:
    today = report.latency_paths[0]
    assert today.dominant_stage.p95_seconds == pytest.approx(300.0)


def test_ltap_paths_are_faster_but_not_zero(report: ScenarioReport) -> None:
    today, feature, analytical = report.latency_paths
    assert feature.p95_seconds == pytest.approx(0.2)
    assert analytical.p95_seconds == pytest.approx(15.1)
    assert speedup(today, feature) == pytest.approx(2400.0)
    assert speedup(today, analytical) == pytest.approx(31.8)
    assert min(feature.p95_seconds, analytical.p95_seconds) > 0


def test_speedup_does_not_divide_by_zero(report: ScenarioReport) -> None:
    today = report.latency_paths[0]
    empty = type(today)(name="nothing", stages=())
    assert speedup(today, empty) == 0.0


def test_sync_tier_costs_eighteen_thousand_a_month(report: ScenarioReport) -> None:
    assert report.cost.sync_tier_monthly == 18_000


def test_the_saving_is_net_of_what_replaces_it(report: ScenarioReport) -> None:
    assert report.cost.replacement_monthly == 5_200
    assert report.cost.net_monthly_saving == 12_800

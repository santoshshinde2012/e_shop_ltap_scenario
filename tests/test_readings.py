"""The article's central claim: 3 of 12, and which 3."""

from __future__ import annotations

from e_shop_ltap.inventory_service import ScenarioService
from e_shop_ltap.models import ScenarioReport
from e_shop_ltap.render import render_text
from e_shop_ltap.repository import CsvInventoryRepository
from e_shop_ltap.rules import SecondCopyRule

SYNC_TIER = {"J01", "J02", "J03"}


def test_second_copy_rule_retires_three_of_twelve(report: ScenarioReport) -> None:
    assert report.governed.total == 12
    assert report.governed.retired_count == 3
    assert len(report.governed.kept) == 9


def test_it_retires_the_sync_tier_and_nothing_else(report: ScenarioReport) -> None:
    assert set(report.governed.retired_ids) == SYNC_TIER


def test_headline_reading_retires_everything(report: ScenarioReport) -> None:
    headline = report.comparisons[0]
    assert headline.reading.retired_count == 12
    assert not headline.count_matches
    assert len(headline.wrongly_retired) == 9


def test_keyword_scan_gets_the_right_count_and_the_wrong_list(report: ScenarioReport) -> None:
    keyword = report.comparisons[1]
    assert keyword.reading.retired_count == 3
    assert keyword.count_matches
    assert not keyword.set_matches


def test_keyword_scan_deletes_a_silver_transform_and_keeps_the_reconciliation(
    report: ScenarioReport,
) -> None:
    keyword = report.comparisons[1]
    assert [j.job_id for j in keyword.wrongly_retired] == ["J07"]
    assert [j.job_id for j in keyword.wrongly_kept] == ["J03"]


def test_every_naive_reading_disagrees_with_the_governed_one(report: ScenarioReport) -> None:
    assert report.every_naive_reading_is_wrong


def test_a_reading_that_agrees_is_reported_as_agreeing() -> None:
    """Guard the happy branch: two readings of the same rule must not be called wrong."""
    service = ScenarioService(
        repository=CsvInventoryRepository(),
        governed_rule=SecondCopyRule(),
        naive_rules=(SecondCopyRule(),),
    )
    report = service.build_report()
    assert report.comparisons[0].agrees
    assert not report.every_naive_reading_is_wrong
    assert "agrees with the second-copy rule" in render_text(report)

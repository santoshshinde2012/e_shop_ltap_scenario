"""The five-question walk, including the readings the article does not print."""

from __future__ import annotations

from e_shop_ltap.decision import FiveQuestionPolicy
from e_shop_ltap.models import Answer, ScenarioReport


def answer(question_id: str, value: bool, evidence: str = "-") -> Answer:
    return Answer(question_id=question_id, question=question_id, answer=value, evidence=evidence)


def test_e_shop_lands_on_a_read_path_pilot(report: ScenarioReport) -> None:
    recommendation = report.recommendation
    assert recommendation.level == "pilot"
    assert any("read path only" in brake for brake in recommendation.brakes)
    assert any("governance" in item for item in recommendation.prerequisites)


def test_sync_jobs_alone_only_earn_watch() -> None:
    recommendation = FiveQuestionPolicy().recommend((answer("Q1", True), answer("Q2", False)))
    assert recommendation.level == "watch"
    assert recommendation.brakes == ()


def test_no_yes_anywhere_means_no_action() -> None:
    answers = tuple(answer(f"Q{n}", False) for n in range(1, 5))
    assert FiveQuestionPolicy().recommend(answers).level == "no action"


def test_the_brake_applies_without_lowering_the_level() -> None:
    recommendation = FiveQuestionPolicy().recommend((answer("Q2", True), answer("Q3", True)))
    assert recommendation.level == "pilot"
    assert len(recommendation.brakes) == 1

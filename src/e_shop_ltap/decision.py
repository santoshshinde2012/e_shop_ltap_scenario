"""The five-question walk, as a policy rather than a paragraph."""

from __future__ import annotations

from .models import Answer, Recommendation

# Question id -> (rung it earns, why). Q3 is the brake, Q4 is a precondition.
_RUNGS = {
    "Q1": ("watch", "sync-only jobs exist, so there is something for LTAP to retire"),
    "Q2": ("pilot", "a real use case is blocked by stale data"),
}
_LEVEL_ORDER = ("no action", "watch", "pilot")


class FiveQuestionPolicy:
    """Highest honest yes sets the level; Q3 caps the scope; Q4 adds a precondition."""

    def recommend(self, answers: tuple[Answer, ...]) -> Recommendation:
        said_yes = {a.question_id for a in answers if a.answer}
        evidence = {a.question_id: a.evidence for a in answers}

        level = "no action"
        reasons: list[str] = []
        for question_id, (rung, why) in _RUNGS.items():
            if question_id in said_yes:
                reasons.append(f"{why} ({evidence[question_id]})")
                if _LEVEL_ORDER.index(rung) > _LEVEL_ORDER.index(level):
                    level = rung

        brakes: list[str] = []
        if "Q3" in said_yes:
            brakes.append(f"read path only - {evidence['Q3']}")

        prerequisites: list[str] = []
        if "Q4" in said_yes:
            prerequisites.append(f"governance before wider access - {evidence['Q4']}")

        return Recommendation(
            level=level,
            reasons=tuple(reasons),
            brakes=tuple(brakes),
            prerequisites=tuple(prerequisites),
        )

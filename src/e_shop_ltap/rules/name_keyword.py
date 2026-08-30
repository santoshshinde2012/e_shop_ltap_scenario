"""The reading most teams reach for first: grep the job names."""

from __future__ import annotations

from ..models import Job
from ..schema import SYNC_NAME_KEYWORDS


class NameKeywordRule:
    """Matches sync-sounding words in the job name.

    Fast, defensible in a planning meeting, and wrong in both directions at once. It misses
    a reconciliation job that never says "sync", and it catches a Silver transform that
    happens to say "merge". On the E-Shop inventory it lands on the right *count*, which is
    what makes it dangerous.
    """

    label = "Name keyword scan (grep the schedule)"

    def __init__(self, keywords: tuple[str, ...] = SYNC_NAME_KEYWORDS) -> None:
        self._keywords = keywords

    def is_retired_by_ltap(self, job: Job) -> bool:
        name = job.name.lower()
        return any(keyword in name for keyword in self._keywords)

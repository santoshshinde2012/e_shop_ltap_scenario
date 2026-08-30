"""The governed reading: retire a job only if the second copy is its whole reason to exist."""

from __future__ import annotations

from ..models import Job


class SecondCopyRule:
    """Sync-only when a job neither brings in outside data nor changes what the data means.

    Both halves matter. A job that pulls a supplier feed brings in facts the lakehouse
    would not otherwise have, so shared storage cannot retire it. A job that dedupes
    orders or normalises currency changes meaning, so shared storage cannot retire that
    either. What is left copies rows between two stores, or proves the two stores still
    agree — and both of those disappear when there is one store.
    """

    label = "Second-copy rule (what the job does, not what it is called)"

    def is_retired_by_ltap(self, job: Job) -> bool:
        return not job.external_input and not job.transform_kind.changes_meaning

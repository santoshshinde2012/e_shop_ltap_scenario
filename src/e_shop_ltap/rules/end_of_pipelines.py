"""The keynote reading, taken literally."""

from __future__ import annotations

from ..models import Job


class EndOfPipelinesRule:
    """If pipelines have ended, every scheduled job goes.

    Nobody defends this in writing. Plenty of roadmaps are built on it.
    """

    label = 'Headline reading ("the end of pipelines")'

    def is_retired_by_ltap(self, job: Job) -> bool:
        return True

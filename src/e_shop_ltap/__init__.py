"""E-Shop — what LTAP actually retires from a pipeline inventory.

Twelve scheduled jobs at a fictional mid-market retailer, read three ways:

* the **second-copy rule** asks what each job does — a job that neither brings in outside
  data nor changes what the data means exists only because two stores cannot share
  storage. It retires **3 of 12**;
* the **headline reading** takes "the end of pipelines" literally and retires **12 of 12**;
* a **name keyword scan** greps the schedule and also retires 3 — the *wrong* 3. It drops a
  Silver transform that happens to say "merge" and keeps a reconciliation job that never
  says "sync". Right count, wrong list, which is the harder failure to notice.

The same run prints the staleness budget (8 minutes today, 0.2 s on the LTAP feature path,
15.1 s on the analytical one — not zero), the sync tier's monthly cost, and the commitment
level the five-question walk arrives at.

All E-Shop numbers are synthetic. Swap in your own with ``--data-dir``.
"""

from __future__ import annotations

from .models import (
    CostComparison,
    InventoryReading,
    Job,
    LatencyPath,
    ReadingComparison,
    Recommendation,
    ScenarioReport,
    TransformKind,
)

__version__ = "1.0.0"

__all__ = [
    "CostComparison",
    "InventoryReading",
    "Job",
    "LatencyPath",
    "ReadingComparison",
    "Recommendation",
    "ScenarioReport",
    "TransformKind",
    "__version__",
]

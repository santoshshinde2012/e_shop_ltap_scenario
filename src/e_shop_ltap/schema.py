"""Where the seed data lives and what the article's baseline claims are.

Change these and the tests fail, which is the point: the article quotes this file's run.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

DATA_DIR: Final = Path(__file__).parent / "data"

JOBS_CSV: Final = DATA_DIR / "jobs.csv"
LATENCY_CSV: Final = DATA_DIR / "latency_budget.csv"
COST_CSV: Final = DATA_DIR / "sync_cost.csv"
ANSWERS_CSV: Final = DATA_DIR / "decision_answers.csv"

# Keywords a name-matching scan would look for. Deliberately the list a reasonable
# engineer would write in ten seconds — which is why it gets the right count and the
# wrong jobs.
SYNC_NAME_KEYWORDS: Final = ("cdc", "debezium", "sync", "merge", "replicat", "mirror")

# Path names, kept in one place so the CSV, the renderer and the tests agree.
TWO_COPY_PATH: Final = "two_copy_cdc"
FEATURE_PATH: Final = "ltap_feature_path"
ANALYTICAL_PATH: Final = "ltap_analytical_path"

PATH_TITLES: Final = {
    TWO_COPY_PATH: "Today - Postgres commit to a fraud feature, through CDC",
    FEATURE_PATH: "LTAP - streaming feature to the Lakebase-backed online store",
    ANALYTICAL_PATH: "LTAP - Postgres commit to an analytical read on Delta",
}

# e_shop_ltap_scenario

[![CI](https://github.com/santoshshinde2012/e_shop_ltap_scenario/actions/workflows/ci.yml/badge.svg)](https://github.com/santoshshinde2012/e_shop_ltap_scenario/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Buy Me a Coffee](https://img.shields.io/badge/buymeacoffee-black?style=for-the-badge&logo=buymeacoffee&logoColor=white)](https://buymeacoffee.com/santoshshin)

**Count what LTAP actually retires from a pipeline inventory.** Companion code for *The Second Copy
Problem: What LTAP Actually Removes*.

Databricks announced LTAP under the banner "the end of pipelines". The interesting question is not
whether the architecture is real — it is *which of your scheduled jobs would actually stop running*.
This repo answers that for one worked scenario, three ways, and lets you point the same rules at
your own job list.

## The three readings

Twelve scheduled jobs at **E-Shop**, a fictional mid-market retailer with a Postgres order book and a
Delta lakehouse. Same list, three ways of reading it:

| Reading | Retires | Verdict |
|---|---:|---|
| **Second-copy rule** — what the job *does* | **3 of 12** | the sync tier, and nothing else |
| Headline reading — "the end of pipelines" | 12 of 12 | wrong count, by nine |
| Name keyword scan — grep the schedule | 3 of 12 | **right count, wrong list** |

The third row is the one worth sitting with. A keyword scan lands on the same number as the governed
rule, so it survives a planning meeting — but it retires `J07 Silver: returns and refunds merge`
because the name says "merge", and it keeps `J03 Nightly reconciliation` because the name never says
"sync". You would delete a business transform and keep a job whose only purpose is proving that two
copies still match.

The governed rule asks two questions of each job instead: does it bring in data from outside, and
does it change what the data means? A job that does neither exists only because two stores cannot
share storage. That is the definition LTAP is aimed at.

## Quick start

```bash
git clone https://github.com/santoshshinde2012/e_shop_ltap_scenario.git
cd e_shop_ltap_scenario
./run_demo.sh
```

That creates a venv, installs the package, runs the tests, and prints the report. No runtime
dependencies beyond the standard library.

Already have a venv?

```bash
pip install -e ".[dev]" && e-shop-ltap
```

## Expected output

Pasted from a real run, and checked in CI against `docs/sample_output.txt`:

```
=== E-Shop — what LTAP actually retires ===

Second-copy rule (what the job does, not what it is called)
  Retires 3 of 12:
    J01  Debezium CDC connector (Postgres -> Kafka)
    J02  Spark merge into gold.orders
    J03  Nightly reconciliation of row counts and sums
  Keeps 9 — ingestion, transforms, quality tests, features, reporting.

Headline reading ("the end of pipelines")
  Retires 12 of 12 — wrong count.
    would retire  J04  Supplier catalogue feed ingest
    would retire  J05  Carrier tracking feed ingest
    would retire  J06  Silver: order dedupe and currency normalisation
    ... and 6 more that keep the data trustworthy

Name keyword scan (grep the schedule)
  Retires 3 of 12 — right count, wrong list.
    would retire  J07  Silver: returns and refunds merge
    would keep    J03  Nightly reconciliation of row counts and sums
```

The run continues with the staleness budget, the sync-tier cost and the decision. Full text:
[`docs/sample_output.txt`](docs/sample_output.txt).

Exit code is `0` only when the governed rule retires something **and** every other reading disagrees
with it. If a change ever makes the naive readings correct, the demo fails.

## What else the run prints

**Staleness, committed write to the read that acts on it (p95).** Today's CDC path is 480 s — eight
minutes, and 300 of those seconds are just waiting for the next merge window. The LTAP feature path
is 0.2 s. The LTAP analytical path is 15.1 s, because a managed change data feed still flushes on an
interval. Neither is zero, and that is the honest headline: the sync did not vanish, it moved into
the storage layer where you no longer operate it — and no longer see it.

**Sync tier, monthly.** $18,000 across four line items. Net $12,800 once you subtract what replaces
it. A cost saving that ignores the replacement is not a cost saving.

**Decision.** The five-question walk: `pilot`, braked to the read path because checkout moves money,
with governance as a precondition because agents read these tables.

## Run it on your own inventory

```bash
mkdir my-platform && cp src/e_shop_ltap/data/*.csv my-platform/
# edit my-platform/jobs.csv — one row per scheduled job
e-shop-ltap --data-dir my-platform
e-shop-ltap --data-dir my-platform --json | jq '.governed.retired_count'
```

`jobs.csv` describes each job by what it observably does, which is the whole trick:

| Column | Meaning |
|---|---|
| `transform_kind` | `copy`, `compare`, `derive`, `aggregate` or `validate` — `copy` and `compare` change nothing about meaning |
| `external_input` | `true` when the job brings in data the lakehouse would not otherwise have |
| `source`, `target` | which stores it moves data between |
| `downstream` | semicolon-separated job ids that depend on it |

Nothing in the rule reads the job's *name*. That is deliberate.

## Layout

| Path | Purpose |
|---|---|
| `src/e_shop_ltap/data/*.csv` | The E-Shop scenario — jobs, latency stages, cost lines, the five answers. Synthetic. |
| `src/e_shop_ltap/models.py` | Frozen dataclasses. Every number the article quotes is reported through one. |
| `src/e_shop_ltap/protocols.py` | `RetirementRule`, `InventoryRepository`, `DecisionPolicy` — the only types orchestration knows |
| `src/e_shop_ltap/repository.py` | The one module that reads files |
| `src/e_shop_ltap/rules/second_copy.py` | The governed rule: no outside data, no change in meaning |
| `src/e_shop_ltap/rules/name_keyword.py` | The keyword scan, and why it is dangerous rather than merely wrong |
| `src/e_shop_ltap/rules/end_of_pipelines.py` | The headline, taken literally |
| `src/e_shop_ltap/lag_model.py` | Stages into end-to-end paths; the speed-up arithmetic |
| `src/e_shop_ltap/decision.py` | The five-question walk as a policy |
| `src/e_shop_ltap/inventory_service.py` | Orchestration only |
| `src/e_shop_ltap/render.py` | Text and JSON |
| `src/e_shop_ltap/cli.py` | Composition root — the only place concretes are wired |
| `tests/` | 22 tests locking the article's numbers |
| `docs/architecture.md` | How the pieces fit, and why the rule is shaped this way |

Adding a fourth reading is a new class in `rules/` plus one line in `build_service()`.

## Development

```bash
make setup     # venv + dev extras
make check     # ruff, mypy --strict, pytest with a 90% coverage floor
make sample    # refresh docs/sample_output.txt after an intentional change
```

CI runs the same checks on Python 3.11 through 3.14, builds the wheel, installs it clean, and
diffs the committed sample output against a real run.

## About the numbers

Every E-Shop figure is **synthetic** — a placeholder for a measurement you take on your own
platform. The vendor-reported latencies the model uses (a sub-second streaming feature path, a
change data feed that flushes on an interval) are hypotheses until you benchmark them on your own
mix. The point of the code is the *method*, not the numbers.

## Licence

MIT — see [LICENSE](LICENSE).

# How this fits together

The demo answers one question — *which of these jobs would actually stop running?* — and it answers
it three ways so the comparison is visible rather than asserted.

## The flow

```
data/*.csv
   │
   ▼
CsvInventoryRepository        the only module that touches the filesystem
   │  Job, LatencyStage, CostLine, Answer   (frozen dataclasses)
   ▼
ScenarioService               orchestration only — knows protocols, not classes
   ├── SecondCopyRule         the governed reading
   ├── EndOfPipelinesRule ┐   the two naive readings, held against the governed one
   ├── NameKeywordRule    ┘
   ├── build_paths()          latency stages → end-to-end paths
   └── FiveQuestionPolicy     the answers → a commitment level
   │
   ▼  ScenarioReport
render_text() / to_dict()     two shapes of the same report
   │
   ▼
cli.run()                     prints it, returns the exit code
```

`cli.build_service()` is the composition root. It is the only function in the package that names a
concrete class; everything above it takes a protocol.

## Why the rule is shaped this way

The tempting definition of a sync-only job is "it has CDC in the name". The honest one is a property
of the data flow:

> A job exists only because two stores cannot share storage **if** it brings in no data from outside
> and changes nothing about what the data means.

Both halves are load-bearing.

- Drop the first half and every ingestion job looks retirable — a supplier feed does not transform
  anything, but the lakehouse would simply not have that data without it.
- Drop the second half and every transform looks retirable — a currency normalisation reads and
  writes the same lakehouse, but the rows that come out mean something different from the rows that
  went in.

What survives both filters is genuinely narrow: connectors, merges, and reconciliation jobs. That is
the sync tier, and it is exactly what one shared copy of the data removes.

`TransformKind.changes_meaning` encodes the second half. `copy` and `compare` return `False`;
`derive`, `aggregate` and `validate` return `True`. A validation job is worth a word here: it emits
no new rows, but it produces a judgement about them that nothing else in the platform produces, so
shared storage does not retire it.

## Why the keyword scan is in the repo

It would be easy to include only the governed rule and claim it is better. The keyword scan is here
because it fails in the way real reviews fail: it produces the **right count** on this inventory. A
team that only compares totals would sign off on a plan that deletes a Silver transform and keeps a
reconciliation job.

`ReadingComparison` therefore reports `count_matches` and `set_matches` separately, and the renderer
says "right count, wrong list" when they disagree. The distinction is the point.

## Why the latency model has three paths, not two

The simple story is "eight minutes becomes nothing". The model refuses to tell it. There are two
different LTAP paths and they behave differently:

- the **feature path** — a streaming feature into a Lakebase-backed online store — is sub-second;
- the **analytical path** — a Postgres commit becoming readable on Delta — waits for a managed change
  data feed to flush, which happens on an interval measured in seconds, not milliseconds.

Modelling them as one number would hide the thing worth knowing: the interval did not disappear, it
changed owner. `LatencyPath.dominant_stage` exists so the report always says which stage is actually
costing you the time — today that is the five-minute merge window, and after a migration it is
someone else's flush.

## Extending it

- **A fourth reading**: a class in `rules/` with `label` and `is_retired_by_ltap`, plus one line in
  `build_service()`.
- **A different decision walk**: anything that satisfies `DecisionPolicy` can be passed into
  `ScenarioService`.
- **A real inventory**: implement `InventoryRepository` against your scheduler's API instead of CSVs.
  Nothing above the repository changes.

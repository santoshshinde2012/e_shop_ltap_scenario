# Contributing

Issues and pull requests are welcome. This is a small demo repo attached to an article, so the bar
is less about scale and more about the numbers staying honest.

## Before you open a PR

```bash
make setup
make check
```

`make check` runs ruff (lint + format), `mypy --strict`, and pytest with a 90% coverage floor —
the same thing CI runs.

## The rules of the house

- **A new reading of the inventory is a new class**, not an edit to `ScenarioService`. Drop a file in
  `src/e_shop_ltap/rules/`, give it a `label` and an `is_retired_by_ltap`, and add one line to
  `build_service()`.
- **Orchestration depends on protocols.** If `inventory_service.py` or `cli.run()` needs to import a
  concrete class, something is in the wrong place.
- **Value objects are frozen dataclasses.** Nothing in the report should be mutable after it is built.
- **Tests lock the scenario's numbers**, not internals. If you change the data or a rule, update the
  tests *and* run `make sample` so `docs/sample_output.txt` matches a real run — CI diffs them.
- Keep docstrings to one line where one line will do, and make it say *why*.

## Changing the scenario

The E-Shop numbers are synthetic and deliberately load-bearing: the article quotes them. If you want
to model a different platform, do it with `--data-dir` rather than by editing
`src/e_shop_ltap/data/`. New scenarios are welcome as fixtures under `tests/`.

## Reporting something

Use the issue templates. If it is a security concern, see [SECURITY.md](SECURITY.md) instead.

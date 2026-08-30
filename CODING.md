# Coding standards for this repo

Follows [`voice/coding-standards.md`](https://github.com/santoshshinde2012/blogs/blob/main/voice/coding-standards.md)
in the writing workspace this demo was built for. This file travels with the code, so the link is
absolute — it resolves both here and in the standalone repo.

- **S** one job per module — `repository.py` (read the CSVs), one rule per file under `rules/`,
  `lag_model.py` (staleness paths), `decision.py` (the five-question walk),
  `inventory_service.py` (orchestration only), `render.py` (output), `cli.py` (entry point)
- **O** a fourth reading of the inventory is a new class in `rules/` plus one line in
  `build_service()`; `ScenarioService` does not change
- **L** every rule honours `RetirementRule` (`label` + `is_retired_by_ltap`); the tests pass a
  frozen fake service into `run()` and the exit code still works
- **I** the protocols are one to four members wide — `RetirementRule` is two
- **D** `inventory_service.py` and `cli.run()` depend on `protocols.py`; concretes are wired in
  `build_service()` and nowhere else
- `from __future__ import annotations`, type hints everywhere, `@dataclass(frozen=True)` for value
  objects, relative imports inside the package, no secrets, one-line docstrings that say *why*
- Tests lock the article's numbers — 3 of 12, the `{J01, J02, J03}` set, 480 s / 0.2 s / 15.1 s,
  $18,000 and $12,800, the `pilot` level — not internals. "Expected output" in the README is
  pasted from a real run.

Before publish: `./run_demo.sh` must pass. That is what `scripts/verify_practical.sh` runs.

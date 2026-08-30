# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[semantic versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-08-30

First public release, alongside *The Second Copy Problem: What LTAP Actually Removes*.

### Added

- `e-shop-ltap` CLI: reads a pipeline inventory three ways and prints the report (`--json` for the
  machine-readable form, `--data-dir` to run the rules over your own job list).
- `SecondCopyRule` — retires a job only when it neither brings in outside data nor changes what the
  data means.
- `NameKeywordRule` and `EndOfPipelinesRule` — the two readings that get it wrong, kept so the demo
  can show *how* they get it wrong rather than assert that they do.
- Staleness model: stages composed into end-to-end paths, with the speed-up arithmetic between them.
- Sync-tier cost model, net of what replaces the tier.
- `FiveQuestionPolicy` — the article's decision walk, with brakes and preconditions.
- 22 tests locking every number the article quotes; CI on Python 3.11-3.14 with ruff,
  `mypy --strict`, a 90% coverage floor, a clean-wheel install check, and a diff of
  `docs/sample_output.txt` against a real run.

[1.0.0]: https://github.com/santoshshinde2012/e_shop_ltap_scenario/releases/tag/v1.0.0

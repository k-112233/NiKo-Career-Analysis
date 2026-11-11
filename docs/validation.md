# v1.0.0 validation

## Checked locally

- Isolated environment installation from the package index, separate from the original project environment.
- 12 Python checks covering metric definitions, missingness, invalid input, mixed rating suppression, map-vs-series filtering, player identity, duplicate joins, conflicting observations and near-date duplicates.
- Node execution of the actual generated dashboard script, including game/team filters and empty states.
- Headless Microsoft Edge: desktop 1440×1100, mobile 390×844, real CSV download (195 G2 CS2 rows), ADR, missing Rating, mixed-rating guard, report image loading and the root entry redirect.
- Three trusted project notebooks executed; their saved outputs are included for GitHub rendering.
- Release file hashes and exclusions, extracted clean offline report rebuild, Python/Node checks, notebook execution and unchanged canonical input hash.

The local Python is 3.11.9 and Node is 24.16.0. Runtime dependencies are frozen in requirements.lock. The CI workflow defines Python 3.11/3.12 checks with Node 22; **remote GitHub Actions have not run before upload**.

## Re-run

```bash
python -m tools.build_portfolio
python -m unittest discover -s checks -v
node checks/dashboard.cjs
python -m tools.execute_notebooks --check
python -m tools.build_release
python -m tools.verify_release
```

Optional real-browser checks require Playwright and a local browser; they are not part of the minimal runtime install:

```bash
python -m pip install playwright
python checks/browser_smoke.py --channel msedge
```

The browser check writes desktop/mobile previews under docs/images. To use Playwright-managed Chromium instead, install it using `python -m playwright install chromium` and run with `--channel chromium`.

The source ZIP uses an explicit allowlist and excludes old crawler placeholders, database-mutating experiments, raw archives, virtual environments and generated databases. RELEASE_MANIFEST.json contains per-file hashes. The adjacent .zip.sha256 checks the downloaded ZIP; tools.verify_release independently verifies both and rebuilds in a temporary directory.

## v1 acceptance scope

v1 is an observational portfolio release on a documented fixed snapshot. Sparse career periods, date ambiguities, non-random excerpts and unverified legacy Rating methodology remain documented data limitations. No missing statistics are invented. These limits bound the research claims and do not prevent reproducing the delivered analyses.

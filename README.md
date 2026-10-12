# The Mundhe Effect

A free, independent public-record directory for Maharashtra food businesses. Not affiliated with Tukaram Mundhe, Maharashtra FDA, FSSAI or any government agency.

## Consolidated expansion — 12 October 2026

- **692 directory entries**, preserving all 43 existing records and their original event fields.
- **640 new licence-linked FSSAI entries** with **659 historical favourable audit records**, verified against the official published register. Repeat audits remain separate timeline events.
- **9 new media-supported entries** recording reinstatements or stays alongside preceding actions/inspections.
- Official favourable records cover **32 named districts plus unspecified Mumbai jurisdictions**. Other media entries also cover Mumbai City. Coverage remains partial; Dharashiv, Gadchiroli and Solapur have no included records.
- Browsing now supports district/region, source, event type, licence-number search, and pagination. Each detail view states that current licensing is unverified.

The official audit records are from **2018–2021**, not current clearances. Counts are directory entries, not a guaranteed number of unique physical premises. Do not combine same-name outlets across sources without reliable identity evidence.

Read [methodology](docs/methodology.md), [district coverage](docs/coverage.md), and [validation report](docs/update-2026-10-12.md).

## Free local preview

Use Python 3.11 or later (CI uses 3.12):

```sh
python3 -m http.server 8000
```

Open http://localhost:8000. The static site needs HTTP to load JSON. There is no package install, database, login, paid service or API key.

## Daily pipeline

`.github/workflows/daily-scan.yml` runs around **08:47 IST** on the default branch, and can be run manually from Actions. GitHub schedules can be delayed or disabled after repository inactivity.

It runs 40 public RSS searches (36 district queries plus statewide/Marathi/follow-up searches) and monitors three official listings. Source changes prompt review; they do not automatically change the public directory. New news leads store generic titles and source links instead of unverified headline allegations. Existing queue records and decisions are retained. The website does not consume the review queue.

`data/source_monitor.json` records attempts, successful checks, source changes and failures. `review_required` stays true until a reviewer clears it after checking the source. The workflow summary provides totals. Partial or complete source failures visibly fail the job after preserving successful discovery metadata. No logs print raw headline allegations.

The job has a time limit, source retries, response-size limits, atomic file writes, semantic source fingerprints and a concurrency lock. It stages only `data/review_candidates.json` and `data/source_monitor.json`, verifies the reviewed directory was untouched, and rebases before pushing without force. Branch protection can prevent bot commits; if that occurs, the run fails visibly rather than bypassing it.

Standard Ubuntu runners are free for public repositories under [GitHub's current billing rules](https://docs.github.com/en/billing/concepts/product-billing/github-actions). The daily job refuses private repositories. There are no artifact uploads, caches, paid runners or third-party subscriptions. Existing static hosting is unchanged; no paid plan should be activated.

## Review and apply records

Each published event requires a dated source and exact business/outlet identity. Prefer official documents. Label media events as reported. Check for later reinstatement, revocation or stay, and retain the earlier event. A reopening or stay alone does not establish a satisfactory hygiene audit.

The recorded statuses `positive`, `historical`, `suspension`, and `unknown` describe dated evidence. Current licence status is separately **unknown** throughout this dataset. Never infer that absence of records proves safety, wrongdoing or that an inspection never occurred. Unspecified addresses and blank cities are intentional when sources do not provide them.

To reproduce the reviewed FSSAI import from the checked-in snapshot:

```sh
python3 scripts/import_fssai.py --snapshot data/sources/fssai-2026-10-12.json
# Preview above; apply only after source and identity review:
python3 scripts/import_fssai.py --snapshot data/sources/fssai-2026-10-12.json --apply
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

This import is idempotent and preserves an existing record's status/history. It never downloads or publishes fresh source data on its own. Source layout changes and inconsistent scores fail closed or exclude the row. The snapshot records exact source columns and the upstream download hash. See the methodology for the conservative favourable-record inclusion criteria.

New imports from other snapshots require updating the snapshot provenance and validator deliberately; daily collection never runs the importer.

`validate.yml` checks pull requests and pushes to main. Structural validation cannot determine whether an article is true or a licence is currently valid; source review remains necessary.

## Corrections and publishing

Use [repository issues](https://github.com/ishaandirect-wq/the-mundhe-effect/issues/new) for sourced corrections. The original placeholder email has been removed. Include only public evidence, the exact outlet and the entry ID.

Merge the consolidated pull request to apply the update. The existing connected static hosting deployment should then pick up main; no hosting configuration or paid service is introduced. This repository does not yet contain exhaustive official FDA inspection/clearance data. Full coverage depends on further publicly available source material and continued review.

Bulk official entries are stored in 13 files under `data/establishments/`, with up to 50 licence-linked records per file. `data/establishments.json` retains the original entries and lists the additional files. The website and offline validator load every part before displaying or validating the complete directory. This keeps the bulk update reviewable through GitHub tooling; all 692 entries and all source evidence are retained.

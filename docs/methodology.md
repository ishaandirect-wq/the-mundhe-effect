# Sources, coverage and interpretation

Prepared 12 October 2026. This directory contains public-record entries, not a complete Maharashtra food-business registry or a current licensing database.

## What was added

640 licence-linked entries with 659 historical favourable FSSAI Hygiene Rating Scheme records. Source: [FSSAI's public audit register](https://hygiene.fssai.gov.in/adminAuditListFbo.php). Each event links to its individual audit-detail page. The local snapshot retains all 699 Maharashtra rows, exact source jurisdiction labels, names, licence numbers, scores, dates and audit IDs. Its metadata records retrieval time and the SHA-256 of the original download. The original HTML is not redistributed.

Only rows with a 14-digit licence identifier, parseable date, published rating 5 and percentage at least 80 were included as favourable entries. Scores must agree with the published percentage within one percentage point. These conservative import criteria do not redefine FSSAI's scheme. Excluded rows are not adverse findings. This subset contains records from 2018–2021; it is not a current audit feed.

The source calls its date columns **Valid From** and **Valid upto**, often showing the same date in both. We retain both verbatim and show the first as a **register valid-from date**, without inferring current certificate validity or expiry. Six individual audit pages across different regions were spot-checked for matching licence and date; all 659 imported events were checked against the downloaded register. This is verification against published source data, not an independent on-site inspection.

Nine additional news-supported entries cover reported licence restoration or stays for Parsi Dairy Farm, Pind Punjab, K Rustom, Noor Mohammadi, Shalimar and four Nagpur businesses. Inspection dates are not silently relabelled as suspension-order dates. A stay, revocation, reinstatement and satisfactory hygiene audit are different outcomes. Original court orders and the original Nagpur RTI reply were not obtained; those events remain explicitly **reported**, with their source links.

## Identity and geography

A licence number is the deduplication key within the FSSAI subset. Repeated audits are retained as separate events. Legal operator names are reproduced as published, including spelling variants. No status is transferred to another branch. Same-name media records and FSSAI entries are not merged without a reliable outlet identity match; the total is a count of directory entries, not a guaranteed count of unique physical premises.

The register supplies a regulatory jurisdiction, not a street address or dependable city. Blank cities and unknown addresses are intentional. Source jurisdictions remain available alongside normalized district names. Greater Mumbai and Mumbai are not arbitrarily assigned to Mumbai City or Mumbai Suburban. Legacy “Thane Zone” labels are retained; the Vasai jurisdiction is grouped under Palghar for browsing. Older district names remain searchable in source jurisdictions.

See [district coverage](coverage.md). Gadchiroli, Solapur and Dharashiv currently have no included records. This is an evidence gap, not evidence that businesses in those districts were never inspected. Daily discovery queries include all 36 districts.

## Preservation and current status

All 43 original entries and every original event field were retained. Legacy source-check limitations are labelled. The prior `last_reviewed` value remains unchanged; `last_expanded`, record-level review dates and event-level checks describe this update without claiming a fresh verification of every legacy event.

Every entry's **current licence status is unverified**. A favourable dated record may coexist with later enforcement evidence. Nothing here certifies present safety, approval, licence validity or illegality.

## Daily discovery and review

The scheduled workflow runs around 08:47 IST, subject to GitHub delays. It uses Python's standard library, public sources and the repository's built-in workflow token. No API keys, paid search, AI service, database, subscription or paid runner is needed.

The scanner searches 36 district queries plus four statewide/Marathi/follow-up queries. It monitors the FSSAI register, Maharashtra FDA press-release listing and general announcements. The FDA monitor fingerprints the main content and government-hosted document links, including its official document CDN; menus and clocks are excluded. It monitors these listings, not every document on the government website, and cannot establish exhaustive statewide coverage.

New news candidates contain a source link, publisher and date, with the generic title “Unreviewed source link”. Raw allegations in headlines are not added. Previously existing queue entries and review decisions are preserved. The website never reads the review queue. Source health records distinguish attempted checks, successful checks, content changes and errors. A changed page is a review prompt, not an enforcement conclusion. Set `review_required` to false only after checking the source; it stays true until reviewed or a new change is found.

Retries, response-size limits, atomic writes and schema guards protect against malformed or unavailable sources. All RSS failures leave the queue intact. Partial failures save successful discoveries but fail the workflow visibly. The workflow stages only discovery links and monitor metadata; it verifies the reviewed directory and snapshots stayed unchanged. Concurrent runs are serialized; pushes rebase onto newer work and never force-push.

A reviewer must read original evidence, confirm outlet identity, check for later restoration/stay/revocation and retain the full history before applying a directory change. This review cannot responsibly be replaced by automatic headline publication.

## Corrections and costs

[Request a sourced correction](https://github.com/ishaandirect-wq/the-mundhe-effect/issues/new). Include the specific entry, outlet and supporting document. Avoid private personal information. The placeholder email has been replaced by this repository's issue link.

The daily job runs only for a public repository on standard Ubuntu runners. GitHub currently provides these runner minutes free for public repositories. No workflow artifacts or caches are uploaded. Existing static hosting is unchanged; do not enable paid services. GitHub may delay scheduled jobs or disable inactive schedules, so absence of a run is not a successful check.

Bulk official entries are stored in 13 files under `data/establishments/`, with up to 50 licence-linked records per file. `data/establishments.json` retains the original entries and lists the additional files. The website and offline validator load every part before displaying or validating the complete directory. This keeps the bulk update reviewable through GitHub tooling; all 692 entries and all source evidence are retained.

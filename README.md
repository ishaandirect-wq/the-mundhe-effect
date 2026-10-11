# The Mundhe Effect

A friendly, completely free, independent public-record directory for food businesses across Maharashtra. **Not affiliated with Maharashtra FDA or FSSAI.**

This is a static website with no paid services or external API keys. Initial data is deliberately small; the objective is to expand coverage responsibly, not to invent clearance records.

## Quick local preview

From the project folder:

```bash
python3 -m http.server 8000
```

Open http://localhost:8000. Do not open index.html directly from the filesystem because the browser loads JSON via fetch.

## Deploy for free (easiest path)

1. Create a new **public** GitHub repository and upload all files in this directory, including `.github/workflows/daily-scan.yml` (some drag-and-drop uploads omit hidden folders; check this).
2. Open [Cloudflare Pages](https://dash.cloudflare.com/) and choose **Workers & Pages → Create → Pages → Connect to Git**. Authorize your repository.
3. Select the repository, choose **no framework**, leave build command blank, and set output directory to `/` (or follow the Pages dashboard's current static-site instructions).
4. Deploy. Use your free `*.pages.dev` URL. A custom domain is not needed.
5. In GitHub, open **Actions → Daily public food-safety news scan → Run workflow** for the first test. The schedule is approximately 08:47 IST daily; GitHub scheduled workflows can be delayed.
6. Open `data/review_candidates.json` in GitHub after a run to see new leads. Review original sources before adding or changing any entries in `data/establishments.json`.

**Note:** The `review_candidates.json` file is publicly viewable in the repository and is a lead list, not a set of verified allegations. It is not used by the website. The scraper can encounter access restrictions or incomplete RSS coverage and is not an authoritative source of comprehensive regulatory actions.

## Adding a directory record

Edit `data/establishments.json` and append an establishment object with a unique `id`, `name`, `address`, `city`, `district`, `category`, `status`, `note`, and an `events` list. Each event needs a `date`, `title`, `description`, and credible `source` URL. Status values: `positive`, `historical`, `suspension`, `unknown`.

- Use **positive** only for a documented favourable inspection / audit result, and name the specific scheme and date.
- Use **historical** when there is an old enforcement event even if resolved (unless a favourable reinspection clearly supports a positive *display status*, while the historical event remains in the timeline).
- Use **suspension** for a documented licence suspension, but do *not* claim it is currently suspended without sufficiently recent official verification.
- Use **unknown** only for neutral, deliberately researched establishments, never as evidence of inspection or approval.
- Never copy action status from one outlet to all branches of a chain.
- Prioritize authoritative government documents; accurately label newspaper accounts as reported.
- Update the top-level `last_reviewed` date only after reviewing published records.

The UI has no login or admin backend. Edits to the reviewed JSON dataset are the approval mechanism. This keeps the site free, safe and simple.

## Corrections and contact

Replace `corrections@example.com` in `index.html` with a public contact email **before launch**, or remove that link if no email inbox is available. Treat business corrections respectfully, retain the original event history, and link to official reinstatement documents where available.

## Known limits

- The site does not yet contain a complete statewide registry. The daily scan finds **news leads**, not all inspections or clearances.
- Google News RSS can change availability and is not a comprehensive substitute for primary FDA records.
- There is no paid AI, no automated regulatory judgement, no CAPTCHA bypass, and no claim that a business is definitively safe or unsafe.
- Cloudflare/GitHub free tiers and their fair-use restrictions apply. Usage beyond their free allowances may require restructuring; do not activate a paid plan.
- For exhaustive official inspection records, a formal Maharashtra FDA data request or RTI may be necessary and may not be free.

## Next expansion (still free)

Add official FDA published-document monitoring, more Marathi-language RSS sources, CSV bulk import with outlet-level matching, and a lightweight browser-based review workflow after the initial launch is validated.

## Independent project name

The Mundhe Effect is an independent public-information project. It is not affiliated with or endorsed by Tukaram Mundhe, Maharashtra FDA, FSSAI, or any government agency. The name is a reference to the public conversation about food-safety enforcement, not an official designation.

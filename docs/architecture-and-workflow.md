# Windward — architecture and workflow explained

## The whole system in one sentence

Windward downloads a fixed set of Elexon forecasts and actuals ahead of time, then lets a React dashboard ask a Python API which forecasts were available at a historical buying cutoff and how those forecasts compared with actual delivery.

There are two separate activities: **offline data preparation** and **interactive analysis**. Opening the dashboard does not trigger a new Elexon download.

## 1. Source data: what comes in

We use only Elexon's public WINDFOR and FUELHH streams.

- **WINDFOR:** expected wind power for a target time, with the timestamp when that forecast was published. The snapshot contains 18,688 records, including multiple revisions for many target hours.
- **FUELHH:** actual generation, filtered to `fuelType = WIND`. There are 1,488 half-hour actual records covering delivery 2 January–1 February.

`startTime` answers **“When will the electricity be delivered?”** `publishTime` answers **“When did this forecast or actual observation become available?”** Confusing these timestamps would invalidate a historical replay.

The date scope is January 1–31 **buying decisions**, so delivery falls January 2–February 1. We fetch forecast publications from December 31 as a lookback for the first decision.

## 2. Offline ingestion: preparing the evidence

File: `scripts/ingest.py`.

The developer runs this script manually. It requests both datasets, retries failed downloads, checks required fields and numeric generation values, checks timezone-aware timestamps, filters actuals to WIND, sorts the records, and writes compressed JSON snapshots.

The output is:

- `data/windfor.json.gz`
- `data/fuelhh.json.gz`
- `data/manifest.json`

The manifest records exact API URLs, download time, record counts, and hashes of the normalized uncompressed content. It makes the analysis reproducible and auditable.

These are **files**, not a database. There is no scheduled refresh service in this version. After refreshing files, restart or redeploy the API so its in-memory indexes use the new snapshot. Both responses are validated before file replacement begins; the three-file snapshot is not a database transaction and should not be refreshed during live serving.

## 3. Python analysis: the domain rules

File: `backend/analysis.py`.

This layer contains pure functions: inputs go in, results come out, without browser or network dependencies. That makes the rules easy to test independently.

### Index the versions

On first use, records are indexed by target timestamp and publication timestamp. Identical duplicates collapse; conflicting values at the same target/publication are rejected. Actuals are filtered to WIND again as a defensive check.

### Reconstruct a decision

Suppose the buyer selects **15 January at 09:00 Europe/London**:

1. Construct the timezone-aware decision cutoff. January London time is GMT, or UTC+0.
2. Generate the 24 delivery hours for January 16.
3. For each delivery hour, find forecasts whose publication timestamp is at or before January 15, 09:00.
4. Select the most recently published eligible forecast.
5. Retain its publication time, age at decision time, and lead time to delivery.

An update published at 09:30 is excluded from the 09:00 decision. A publication exactly at 09:00 is eligible. The app uses publication time as a proxy for availability; real ingestion latency is not reconstructed.

### Align forecast and actual resolution

Every WINDFOR target timestamp in this downloaded January snapshot is on the hour. FUELHH actuals arrive half-hourly. We therefore average the two actual half-hours to obtain comparable hourly mean power:

```text
hourly actual MW = (actual at HH:00 + actual at HH:30) / 2
```

For example, actuals of 6,000 MW and 8,000 MW produce an hourly actual of 7,000 MW. A forecast of 8,000 MW then has a positive error of 1,000 MW and one hour of shortfall exposure of 1,000 MWh.

Both half-hours must exist. If either is missing, that hour's actual and error remain missing. Zero is a valid measurement and is not treated as missing. No forecast interpolation is performed.

### Calculate metrics

```text
error = forecast − actual
MAE = mean(|error|)
RMSE = sqrt(mean(error²))
bias = mean(error)
wind shortfall energy = sum(max(error, 0) × 1 hour)
coverage = matched hourly pairs / expected hours
```

MAE measures typical error size. RMSE emphasizes large errors. Bias shows direction. Positive error means wind was overestimated. All accuracy metrics use matched pairs only; missing data never becomes a zero error.

Power is measured in MW; the interface commonly displays GW, dividing by 1,000. Energy is power multiplied by duration. Summing 24 hourly mean forecast powers times one hour gives daily MWh, displayed as GWh after dividing by 1,000.

## 4. Historical context versus retrospective results

This distinction is central to the product.

**Decision context:** use earlier January buying decisions only. When examining those earlier decisions' actuals, select only actual versions published by the current decision cutoff. Already-published hours from an ongoing delivery day can contribute; future hours and later revisions cannot. The first January buying decision has no earlier January history.

For January 15 at 09:00, this produces 321 matched prior hours, a prior MAE of about 2.06 GW, and a prior P90 shortfall of about 4.32 GW. The P90 is the nearest-rank 90th percentile of `max(error, 0)`, including zero-shortfall hours. It is descriptive sample history, not a guaranteed future bound.

**Retrospective review:** use the latest actual versions present in the fixed snapshot. This powers Reveal actuals and the performance page. Full-month performance is never fed back into an earlier decision as if it had been known then.

## 5. FastAPI: the interface between analysis and UI

File: `backend/main.py`.

The API validates user parameters, calls the analysis functions, and returns JSON or CSV:

- `/api/meta`: dates, defaults, source manifest.
- `/api/decision`: selected next-day profile, retrospective actuals, daily metrics, and time-safe prior-history metrics.
- `/api/performance`: range-wide metrics, daily summaries, error by delivery hour, and largest shortfalls.
- `/api/export`: an auditable CSV using the selected decision dates and cutoff.
- `/api/health`: readiness check for the bundled snapshot.
- `/api/docs`: interactive API documentation.

Invalid dates, malformed cutoffs, and reversed date ranges return HTTP 422. The snapshot indexes and selected-day results are cached inside each Python process. On Vercel, a cold function instance loads its own copy; this is not a shared or permanently persistent cache.

## 6. React: what happens when someone uses the portal

File: `src/main.tsx`; styling: `src/styles.css`.

React owns the current view, dates, cutoff, loading/error state, and visibility toggles using component state. TypeScript describes the expected API response shapes. Vite builds the frontend; Recharts renders the charts.

On initial load, the frontend requests metadata and the default decision. When a date, cutoff, or performance range changes, it sends a new request. An AbortController cancels stale browser requests so an older selection does not overwrite the current one.

The API supplies computed metrics. React formats them and draws the interface; it does not independently reimplement the backend's accuracy formulas.

**Reveal actuals is a display toggle.** The decision response already includes retrospective actuals. Clicking it reveals the second chart line and outcome cards; it does not fetch a new source or make the actuals historically knowable. The separation is a product presentation rule, not an authorization boundary.

**Export CSV is a separate HTTP request.** The link includes the current date/range and cutoff. FastAPI runs the same selection rules and returns a downloadable CSV.

The three navigation views are React state, not separate client-side routes. There is no Redux store, React Router, login system, or client portfolio model in this version.

## 7. Deployment: Vercel and Docker are different paths

**Current public deployment: Vercel.**

Vite builds static React assets into `dist/`. Vercel serves those assets. Requests under `/api/*` are rewritten to `api/index.py`, which exposes the same FastAPI application. The function bundle includes `backend/` and `data/`. The app uses one public origin, avoiding a separate browser-to-backend CORS setup.

We do **not** claim the current Vercel deployment runs the supplied Docker container. It uses static hosting plus a Python function.

**Local/container path: Docker.**

The Dockerfile has a Node stage that builds React and a Python stage containing FastAPI, the bundled data, and the built frontend. Uvicorn runs as a non-root user. FastAPI serves `/` and `/assets` alongside `/api/*`, and the server honors the hosting platform's `PORT`. Docker Compose provides one-command startup and a health check. This image is also suitable for a compatible container host, subject to that host's configuration.

## 8. Verification and the boundary of the pilot

The 27 Python tests cover manually calculated metrics, cutoff boundaries, timezone-aware timestamps, missing data and zero values, duplicate conflicts, historical actual revisions, January/February boundaries, snapshot hashes, API validation, and CSV consistency. Real-data tests exercise all 31 decisions at all six UI cutoff options. The production frontend build and Docker startup were also checked.

GitHub Actions is configured to run tests and builds, but the hosted job could not start because of an account-level restriction. Do not describe hosted CI as passing.

This system does not train a new wind model, stream live data, place trades, compute a client purchase volume, or estimate savings. It has no demand, price, contracted supply, or portfolio allocation inputs. National forecast error is useful context, but it is not the client's actual deficit. Curtailment and source-scope differences may contribute to the measured discrepancy.

## A 60-second architecture explanation you can practice

> Windward has two main stages. First, an offline Python script downloads Elexon's wind forecasts and actuals, validates them, and stores a reproducible compressed snapshot with a source manifest.
>
> When a user selects a buying date and cutoff in the React portal, FastAPI reads the cached snapshot indexes and chooses the latest forecast published by that cutoff for each next-day delivery hour. We compare hourly forecasts with the average of the two half-hour actuals, then calculate error, MAE, RMSE, bias, and coverage.
>
> Historical decision context only uses information available by that time. Retrospective results are clearly labelled separately. The API returns JSON to React, which displays the charts and audit trail, and can export the same selection as CSV.
>
> The public app uses Vercel static hosting plus a Python function. Docker is a separate, tested way to run the whole app as one service. There is no live ingestion service or database in this pilot.

# Windward recording guide

Target duration: **9 minutes**, maximum **10 minutes total**. Record the real application and use your own narration. Avoid claiming that the tool calculates purchase volume or financial savings. Numbers below refer to the bundled snapshot and a 09:00 GMT cutoff.

For the complete, word-for-word customer pitch with eight timed scenes, use [customer-pitch-5min.md](customer-pitch-5min.md). It targets 4:55 and supersedes the Part 1 outline below. A narration-only copy is in [customer-narration.txt](customer-narration.txt). The detailed technical explanation is in [architecture-and-workflow.md](architecture-and-workflow.md), with editable diagrams under [diagrams/](diagrams/).

## Part 1 — Customer pilot presentation (0:00–4:30)

### 0:00–0:35 — Start with the decision

Show the day-ahead overview.

“Your team has to buy electricity before knowing how much wind will actually arrive. Windward brings together the forecast you had when deciding and the evidence of how forecasts performed. This pilot uses only Elexon's national wind data for January buying decisions.”

### 0:35–1:40 — Replay a real decision

Select **15 January 2026**, cutoff **09:00**. Delivery is **16 January**.

- Expected wind energy: **190.33 GWh**.
- Average forecast power: **7.93 GW**.
- Forecast range: approximately **6.24–10.38 GW**.
- Latest forecast publication: **07:30 GMT**, 1.5 hours old at cutoff.

Explain that only forecasts published by cutoff are eligible. Expand the audit trail and point to the publication timestamp, forecast target, and lead time.

### 1:40–2:25 — Explain uncertainty without hindsight

Show the prior-history panel. The earlier-history sample is restricted to actual publications available by the chosen decision cutoff. It is not full-month information presented as if known in advance.

“The earlier results give a sense of historical error and shortfall exposure. These are descriptive observations, not a guaranteed safety margin. We would need your portfolio, demand, and trading policy before turning this into a purchase recommendation.”

### 2:25–3:00 — Reveal the outcome

Click **Reveal actuals**. Emphasize that actuals were unavailable when buying. For the selected decision, MAE is **0.78 GW**, bias approximately **+0.35 GW**, and cumulative positive wind shortfall **13.62 GWh**.

### 3:00–4:00 — Show the January findings

Open Forecast performance and keep the full January decision range.

- **744 / 744 hours matched**.
- MAE approximately **2.04 GW** and RMSE **2.50 GW**.
- Average bias **+1.75 GW**.
- Wind overestimated in approximately **84.95%** of hours.
- Largest hourly shortfall **6.87 GW**.

Use the daily chart and delivery-hour view to point out patterns. Click **Review** for a large shortfall and inspect that decision. Do not invent a weather explanation or attribute all error to weather; curtailment and data-scope differences may also matter.

### 4:00–4:30 — Close the customer pitch

Show CSV export and data provenance.

“The pilot makes each forecast auditable and turns its error into understandable national wind exposure. The next step would be agreeing a buying cutoff and validating how these national signals map to your actual portfolio.”

## Part 2 — Technical lead review (4:30–9:00)

### 4:30–5:15 — Architecture

Show the repository and explain:

Elexon streams → offline ingestion → compressed snapshot + provenance manifest → pure Python analysis → FastAPI → React.

React is built with Vite and TypeScript. Python serves time-aware selection and metrics. The Docker image builds the UI in a Node stage and runs a non-root Python service, serving both UI and API on one origin. Vercel uses a Python API function with the same analysis code.

### 5:15–6:10 — Data and timing

Open `scripts/ingest.py`, `data/manifest.json`, and `backend/analysis.py`.

- Forecasts are hourly in this real January snapshot, actuals half-hourly.
- Average both half-hour actuals to form an hourly comparison.
- Pick the latest publication at or before the decision cutoff.
- Reject conflicting duplicates; do not zero-fill missing records.
- Decisions January 1–31 imply delivery January 2–February 1.

### 6:10–7:00 — Accuracy and time-safe history

Explain the sign convention and MAE/RMSE/bias/shortfall calculations. Show `build_day()` and the prior-history logic in `backend/main.py`.

“The historical context selects actual revisions as of the decision cutoff. The retrospective performance page uses the latest actual versions in the snapshot. Keeping those paths separate prevents future information leaking into historical advice.”

### 7:00–7:45 — APIs and frontend

Open `/api/docs`. Show `/api/decision`, `/api/performance`, and `/api/export`. Mention validation, process-level immutable-data caching, cancellation of stale browser requests, loading/error states, responsive layouts, and source metadata.

### 7:45–8:30 — Verification

Run or show the results of:

```sh
python -m pytest -q
npm run build
docker compose up --build
```

Point to the hand-calculated metric test, cutoff boundary test, actual revision test, and real-snapshot coverage checks. CI runs the Python tests, React build, and Docker build.

### 8:30–9:00 — Tradeoffs and handover

Explain why a bundled historical snapshot was chosen: fast, deterministic, auditable, and independent of upstream availability during evaluation. It is not a live trading platform.

Mention next steps: client portfolio data, agreed auction timing, confirmed source coverage, monitored ingestion, and empirical validation of any proposed uncertainty model. Mention AI assistance explicitly and that you reviewed and can explain the code.

## Before uploading

- Keep each overview under five minutes and total under ten.
- Confirm charts and text are readable at the recording resolution.
- Hide unrelated browser tabs, terminal secrets, and personal notifications.
- Use an unlisted YouTube upload, not a private upload.
- Watch the uploaded video once and verify access in an incognito window.
- Add the final video and deployment URLs to the README before submission.

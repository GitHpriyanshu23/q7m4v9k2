import csv
import gzip
import io
import json
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from backend.analysis import build_day, decision_cutoff, index_records, metrics

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIRST, LAST = date(2026, 1, 1), date(2026, 1, 31)
app = FastAPI(title="Windward API", version="1.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json")


@lru_cache(maxsize=1)
def snapshot():
    with gzip.open(DATA / "windfor.json.gz", "rt") as f:
        forecasts = json.load(f)
    with gzip.open(DATA / "fuelhh.json.gz", "rt") as f:
        actuals = json.load(f)
    return index_records(forecasts, actuals)


def validate(day: date, cutoff: str):
    if not FIRST <= day <= LAST:
        raise HTTPException(422, "Decision date must be in January 2026")
    if not len(cutoff) == 5 or not cutoff[2] == ":":
        raise HTTPException(422, "Cutoff must be HH:MM in Europe/London")
    try:
        decision_cutoff(day, cutoff)
    except ValueError:
        raise HTTPException(422, "Cutoff must be a valid HH:MM in Europe/London")


@lru_cache(maxsize=256)
def day_result(day: date, cutoff: str):
    return build_day(day, cutoff, *snapshot())


@app.get("/api/health")
def health():
    if not (DATA / "manifest.json").exists():
        raise HTTPException(503, "Data snapshot missing. Run python scripts/ingest.py")
    try:
        snapshot()
    except (OSError, ValueError, KeyError) as error:
        raise HTTPException(503, f"Invalid data snapshot: {error}")
    return {"status": "ok", "mode": "historical-replay"}


@app.get("/api/meta")
def meta():
    return {"name": "Windward", "timezone": "Europe/London", "resolution_minutes": 60,
            "default_cutoff": "09:00", "first_decision": str(FIRST), "last_decision": str(LAST),
            "manifest": json.loads((DATA / "manifest.json").read_text())}


@app.get("/api/decision")
def decision(decision_date: date = date(2026, 1, 15), cutoff: str = "09:00"):
    validate(decision_date, cutoff)
    result = dict(day_result(decision_date, cutoff))
    as_of = decision_cutoff(decision_date, cutoff)
    historical = []
    prior = FIRST
    while prior < decision_date:
        historical.extend(build_day(prior, cutoff, *snapshot(), actual_as_of=as_of)["periods"])
        prior += timedelta(days=1)
    result["prior_history"] = {"metrics": metrics(historical), "as_of": result["cutoff"],
                               "first_decision": str(FIRST), "last_decision": str(decision_date - timedelta(days=1)) if historical else None,
                               "note": "Only earlier January decisions and actual publications available by this decision cutoff. Descriptive history, not a calibrated prediction interval."}
    return result


@app.get("/api/performance")
def performance(start: date = FIRST, end: date = LAST, cutoff: str = "09:00"):
    validate(start, cutoff)
    validate(end, cutoff)
    if start > end:
        raise HTTPException(422, "Start date must not exceed end date")
    days, periods = [], []
    current = start
    while current <= end:
        result = day_result(current, cutoff)
        days.append({"decision_date": str(current), "delivery_date": result["delivery_date"], **result["metrics"]})
        periods.extend({"decision_date": str(current), **p} for p in result["periods"])
        current += timedelta(days=1)
    hourly = []
    for hour in range(24):
        group = [p for p in periods if p["hour"] == f"{hour:02}:00"]
        hourly.append({"hour": f"{hour:02}:00", **metrics(group)})
    worst = sorted([p for p in periods if p["error_mw"] is not None], key=lambda p: p["error_mw"], reverse=True)[:5]
    return {"start": str(start), "end": str(end), "cutoff": cutoff, "metrics": metrics(periods),
            "days": days, "hourly": hourly, "worst": worst}


@app.get("/api/export")
def export(start: date = FIRST, end: date = LAST, cutoff: str = "09:00"):
    performance(start, end, cutoff)  # same validation and date semantics
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["decision_date", "decision_cutoff_utc", "delivery_start_utc", "forecast_publish_utc", "forecast_mw", "actual_mw", "error_forecast_minus_actual_mw", "forecast_age_hours"])
    current = start
    while current <= end:
        day = day_result(current, cutoff)
        for p in day["periods"]:
            writer.writerow([str(current), day["cutoff"], p["start_time"], p["publish_time"], p["forecast_mw"], p["actual_mw"], p["error_mw"], p["age_hours"]])
        current += timedelta(days=1)
    return StreamingResponse(iter([out.getvalue()]), media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="windward-{start}-{end}.csv"'})


# Docker/Heroku: one same-origin service serves the built React app and API.
DIST = ROOT / "dist"
if DIST.exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/")
    def frontend():
        return FileResponse(DIST / "index.html")

    @app.get("/favicon.svg")
    def favicon():
        return FileResponse(DIST / "favicon.svg")

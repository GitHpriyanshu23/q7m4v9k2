"""Pure, deterministic time-aware forecast selection and accuracy calculations."""
from datetime import date, datetime, time, timedelta, timezone
from math import ceil, sqrt
from statistics import mean
from zoneinfo import ZoneInfo

LONDON = ZoneInfo("Europe/London")
UTC = timezone.utc


def timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamps must include a timezone")
    return parsed.astimezone(UTC)


def iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def decision_cutoff(day: date, clock: str) -> datetime:
    return datetime.combine(day, time.fromisoformat(clock), LONDON).astimezone(UTC)


def index_records(forecasts: list[dict], actuals: list[dict]):
    forecast_index, actual_index = {}, {}
    for row in forecasts:
        target, published = timestamp(row["startTime"]), timestamp(row["publishTime"])
        forecast_index.setdefault(target, {})[published] = float(row["generation"])
    for row in actuals:
        if row.get("fuelType") != "WIND":
            continue
        target, published = timestamp(row["startTime"]), timestamp(row["publishTime"])
        actual_index.setdefault(target, {})[published] = float(row["generation"])
    # Conflicting values at the same target/publication must never silently win.
    for rows, fuel_only in ((forecasts, False), (actuals, True)):
        seen = {}
        for row in rows:
            if fuel_only and row.get("fuelType") != "WIND":
                continue
            key = (timestamp(row["startTime"]), timestamp(row["publishTime"]))
            if key in seen and seen[key] != row["generation"]:
                raise ValueError(f"Conflicting duplicate record at {key}")
            seen[key] = row["generation"]
    return forecast_index, actual_index


def latest(versions: dict, cutoff: datetime | None = None):
    candidates = [p for p in versions if cutoff is None or p <= cutoff]
    if not candidates:
        return None, None
    published = max(candidates)
    return versions[published], published


def build_day(day: date, clock: str, forecast_index: dict, actual_index: dict,
              actual_as_of: datetime | None = None) -> dict:
    cutoff = decision_cutoff(day, clock)
    delivery = day + timedelta(days=1)
    start = datetime.combine(delivery, time(), LONDON).astimezone(UTC)
    end = datetime.combine(delivery + timedelta(days=1), time(), LONDON).astimezone(UTC)
    periods = []
    target = start
    while target < end:
        forecast, published = latest(forecast_index.get(target, {}), cutoff)
        first, _ = latest(actual_index.get(target, {}), actual_as_of)
        second, _ = latest(actual_index.get(target + timedelta(minutes=30), {}), actual_as_of)
        actual = (first + second) / 2 if first is not None and second is not None else None
        error = forecast - actual if forecast is not None and actual is not None else None
        periods.append({"start_time": iso(target), "hour": target.astimezone(LONDON).strftime("%H:%M"),
                        "forecast_mw": forecast, "actual_mw": actual, "error_mw": error,
                        "publish_time": iso(published) if published else None,
                        "age_hours": (cutoff - published).total_seconds() / 3600 if published else None,
                        "lead_hours": (target - published).total_seconds() / 3600 if published else None})
        target += timedelta(hours=1)
    return {"decision_date": day.isoformat(), "delivery_date": delivery.isoformat(),
            "cutoff": iso(cutoff), "periods": periods, "metrics": metrics(periods)}


def metrics(periods: list[dict]) -> dict:
    matched = [p for p in periods if p["error_mw"] is not None]
    errors = [p["error_mw"] for p in matched]
    forecasts = [p["forecast_mw"] for p in periods if p["forecast_mw"] is not None]
    actuals = [p["actual_mw"] for p in periods if p["actual_mw"] is not None]
    return {"expected": len(periods), "matched": len(matched), "forecast_count": len(forecasts),
            "coverage_pct": 100 * len(matched) / len(periods) if periods else 0,
            "forecast_energy_mwh": sum(forecasts) if forecasts else None,
            "actual_energy_mwh": sum(actuals) if actuals else None,
            "mae_mw": mean(abs(e) for e in errors) if errors else None,
            "rmse_mw": sqrt(mean(e * e for e in errors)) if errors else None,
            "bias_mw": mean(errors) if errors else None,
            "shortfall_mwh": sum(max(e, 0) for e in errors) if errors else None,
            "overforecast_pct": 100 * sum(e > 0 for e in errors) / len(errors) if errors else None,
            "max_shortfall_mw": max(max(errors), 0) if errors else None,
            "p90_shortfall_mw": sorted(max(e, 0) for e in errors)[ceil(.9 * len(errors)) - 1] if errors else None,
            "mean_forecast_mw": mean(forecasts) if forecasts else None,
            "peak_forecast_mw": max(forecasts) if forecasts else None,
            "min_forecast_mw": min(forecasts) if forecasts else None}

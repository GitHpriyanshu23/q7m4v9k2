from datetime import date
from math import sqrt

import pytest

from backend.analysis import build_day, decision_cutoff, index_records, metrics, timestamp


def forecast(generation, published="2026-01-01T08:00:00Z", target="2026-01-02T00:00:00Z"):
    return {"startTime": target, "publishTime": published, "generation": generation}


def actual(generation, target="2026-01-02T00:00:00Z", published="2026-01-02T01:00:00Z", fuel="WIND"):
    return {**forecast(generation, published, target), "fuelType": fuel}


def day(forecasts, actuals, **kwargs):
    return build_day(date(2026, 1, 1), "09:00", *index_records(forecasts, actuals), **kwargs)


def test_latest_eligible_forecast_excludes_future_publication():
    result = day([forecast(10), forecast(20, "2026-01-01T09:00:00Z"), forecast(999, "2026-01-01T09:00:01Z")], [])
    assert result["periods"][0]["forecast_mw"] == 20
    assert result["periods"][0]["publish_time"] == "2026-01-01T09:00:00Z"


def test_half_hours_are_averaged_and_mwh_uses_one_hour():
    result = day([forecast(200)], [actual(80), actual(120, "2026-01-02T00:30:00Z")])
    assert result["periods"][0]["actual_mw"] == 100
    assert result["metrics"]["shortfall_mwh"] == 100
    assert result["metrics"]["forecast_energy_mwh"] == 200


def test_missing_half_hour_is_missing_not_zero():
    result = day([forecast(200)], [actual(80)])
    assert result["periods"][0]["actual_mw"] is None
    assert result["metrics"]["matched"] == 0
    assert result["metrics"]["mae_mw"] is None


def test_zero_actual_is_valid():
    result = day([forecast(100)], [actual(0), actual(0, "2026-01-02T00:30:00Z")])
    assert result["metrics"]["matched"] == 1
    assert result["metrics"]["mae_mw"] == 100


def test_wind_filter_and_identical_duplicates_do_not_inflate():
    a = [actual(80), actual(120, "2026-01-02T00:30:00Z"), actual(999, fuel="CCGT")]
    result = day([forecast(200)] * 3, a + a)
    assert result["metrics"]["matched"] == 1
    assert result["periods"][0]["actual_mw"] == 100


def test_conflicting_duplicate_is_rejected():
    with pytest.raises(ValueError, match="Conflicting duplicate"):
        index_records([forecast(10), forecast(20)], [])


def test_actual_revisions_respect_as_of_for_prior_history():
    actuals = [actual(10), actual(30, "2026-01-02T00:30:00Z"),
               actual(999, published="2026-01-03T00:00:00Z")]
    historical = day([forecast(100)], actuals, actual_as_of=timestamp("2026-01-02T09:00:00Z"))
    retrospective = day([forecast(100)], actuals)
    assert historical["periods"][0]["actual_mw"] == 20
    assert retrospective["periods"][0]["actual_mw"] == 514.5


def test_unpublished_actuals_are_not_in_prior_history():
    result = day([forecast(100)], [actual(20), actual(40, "2026-01-02T00:30:00Z")], actual_as_of=timestamp("2026-01-01T09:00:00Z"))
    assert result["metrics"]["matched"] == 0


def test_hand_calculated_error_metrics():
    periods = [{"forecast_mw": 150, "actual_mw": 100, "error_mw": 50},
               {"forecast_mw": 70, "actual_mw": 100, "error_mw": -30}]
    result = metrics(periods)
    assert result["mae_mw"] == 40
    assert result["rmse_mw"] == sqrt(1700)
    assert result["bias_mw"] == 10
    assert result["shortfall_mwh"] == 50
    assert result["overforecast_pct"] == 50
    assert result["coverage_pct"] == 100
    assert result["p90_shortfall_mw"] == 50


def test_january_31_delivers_february_1():
    result = build_day(date(2026, 1, 31), "09:00", {}, {})
    assert result["delivery_date"] == "2026-02-01"
    assert len(result["periods"]) == 24
    assert result["periods"][-1]["start_time"] == "2026-02-01T23:00:00Z"


def test_timezone_and_naive_timestamp_validation():
    assert decision_cutoff(date(2026, 1, 1), "09:00") == timestamp("2026-01-01T09:00:00Z")
    with pytest.raises(ValueError):
        timestamp("2026-01-01T09:00:00")

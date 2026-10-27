import csv
import gzip
import hashlib
import io
import json

import pytest
from fastapi.testclient import TestClient

from backend.main import DATA, app

client = TestClient(app)


def test_health_and_snapshot_hashes():
    assert client.get("/api/health").json()["status"] == "ok"
    manifest = client.get("/api/meta").json()["manifest"]
    for source in manifest["sources"]:
        content = gzip.decompress((DATA / source["file"]).read_bytes())
        assert hashlib.sha256(content).hexdigest() == source["sha256"]
        assert len(json.loads(content)) == source["records"]


@pytest.mark.parametrize("clock", ["06:00", "09:00", "09:20", "09:50", "12:00", "15:30"])
def test_all_decisions_have_no_future_forecasts(clock):
    for number in range(1, 32):
        result = client.get("/api/decision", params={"decision_date": f"2026-01-{number:02}", "cutoff": clock})
        assert result.status_code == 200
        body = result.json()
        for period in body["periods"]:
            assert period["publish_time"] is None or period["publish_time"] <= body["cutoff"]


def test_first_decision_does_not_borrow_future_history():
    result = client.get("/api/decision?decision_date=2026-01-01").json()
    assert result["prior_history"]["metrics"]["matched"] == 0
    assert result["prior_history"]["metrics"]["mae_mw"] is None


def test_full_snapshot_has_744_complete_hourly_comparisons():
    result = client.get("/api/performance").json()
    assert result["metrics"]["expected"] == 744
    assert result["metrics"]["matched"] == 744
    assert len(result["days"]) == 31
    assert result["days"][-1]["delivery_date"] == "2026-02-01"
    assert result["metrics"]["mae_mw"] == pytest.approx(2038.9126344086021)


@pytest.mark.parametrize("url", ["/api/decision?decision_date=2025-12-31", "/api/decision?cutoff=25:00", "/api/decision?cutoff=09:00:00", "/api/decision?decision_date=garbage", "/api/performance?start=2026-01-20&end=2026-01-10", "/api/export?start=2026-02-01"])
def test_invalid_queries_are_rejected(url):
    assert client.get(url).status_code == 422


def test_export_matches_selected_day_and_cutoff():
    response = client.get("/api/export?start=2026-01-31&end=2026-01-31&cutoff=06:00")
    assert response.status_code == 200
    rows = list(csv.DictReader(io.StringIO(response.text)))
    assert len(rows) == 24
    assert rows[0]["decision_cutoff_utc"] == "2026-01-31T06:00:00Z"
    assert rows[-1]["delivery_start_utc"] == "2026-02-01T23:00:00Z"

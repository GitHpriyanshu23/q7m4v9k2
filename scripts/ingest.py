"""Fetch the two public Elexon datasets and create an auditable snapshot.

Run from the repository root: python scripts/ingest.py
Only standard-library dependencies are needed. Existing files are replaced only
after both responses have been downloaded and validated successfully.
"""
import gzip
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://data.elexon.co.uk/bmrs/api/v1/datasets/"
QUERIES = {
    "WINDFOR": {"publishDateTimeFrom": "2025-12-31T00:00:00Z", "publishDateTimeTo": "2026-02-01T00:00:00Z"},
    "FUELHH": {"settlementDateFrom": "2026-01-02", "settlementDateTo": "2026-02-01", "fuelType": "WIND"},
}


def main():
    output = ROOT / "data"
    output.mkdir(exist_ok=True)
    staged, sources = {}, []
    for dataset, params in QUERIES.items():
        url = BASE + dataset + "/stream?" + urlencode(params)
        for attempt in range(4):
            try:
                with urlopen(Request(url, headers={"User-Agent": "Windward-assessment/1.0"}), timeout=120) as response:
                    rows = json.load(response)
                break
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"Empty or unexpected response for {dataset}")
        required = {"startTime", "publishTime", "generation"}
        for row in rows:
            if not required <= row.keys() or not isinstance(row["generation"], (int, float)):
                raise ValueError(f"Invalid record in {dataset}: {row}")
            for field in ("startTime", "publishTime"):
                value = datetime.fromisoformat(row[field].replace("Z", "+00:00"))
                if value.tzinfo is None:
                    raise ValueError("Naive source timestamp")
        if dataset == "FUELHH":
            rows = [r for r in rows if r.get("fuelType") == "WIND"]
        rows.sort(key=lambda r: (r["startTime"], r["publishTime"], r["generation"]))
        content = json.dumps(rows, separators=(",", ":"), sort_keys=True).encode()
        filename = dataset.lower() + ".json.gz"
        staged[filename] = gzip.compress(content, mtime=0)
        sources.append({"dataset": dataset, "url": url, "records": len(rows),
                        "sha256": hashlib.sha256(content).hexdigest(), "file": filename})
        print(f"Validated {dataset}: {len(rows)} records", flush=True)
    for filename, content in staged.items():
        temporary = output / (filename + ".tmp")
        temporary.write_bytes(content)
        temporary.replace(output / filename)
    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "sources": sources,
                "decision_dates": ["2026-01-01", "2026-01-31"],
                "delivery_dates": ["2026-01-02", "2026-02-01"]}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("Snapshot and source manifest saved to data/", flush=True)


if __name__ == "__main__":
    main()

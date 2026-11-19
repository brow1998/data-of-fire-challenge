"""Record a few real API pages into tests/fixtures/pages, so tests never need the network.

uv run python tools/record_fixtures.py
"""

import json
from pathlib import Path

from fire import api

OUT = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "pages"

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    pages = api.fetch_pages(watermark="2026-01-01T00:00:00.000", page_size=40)
    for n, (request, rows) in zip(range(1, 4), pages):
        path = OUT / f"page_{n:03d}.json"
        path.write_text(json.dumps({"request": request, "rows": rows}, indent=1, sort_keys=True) + "\n")
        print(f"{path.name}: {len(rows)} rows")

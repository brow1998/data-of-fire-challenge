"""`fire run`: pull new and changed incidents, then rebuild and test the warehouse.

Connection settings come from the standard libpq variables (PGHOST, PGPORT, PGUSER,
PGPASSWORD, PGDATABASE), which both psycopg and the dbt profile read.
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import date
from pathlib import Path

import psycopg

from fire import api, ingest, transform

log = logging.getLogger("fire")


def replay(directory: str):
    """Yield recorded pages, in file name order, in the same shape the API client yields."""
    for path in sorted(Path(directory).glob("*.json")):
        page = json.loads(path.read_text())
        yield page["request"], page["rows"]


def _date(value: str) -> str:
    return date.fromisoformat(value).isoformat()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="fire", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="ingest, then dbt build (models + tests)")
    run.add_argument("--since", type=_date, help="only incidents on or after this date (YYYY-MM-DD)")
    run.add_argument("--replay", metavar="DIR", help="load recorded pages from DIR instead of the live API")
    run.add_argument("--skip-ingest", action="store_true", help="only rebuild the warehouse")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", force=True)

    if not args.skip_ingest:
        with psycopg.connect(autocommit=True) as conn:
            ingest.setup(conn)
            mark = ingest.watermark(conn)
            log.info("watermark: %s", mark or "none, full load")
            pages = replay(args.replay) if args.replay else api.fetch_pages(mark, since=args.since)
            result = ingest.ingest(conn, pages)
            log.info(
                "ingest done: %d pages seen, %d stored; %d rows seen, %d new",
                result.pages_seen,
                result.pages_stored,
                result.rows_seen,
                result.rows_stored,
            )

    transform.run_dbt(["build"])


if __name__ == "__main__":
    main()

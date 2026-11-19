"""Land API pages in Postgres untouched, with a receipt for every row.

raw.pages     one row per stored page: content hash, when it was fetched, the exact request
raw.incidents one row per record version, keyed by (id, data_as_of), pointing at its page

A record version we already hold is never stored again, so re-running against an
unchanged source writes nothing.
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Iterable
from dataclasses import dataclass

import psycopg
from psycopg.types.json import Jsonb

log = logging.getLogger(__name__)

DDL = """
create schema if not exists raw;

create table if not exists raw.pages (
    page_id     text primary key,
    fetched_at  timestamptz not null default now(),
    request     jsonb not null,
    row_count   integer not null
);

create table if not exists raw.incidents (
    page_id     text not null references raw.pages (page_id),
    row_number  integer not null,
    id          text not null,
    data_as_of  text not null,
    record      jsonb not null,
    primary key (page_id, row_number),
    unique (id, data_as_of)
);
"""


@dataclass
class IngestResult:
    pages_seen: int = 0
    pages_stored: int = 0
    rows_seen: int = 0
    rows_stored: int = 0


def setup(conn: psycopg.Connection) -> None:
    conn.execute(DDL)
    conn.commit()


def watermark(conn: psycopg.Connection) -> str | None:
    return conn.execute("select max(data_as_of) from raw.incidents").fetchone()[0]


def _page_id(rows: list[dict]) -> str:
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def store_page(conn: psycopg.Connection, request: dict, rows: list[dict]) -> int:
    """Store the record versions in `rows` we don't hold yet. Returns how many were new."""
    valid = [r for r in rows if r.get("id") and r.get("data_as_of")]
    if len(valid) < len(rows):
        log.warning("skipping %d records without id or data_as_of", len(rows) - len(valid))

    keys = [(r["id"], r["data_as_of"]) for r in valid]
    known = {
        (i, d)
        for i, d in conn.execute(
            "select id, data_as_of from raw.incidents where (id, data_as_of) in (select * from unnest(%s::text[], %s::text[]))",
            ([k[0] for k in keys], [k[1] for k in keys]),
        )
    }
    # Keyed by version, so a record repeated inside one page is stored once.
    new = list({(r["id"], r["data_as_of"]): r for r in valid if (r["id"], r["data_as_of"]) not in known}.values())
    if not new:
        return 0

    page_id = _page_id(new)
    with conn.transaction():
        conn.execute(
            "insert into raw.pages (page_id, request, row_count) values (%s, %s, %s) on conflict do nothing",
            (page_id, Jsonb(request), len(new)),
        )
        with conn.cursor().copy("copy raw.incidents (page_id, row_number, id, data_as_of, record) from stdin") as copy:
            for n, r in enumerate(new):
                copy.write_row((page_id, n, r["id"], r["data_as_of"], json.dumps(r)))
    return len(new)


def ingest(conn: psycopg.Connection, pages: Iterable[tuple[dict, list[dict]]]) -> IngestResult:
    result = IngestResult()
    for request, rows in pages:
        stored = store_page(conn, request, rows)
        result.pages_seen += 1
        result.rows_seen += len(rows)
        result.pages_stored += stored > 0
        result.rows_stored += stored
        log.info("page %d: %d rows, %d new", result.pages_seen, len(rows), stored)
    return result

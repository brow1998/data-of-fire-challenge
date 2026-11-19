"""Client for the San Francisco Fire Incidents dataset on Socrata (data.sf.gov)."""

from __future__ import annotations

import time
from collections.abc import Iterator

import requests

URL = "https://data.sf.gov/resource/wr8u-xric.json"
PAGE_SIZE = 50_000


class ApiError(RuntimeError):
    pass


def _get(session: requests.Session, params: dict, retries: int, backoff: float) -> list[dict]:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = session.get(URL, params=params, timeout=120)
            if response.status_code == 200:
                payload = response.json()
                if not isinstance(payload, list):
                    raise ApiError(f"expected a JSON array, got {type(payload).__name__}")
                return payload
            if response.status_code < 500 and response.status_code != 429:
                raise ApiError(f"HTTP {response.status_code}: {response.text[:200]}")
            last_error = ApiError(f"HTTP {response.status_code}")
        except (requests.ConnectionError, requests.Timeout, ValueError) as exc:
            last_error = exc
        time.sleep(backoff * 2**attempt)
    raise ApiError(f"giving up after {retries} attempts: {last_error}")


def fetch_pages(
    watermark: str | None,
    since: str | None = None,
    page_size: int = PAGE_SIZE,
    retries: int = 5,
    backoff: float = 2.0,
    session: requests.Session | None = None,
) -> Iterator[tuple[dict, list[dict]]]:
    """Yield (request params, rows) for every record with data_as_of >= watermark.

    The watermark is inclusive on purpose: records published in the same second as the
    last one we saw are fetched again and dropped by the (id, data_as_of) key downstream,
    instead of being missed.
    """
    session = session or requests.Session()
    filters = []
    if watermark:
        filters.append(f"data_as_of >= '{watermark}'")
    if since:
        filters.append(f"incident_date >= '{since}'")
    offset = 0
    while True:
        params = {"$order": "data_as_of, id", "$limit": page_size, "$offset": offset}
        if filters:
            params["$where"] = " AND ".join(filters)
        rows = _get(session, params, retries, backoff)
        if rows:
            yield params, rows
        if len(rows) < page_size:
            return
        offset += page_size

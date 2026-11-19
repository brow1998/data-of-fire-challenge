# Data of Fire

[![ci](https://github.com/brow1998/data-of-fire-challenge/actions/workflows/ci.yml/badge.svg)](https://github.com/brow1998/data-of-fire-challenge/actions/workflows/ci.yml)

A small warehouse for [San Francisco fire incidents](https://data.sf.gov/Public-Safety/Fire-Incidents/wr8u-xric),
built so a BI team can slice incidents by any time period, neighborhood district and battalion.

It pulls only new and changed records from the city's open data API, lands them untouched in
Postgres with a receipt for every row, and builds a tested dimensional model with dbt.

```text
data.sf.gov API ──► raw.pages / raw.incidents ──► staging ──► marts ──► reports
   (Socrata)          untouched, append-only       latest     star       BI-ready
                      keyed by (id, data_as_of)    version    schema     views
```

## Quick start

Needs Docker. One command, from a clean checkout:

```bash
docker compose run --rm pipeline
```

That starts Postgres, loads the full history (about 733,000 incidents, under five minutes), then runs
`dbt build`, which builds every model and runs every data test. Run it again and it fetches only what
changed since the last run.

The warehouse is then on `localhost:6543` (database, user and password are all `fire`). To explore it
in Metabase:

```bash
docker compose --profile bi up -d metabase
```

Then open <http://localhost:3000> and add a PostgreSQL connection to host `db`, port `5432`.

## What you get

| Schema | Object | Grain |
|---|---|---|
| `raw` | `pages` | One API page we stored: content hash, fetch time, the exact request |
| `raw` | `incidents` | One record version, untouched JSON, pointing at its page |
| `staging` | `stg_fire__incidents` | One incident, latest version, typed |
| `marts` | `fct_fire_incidents` | One incident, with response time, casualties, losses and its receipt |
| `marts` | `dim_date`, `dim_district`, `dim_battalion` | Conformed dimensions; `Unknown` members for incidents the source left blank |
| `reports` | `agg_incidents_daily` | Day × district × battalion: the table BI tools roll up to any period |
| `reports` | `rpt_incidents_by_month_district` | Month × district |
| `reports` | `rpt_incidents_by_battalion_year` | Year × battalion, with median response time |

```text
 year | battalion_code | incidents | fatalities | injuries | median_response_minutes
------+----------------+-----------+------------+----------+-------------------------
 2025 | B02            |      6953 |          1 |        4 |                     4.3
 2025 | B03            |      5741 |          0 |        3 |                     4.7
 2025 | B04            |      4694 |          0 |        4 |                     4.0
```

## How it behaves

**Running it twice gives the same answer.** Raw is keyed by `(id, data_as_of)`: a record version
already held is never stored again, so a second run against an unchanged source writes nothing, and
the model rebuilds to the same rows.

**It only asks for what changed.** The watermark is the latest `data_as_of` held. Requests ask for
`data_as_of >= watermark`. The bound is inclusive, so records published in the same second as the
last one are fetched again and dropped by the key instead of being missed. (`:updated_at` is useless
here: the city reloads the dataset in bulk and resets it on every row.)

**Every number has a receipt.** Each fact row carries `source_page_id` and `source_row_number`,
pointing at the exact raw record behind it, and each raw page records the request that produced it.
A dbt test fails the build if any receipt doesn't resolve.

**Nothing is lost between layers.** A dbt test fails the build if an incident id exists in raw but
not in the fact table, or the other way round.

**The API is not trusted.** Server errors and rate limits are retried with backoff; client errors
fail fast; a non-JSON body (a maintenance page, a redirect) is an error, not data.

## Options

```bash
docker compose run --rm pipeline fire run --since 2024-01-01   # backfill only recent incidents
docker compose run --rm pipeline fire run --skip-ingest        # rebuild the model only
```

## Tests

The suite runs against recorded real API pages in `tests/fixtures/` and refuses any network
connection other than the database. It needs a Postgres to talk to:

```bash
docker compose run --rm tests
```

Or with your own Postgres, set the usual `PG*` variables and run `uv run pytest`.
`uv run python tools/record_fixtures.py` re-records the fixtures.

## Layout

```text
src/fire/api.py        Socrata client: paging, retries, error handling
src/fire/ingest.py     raw schema, watermark, idempotent page storage
src/fire/cli.py        `fire run`: ingest, then dbt build
dbt/models/            staging → marts → reports, with schema tests
dbt/tests/             cross-layer tests: completeness and receipts
tests/                 pytest suite on recorded pages
```

## License

[MIT](LICENSE)

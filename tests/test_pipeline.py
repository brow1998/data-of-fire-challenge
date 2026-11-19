import json

from conftest import FIXTURES

from fire import cli, ingest


def run_replay(directory):
    cli.main(["run", "--replay", str(directory)])


def one(conn, sql, *params):
    return conn.execute(sql, params).fetchone()[0]


def fact_snapshot(conn):
    return conn.execute("select * from marts.fct_fire_incidents order by incident_id").fetchall()


def fixture_rows():
    return [r for p in sorted(FIXTURES.glob("*.json")) for r in json.loads(p.read_text())["rows"]]


def test_one_run_builds_and_tests_the_warehouse(conn):
    run_replay(FIXTURES)  # dbt build fails the run if any data test fails
    distinct_ids = len({r["id"] for r in fixture_rows()})
    assert one(conn, "select count(*) from marts.fct_fire_incidents") == distinct_ids
    assert one(conn, "select sum(incidents) from reports.agg_incidents_daily") == distinct_ids


def test_running_twice_stores_nothing_new_and_changes_nothing(conn):
    run_replay(FIXTURES)
    raw_before = one(conn, "select count(*) from raw.incidents")
    fact_before = fact_snapshot(conn)

    run_replay(FIXTURES)

    assert one(conn, "select count(*) from raw.incidents") == raw_before
    assert one(conn, "select count(*) from raw.pages") == len(list(FIXTURES.glob("*.json")))
    assert fact_snapshot(conn) == fact_before


def test_a_newer_version_replaces_the_old_one(conn, tmp_path):
    run_replay(FIXTURES)
    original = fixture_rows()[0]
    newer = {**original, "data_as_of": "2099-01-01T00:00:00.000", "civilian_injuries": "7"}
    (tmp_path / "update.json").write_text(json.dumps({"request": {"test": "update"}, "rows": [newer]}))

    run_replay(tmp_path)

    row = conn.execute(
        "select civilian_injuries, source_page_id from marts.fct_fire_incidents where incident_id = %s",
        (original["id"],),
    ).fetchone()
    assert row[0] == 7
    assert row[1] == one(conn, "select page_id from raw.incidents where data_as_of = '2099-01-01T00:00:00.000'")
    assert one(conn, "select count(*) from marts.fct_fire_incidents") == len({r["id"] for r in fixture_rows()})


def test_a_record_repeated_across_pages_is_stored_once(conn):
    ingest.setup(conn)
    rows = fixture_rows()[:3]
    ingest.ingest(conn, [({"p": 1}, rows), ({"p": 2}, rows[1:] + rows[1:])])
    assert one(conn, "select count(*) from raw.incidents") == 3
    assert one(conn, "select count(*) from raw.pages") == 1


def test_every_fact_row_has_a_receipt(conn):
    run_replay(FIXTURES)
    orphans = one(
        conn,
        """select count(*) from marts.fct_fire_incidents f
           left join raw.incidents r on r.page_id = f.source_page_id and r.row_number = f.source_row_number
           where r.id is distinct from f.incident_id""",
    )
    assert orphans == 0

import pytest
import responses

from fire import api


def page(n):
    return [{"id": str(i), "data_as_of": "2026-01-01T00:00:00.000"} for i in range(n)]


@responses.activate
def test_pages_until_a_short_page():
    responses.get(api.URL, json=page(2))
    responses.get(api.URL, json=page(1))
    pages = list(api.fetch_pages(None, page_size=2, backoff=0))
    assert [len(rows) for _, rows in pages] == [2, 1]
    assert [r["$offset"] for r, _ in pages] == [0, 2]


@responses.activate
def test_watermark_is_inclusive_and_since_filters_incident_date():
    responses.get(api.URL, json=[])
    list(api.fetch_pages("2026-01-01T00:00:00.000", since="2024-01-01", backoff=0))
    where = responses.calls[0].request.params["$where"]
    assert where == "data_as_of >= '2026-01-01T00:00:00.000' AND incident_date >= '2024-01-01'"


@responses.activate
def test_retries_server_errors_then_succeeds():
    responses.get(api.URL, status=503)
    responses.get(api.URL, status=429)
    responses.get(api.URL, json=page(1))
    assert len(list(api.fetch_pages(None, page_size=5, backoff=0))) == 1


@responses.activate
def test_client_errors_fail_fast():
    responses.get(api.URL, status=400, body="bad query")
    with pytest.raises(api.ApiError, match="HTTP 400"):
        list(api.fetch_pages(None, backoff=0))
    assert len(responses.calls) == 1


@responses.activate
def test_an_html_error_page_is_not_data():
    responses.get(api.URL, body="<html>maintenance</html>", status=200)
    with pytest.raises(api.ApiError):
        list(api.fetch_pages(None, retries=2, backoff=0))

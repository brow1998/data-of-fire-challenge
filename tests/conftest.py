import os
import socket
import uuid
from pathlib import Path

import psycopg
import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "pages"

_real_getaddrinfo = socket.getaddrinfo


@pytest.fixture(autouse=True)
def no_internet(monkeypatch):
    """Fail any test that tries to resolve a host other than the database."""
    allowed = {"localhost", "127.0.0.1", "::1", os.environ.get("PGHOST", "localhost")}

    def guarded(host, *args, **kwargs):
        if host not in allowed:
            raise RuntimeError(f"tests must not use the network (tried {host})")
        return _real_getaddrinfo(host, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", guarded)


@pytest.fixture
def database(monkeypatch):
    """A throwaway database on the configured server, so tests never touch pipeline data."""
    name = f"fire_test_{uuid.uuid4().hex[:8]}"
    with psycopg.connect(autocommit=True) as admin:
        admin.execute(f'create database "{name}"')
    monkeypatch.setenv("PGDATABASE", name)
    try:
        yield name
    finally:
        monkeypatch.setenv("PGDATABASE", os.environ.get("POSTGRES_DB", "postgres"))
        with psycopg.connect(autocommit=True, dbname="postgres") as admin:
            admin.execute(f'drop database "{name}" with (force)')


@pytest.fixture
def conn(database):
    with psycopg.connect(autocommit=True) as c:
        yield c

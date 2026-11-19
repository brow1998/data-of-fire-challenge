"""Run dbt programmatically against the same Postgres the ingestion wrote to."""

from __future__ import annotations

from pathlib import Path

from dbt.cli.main import dbtRunner

DBT_DIR = Path(__file__).resolve().parents[2] / "dbt"


def run_dbt(command: list[str]) -> None:
    args = [*command, "--project-dir", str(DBT_DIR), "--profiles-dir", str(DBT_DIR)]
    result = dbtRunner().invoke(args)
    if not result.success:
        raise RuntimeError(f"dbt {' '.join(command)} failed: {result.exception or 'see the log above'}")

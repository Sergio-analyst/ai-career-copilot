"""SQLite persistence for scraped LinkedIn job vacancies."""

import sqlite3
from pathlib import Path
from typing import Optional

from models import Job

DB_PATH = Path(__file__).resolve().parent / "jobs.db"


def _get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_database() -> None:
    """Create the jobs table if it doesn't already exist."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with _get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                linkedin_url TEXT UNIQUE,
                title TEXT,
                company TEXT,
                location TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def job_exists(url: str) -> bool:
    """Return True if a job with this url is already stored."""
    if not url:
        return False

    with _get_connection() as conn:
        cursor = conn.execute(
            "SELECT 1 FROM jobs WHERE linkedin_url = ? LIMIT 1", (url,)
        )
        return cursor.fetchone() is not None


def save_job(job: Job) -> bool:
    """Insert a new job into the database.

    Returns True if the job was inserted, False if it was skipped
    (missing url, or a job with this url already exists).
    """
    if not job.url:
        return False

    with _get_connection() as conn:
        try:
            conn.execute(
                """
                INSERT INTO jobs (linkedin_url, title, company, location, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (job.url, job.title, job.company, job.location, job.status),
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # linkedin_url UNIQUE constraint hit a duplicate.
            return False


def get_all_jobs() -> list[Job]:
    """Return every stored job, most recently added first."""
    with _get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT id, linkedin_url, title, company, location, status, created_at "
            "FROM jobs ORDER BY id DESC"
        )
        rows = cursor.fetchall()

    return [
        Job(
            url=row["linkedin_url"],
            title=row["title"],
            company=row["company"],
            location=row["location"],
            status=row["status"],
        )
        for row in rows
    ]
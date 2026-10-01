import os
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite


DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    "/app/data/dashboard.db",
)


async def init_db():
    Path(DATABASE_PATH).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS usage_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,

                usage_total REAL NOT NULL DEFAULT 0,
                usage_daily REAL NOT NULL DEFAULT 0,
                usage_weekly REAL NOT NULL DEFAULT 0,
                usage_monthly REAL NOT NULL DEFAULT 0,

                limit_amount REAL,
                limit_remaining REAL,

                created_at TEXT NOT NULL
            )
            """
        )

        await db.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_usage_snapshots_provider_created
            ON usage_snapshots (
                provider,
                created_at
            )
            """
        )

        await db.commit()


async def save_snapshot(
    provider: str,
    data: dict,
) -> bool:

    current = (
        float(data.get("usage") or 0),
        float(data.get("usage_daily") or 0),
        float(data.get("usage_weekly") or 0),
        float(data.get("usage_monthly") or 0),
        data.get("limit"),
        data.get("limit_remaining"),
    )

    async with aiosqlite.connect(DATABASE_PATH) as db:

        cursor = await db.execute(
            """
            SELECT
                usage_total,
                usage_daily,
                usage_weekly,
                usage_monthly,
                limit_amount,
                limit_remaining
            FROM usage_snapshots
            WHERE provider = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (provider,),
        )

        previous = await cursor.fetchone()

        if previous is not None:
            if tuple(previous) == current:
                return False

        await db.execute(
            """
            INSERT INTO usage_snapshots (
                provider,
                usage_total,
                usage_daily,
                usage_weekly,
                usage_monthly,
                limit_amount,
                limit_remaining,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                provider,
                *current,
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        await db.commit()

    return True


async def get_history(
    provider: str,
    limit: int = 30,
) -> list[dict]:

    limit = max(1, min(limit, 500))

    async with aiosqlite.connect(DATABASE_PATH) as db:

        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT
                id,
                provider,
                usage_total,
                usage_daily,
                usage_weekly,
                usage_monthly,
                limit_amount,
                limit_remaining,
                created_at
            FROM usage_snapshots
            WHERE provider = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                provider,
                limit,
            ),
        )

        rows = await cursor.fetchall()

    return [
        dict(row)
        for row in rows
    ]

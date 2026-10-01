import os
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite


DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    "/app/data/dashboard.db",
)


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


async def init_db():
    Path(DATABASE_PATH).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    async with aiosqlite.connect(DATABASE_PATH) as db:

        # OpenRouter usage history
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

        # Provider balance history
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS balance_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                provider TEXT NOT NULL,
                currency TEXT NOT NULL,

                total_balance REAL NOT NULL DEFAULT 0,
                topped_up_balance REAL NOT NULL DEFAULT 0,
                granted_balance REAL NOT NULL DEFAULT 0,

                created_at TEXT NOT NULL
            )
            """
        )

        await db.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_balance_snapshots_provider_created
            ON balance_snapshots (
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
                utc_now(),
            ),
        )

        await db.commit()

    return True


async def get_history(
    provider: str,
    limit: int = 30,
) -> list[dict]:

    limit = max(
        1,
        min(limit, 500),
    )

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


async def save_balance_snapshot(
    provider: str,
    currency: str,
    total_balance: float,
    topped_up_balance: float,
    granted_balance: float,
) -> bool:

    current = (
        float(total_balance),
        float(topped_up_balance),
        float(granted_balance),
    )

    async with aiosqlite.connect(DATABASE_PATH) as db:

        cursor = await db.execute(
            """
            SELECT
                total_balance,
                topped_up_balance,
                granted_balance
            FROM balance_snapshots
            WHERE
                provider = ?
                AND currency = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                provider,
                currency,
            ),
        )

        previous = await cursor.fetchone()

        if previous is not None:
            if tuple(previous) == current:
                return False

        await db.execute(
            """
            INSERT INTO balance_snapshots (
                provider,
                currency,
                total_balance,
                topped_up_balance,
                granted_balance,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                provider,
                currency,
                current[0],
                current[1],
                current[2],
                utc_now(),
            ),
        )

        await db.commit()

    return True


async def get_balance_history(
    provider: str,
    currency: str = "USD",
    limit: int = 30,
) -> list[dict]:

    limit = max(
        1,
        min(limit, 500),
    )

    async with aiosqlite.connect(DATABASE_PATH) as db:

        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT
                id,
                provider,
                currency,
                total_balance,
                topped_up_balance,
                granted_balance,
                created_at
            FROM balance_snapshots
            WHERE
                provider = ?
                AND currency = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                provider,
                currency,
                limit,
            ),
        )

        rows = await cursor.fetchall()

    return [
        dict(row)
        for row in rows
    ]

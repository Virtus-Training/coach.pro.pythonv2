"""SQLite database manager with migration support."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterator


class DBManager:
    """Singleton service managing SQLite connection and migrations."""

    _instance: DBManager | None = None

    def __init__(self) -> None:
        self.db_path = Path("db/app.db")
        self.migrations_path = Path("db/migrations")
        self.conn = self._connect()
        self._apply_migrations()
        self._verify_integrity()

    @classmethod
    def get_instance(cls) -> "DBManager":
        """Return the single :class:`DBManager` instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _connect(self) -> sqlite3.Connection:
        """Create a SQLite connection with WAL mode enabled.

        The database file is created if missing. If the file exists but is
        corrupt, it is removed and recreated to avoid application crashes.
        """
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.migrations_path.mkdir(parents=True, exist_ok=True)

        need_init = False
        if self.db_path.exists():
            try:
                tmp_conn = sqlite3.connect(self.db_path)
                status = tmp_conn.execute("PRAGMA integrity_check").fetchone()[0]
                tmp_conn.close()
                if status.lower() != "ok":
                    need_init = True
            except sqlite3.DatabaseError:
                need_init = True
        else:
            need_init = True

        if need_init and self.db_path.exists():
            self.db_path.unlink()

        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _apply_migrations(self) -> None:
        """Apply pending SQL migrations from ``db/migrations`` directory."""
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                applied_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        row = self.conn.execute("SELECT MAX(version) FROM schema_migrations").fetchone()
        current_version = row[0] if row[0] is not None else 0

        for path in self._migration_files():
            version = int(path.stem.split("_", 1)[0])
            if version > current_version:
                script = path.read_text()
                try:
                    self.conn.execute("BEGIN")
                    self.conn.executescript(script)
                    self.conn.execute(
                        "INSERT INTO schema_migrations (version) VALUES (?)",
                        (version,),
                    )
                    self.conn.commit()
                    current_version = version
                except sqlite3.Error as exc:
                    self.conn.rollback()
                    raise exc

    def _migration_files(self) -> Iterator[Path]:
        """Yield migration files ordered by their version prefix."""
        return iter(sorted(self.migrations_path.glob("*.sql")))

    def _verify_integrity(self) -> None:
        """Run SQLite integrity check to ensure database is valid."""
        result = self.conn.execute("PRAGMA integrity_check").fetchone()[0]
        if result.lower() != "ok":  # pragma: no cover - defensive programming
            raise sqlite3.DatabaseError(f"Integrity check failed: {result}")

    def get_connection(self) -> sqlite3.Connection:
        """Return the active SQLite connection."""
        return self.conn


__all__ = ["DBManager"]

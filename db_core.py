import os
import sys
import sqlite3
import random
from typing import Optional, List, Tuple


def app_dir() -> str:
    # Works for .py and for packaged .exe (PyInstaller)
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


DB_FILE = os.path.join(app_dir(), "prison.db")


class PrisonRepo:
    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_file)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            # --- core tables ---
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prisons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    location TEXT NOT NULL,
                    capacity INTEGER NOT NULL CHECK(capacity >= 0)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS prisoners (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    dob TEXT,
                    crime TEXT,
                    prison_id INTEGER NOT NULL,
                    FOREIGN KEY(prison_id) REFERENCES prisons(id) ON DELETE RESTRICT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_prisoners_name ON prisoners(full_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_prisoners_prison ON prisoners(prison_id)")

            # --- NEW: guards ---
            conn.execute("""
                CREATE TABLE IF NOT EXISTS guards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prison_id INTEGER NOT NULL,
                    rank TEXT NOT NULL,
                    FOREIGN KEY(prison_id) REFERENCES prisons(id) ON DELETE RESTRICT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_guards_prison ON guards(prison_id)")

            # --- NEW: audit log (simple) ---
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL DEFAULT (datetime('now')),
                    entity TEXT NOT NULL,      -- 'prisoner' or 'guard'
                    action TEXT NOT NULL,      -- 'added' or 'deleted'
                    entity_id INTEGER NOT NULL,
                    prison_id INTEGER
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_log(ts)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_log(entity, action)")

            # --- Triggers: only INSERT/DELETE for prisoners + guards ---
            conn.execute("DROP TRIGGER IF EXISTS trg_prisoners_ai")
            conn.execute("DROP TRIGGER IF EXISTS trg_prisoners_ad")
            conn.execute("DROP TRIGGER IF EXISTS trg_guards_ai")
            conn.execute("DROP TRIGGER IF EXISTS trg_guards_ad")

            conn.execute("""
                CREATE TRIGGER trg_prisoners_ai
                AFTER INSERT ON prisoners
                BEGIN
                    INSERT INTO audit_log(entity, action, entity_id, prison_id)
                    VALUES ('prisoner', 'added', NEW.id, NEW.prison_id);
                END;
            """)
            conn.execute("""
                CREATE TRIGGER trg_prisoners_ad
                AFTER DELETE ON prisoners
                BEGIN
                    INSERT INTO audit_log(entity, action, entity_id, prison_id)
                    VALUES ('prisoner', 'deleted', OLD.id, OLD.prison_id);
                END;
            """)

            conn.execute("""
                CREATE TRIGGER trg_guards_ai
                AFTER INSERT ON guards
                BEGIN
                    INSERT INTO audit_log(entity, action, entity_id, prison_id)
                    VALUES ('guard', 'added', NEW.id, NEW.prison_id);
                END;
            """)
            conn.execute("""
                CREATE TRIGGER trg_guards_ad
                AFTER DELETE ON guards
                BEGIN
                    INSERT INTO audit_log(entity, action, entity_id, prison_id)
                    VALUES ('guard', 'deleted', OLD.id, OLD.prison_id);
                END;
            """)

    # -----------------
    # Prisons
    # -----------------
    def add_prison(self, name: str, location: str, capacity: int) -> int:
        name = name.strip()
        location = location.strip()
        if not name:
            raise ValueError("Prison name is required.")
        if not location:
            raise ValueError("Prison location is required.")
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO prisons(name, location, capacity) VALUES (?, ?, ?)",
                (name, location, capacity)
            )
            return cur.lastrowid

    def list_prisons(self) -> List[Tuple]:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT id, name, location, capacity FROM prisons ORDER BY name"
            )
            return cur.fetchall()

    def prison_population(self, prison_id: int) -> int:
        with self._connect() as conn:
            cur = conn.execute("SELECT COUNT(*) FROM prisoners WHERE prison_id = ?", (prison_id,))
            return int(cur.fetchone()[0])

    def prison_guard_count(self, prison_id: int) -> int:
        with self._connect() as conn:
            cur = conn.execute("SELECT COUNT(*) FROM guards WHERE prison_id = ?", (prison_id,))
            return int(cur.fetchone()[0])

    def prison_contents(self, prison_id: int) -> List[Tuple]:
        with self._connect() as conn:
            cur = conn.execute("""
                SELECT p.id, p.full_name, p.dob, p.crime
                FROM prisoners p
                WHERE p.prison_id = ?
                ORDER BY p.full_name
            """, (prison_id,))
            return cur.fetchall()

    def delete_prison(self, prison_id: int) -> None:
        # Friendly errors (FK would restrict anyway)
        if self.prison_population(prison_id) > 0:
            raise ValueError("Cannot delete prison: it still has prisoners.")
        if self.prison_guard_count(prison_id) > 0:
            raise ValueError("Cannot delete prison: it still has guards.")
        with self._connect() as conn:
            conn.execute("DELETE FROM prisons WHERE id = ?", (prison_id,))

    def _get_prison_capacity(self, prison_id: int) -> Optional[int]:
        with self._connect() as conn:
            cur = conn.execute("SELECT capacity FROM prisons WHERE id = ?", (prison_id,))
            row = cur.fetchone()
            return int(row[0]) if row else None
    
    def prison_guard_count(self, prison_id: int) -> int:
        with self._connect() as conn:
            cur = conn.execute("SELECT COUNT(*) FROM guards WHERE prison_id = ?", (prison_id,))
            return int(cur.fetchone()[0])


    # -----------------
    # Prisoners
    # -----------------
    def get_random_available_prison(self) -> Optional[int]:
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT p.id
                FROM prisons p
                WHERE (
                    SELECT COUNT(*)
                    FROM prisoners pr
                    WHERE pr.prison_id = p.id
                ) < p.capacity
            """).fetchall()
        if not rows:
            return None
        return random.choice(rows)[0]

    def add_prisoner(
        self,
        full_name: str,
        dob: Optional[str] = None,
        crime: Optional[str] = None,
        prison_id: Optional[int] = None
    ) -> int:
        full_name = full_name.strip()
        if not full_name:
            raise ValueError("full_name cannot be empty")

        if prison_id is None:
            prison_id = self.get_random_available_prison()
            if prison_id is None:
                raise ValueError("No prisons with free capacity available.")

        pop = self.prison_population(prison_id)
        cap = self._get_prison_capacity(prison_id)
        if cap is None:
            raise ValueError("Prison does not exist.")
        if pop >= cap:
            raise ValueError("Prison is at full capacity.")

        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO prisoners(full_name, dob, crime, prison_id) VALUES (?, ?, ?, ?)",
                (full_name, dob, crime, prison_id)
            )
            return cur.lastrowid

    def delete_prisoner(self, prisoner_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM prisoners WHERE id = ?", (prisoner_id,))

    def search_prisoners(self, text: str) -> List[Tuple]:
        q = f"%{text.strip()}%"
        with self._connect() as conn:
            cur = conn.execute("""
                SELECT p.id, p.full_name, p.dob, p.crime,
                       pr.id as prison_id, pr.name as prison_name
                FROM prisoners p
                JOIN prisons pr ON pr.id = p.prison_id
                WHERE p.full_name LIKE ? OR p.crime LIKE ?
                ORDER BY p.full_name
            """, (q, q))
            return cur.fetchall()

    def list_prisoners(self) -> List[Tuple]:
        with self._connect() as conn:
            cur = conn.execute("""
                SELECT p.id, p.full_name, p.dob, p.crime,
                       pr.id as prison_id, pr.name as prison_name
                FROM prisoners p
                JOIN prisons pr ON pr.id = p.prison_id
                ORDER BY p.id DESC
            """)
            return cur.fetchall()

    # -----------------
    # Guards
    # -----------------
    def add_guard(self, prison_id: int, rank: str) -> int:
        rank = rank.strip()
        if not rank:
            raise ValueError("Rank is required.")
        if self._get_prison_capacity(prison_id) is None:
            raise ValueError("Prison does not exist.")
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO guards(prison_id, rank) VALUES (?, ?)",
                (prison_id, rank)
            )
            return cur.lastrowid

    def update_guard(self, guard_id: int, prison_id: int, rank: str) -> None:
        rank = rank.strip()
        if not rank:
            raise ValueError("Rank is required.")
        if self._get_prison_capacity(prison_id) is None:
            raise ValueError("Prison does not exist.")
        with self._connect() as conn:
            conn.execute(
                "UPDATE guards SET prison_id = ?, rank = ? WHERE id = ?",
                (prison_id, rank, guard_id)
            )

    def delete_guard(self, guard_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM guards WHERE id = ?", (guard_id,))

    def list_guards(self) -> List[Tuple]:
        with self._connect() as conn:
            cur = conn.execute("""
                SELECT g.id, g.prison_id, pr.name as prison_name, g.rank
                FROM guards g
                JOIN prisons pr ON pr.id = g.prison_id
                ORDER BY g.id DESC
            """)
            return cur.fetchall()

    def search_guards(self, text: str) -> List[Tuple]:
        q = f"%{text.strip()}%"
        with self._connect() as conn:
            cur = conn.execute("""
                SELECT g.id, g.prison_id, pr.name as prison_name, g.rank
                FROM guards g
                JOIN prisons pr ON pr.id = g.prison_id
                WHERE g.rank LIKE ? OR pr.name LIKE ?
                ORDER BY g.id DESC
            """, (q, q))
            return cur.fetchall()

    # -----------------
    # Audit
    # -----------------
    def list_audit(self, limit: int = 200) -> List[Tuple]:
        with self._connect() as conn:
            cur = conn.execute("""
                SELECT id, ts, entity, action, entity_id, prison_id
                FROM audit_log
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            return cur.fetchall()

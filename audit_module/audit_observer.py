"""
audit_observer.py
-----------------
Implements the Observer design pattern for the Prison Management System's audit logging.

Pattern:  Observer (Behavioral, GoF)
Subject:  PrisonEventPublisher  — fires events when prisoners/guards are added or deleted
Observer: AuditLogObserver       — writes each event to the SQLite audit_log table

This module is intentionally decoupled from db_core.py and gui_app.py so it can be
extended (e.g. a future EmailAlertObserver) without touching existing code.
"""

from __future__ import annotations

import sqlite3
from abc import ABC, abstractmethod
from typing import List


# ---------------------------------------------------------------------------
# Observer interface
# ---------------------------------------------------------------------------

class AuditObserver(ABC):
    """Abstract base class for all observers that react to prison events."""

    @abstractmethod
    def on_event(self, entity: str, action: str, entity_id: int, prison_id: int | None) -> None:
        """
        Called by the publisher whenever a tracked event occurs.

        Parameters
        ----------
        entity    : 'prisoner' or 'guard'
        action    : 'added'    or 'deleted'
        entity_id : primary key of the affected row
        prison_id : the prison the entity belongs to (may be None)
        """


# ---------------------------------------------------------------------------
# Concrete observer — writes to audit_log
# ---------------------------------------------------------------------------

class AuditLogObserver(AuditObserver):
    """
    Writes audit events to the audit_log table in the SQLite database.
    This mirrors what the SQL triggers already do, making the pattern
    explicit at the application layer for demonstration purposes.
    """

    def __init__(self, db_file: str) -> None:
        self._db_file = db_file

    def on_event(self, entity: str, action: str, entity_id: int, prison_id: int | None) -> None:
        with sqlite3.connect(self._db_file) as conn:
            conn.execute(
                """
                INSERT INTO audit_log(entity, action, entity_id, prison_id)
                VALUES (?, ?, ?, ?)
                """,
                (entity, action, entity_id, prison_id),
            )


# ---------------------------------------------------------------------------
# Subject (Publisher)
# ---------------------------------------------------------------------------

class PrisonEventPublisher:
    """
    Maintains a list of observers and notifies them when a prison-related
    event (prisoner added, guard deleted, etc.) occurs.

    Usage
    -----
        publisher = PrisonEventPublisher()
        publisher.subscribe(AuditLogObserver(DB_FILE))

        # Later, after inserting a prisoner:
        publisher.notify("prisoner", "added", new_id, prison_id)
    """

    def __init__(self) -> None:
        self._observers: List[AuditObserver] = []

    def subscribe(self, observer: AuditObserver) -> None:
        """Register a new observer."""
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: AuditObserver) -> None:
        """Remove a previously registered observer."""
        self._observers.remove(observer)

    def notify(self, entity: str, action: str, entity_id: int, prison_id: int | None = None) -> None:
        """Broadcast an event to all registered observers."""
        for observer in self._observers:
            observer.on_event(entity, action, entity_id, prison_id)


# ---------------------------------------------------------------------------
# Quick smoke-test (run this file directly to verify the wiring)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os, tempfile

    # Create a temporary DB with the audit_log table
    tmp = tempfile.mktemp(suffix=".db")
    with sqlite3.connect(tmp) as conn:
        conn.execute("""
            CREATE TABLE audit_log (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                ts        TEXT NOT NULL DEFAULT (datetime('now')),
                entity    TEXT NOT NULL,
                action    TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                prison_id INTEGER
            )
        """)

    publisher = PrisonEventPublisher()
    publisher.subscribe(AuditLogObserver(tmp))

    publisher.notify("prisoner", "added",   entity_id=42, prison_id=1)
    publisher.notify("guard",    "deleted",  entity_id=7,  prison_id=1)

    with sqlite3.connect(tmp) as conn:
        rows = conn.execute("SELECT entity, action, entity_id FROM audit_log").fetchall()

    print("Audit log entries:")
    for row in rows:
        print(" ", row)

    os.remove(tmp)
    print("Smoke-test passed.")

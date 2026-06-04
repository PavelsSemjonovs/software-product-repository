# Audit Module — Observer Pattern

## Selected Pattern: Observer (Behavioral, GoF)

### Why Observer?

The Prison Management System already tracks every prisoner and guard insertion/deletion through SQLite triggers. The **Observer pattern** formalises this "something happened → something reacts" relationship at the application layer, making the architecture explicit and extensible.

The fit is natural:

| System concept | Observer role |
|---|---|
| Add/delete a prisoner or guard | **Event** (notification trigger) |
| `PrisonEventPublisher` | **Subject** — knows that something happened |
| `AuditLogObserver` | **Concrete Observer** — reacts by writing to `audit_log` |
| Future: `EmailAlertObserver` | New observer, **zero changes** to existing code |

An alternative like the **Command** pattern would have worked for undo/redo, but the system has no such requirement. **Strategy** would be appropriate if the *way* records are saved needed to change at runtime — it does not. Observer is the minimal, correct fit.

---

## Module Structure

```
audit_module/
├── audit_observer.py   # Pattern implementation
└── README.md           # This file
```

### Key classes

| Class | Role |
|---|---|
| `AuditObserver` | Abstract base — defines the `on_event()` interface |
| `AuditLogObserver` | Concrete observer — writes events to the SQLite `audit_log` table |
| `PrisonEventPublisher` | Subject — holds the observer list and fires `notify()` |

---

## How This Module Interacts with the Rest of the System

```
gui_app.py
    │
    │  user clicks "Add prisoner"
    ▼
db_core.py  ──► PrisonRepo.add_prisoner()
    │
    │  after INSERT succeeds
    ▼
PrisonEventPublisher.notify("prisoner", "added", new_id, prison_id)
    │
    ▼
AuditLogObserver.on_event()  ──► writes row to audit_log table
```

The GUI (`gui_app.py`) and database layer (`db_core.py`) do not need to know about the observer list. The publisher is created once at application startup and injected wherever events should be fired.

> **Note:** The existing SQL triggers in `db_core.py` already write to `audit_log` at the database level. This module makes the same logic visible and testable at the Python layer, in line with the assignment requirement to demonstrate the pattern in code.

---

## Prompt Used with AI Agent

> *"Implement an audit notification system for the Prison Management System using the Observer pattern. Create a `PrisonEventPublisher` (Subject) and an `AuditLogObserver` (Concrete Observer) that writes to the existing `audit_log` SQLite table. The observer interface must be abstract so future observers (e.g. email alerts) can be added without modifying existing classes. Follow the constraints in AGENTS.md: Python only, SQLite, no new external dependencies."*

---

## Compliance with AGENTS.md

- Python only — no new dependencies introduced
- SQLite used for persistence
- Does not modify the existing database schema
- Audit log functionality is preserved and extended, not replaced
- Code is modular and focused on a single responsibility

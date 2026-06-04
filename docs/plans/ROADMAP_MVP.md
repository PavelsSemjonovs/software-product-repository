# Prison Management System MVP Roadmap

## Project goal

The goal of this project is to provide a simple desktop application for managing a prison database. The system allows the user to manage prisons, prisoners, guards, audit records, and computed cell assignments using a Tkinter graphical interface and an SQLite database.

## Current system

The current project already includes:

- SQLite database initialization.
- Prison management.
- Prisoner management.
- Guard management.
- Audit log for prisoner and guard insert/delete actions.
- Computed cell assignment view.
- Tkinter GUI with multiple tabs.
- Basic authorization dialog.
- Observer pattern audit module (`audit_module/`).
- Streamlit web interface (`ui_app.py`) connected to backend and Observer pattern.

## MVP scope

The MVP should include:

- Add, view, search, and delete prisoners.
- Add, view, and delete prisons.
- Add, view, update, search, and delete guards.
- Prevent deleting prisons that still contain prisoners or guards.
- Enforce prison capacity limits.
- Display audit records.
- Display computed cell assignments.
- Keep the application usable through a simple desktop GUI.

## Deferred features

The following features are not part of the MVP and may be added later:

- Role-based authentication.
- Password hashing.
- Advanced reporting.
- Export to PDF or Excel.
- Advanced prisoner history tracking.
- Separate cell table in the database.
- Web version of the application.
- Multi-user support.
- Cloud database storage.
- `EmailAlertObserver` — extend audit module with email notifications.

## Stage 1: Stabilize existing project ✅

- Review `db_core.py` and `gui_app.py`.
- Remove duplicated or unnecessary code.
- Check that all tabs load correctly.
- Confirm that database tables are created automatically.
- Confirm that foreign key constraints work correctly.

## Stage 2: Improve input validation ✅

- Validate prison capacity input.
- Validate required fields before database insertion.
- Improve error messages in the GUI.
- Handle invalid IDs gracefully.
- Check empty search behavior.

## Stage 3: Testing ✅

- Test adding and deleting prisons.
- Test adding prisoners until prison capacity is reached.
- Test deleting prisoners and guards.
- Test audit log creation.
- Test guard update behavior.
- Test computed cell assignment logic.

## Stage 4: Design Pattern Implementation ✅

- Feature selected: Audit logging system.
- Pattern selected: Observer (Behavioral, GoF).
- Created `audit_module/` directory with `audit_observer.py` and `README.md`.
- Implemented abstract `AuditObserver` interface.
- Implemented `AuditLogObserver` writing events to the SQLite `audit_log` table.
- Implemented `PrisonEventPublisher` subject managing observer subscriptions.
- Updated architecture diagram to reflect the new module.
- Recorded experiment log in PKM repository.

### Scope adjustments

No scope changes were required. The Observer pattern mapped directly onto the existing audit trigger logic. The module was added as a new directory without modifying `db_core.py` or `gui_app.py`.

## Stage 5: Spec-Driven UI Development ✅

- Created `docs/DESIGN.md` defining the UI design contract (framework, colors, typography, component rules).
- Generated `ui_app.py` — Streamlit web interface following the design contract.
- UI connects to `db_core.py` for all CRUD operations.
- Every add/delete action fires the Observer pattern via `PrisonEventPublisher.notify()`.
- Audit Log section displays all Observer-recorded events.
- Dashboard shows live metrics (prison count, population, capacity, guards).
- Recorded SDD experiment log in PKM repository.

### Scope adjustments

Streamlit was chosen over React/HTML as it requires no additional build tooling and integrates natively with the existing Python codebase. This aligns with the AGENTS.md constraint of keeping the project lightweight.

## Stage 6: Documentation ✅

- Document project structure.
- Explain how to run the application.
- Explain database tables.
- Explain current limitations.
- Update README if needed.

## Stage 7: Final polish

- Clean formatting.
- Remove unused code.
- Make sure the application starts correctly.
- Prepare the repository for public submission.
- Confirm that `AGENTS.md` and `/docs` files are included.

## Success criteria

The MVP is complete when the user can run the desktop application, manage prisons, prisoners, and guards, view audit logs, and see computed cell assignments without database or GUI errors.

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

## Stage 1: Stabilize existing project

- Review `db_core.py` and `gui_app.py`.
- Remove duplicated or unnecessary code.
- Check that all tabs load correctly.
- Confirm that database tables are created automatically.
- Confirm that foreign key constraints work correctly.

## Stage 2: Improve input validation

- Validate prison capacity input.
- Validate required fields before database insertion.
- Improve error messages in the GUI.
- Handle invalid IDs gracefully.
- Check empty search behavior.

## Stage 3: Testing

- Test adding and deleting prisons.
- Test adding prisoners until prison capacity is reached.
- Test deleting prisoners and guards.
- Test audit log creation.
- Test guard update behavior.
- Test computed cell assignment logic.

## Stage 4: Documentation

- Document project structure.
- Explain how to run the application.
- Explain database tables.
- Explain current limitations.
- Update README if needed.

## Stage 5: Final polish

- Clean formatting.
- Remove unused code.
- Make sure the application starts correctly.
- Prepare the repository for public submission.
- Confirm that `AGENTS.md` and `/docs` files are included.

## Success criteria

The MVP is complete when the user can run the desktop application, manage prisons, prisoners, and guards, view audit logs, and see computed cell assignments without database or GUI errors.

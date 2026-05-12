# AGENTS.md

## Project concept

- This repository contains a **Python Prison Management System**.
- The application uses:
  - `db_core.py` for SQLite database logic.
  - `gui_app.py` for the Tkinter desktop interface.
- The system manages prisons, prisoners, guards, audit logs, and computed cell assignments.
- The goal is to keep the project simple, maintainable, and suitable for a university software engineering assignment.

## Required context

- Before making changes, always read the relevant files in `/docs`.
- Start with:
  - `/docs/pm_approach.md`
  - `/docs/plans/ROADMAP_MVP.md`
- Do not invent new features unless they are described in the roadmap or approved by the human developer.

## Technology rules

- Use Python.
- Use SQLite for local database storage.
- Use Tkinter for the graphical user interface.
- Keep the project lightweight and avoid unnecessary external dependencies.
- Keep database logic inside `db_core.py`.
- Keep GUI logic inside `gui_app.py`.

## Coding rules

- Prefer readable and simple code over complex abstractions.
- Use descriptive names for functions, variables, and database fields.
- Validate user input before writing to the database.
- Preserve foreign key rules and database constraints.
- Do not remove audit log functionality.
- Do not change existing database schema without updating documentation.
- Do not hardcode new credentials or sensitive data.
- Keep error messages clear for the user.

## AI assistant responsibilities

- Generate small, focused code improvements.
- Suggest unit tests for database methods.
- Help refactor duplicated code.
- Improve comments and documentation.
- Identify possible edge cases.
- Preserve the existing architecture unless instructed otherwise.

## Human developer responsibilities

- Approve architecture changes.
- Review AI-generated code before merging.
- Decide which features belong in the MVP.
- Test GUI behavior manually.
- Make final decisions about database schema changes.
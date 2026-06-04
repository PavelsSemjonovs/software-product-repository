# Roadmap — Prison Management System MVP

## Status Legend

| Symbol | Meaning |
|---|---|
| ✅ | Complete |
| 🔄 | In Progress |
| 🔲 | Planned |

---

## Stage 1 — Project Setup ✅

- [x] Repository created and structured
- [x] `README.md` written with product idea, problem, and target users
- [x] `AGENTS.md` written with technology rules, coding rules, and AI/human responsibilities
- [x] `/docs` folder created with initial planning documents

---

## Stage 2 — Core Application (MVP) ✅

- [x] SQLite database schema designed (`prisons`, `prisoners`, `guards`, `audit_log`)
- [x] `db_core.py` implemented with full CRUD operations and validation
- [x] `gui_app.py` implemented with Tkinter tabs: Prisoners, Prisons, Guards, Audit, Cells
- [x] Foreign key constraints and capacity validation enforced
- [x] Audit logging via SQL triggers
- [x] Search functionality for prisoners and guards
- [x] Computed cell assignment display

---

## Stage 3 — AI Agent Setup & Documentation ✅

- [x] `AGENTS.md` refined with explicit constraints for AI assistant
- [x] Architecture documented in `/docs/architecture.md`
- [x] Roadmap established in `/docs/plans/roadmap.md`
- [x] Project management approach documented in `/docs/pm_approach.md`

---

## Stage 4 — Design Pattern Implementation ✅

- [x] Feature selected: Audit logging system
- [x] Pattern selected: **Observer (Behavioral, GoF)**
- [x] `audit_module/` directory created
- [x] `audit_module/audit_observer.py` implemented:
  - Abstract `AuditObserver` interface
  - Concrete `AuditLogObserver` writing to SQLite
  - `PrisonEventPublisher` subject managing observer subscriptions
- [x] `audit_module/README.md` written with pattern rationale and integration description
- [x] Architecture diagram updated to reflect new module and dependencies
- [x] Experiment log created in PKM repository

### Scope Adjustments

> No scope changes were required. The Observer pattern mapped directly onto the existing audit trigger logic. The module was added as a new directory without modifying `db_core.py` or `gui_app.py`, consistent with the Open/Closed principle.

---

## Stage 5 — Testing & Refinement 🔲

- [ ] Unit tests for `db_core.py` database methods
- [ ] Unit tests for `AuditLogObserver`
- [ ] Edge case validation (empty inputs, duplicate names, capacity overflow)
- [ ] GUI usability review

---

## Stage 6 — Future Features (Post-MVP) 🔲

- [ ] User authentication with hashed passwords
- [ ] Reporting and data export (CSV)
- [ ] Transfer prisoners between prisons
- [ ] `EmailAlertObserver` — extend audit module with email notifications
- [ ] Cloud storage option

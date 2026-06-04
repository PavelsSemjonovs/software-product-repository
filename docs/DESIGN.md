# DESIGN.md — Prison Management System UI Design Contract

This file defines the strict UI constraints for the Prison Management System's web interface.
All AI-generated frontend code must follow these rules exactly. Deviations are not permitted
without updating this contract first.

---

## 1. Framework Choice

- **Framework:** Streamlit (Python)
- **Reason:** The project is pure Python with no external dependencies. Streamlit integrates
  directly with `db_core.py` and `audit_module/audit_observer.py` without requiring a separate
  frontend build step.
- **Entry point:** `ui_app.py` in the project root.
- **Python version:** 3.8+
- **Install:** `pip install streamlit`

---

## 2. Color Palette

| Role | Hex | Usage |
|---|---|---|
| Primary | `#1B4F72` | Sidebar background, primary buttons, headings |
| Secondary | `#2E86C1` | Highlights, active tab indicators, links |
| Background | `#F4F6F7` | Main page background |
| Surface | `#FFFFFF` | Cards, form containers, table backgrounds |
| Text | `#1C2833` | All body text |
| Text Muted | `#717D7E` | Labels, captions, helper text |
| Success | `#1E8449` | Confirmation messages |
| Error | `#922B21` | Error messages, validation failures |
| Warning | `#B7950B` | Capacity warnings |

---

## 3. Typography & Spacing

- **Page title:** `st.title()` — used once per page only.
- **Section headings:** `st.subheader()` — one per logical section.
- **Body text:** `st.write()` or `st.markdown()` — standard size, color `#1C2833`.
- **Captions / helper text:** `st.caption()` — color `#717D7E`.
- **Spacing rule:** Always use `st.divider()` between major sections.
- **Form padding:** All input forms must be wrapped in `st.form()` with a clear submit button.
- **Metric displays:** Use `st.metric()` for numeric summaries (population, capacity, guard count).

---

## 4. Component Rules

### Buttons
- All action buttons use `st.button()` or `st.form_submit_button()`.
- Destructive actions (delete) must use a confirmation step — never delete on first click.
- Never place two primary action buttons side by side without a `st.columns()` separator.
- Delete buttons must be visually separated from add/edit buttons.

### Tables / Data Display
- All list data is displayed using `st.dataframe()` with `use_container_width=True`.
- Tables must never be replaced with raw `st.write()` for structured data.
- Column headers must use Title Case.

### Forms
- Every form must have a clear label on every input field.
- Optional fields must be marked `(optional)` in the label.
- Required fields must be validated before submission — show `st.error()` inline, never a popup.

### Messages
- Success: `st.success("...")`
- Error: `st.error("...")`
- Warning: `st.warning("...")`
- Info: `st.info("...")`
- Never use `st.write()` for status messages.

### Sidebar
- Navigation between sections (Prisons, Prisoners, Guards, Audit Log) lives in `st.sidebar`.
- Sidebar background styled with Primary color `#1B4F72` via custom CSS.
- Section selector uses `st.sidebar.radio()`.

### Layout
- Use `st.columns()` for side-by-side metrics only.
- Never nest more than 2 levels of columns.
- Page width: wide mode (`st.set_page_config(layout="wide")`).

---

## 5. Connection to Backend (Mandatory)

The UI must connect to the following existing modules:

| UI Action | Backend call |
|---|---|
| Add prison | `PrisonRepo.add_prison()` |
| Delete prison | `PrisonRepo.delete_prison()` |
| Add prisoner | `PrisonRepo.add_prisoner()` + `PrisonEventPublisher.notify()` |
| Delete prisoner | `PrisonRepo.delete_prisoner()` + `PrisonEventPublisher.notify()` |
| Add guard | `PrisonRepo.add_guard()` + `PrisonEventPublisher.notify()` |
| Delete guard | `PrisonRepo.delete_guard()` + `PrisonEventPublisher.notify()` |
| View audit log | `PrisonRepo.list_audit()` |
| Search prisoners | `PrisonRepo.search_prisoners()` |
| Search guards | `PrisonRepo.search_guards()` |

Every add/delete action for prisoners and guards **must** fire the Observer pattern
(`PrisonEventPublisher.notify()`) from `audit_module/audit_observer.py`.

---

## 6. Accessibility Rules

- Every `st.dataframe()` must have a descriptive heading immediately above it.
- Every form must have a visible submit button with a descriptive label (not just "Submit").
- Error messages must describe what went wrong and how to fix it.
- Do not rely on color alone to convey meaning — always pair color with text.

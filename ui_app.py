"""
ui_app.py
---------
Streamlit web interface for the Prison Management System.

Spec: /docs/DESIGN.md
Backend: db_core.py (PrisonRepo)
Pattern: audit_module/audit_observer.py (Observer — PrisonEventPublisher + AuditLogObserver)

Run with:
    pip install streamlit
    streamlit run ui_app.py
"""

import streamlit as st
import pandas as pd
from db_core import PrisonRepo, DB_FILE
from audit_module.audit_observer import PrisonEventPublisher, AuditLogObserver

# ---------------------------------------------------------------------------
# Page config — must be first Streamlit call
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Prison Management System",
    page_icon="🏛️",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Custom CSS — enforce DESIGN.md color palette
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #1B4F72;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #FFFFFF !important;
    }
    h1, h2, h3 {
        color: #1B4F72;
    }
    .stButton > button {
        border-radius: 6px;
        background-color: #2E86C1;
        color: white;
        border: none;
    }
    .stButton > button:hover {
        background-color: #1B4F72;
        color: white;
    }
    .block-container {
        background-color: #F4F6F7;
    }
    /* ── Input fields — force light mode appearance ── */
    input, textarea, [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {
        background-color: #FFFFFF !important;
        color: #1C2833 !important;
    }
    [data-baseweb="input"], [data-baseweb="textarea"],
    [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #AEB6BF !important;
    }
    /* Number input */
    [data-testid="stNumberInput"] input {
        background-color: #FFFFFF !important;
        color: #1C2833 !important;
    }
    /* Select / dropdown */
    [data-baseweb="select"] * {
        background-color: #FFFFFF !important;
        color: #1C2833 !important;
    }
    /* Labels above inputs */
    label[data-testid="stWidgetLabel"] p,
    .stTextInput label, .stNumberInput label,
    .stSelectbox label, .stTextArea label {
        color: #1C2833 !important;
        font-weight: 600;
    }
    /* Form container */
    [data-testid="stForm"] {
        background-color: #FFFFFF;
        border: 1px solid #D0D3D4;
        border-radius: 8px;
        padding: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Initialise backend — repo + observer pattern
# ---------------------------------------------------------------------------

@st.cache_resource
def get_repo():
    return PrisonRepo(DB_FILE)

@st.cache_resource
def get_publisher():
    publisher = PrisonEventPublisher()
    publisher.subscribe(AuditLogObserver(DB_FILE))
    return publisher

repo = get_repo()
publisher = get_publisher()

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------

st.sidebar.title("🏛️ Prison Management")
st.sidebar.caption("Navigation")

section = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Prisons", "Prisoners", "Guards", "Audit Log"],
)

# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

if section == "Dashboard":
    st.title("Prison Management System")
    st.caption("Overview of all facilities")
    st.divider()

    prisons = repo.list_prisons()
    total_capacity = sum(p[3] for p in prisons)
    total_population = sum(repo.prison_population(p[0]) for p in prisons)
    total_guards = sum(repo.prison_guard_count(p[0]) for p in prisons)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Prisons", len(prisons))
    col2.metric("Total Prisoners", total_population)
    col3.metric("Total Capacity", total_capacity)
    col4.metric("Total Guards", total_guards)

    st.divider()
    st.subheader("Facility Overview")

    if prisons:
        rows = []
        for pid, name, location, capacity in prisons:
            population = repo.prison_population(pid)
            guards = repo.prison_guard_count(pid)
            fill_pct = round((population / capacity * 100), 1) if capacity > 0 else 0
            rows.append({
                "ID": pid,
                "Name": name,
                "Location": location,
                "Capacity": capacity,
                "Population": population,
                "Guards": guards,
                "Fill %": f"{fill_pct}%",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info("No prisons registered yet. Go to the Prisons section to add one.")

# ---------------------------------------------------------------------------
# Prisons
# ---------------------------------------------------------------------------

elif section == "Prisons":
    st.title("Prisons")
    st.divider()

    # Add prison form
    st.subheader("Add New Prison")
    with st.form("add_prison_form"):
        col1, col2, col3 = st.columns(3)
        name = col1.text_input("Prison Name")
        location = col2.text_input("Location")
        capacity = col3.number_input("Capacity", min_value=1, step=1, value=50)
        submitted = st.form_submit_button("Add Prison")

    if submitted:
        if not name.strip():
            st.error("Prison name is required.")
        elif not location.strip():
            st.error("Location is required.")
        else:
            try:
                repo.add_prison(name.strip(), location.strip(), int(capacity))
                st.success(f"Prison '{name}' added successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Could not add prison: {e}")

    st.divider()
    st.subheader("All Prisons")

    prisons = repo.list_prisons()
    if prisons:
        rows = []
        for pid, pname, location, cap in prisons:
            pop = repo.prison_population(pid)
            guards = repo.prison_guard_count(pid)
            rows.append({"ID": pid, "Name": pname, "Location": location,
                          "Capacity": cap, "Population": pop, "Guards": guards})
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

        st.divider()
        st.subheader("Delete Prison")
        prison_options = {f"{p[1]} (ID: {p[0]})": p[0] for p in prisons}
        selected = st.selectbox("Select prison to delete", list(prison_options.keys()))
        if st.button("Delete Selected Prison"):
            pid = prison_options[selected]
            try:
                repo.delete_prison(pid)
                st.success(f"Prison deleted.")
                st.rerun()
            except Exception as e:
                st.error(f"Could not delete: {e}")
    else:
        st.info("No prisons found.")

# ---------------------------------------------------------------------------
# Prisoners
# ---------------------------------------------------------------------------

elif section == "Prisoners":
    st.title("Prisoners")
    st.divider()

    st.subheader("Add New Prisoner")
    with st.form("add_prisoner_form"):
        col1, col2 = st.columns(2)
        full_name = col1.text_input("Full Name")
        dob = col2.text_input("Date of Birth (optional)", placeholder="YYYY-MM-DD")
        col3, col4 = st.columns(2)
        crime = col3.text_input("Crime (optional)")
        prisons = repo.list_prisons()
        prison_options = {"Auto-assign to available prison": None}
        prison_options.update({f"{p[1]} (ID: {p[0]})": p[0] for p in prisons})
        prison_choice = col4.selectbox("Prison (optional)", list(prison_options.keys()))
        submitted = st.form_submit_button("Add Prisoner")

    if submitted:
        if not full_name.strip():
            st.error("Full name is required.")
        else:
            try:
                prison_id = prison_options[prison_choice]
                new_id = repo.add_prisoner(
                    full_name.strip(),
                    dob.strip() or None,
                    crime.strip() or None,
                    prison_id,
                )
                # Fire Observer pattern — audit log entry via AuditLogObserver
                publisher.notify("prisoner", "added", new_id, prison_id)
                st.success(f"Prisoner '{full_name}' added (ID: {new_id}).")
                st.rerun()
            except Exception as e:
                st.error(f"Could not add prisoner: {e}")

    st.divider()
    st.subheader("Search Prisoners")
    search_term = st.text_input("Search by name or crime", placeholder="Leave blank to show all")

    if search_term.strip():
        prisoners = repo.search_prisoners(search_term)
    else:
        prisoners = repo.list_prisoners()

    if prisoners:
        df = pd.DataFrame(prisoners, columns=["ID", "Full Name", "DOB", "Crime", "Prison ID", "Prison Name"])
        st.dataframe(df, use_container_width=True)

        st.divider()
        st.subheader("Delete Prisoner")
        prisoner_options = {f"{p[1]} (ID: {p[0]})": p for p in prisoners}
        selected = st.selectbox("Select prisoner to delete", list(prisoner_options.keys()))
        if st.button("Delete Selected Prisoner"):
            row = prisoner_options[selected]
            try:
                repo.delete_prisoner(row[0])
                # Fire Observer pattern
                publisher.notify("prisoner", "deleted", row[0], row[4])
                st.success("Prisoner deleted.")
                st.rerun()
            except Exception as e:
                st.error(f"Could not delete: {e}")
    else:
        st.info("No prisoners found.")

# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------

elif section == "Guards":
    st.title("Guards")
    st.divider()

    prisons = repo.list_prisons()
    if not prisons:
        st.warning("No prisons exist yet. Add a prison before adding guards.")
    else:
        st.subheader("Add New Guard")
        with st.form("add_guard_form"):
            col1, col2 = st.columns(2)
            prison_options = {f"{p[1]} (ID: {p[0]})": p[0] for p in prisons}
            prison_choice = col1.selectbox("Prison", list(prison_options.keys()))
            rank = col2.text_input("Rank")
            submitted = st.form_submit_button("Add Guard")

        if submitted:
            if not rank.strip():
                st.error("Rank is required.")
            else:
                try:
                    prison_id = prison_options[prison_choice]
                    new_id = repo.add_guard(prison_id, rank.strip())
                    # Fire Observer pattern
                    publisher.notify("guard", "added", new_id, prison_id)
                    st.success(f"Guard added (ID: {new_id}).")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not add guard: {e}")

        st.divider()
        st.subheader("Search Guards")
        search_term = st.text_input("Search by rank or prison name", placeholder="Leave blank to show all")

        guards = repo.search_guards(search_term) if search_term.strip() else repo.list_guards()

        if guards:
            df = pd.DataFrame(guards, columns=["ID", "Prison ID", "Prison Name", "Rank"])
            st.dataframe(df, use_container_width=True)

            st.divider()
            st.subheader("Delete Guard")
            guard_options = {f"ID {g[0]} — {g[3]} at {g[2]}": g for g in guards}
            selected = st.selectbox("Select guard to delete", list(guard_options.keys()))
            if st.button("Delete Selected Guard"):
                row = guard_options[selected]
                try:
                    repo.delete_guard(row[0])
                    # Fire Observer pattern
                    publisher.notify("guard", "deleted", row[0], row[1])
                    st.success("Guard deleted.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not delete: {e}")
        else:
            st.info("No guards found.")

# ---------------------------------------------------------------------------
# Audit Log
# ---------------------------------------------------------------------------

elif section == "Audit Log":
    st.title("Audit Log")
    st.caption("All add and delete events for prisoners and guards, recorded by the Observer pattern.")
    st.divider()

    col1, col2 = st.columns([1, 3])
    limit = col1.number_input("Show last N entries", min_value=10, max_value=1000, value=100, step=10)

    records = repo.list_audit(limit=int(limit))

    if records:
        df = pd.DataFrame(records, columns=["ID", "Timestamp", "Entity", "Action", "Entity ID", "Prison ID"])
        st.dataframe(df, use_container_width=True)
        st.caption(f"Showing {len(records)} most recent audit entries.")
    else:
        st.info("No audit records yet. Add or delete prisoners and guards to generate entries.")

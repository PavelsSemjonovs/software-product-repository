import tkinter as tk
from tkinter import ttk, messagebox

from db_core import PrisonRepo


class LoginDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Authorization")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.result = False
        self.geometry("320x170")

        ttk.Label(self, text="Username:").pack(pady=(12, 0))
        self.user_var = tk.StringVar()
        user_entry = ttk.Entry(self, textvariable=self.user_var)
        user_entry.pack(fill="x", padx=16, pady=4)

        ttk.Label(self, text="Password:").pack(pady=(8, 0))
        self.pass_var = tk.StringVar()
        pass_entry = ttk.Entry(self, textvariable=self.pass_var, show="*")
        pass_entry.pack(fill="x", padx=16, pady=4)

        btns = ttk.Frame(self)
        btns.pack(pady=12)

        ttk.Button(btns, text="Login", command=self.on_login).pack(side="left", padx=6)
        ttk.Button(btns, text="Cancel", command=self.on_cancel).pack(side="left", padx=6)

        self.grab_set()
        self.lift()
        self.focus_force()
        user_entry.focus_set()

        self.bind("<Return>", lambda e: self.on_login())
        self.bind("<Escape>", lambda e: self.on_cancel())

    def on_login(self):
        u = self.user_var.get().strip()
        p = self.pass_var.get().strip()
        if u == "123" and p == "123":
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Error", "Wrong username or password.")

    def on_cancel(self):
        self.result = False
        self.destroy()


class PrisonApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Prison Management")
        self.geometry("1050x600")

        self.repo = PrisonRepo()

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True)

        self.tab_prisoners = ttk.Frame(self.tabs)
        self.tab_prisons = ttk.Frame(self.tabs)
        self.tab_guards = ttk.Frame(self.tabs)
        self.tab_audit = ttk.Frame(self.tabs)
        self.tab_cells = ttk.Frame(self.tabs)

        self.tabs.add(self.tab_prisoners, text="Prisoners")
        self.tabs.add(self.tab_prisons, text="Prisons")
        self.tabs.add(self.tab_guards, text="Guards")
        self.tabs.add(self.tab_audit, text="Audit")
        self.tabs.add(self.tab_cells, text="Cells")

        self._build_prisoners_tab()
        self._build_prisons_tab()
        self._build_guards_tab()
        self._build_audit_tab()
        self._build_cells_tab()

        self.refresh_prisons()
        self.refresh_prisoners()
        self.refresh_guards()
        self.refresh_audit()
        self.refresh_cells()

    # -----------------
    # Prisoners tab
    # -----------------
    def _build_prisoners_tab(self):
        top = ttk.Frame(self.tab_prisoners)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Label(top, text="Search (name/crime):").pack(side="left")
        self.prisoner_search_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.prisoner_search_var, width=40).pack(side="left", padx=6)

        ttk.Button(top, text="Search", command=self.search_prisoners).pack(side="left")
        ttk.Button(top, text="Show All", command=self.refresh_prisoners).pack(side="left", padx=6)

        cols = ("Prisoner ID", "Full Name", "Date of birth", "Crime", "Prison Name")
        self.prisoners_tree = ttk.Treeview(self.tab_prisoners, columns=cols, show="headings", height=16)
        for c, w in [("Prisoner ID", 70), ("Full Name", 240), ("Date of birth", 110), ("Crime", 240), ("Prison Name", 240)]:
            self.prisoners_tree.heading(c, text=c)
            self.prisoners_tree.column(c, width=w, anchor="w")
        self.prisoners_tree.pack(fill="both", expand=True, padx=10)

        bottom = ttk.LabelFrame(self.tab_prisoners, text="Add / Delete prisoner")
        bottom.pack(fill="x", padx=10, pady=10)

        self.full_name_var = tk.StringVar()
        self.dob_var = tk.StringVar()
        self.crime_var = tk.StringVar()
        self.prison_id_var = tk.StringVar()

        row1 = ttk.Frame(bottom)
        row1.pack(fill="x", pady=4)
        ttk.Label(row1, text="Full name").pack(side="left")
        ttk.Entry(row1, textvariable=self.full_name_var, width=25).pack(side="left", padx=6)
        ttk.Label(row1, text="DOB (YYYY-MM-DD)").pack(side="left", padx=(12, 0))
        ttk.Entry(row1, textvariable=self.dob_var, width=14).pack(side="left", padx=6)
        ttk.Label(row1, text="Crime").pack(side="left", padx=(12, 0))
        ttk.Entry(row1, textvariable=self.crime_var, width=25).pack(side="left", padx=6)

        row2 = ttk.Frame(bottom)
        row2.pack(fill="x", pady=4)
        ttk.Label(row2, text="Prison ID (optional)").pack(side="left")
        ttk.Entry(row2, textvariable=self.prison_id_var, width=10).pack(side="left", padx=6)
        ttk.Button(row2, text="Add prisoner", command=self.add_prisoner).pack(side="left", padx=6)
        ttk.Button(row2, text="Delete selected", command=self.delete_selected_prisoner).pack(side="left", padx=6)

    def refresh_prisoners(self):
        self._load_prisoners(self.repo.list_prisoners())

    def search_prisoners(self):
        text = self.prisoner_search_var.get().strip()
        if not text:
            self.refresh_prisoners()
            return
        self._load_prisoners(self.repo.search_prisoners(text))

    def _load_prisoners(self, rows):
        for item in self.prisoners_tree.get_children():
            self.prisoners_tree.delete(item)
        for r in rows:
            pid, name, dob, crime, prison_id, prison_name = r
            self.prisoners_tree.insert("", "end", values=(pid, name, dob or "", crime or "", prison_name or ""))

    def add_prisoner(self):
        try:
            full_name = self.full_name_var.get().strip()
            dob = self.dob_var.get().strip() or None
            crime = self.crime_var.get().strip() or None

            prison_id_str = self.prison_id_var.get().strip()
            prison_id = int(prison_id_str) if prison_id_str else None

            new_id = self.repo.add_prisoner(full_name, dob, crime, prison_id)

            messagebox.showinfo("OK", f"Added prisoner id={new_id}")
            self.full_name_var.set("")
            self.dob_var.set("")
            self.crime_var.set("")
            self.prison_id_var.set("")

            self.refresh_prisoners()
            self.refresh_prisons()
            self.refresh_cells()
            self.refresh_audit()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_selected_prisoner(self):
        sel = self.prisoners_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a prisoner row first.")
            return

        values = self.prisoners_tree.item(sel[0], "values")
        prisoner_id = int(values[0])

        if not messagebox.askyesno("Confirm", f"Delete prisoner id={prisoner_id}?"):
            return

        try:
            self.repo.delete_prisoner(prisoner_id)
            self.refresh_prisoners()
            self.refresh_prisons()
            self.refresh_cells()
            self.refresh_audit()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # -----------------
    # Prisons tab
    # -----------------
    def _build_prisons_tab(self):
        top = ttk.Frame(self.tab_prisons)
        top.pack(fill="x", padx=10, pady=10)

        self.prison_name_var = tk.StringVar()
        self.prison_location_var = tk.StringVar()
        self.prison_capacity_var = tk.StringVar()

        ttk.Button(top, text="Refresh", command=self.refresh_prisons).pack(side="left")
        ttk.Button(top, text="Delete selected", command=self.delete_selected_prison).pack(side="left", padx=6)

        form = ttk.Frame(self.tab_prisons)
        form.pack(fill="x", padx=10, pady=5)

        ttk.Label(form, text="Name").pack(side="left")
        ttk.Entry(form, textvariable=self.prison_name_var, width=20).pack(side="left", padx=4)

        ttk.Label(form, text="Location").pack(side="left")
        ttk.Entry(form, textvariable=self.prison_location_var, width=20).pack(side="left", padx=4)

        ttk.Label(form, text="Capacity").pack(side="left")
        ttk.Entry(form, textvariable=self.prison_capacity_var, width=8).pack(side="left", padx=4)

        ttk.Button(form, text="Add prison", command=self.add_prison).pack(side="left", padx=6)

        cols = ("Prison ID", "Prison name", "Location", "Capacity", "Population", "Guards")
        self.prisons_tree = ttk.Treeview(self.tab_prisons, columns=cols, show="headings", height=12)
        for c, w in [("Prison ID", 70), ("Prison name", 240), ("Location", 200), ("Capacity", 90), ("Population", 90), ("Guards", 90)]:
            self.prisons_tree.heading(c, text=c)
            self.prisons_tree.column(c, width=w, anchor="w")
        self.prisons_tree.pack(fill="x", padx=10)

        contents_frame = ttk.LabelFrame(self.tab_prisons, text="Prison contents (double-click a prison row)")
        contents_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols2 = ("Prisoner ID", "Full Name", "Date of birth", "Crime")
        self.contents_tree = ttk.Treeview(contents_frame, columns=cols2, show="headings", height=12)
        for c, w in [("Prisoner ID", 90), ("Full Name", 260), ("Date of birth", 120), ("Crime", 420)]:
            self.contents_tree.heading(c, text=c)
            self.contents_tree.column(c, width=w, anchor="w")
        self.contents_tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.prisons_tree.bind("<Double-1>", self.on_prison_double_click)

    def add_prison(self):
        try:
            name = self.prison_name_var.get().strip()
            loc = self.prison_location_var.get().strip()
            cap = int(self.prison_capacity_var.get())
            self.repo.add_prison(name, loc, cap)

            self.prison_name_var.set("")
            self.prison_location_var.set("")
            self.prison_capacity_var.set("")

            self.refresh_prisons()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_selected_prison(self):
        sel = self.prisons_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a prison row first.")
            return

        values = self.prisons_tree.item(sel[0], "values")
        prison_id = int(values[0])

        if not messagebox.askyesno("Confirm", f"Delete prison id={prison_id}?"):
            return

        try:
            self.repo.delete_prison(prison_id)
            self.refresh_prisons()
            self.refresh_prisoners()
            self.refresh_guards()
            self.refresh_cells()
            # audit does NOT track prisons, per your requirement
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_prisons(self):
        for item in self.prisons_tree.get_children():
            self.prisons_tree.delete(item)

        for (pid, name, loc, cap) in self.repo.list_prisons():
            pop = self.repo.prison_population(pid)
            guards = self.repo.prison_guard_count(pid)
            self.prisons_tree.insert("", "end", values=(pid, name, loc, cap, pop, guards))

    def on_prison_double_click(self, event):
        sel = self.prisons_tree.selection()
        if not sel:
            return
        values = self.prisons_tree.item(sel[0], "values")
        prison_id = int(values[0])

        for item in self.contents_tree.get_children():
            self.contents_tree.delete(item)

        for (prisoner_id, full_name, dob, crime) in self.repo.prison_contents(prison_id):
            self.contents_tree.insert("", "end", values=(prisoner_id, full_name, dob or "", crime or ""))

    # -----------------
    # Guards tab
    # -----------------
    def _build_guards_tab(self):
        top = ttk.Frame(self.tab_guards)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Label(top, text="Search (rank/prison):").pack(side="left")
        self.guard_search_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.guard_search_var, width=40).pack(side="left", padx=6)

        ttk.Button(top, text="Search", command=self.search_guards).pack(side="left")
        ttk.Button(top, text="Show All", command=self.refresh_guards).pack(side="left", padx=6)

        cols = ("Guard ID", "Prison ID", "Prison Name", "Rank")
        self.guards_tree = ttk.Treeview(self.tab_guards, columns=cols, show="headings", height=16)
        for c, w in [("Guard ID", 70), ("Prison ID", 90), ("Prison Name", 260), ("Rank", 260)]:
            self.guards_tree.heading(c, text=c)
            self.guards_tree.column(c, width=w, anchor="w")
        self.guards_tree.pack(fill="both", expand=True, padx=10)

        form = ttk.LabelFrame(self.tab_guards, text="Add / Edit / Delete guard")
        form.pack(fill="x", padx=10, pady=10)

        self.guard_prison_id_var = tk.StringVar()
        self.guard_rank_var = tk.StringVar()

        row = ttk.Frame(form)
        row.pack(fill="x", pady=6)

        ttk.Label(row, text="Prison ID").pack(side="left")
        ttk.Entry(row, textvariable=self.guard_prison_id_var, width=10).pack(side="left", padx=6)

        ttk.Label(row, text="Rank").pack(side="left", padx=(10, 0))
        ttk.Entry(row, textvariable=self.guard_rank_var, width=30).pack(side="left", padx=6)

        ttk.Button(row, text="Add", command=self.add_guard).pack(side="left", padx=6)
        ttk.Button(row, text="Update selected", command=self.update_selected_guard).pack(side="left", padx=6)
        ttk.Button(row, text="Delete selected", command=self.delete_selected_guard).pack(side="left", padx=6)

        ttk.Label(form, text="Tip: click a guard row to load it into the form").pack(anchor="w", padx=10, pady=(0, 8))
        self.guards_tree.bind("<<TreeviewSelect>>", self.on_guard_select)

    def on_guard_select(self, event):
        sel = self.guards_tree.selection()
        if not sel:
            return
        values = self.guards_tree.item(sel[0], "values")
        # (id, prison_id, prison_name, rank)
        self.guard_prison_id_var.set(values[1])
        self.guard_rank_var.set(values[3])

    def refresh_guards(self):
        self._load_guards(self.repo.list_guards())

    def search_guards(self):
        text = self.guard_search_var.get().strip()
        if not text:
            self.refresh_guards()
            return
        self._load_guards(self.repo.search_guards(text))

    def _load_guards(self, rows):
        for item in self.guards_tree.get_children():
            self.guards_tree.delete(item)
        for (gid, prison_id, prison_name, rank) in rows:
            self.guards_tree.insert("", "end", values=(gid, prison_id, prison_name, rank))

    def add_guard(self):
        try:
            prison_id = int(self.guard_prison_id_var.get().strip())
            rank = self.guard_rank_var.get().strip()
            new_id = self.repo.add_guard(prison_id, rank)

            messagebox.showinfo("OK", f"Added guard id={new_id}")
            self.guard_prison_id_var.set("")
            self.guard_rank_var.set("")

            self.refresh_guards()
            self.refresh_prisons()
            self.refresh_audit()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_selected_guard(self):
        sel = self.guards_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a guard row first.")
            return
        values = self.guards_tree.item(sel[0], "values")
        guard_id = int(values[0])

        try:
            prison_id = int(self.guard_prison_id_var.get().strip())
            rank = self.guard_rank_var.get().strip()
            self.repo.update_guard(guard_id, prison_id, rank)

            self.refresh_guards()
            self.refresh_prisons()
            # No audit on edits (per your requirement)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_selected_guard(self):
        sel = self.guards_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a guard row first.")
            return
        values = self.guards_tree.item(sel[0], "values")
        guard_id = int(values[0])

        if not messagebox.askyesno("Confirm", f"Delete guard id={guard_id}?"):
            return

        try:
            self.repo.delete_guard(guard_id)
            self.refresh_guards()
            self.refresh_prisons()
            self.refresh_audit()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # -----------------
    # Audit tab
    # -----------------
    def _build_audit_tab(self):
        top = ttk.Frame(self.tab_audit)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Button(top, text="Refresh", command=self.refresh_audit).pack(side="left")

        ttk.Label(top, text="Show last").pack(side="left", padx=(20, 4))
        self.audit_limit_var = tk.StringVar(value="200")
        ttk.Entry(top, textvariable=self.audit_limit_var, width=8).pack(side="left")

        ttk.Button(top, text="Apply", command=self.refresh_audit).pack(side="left", padx=6)

        cols = ("lid", "Timestamp", "Entity", "Action", "Entity ID", "Prison ID")
        self.audit_tree = ttk.Treeview(self.tab_audit, columns=cols, show="headings", height=20)
        widths = {"lid": 70, "Timestamp": 160, "Entity": 100, "Action": 100, "Entity ID": 90, "Prison ID": 90}
        for c in cols:
            self.audit_tree.heading(c, text=c)
            self.audit_tree.column(c, width=widths[c], anchor="w")
        self.audit_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_audit(self):
        for item in self.audit_tree.get_children():
            self.audit_tree.delete(item)

        try:
            limit = int(self.audit_limit_var.get().strip())
        except Exception:
            limit = 200
            self.audit_limit_var.set("200")

        for (aid, ts, entity, action, entity_id, prison_id) in self.repo.list_audit(limit=limit):
            self.audit_tree.insert("", "end", values=(aid, ts, entity, action, entity_id, prison_id if prison_id is not None else ""))

    # -----------------
    # Cells tab (computed: 2 inmates per cell)
    # -----------------
    def _build_cells_tab(self):
        top = ttk.Frame(self.tab_cells)
        top.pack(fill="x", padx=10, pady=10)
        ttk.Button(top, text="Refresh", command=self.refresh_cells).pack(side="left")

        cols = ("Prison ID", "Prison Name", "Cell number", "Prisoner ID", "Full Name")
        self.cells_tree = ttk.Treeview(self.tab_cells, columns=cols, show="headings", height=18)

        widths = {"Prison ID": 80, "Prison Name": 220, "Cell number": 80, "Prisoner ID": 90, "Full Name": 320}
        for c in cols:
            self.cells_tree.heading(c, text=c)
            self.cells_tree.column(c, width=widths[c], anchor="w")

        self.cells_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_cells(self):
        for item in self.cells_tree.get_children():
            self.cells_tree.delete(item)

        for (prison_id, prison_name, loc, cap) in self.repo.list_prisons():
            inmates = self.repo.prison_contents(prison_id)  # (id, full_name, dob, crime)

            cell_no = 1
            i = 0
            while i < len(inmates):
                for j in range(2):
                    if i + j >= len(inmates):
                        break
                    prisoner_id, full_name, dob, crime = inmates[i + j]
                    self.cells_tree.insert("", "end", values=(prison_id, prison_name, cell_no, prisoner_id, full_name))
                i += 2
                cell_no += 1


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    dlg = LoginDialog(root)
    root.wait_window(dlg)

    if dlg.result:
        root.destroy()
        app = PrisonApp()
        app.mainloop()
    else:
        root.destroy()

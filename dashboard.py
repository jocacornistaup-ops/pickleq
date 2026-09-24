"""
dashboard.py
------------
Everything the user sees after logging in: the queue, the court/timer
board, and the usage log - organized into tabs.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import database
import styles


class Dashboard(tk.Tk):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.is_staff = user["role"] == "staff"
        self.alerted_courts = set()  # avoid repeating the "time's up" popup

        self.title("PICKLEQ - Dashboard")
        self.geometry("1080x680")
        self.minsize(900, 600)
        self.configure(bg=styles.OFF_WHITE)

        styles.apply_theme(self)
        self._build_header()
        self._build_tabs()

        self.refresh_all()
        self.after(1000, self._tick)

    # ------------------------------------------------------------------
    def _build_header(self):
        header = tk.Frame(self, bg=styles.NAVY, height=64)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(header, text="🥒 PICKLEQ", font=(styles.FONT_FAMILY, 16, "bold"),
                 fg=styles.WHITE, bg=styles.NAVY).pack(side="left", padx=20)

        role_badge = "Court Staff" if self.is_staff else "Player"
        tk.Label(header, text=f"{self.user['full_name']}  ·  {role_badge}",
                 font=(styles.FONT_FAMILY, 10), fg=styles.SKY, bg=styles.NAVY).pack(side="right", padx=12)

        ttk.Button(header, text="Log Out", style="Outline.TButton",
                   command=self._logout).pack(side="right", padx=8, pady=14)

    def _logout(self):
        self.destroy()
        import login_window
        login_window.LoginWindow(on_success=launch_dashboard).mainloop()

    # ------------------------------------------------------------------
    def _build_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=14)

        self.queue_tab = tk.Frame(self.notebook, bg=styles.OFF_WHITE)
        self.courts_tab = tk.Frame(self.notebook, bg=styles.OFF_WHITE)
        self.log_tab = tk.Frame(self.notebook, bg=styles.OFF_WHITE)

        self.notebook.add(self.queue_tab, text="  Digital Queue  ")
        self.notebook.add(self.courts_tab, text="  Courts & Timer  ")
        self.notebook.add(self.log_tab, text="  Usage Log  ")

        self._build_queue_tab()
        self._build_courts_tab()
        self._build_log_tab()

    # ==================================================================
    # TAB 1 — Digital Queue Joining + Real-Time Queue Display + Group/Team
    # ==================================================================
    def _build_queue_tab(self):
        root = self.queue_tab

        # --- join form (players only see it, staff can also add walk-ins) ---
        form_card = tk.Frame(root, bg=styles.WHITE, highlightbackground="#D7E3EE", highlightthickness=1)
        form_card.pack(fill="x", pady=(0, 12))

        tk.Label(form_card, text="Join the Queue", font=(styles.FONT_FAMILY, 12, "bold"),
                 fg=styles.NAVY, bg=styles.WHITE).grid(row=0, column=0, columnspan=5, sticky="w", padx=14, pady=(10, 2))

        tk.Label(form_card, text="Name / Team Name", bg=styles.WHITE, fg=styles.GREY_TEXT,
                 font=(styles.FONT_FAMILY, 9)).grid(row=1, column=0, sticky="w", padx=14)
        self.party_name_var = tk.StringVar(value=self.user["full_name"])
        styles.rounded_entry(form_card, self.party_name_var, width=24).grid(row=2, column=0, padx=14, pady=(0, 12), ipady=5)

        tk.Label(form_card, text="Party Type", bg=styles.WHITE, fg=styles.GREY_TEXT,
                 font=(styles.FONT_FAMILY, 9)).grid(row=1, column=1, sticky="w")
        self.party_size_var = tk.StringVar(value="Solo (1)")
        size_box = ttk.Combobox(
            form_card, textvariable=self.party_size_var, state="readonly", width=16,
            values=["Solo (1)", "Pair (2)", "Team (4)"]
        )
        size_box.grid(row=2, column=1, padx=10, pady=(0, 12))

        ttk.Button(form_card, text="JOIN QUEUE", style="Blue.TButton",
                   command=self._handle_join_queue).grid(row=2, column=2, padx=10)

        if self.is_staff:
            ttk.Button(form_card, text="Send Next Party to Available Court", style="Outline.TButton",
                       command=self._handle_send_to_court).grid(row=2, column=3, padx=10)

        # --- live queue table ---
        table_card = tk.Frame(root, bg=styles.WHITE, highlightbackground="#D7E3EE", highlightthickness=1)
        table_card.pack(fill="both", expand=True)

        tk.Label(table_card, text="Current Queue (live)", font=(styles.FONT_FAMILY, 12, "bold"),
                 fg=styles.NAVY, bg=styles.WHITE).pack(anchor="w", padx=14, pady=(10, 4))

        columns = ("pos", "name", "size", "joined", "status")
        self.queue_tree = ttk.Treeview(table_card, columns=columns, show="headings", height=10)
        for col, label, width in [
            ("pos", "#", 40), ("name", "Name / Team", 220), ("size", "Party Size", 100),
            ("joined", "Joined At", 160), ("status", "Status", 120)
        ]:
            self.queue_tree.heading(col, text=label)
            self.queue_tree.column(col, width=width, anchor="center" if col != "name" else "w")
        self.queue_tree.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        if self.is_staff:
            btn_row = tk.Frame(table_card, bg=styles.WHITE)
            btn_row.pack(fill="x", padx=14, pady=(0, 12))
            ttk.Button(btn_row, text="Remove Selected", style="Danger.TButton",
                       command=self._handle_remove_selected).pack(side="left")

    def _handle_join_queue(self):
        name = self.party_name_var.get().strip()
        if not name:
            messagebox.showwarning("Missing info", "Please enter a name or team name.")
            return
        size_map = {"Solo (1)": 1, "Pair (2)": 2, "Team (4)": 4}
        size = size_map.get(self.party_size_var.get(), 1)
        database.join_queue(name, size, user_id=self.user["id"])
        messagebox.showinfo("Queued!", f"{name} has been added to the queue.")
        self.refresh_queue()

    def _handle_remove_selected(self):
        selected = self.queue_tree.selection()
        if not selected:
            return
        queue_id = self.queue_tree.item(selected[0], "tags")[0]
        database.remove_from_queue(int(queue_id))
        self.refresh_queue()

    def _handle_send_to_court(self):
        waiting = database.get_waiting_queue()
        if not waiting:
            messagebox.showinfo("Queue empty", "There is no one waiting in the queue.")
            return
        available = [c for c in database.get_courts() if c["status"] == "available"]
        if not available:
            messagebox.showinfo("No courts free", "All courts are currently occupied.")
            return

        next_party = waiting[0]
        court = available[0]
        minutes = self._ask_minutes()
        if minutes is None:
            return
        ok, msg = database.start_session(court["id"], next_party["id"], minutes)
        if ok:
            messagebox.showinfo("Court assigned", f"{next_party['party_name']} is now playing on {court['name']}.")
        else:
            messagebox.showerror("Couldn't start session", msg)
        self.refresh_all()

    def _ask_minutes(self):
        popup = tk.Toplevel(self)
        popup.title("Session Length")
        popup.geometry("280x150")
        popup.configure(bg=styles.WHITE)
        popup.grab_set()

        tk.Label(popup, text="Session length (minutes)", bg=styles.WHITE,
                 fg=styles.NAVY, font=(styles.FONT_FAMILY, 10, "bold")).pack(pady=(16, 6))
        minutes_var = tk.StringVar(value="15")
        styles.rounded_entry(popup, minutes_var, width=10).pack(ipady=5)

        result = {"value": None}

        def confirm():
            try:
                result["value"] = int(minutes_var.get())
            except ValueError:
                messagebox.showwarning("Invalid", "Enter a whole number of minutes.")
                return
            popup.destroy()

        ttk.Button(popup, text="Start Session", style="Blue.TButton", command=confirm).pack(pady=14)
        self.wait_window(popup)
        return result["value"]

    def refresh_queue(self):
        for row in self.queue_tree.get_children():
            self.queue_tree.delete(row)
        for i, q in enumerate(database.get_waiting_queue(), start=1):
            joined = datetime.fromisoformat(q["join_time"]).strftime("%I:%M %p")
            self.queue_tree.insert(
                "", "end",
                values=(i, q["party_name"], q["party_size"], joined, q["status"].title()),
                tags=(str(q["id"]),)
            )

    # ==================================================================
    # TAB 2 — Courts & Automated Rotation Timer + Notification Alerts
    # ==================================================================
    def _build_courts_tab(self):
        root = self.courts_tab
        tk.Label(root, text="Court Status", font=(styles.FONT_FAMILY, 12, "bold"),
                 fg=styles.NAVY, bg=styles.OFF_WHITE).pack(anchor="w", pady=(0, 8))

        self.courts_frame = tk.Frame(root, bg=styles.OFF_WHITE)
        self.courts_frame.pack(fill="both", expand=True)
        self.court_widgets = {}  # court_id -> dict of widget refs

    def refresh_courts(self):
        courts = database.get_courts()

        # (re)build cards only if the set of courts changed
        if set(self.court_widgets.keys()) != {c["id"] for c in courts}:
            for w in self.courts_frame.winfo_children():
                w.destroy()
            self.court_widgets.clear()
            for i, c in enumerate(courts):
                self._build_court_card(c, i)

        for c in courts:
            self._update_court_card(c)

    def _build_court_card(self, court, index):
        card = tk.Frame(self.courts_frame, bg=styles.WHITE, highlightbackground="#D7E3EE",
                         highlightthickness=1, width=230, height=200)
        card.grid(row=index // 4, column=index % 4, padx=10, pady=10, sticky="n")
        card.grid_propagate(False)

        name_lbl = tk.Label(card, text=court["name"], font=(styles.FONT_FAMILY, 13, "bold"),
                             fg=styles.NAVY, bg=styles.WHITE)
        name_lbl.pack(pady=(16, 4))

        status_lbl = tk.Label(card, text="", font=(styles.FONT_FAMILY, 10, "bold"), bg=styles.WHITE)
        status_lbl.pack()

        party_lbl = tk.Label(card, text="", font=(styles.FONT_FAMILY, 10), fg=styles.GREY_TEXT, bg=styles.WHITE)
        party_lbl.pack(pady=(6, 0))

        timer_lbl = tk.Label(card, text="", font=(styles.FONT_FAMILY, 20, "bold"), fg=styles.BLUE, bg=styles.WHITE)
        timer_lbl.pack(pady=(8, 8))

        action_btn = ttk.Button(card, text="End Session", style="Danger.TButton",
                                 command=lambda cid=court["id"]: self._handle_end_session(cid))

        self.court_widgets[court["id"]] = {
            "card": card, "status": status_lbl, "party": party_lbl,
            "timer": timer_lbl, "action": action_btn,
        }

    def _update_court_card(self, court):
        widgets = self.court_widgets[court["id"]]
        occupied = court["status"] == "occupied"

        widgets["status"].config(
            text="● OCCUPIED" if occupied else "● AVAILABLE",
            fg=styles.DANGER if occupied else styles.SUCCESS,
        )
        widgets["party"].config(text=f"Playing: {court['current_party']}" if occupied else "Ready for next party")

        if occupied:
            start = datetime.fromisoformat(court["session_start"])
            elapsed = (datetime.now() - start).total_seconds()
            remaining = court["session_minutes"] * 60 - elapsed

            if remaining <= 0:
                widgets["timer"].config(text="TIME'S UP", fg=styles.DANGER)
                self._maybe_notify(court)
            else:
                mins, secs = divmod(int(remaining), 60)
                color = styles.DANGER if remaining <= 60 else styles.BLUE
                widgets["timer"].config(text=f"{mins:02d}:{secs:02d}", fg=color)
                if remaining <= 60:
                    self._maybe_notify(court, ending_soon=True)

            if self.is_staff:
                widgets["action"].pack(pady=(0, 12))
        else:
            widgets["timer"].config(text="--:--", fg=styles.GREY_TEXT)
            widgets["action"].pack_forget()

    def _maybe_notify(self, court, ending_soon=False):
        key = (court["id"], "soon" if ending_soon else "done")
        if key in self.alerted_courts:
            return
        self.alerted_courts.add(key)
        if ending_soon:
            messagebox.showinfo("⏰ Notification", f"{court['name']} is about to be ready — 1 minute left!")
        else:
            messagebox.showinfo("⏰ Notification", f"Time's up on {court['name']}! Please rotate to the next party.")

    def _handle_end_session(self, court_id):
        database.end_session(court_id)
        self.alerted_courts = {k for k in self.alerted_courts if k[0] != court_id}
        self.refresh_all()

    # ==================================================================
    # TAB 3 — Court Usage Log
    # ==================================================================
    def _build_log_tab(self):
        root = self.log_tab
        tk.Label(root, text="Court Usage History", font=(styles.FONT_FAMILY, 12, "bold"),
                 fg=styles.NAVY, bg=styles.OFF_WHITE).pack(anchor="w", pady=(0, 8))

        card = tk.Frame(root, bg=styles.WHITE, highlightbackground="#D7E3EE", highlightthickness=1)
        card.pack(fill="both", expand=True)

        columns = ("court", "party", "start", "end", "duration")
        self.log_tree = ttk.Treeview(card, columns=columns, show="headings", height=14)
        for col, label, width in [
            ("court", "Court", 100), ("party", "Party", 200), ("start", "Start Time", 170),
            ("end", "End Time", 170), ("duration", "Duration (min)", 120)
        ]:
            self.log_tree.heading(col, text=label)
            self.log_tree.column(col, width=width, anchor="center" if col != "party" else "w")
        self.log_tree.pack(fill="both", expand=True, padx=14, pady=14)

    def refresh_log(self):
        for row in self.log_tree.get_children():
            self.log_tree.delete(row)
        for entry in database.get_usage_log():
            start = datetime.fromisoformat(entry["start_time"]).strftime("%b %d, %I:%M %p")
            end = datetime.fromisoformat(entry["end_time"]).strftime("%b %d, %I:%M %p")
            self.log_tree.insert(
                "", "end",
                values=(entry["court_name"], entry["party_name"], start, end, entry["duration_minutes"])
            )

    # ------------------------------------------------------------------
    def refresh_all(self):
        self.refresh_queue()
        self.refresh_courts()
        self.refresh_log()

    def _tick(self):
        """Runs once a second so timers and the queue stay live for everyone."""
        self.refresh_courts()
        self.after(1000, self._tick)


def launch_dashboard(user):
    Dashboard(user).mainloop()

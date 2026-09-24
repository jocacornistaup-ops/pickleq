"""
login_window.py
----------------
The very first thing the user sees: a full-window blue -> white gradient
with a centered white "card" holding the login (and register) form.
"""

import tkinter as tk
from tkinter import ttk, messagebox

import database
import styles


class LoginWindow(tk.Tk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success  # callback(user_dict) called after a good login

        self.title("PICKLEQ - Sign In")
        self.geometry("980x640")
        self.minsize(820, 560)
        self.configure(bg=styles.WHITE)

        styles.apply_theme(self)

        # ---- background gradient canvas ----
        self.bg_canvas = tk.Canvas(self, highlightthickness=0, bd=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_canvas.bind("<Configure>", self._on_resize)

        # ---- centered white card ----
        self.card = tk.Frame(self, bg=styles.WHITE, highlightthickness=0)
        self.card_width = 400
        self.card_height = 460
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=self.card_width, height=self.card_height)

        self._build_login_form()

    # ------------------------------------------------------------------
    def _on_resize(self, event):
        styles.draw_vertical_gradient(self.bg_canvas, event.width, event.height, styles.BLUE, styles.WHITE)

    def _clear_card(self):
        for widget in self.card.winfo_children():
            widget.destroy()

    # ------------------------------------------------------------------
    # LOGIN FORM
    # ------------------------------------------------------------------
    def _build_login_form(self):
        self._clear_card()
        card = self.card

        tk.Label(card, text="🥒", font=("Segoe UI Emoji", 28), bg=styles.WHITE).pack(pady=(28, 0))
        tk.Label(
            card, text="PICKLEQ", font=(styles.FONT_FAMILY, 20, "bold"),
            fg=styles.NAVY, bg=styles.WHITE
        ).pack()
        tk.Label(
            card, text="Pickleball Court Queue Assistant", font=(styles.FONT_FAMILY, 9),
            fg=styles.GREY_TEXT, bg=styles.WHITE
        ).pack(pady=(0, 18))

        form = tk.Frame(card, bg=styles.WHITE)
        form.pack(fill="x", padx=40)

        tk.Label(form, text="Username", font=(styles.FONT_FAMILY, 9, "bold"),
                 fg=styles.NAVY, bg=styles.WHITE, anchor="w").pack(fill="x")
        self.username_var = tk.StringVar()
        styles.rounded_entry(form, self.username_var).pack(fill="x", pady=(2, 12), ipady=6)

        tk.Label(form, text="Password", font=(styles.FONT_FAMILY, 9, "bold"),
                 fg=styles.NAVY, bg=styles.WHITE, anchor="w").pack(fill="x")
        self.password_var = tk.StringVar()
        pw_entry = styles.rounded_entry(form, self.password_var, show="•")
        pw_entry.pack(fill="x", pady=(2, 4), ipady=6)
        pw_entry.bind("<Return>", lambda e: self._handle_login())

        self.login_role_var = tk.StringVar(value="player")
        role_row = tk.Frame(form, bg=styles.WHITE)
        role_row.pack(fill="x", pady=(6, 16))
        tk.Radiobutton(role_row, text="Player", variable=self.login_role_var, value="player",
                        bg=styles.WHITE, fg=styles.GREY_TEXT, selectcolor=styles.OFF_WHITE,
                        font=(styles.FONT_FAMILY, 9)).pack(side="left")
        tk.Radiobutton(role_row, text="Court Staff", variable=self.login_role_var, value="staff",
                        bg=styles.WHITE, fg=styles.GREY_TEXT, selectcolor=styles.OFF_WHITE,
                        font=(styles.FONT_FAMILY, 9)).pack(side="left", padx=(14, 0))

        ttk.Button(form, text="LOG IN", style="Blue.TButton",
                   command=self._handle_login).pack(fill="x", pady=(0, 10))

        switch_row = tk.Frame(card, bg=styles.WHITE)
        switch_row.pack(pady=(4, 0))
        tk.Label(switch_row, text="No account yet?", font=(styles.FONT_FAMILY, 9),
                 fg=styles.GREY_TEXT, bg=styles.WHITE).pack(side="left")
        link = tk.Label(switch_row, text="Register", font=(styles.FONT_FAMILY, 9, "bold"),
                         fg=styles.BLUE, bg=styles.WHITE, cursor="hand2")
        link.pack(side="left", padx=(4, 0))
        link.bind("<Button-1>", lambda e: self._build_register_form())

        tk.Label(card, text="Default staff login — admin / admin123",
                 font=(styles.FONT_FAMILY, 8), fg="#A9B7C3", bg=styles.WHITE).pack(side="bottom", pady=10)

    def _handle_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()
        if not username or not password:
            messagebox.showwarning("Missing info", "Please enter both your username and password.")
            return

        user = database.verify_user(username, password)
        if user is None:
            messagebox.showerror("Login failed", "Incorrect username or password.")
            return

        wanted_role = self.login_role_var.get()
        if user["role"] != wanted_role:
            messagebox.showerror(
                "Wrong login type",
                f"That account is registered as '{user['role']}', not '{wanted_role}'."
            )
            return

        self.destroy()
        self.on_success(user)

    # ------------------------------------------------------------------
    # REGISTER FORM
    # ------------------------------------------------------------------
    def _build_register_form(self):
        self._clear_card()
        card = self.card

        tk.Label(card, text="Create an Account", font=(styles.FONT_FAMILY, 17, "bold"),
                 fg=styles.NAVY, bg=styles.WHITE).pack(pady=(30, 2))
        tk.Label(card, text="Join PICKLEQ as a player", font=(styles.FONT_FAMILY, 9),
                 fg=styles.GREY_TEXT, bg=styles.WHITE).pack(pady=(0, 14))

        form = tk.Frame(card, bg=styles.WHITE)
        form.pack(fill="x", padx=40)

        def labeled_entry(label_text, show=None):
            tk.Label(form, text=label_text, font=(styles.FONT_FAMILY, 9, "bold"),
                      fg=styles.NAVY, bg=styles.WHITE, anchor="w").pack(fill="x")
            var = tk.StringVar()
            styles.rounded_entry(form, var, show=show).pack(fill="x", pady=(2, 10), ipady=5)
            return var

        self.reg_fullname_var = labeled_entry("Full Name")
        self.reg_username_var = labeled_entry("Username")
        self.reg_password_var = labeled_entry("Password", show="•")

        ttk.Button(form, text="CREATE ACCOUNT", style="Blue.TButton",
                   command=self._handle_register).pack(fill="x", pady=(6, 8))

        switch_row = tk.Frame(card, bg=styles.WHITE)
        switch_row.pack()
        tk.Label(switch_row, text="Already have an account?", font=(styles.FONT_FAMILY, 9),
                 fg=styles.GREY_TEXT, bg=styles.WHITE).pack(side="left")
        link = tk.Label(switch_row, text="Log In", font=(styles.FONT_FAMILY, 9, "bold"),
                         fg=styles.BLUE, bg=styles.WHITE, cursor="hand2")
        link.pack(side="left", padx=(4, 0))
        link.bind("<Button-1>", lambda e: self._build_login_form())

    def _handle_register(self):
        full_name = self.reg_fullname_var.get().strip()
        username = self.reg_username_var.get().strip()
        password = self.reg_password_var.get()

        if not full_name or not username or not password:
            messagebox.showwarning("Missing info", "Please fill in every field.")
            return
        if len(password) < 4:
            messagebox.showwarning("Weak password", "Password should be at least 4 characters.")
            return

        ok, msg = database.create_user(full_name, username, password, role="player")
        if ok:
            messagebox.showinfo("Success", msg + "\nYou can now log in.")
            self._build_login_form()
        else:
            messagebox.showerror("Registration failed", msg)

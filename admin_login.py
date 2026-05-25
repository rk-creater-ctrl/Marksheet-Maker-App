import os
import tkinter as tk
from tkinter import messagebox, ttk

from ui_theme import COLORS, FONT, configure_style, create_logo_mark, maximize, set_window_icon


ADMIN_PASSWORD = os.environ.get("SCHOOL_MARKSHEET_ADMIN_PASSWORD", "admin123")


class AdminLoginFrame(ttk.Frame):
    def __init__(self, parent, on_success, on_back):
        super().__init__(parent, style="App.TFrame")
        self.on_success = on_success
        self.on_back = on_back
        self.password_var = tk.StringVar()
        self.status_var = tk.StringVar(value="")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build()

    def _build(self):
        header = tk.Frame(self, bg=COLORS["brand"], highlightthickness=0)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 24))
        header.columnconfigure(2, weight=1)

        tk.Frame(header, bg=COLORS["rose"], width=8).grid(row=0, column=0, rowspan=3, sticky="ns")
        ttk.Button(header, text="Back", style="Ghost.TButton", command=self.on_back).grid(
            row=0, column=1, columnspan=2, sticky="w", padx=22, pady=(18, 0)
        )
        create_logo_mark(header, size=56, background=COLORS["brand"]).grid(row=1, column=1, rowspan=2, padx=(22, 0), pady=(12, 18))
        tk.Label(
            header,
            text="Admin Login",
            bg=COLORS["brand"],
            fg="#ffffff",
            font=(FONT, 24, "bold"),
        ).grid(row=1, column=2, sticky="w", padx=16, pady=(12, 0))
        tk.Label(
            header,
            text="Secure access for student records and marksheet publishing",
            bg=COLORS["brand"],
            fg="#cbd5e1",
            font=(FONT, 10),
        ).grid(row=2, column=2, sticky="w", padx=16, pady=(2, 18))

        card = tk.Frame(self, bg=COLORS["surface"], highlightbackground=COLORS["border"], highlightthickness=1)
        card.grid(row=1, column=0, sticky="")
        card.columnconfigure(0, weight=1)

        tk.Frame(card, bg=COLORS["rose"], height=6).grid(row=0, column=0, sticky="ew")
        content = ttk.Frame(card, style="Surface.TFrame", padding=28)
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)

        badge = tk.Canvas(content, width=58, height=58, bg=COLORS["surface"], highlightthickness=0)
        badge.grid(row=0, column=0, sticky="w", pady=(0, 14))
        badge.create_oval(4, 4, 54, 54, fill=COLORS["rose_soft"], outline=COLORS["rose"], width=2)
        badge.create_rectangle(22, 27, 38, 39, fill=COLORS["rose"], outline=COLORS["rose"])
        badge.create_arc(20, 14, 40, 34, start=0, extent=180, outline=COLORS["rose"], width=3, style="arc")

        ttk.Label(content, text="Enter Admin Password", style="Section.TLabel").grid(row=1, column=0, sticky="w")
        entry = ttk.Entry(content, textvariable=self.password_var, show="*", font=("Segoe UI", 12), width=34)
        entry.grid(row=2, column=0, sticky="ew", pady=(14, 10))
        entry.focus_set()
        entry.bind("<Return>", lambda _event: self._login())

        ttk.Label(content, textvariable=self.status_var, style="Muted.TLabel").grid(row=3, column=0, sticky="w", pady=(0, 16))
        ttk.Button(content, text="Login", style="Primary.TButton", command=self._login).grid(row=4, column=0, sticky="ew")

    def _login(self):
        if self.password_var.get() == ADMIN_PASSWORD:
            self.status_var.set("")
            self.on_success()
            return

        self.password_var.set("")
        self.status_var.set("Password did not match.")
        messagebox.showerror("Login Failed", "Wrong admin password.")


def start():
    root = tk.Tk()
    root.title("Admin Login")
    maximize(root)
    configure_style(root)
    set_window_icon(root)
    container = ttk.Frame(root, style="App.TFrame", padding=(28, 24))
    container.pack(fill="both", expand=True)

    def clear_container():
        for child in container.winfo_children():
            child.destroy()

    def show_login():
        clear_container()
        root.title("Admin Login")
        frame = AdminLoginFrame(container, on_success=show_panel, on_back=root.destroy)
        frame.pack(fill="both", expand=True)

    def show_panel():
        from admin_panel import AdminPanelFrame

        clear_container()
        root.title("Admin Panel - School Marksheet System")
        frame = AdminPanelFrame(container, on_back=show_login)
        frame.pack(fill="both", expand=True)

    show_login()
    root.mainloop()


if __name__ == "__main__":
    start()

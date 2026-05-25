import tkinter as tk
from tkinter import ttk

from admin_login import AdminLoginFrame
from admin_panel import AdminPanelFrame
from data_store import DataStoreError, DB_FILE, list_records
from ui_theme import COLORS, FONT, configure_style, create_logo_mark, maximize, set_window_icon
from user_view import UserViewFrame


APP_TITLE = "School Marksheet System"


class SchoolMarksheetApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        maximize(self.root)
        configure_style(self.root)
        set_window_icon(self.root)

        self.container = ttk.Frame(self.root, style="App.TFrame", padding=(28, 24))
        self.container.pack(fill="both", expand=True)
        self.current_frame = None

        self.show_home()

    def run(self):
        self.root.mainloop()

    def _swap(self, frame_factory):
        if self.current_frame is not None:
            self.current_frame.destroy()

        self.current_frame = frame_factory(self.container)
        self.current_frame.pack(fill="both", expand=True)

    def show_home(self):
        self._swap(
            lambda parent: HomeFrame(
                parent,
                on_admin=self.show_admin_login,
                on_student=self.show_student_portal,
            )
        )

    def show_admin_login(self):
        self._swap(
            lambda parent: AdminLoginFrame(
                parent,
                on_success=self.show_admin_panel,
                on_back=self.show_home,
            )
        )

    def show_admin_panel(self):
        self._swap(lambda parent: AdminPanelFrame(parent, on_back=self.show_home))

    def show_student_portal(self):
        self._swap(lambda parent: UserViewFrame(parent, on_back=self.show_home))


class HomeFrame(ttk.Frame):
    def __init__(self, parent, on_admin, on_student):
        super().__init__(parent, style="App.TFrame")
        self.on_admin = on_admin
        self.on_student = on_student

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = tk.Frame(self, bg=COLORS["brand"], highlightthickness=0)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 28))
        header.columnconfigure(2, weight=1)

        tk.Frame(header, bg=COLORS["primary"], width=8).grid(row=0, column=0, rowspan=3, sticky="ns")
        create_logo_mark(header, size=74, background=COLORS["brand"]).grid(row=0, column=1, rowspan=2, padx=(24, 0))
        tk.Label(
            header,
            text=APP_TITLE,
            bg=COLORS["brand"],
            fg="#ffffff",
            font=(FONT, 30, "bold"),
        ).grid(row=0, column=2, sticky="w", padx=18, pady=(22, 2))
        tk.Label(
            header,
            text="Create, manage, search, and export academic marksheets",
            bg=COLORS["brand"],
            fg="#cbd5e1",
            font=(FONT, 11),
        ).grid(row=1, column=2, sticky="w", padx=18, pady=(0, 22))

        strip = tk.Frame(header, bg=COLORS["brand"], height=8)
        strip.grid(row=2, column=1, columnspan=2, sticky="ew")
        strip.columnconfigure((0, 1, 2, 3), weight=1, uniform="strip")
        for index, color in enumerate((COLORS["primary"], COLORS["secondary"], COLORS["accent"], COLORS["rose"])):
            tk.Frame(strip, bg=color, height=8).grid(row=0, column=index, sticky="ew")

        body = ttk.Frame(self, style="App.TFrame")
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure((0, 1), weight=1, uniform="home")
        body.rowconfigure(1, weight=1)

        stats = self._build_stats(body)
        stats.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 18))

        self._action_panel(
            body,
            column=0,
            title="Admin Panel",
            details="Manage student records, subjects, marks, and PDF exports.",
            button_text="Open Admin",
            command=self.on_admin,
        )
        self._action_panel(
            body,
            column=1,
            title="Student Result Portal",
            details="Search saved results by session and roll number.",
            button_text="View Result",
            command=self.on_student,
        )

    def _build_stats(self, parent):
        panel = ttk.Frame(parent, style="App.TFrame")
        panel.columnconfigure((0, 1, 2), weight=1, uniform="stats")

        try:
            records = list_records()
            sessions = {record["session"] for record in records}
            values = [
                ("Students", str(len(records))),
                ("Sessions", str(len(sessions))),
                ("Data File", DB_FILE.name),
            ]
        except DataStoreError as exc:
            values = [("Students", "0"), ("Sessions", "0"), ("Data File", str(exc))]

        accents = [
            (COLORS["primary_soft"], COLORS["primary_dark"]),
            (COLORS["secondary_soft"], COLORS["secondary_dark"]),
            (COLORS["accent_soft"], COLORS["accent_dark"]),
        ]
        for index, (label, value) in enumerate(values):
            bg, fg = accents[index]
            cell = tk.Frame(panel, bg=bg, highlightbackground=COLORS["border"], highlightthickness=1, padx=16, pady=14)
            cell.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 16, 0))
            tk.Label(cell, text=value, bg=bg, fg=fg, font=(FONT, 22, "bold")).pack(anchor="w")
            tk.Label(cell, text=label.upper(), bg=bg, fg=COLORS["muted"], font=(FONT, 9, "bold")).pack(
                anchor="w", pady=(3, 0)
            )

        return panel

    def _action_panel(self, parent, column, title, details, button_text, command):
        colors = (
            (COLORS["primary"], COLORS["primary_soft"], "A", "Primary.TButton"),
            (COLORS["secondary"], COLORS["secondary_soft"], "S", "Secondary.TButton"),
        )
        accent, soft, initial, button_style = colors[column]

        panel = tk.Frame(parent, bg=COLORS["surface"], highlightbackground=COLORS["border"], highlightthickness=1)
        panel.grid(row=1, column=column, sticky="nsew", padx=(0, 10) if column == 0 else (10, 0))
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)

        tk.Frame(panel, bg=accent, height=7).grid(row=0, column=0, sticky="ew")
        content = tk.Frame(panel, bg=COLORS["surface"], padx=26, pady=24)
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(2, weight=1)

        badge = tk.Canvas(content, width=54, height=54, bg=COLORS["surface"], highlightthickness=0)
        badge.grid(row=0, column=0, sticky="w")
        badge.create_oval(3, 3, 51, 51, fill=soft, outline=accent, width=2)
        badge.create_text(27, 28, text=initial, fill=accent, font=(FONT, 18, "bold"))

        ttk.Label(content, text=title, style="Section.TLabel").grid(row=1, column=0, sticky="w", pady=(18, 8))
        ttk.Label(content, text=details, style="Muted.TLabel", wraplength=360).grid(row=2, column=0, sticky="nw")
        ttk.Button(content, text=button_text, style=button_style, command=command).grid(
            row=3, column=0, sticky="w", pady=(28, 0)
        )


if __name__ == "__main__":
    SchoolMarksheetApp().run()

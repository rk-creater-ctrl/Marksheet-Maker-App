import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from data_store import DataStoreError, default_output_path, get_student, load_db
from marksheet_utils import calculate_summary, get_grade, subject_obtained
from pdf_generator import generate_pdf
from ui_theme import COLORS, FONT, configure_style, create_logo_mark, maximize, set_window_icon


class UserViewFrame(ttk.Frame):
    def __init__(self, parent, on_back):
        super().__init__(parent, style="App.TFrame")
        self.on_back = on_back
        self.current_record = None
        self.current_roll = ""
        self.current_session = ""

        self.session_var = tk.StringVar()
        self.roll_var = tk.StringVar()
        self.status_var = tk.StringVar(value="")

        self.school_var = tk.StringVar(value="-")
        self.name_var = tk.StringVar(value="-")
        self.father_var = tk.StringVar(value="-")
        self.mother_var = tk.StringVar(value="-")
        self.class_var = tk.StringVar(value="-")
        self.dob_var = tk.StringVar(value="-")
        self.total_var = tk.StringVar(value="-")
        self.percent_var = tk.StringVar(value="-")
        self.result_var = tk.StringVar(value="-")
        self.division_var = tk.StringVar(value="-")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self._build()
        self.reload_sessions()

    def _build(self):
        header = tk.Frame(self, bg=COLORS["brand"], highlightthickness=0)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        header.columnconfigure(2, weight=1)

        tk.Frame(header, bg=COLORS["info"], width=8).grid(row=0, column=0, rowspan=3, sticky="ns")
        ttk.Button(header, text="Back", style="Ghost.TButton", command=self.on_back).grid(
            row=0, column=1, columnspan=2, sticky="w", padx=22, pady=(18, 0)
        )
        create_logo_mark(header, size=56, background=COLORS["brand"]).grid(row=1, column=1, rowspan=2, padx=(22, 0), pady=(12, 18))
        tk.Label(
            header,
            text="Student Result Portal",
            bg=COLORS["brand"],
            fg="#ffffff",
            font=(FONT, 24, "bold"),
        ).grid(row=1, column=2, sticky="w", padx=16, pady=(12, 0))
        tk.Label(
            header,
            textvariable=self.status_var,
            bg=COLORS["brand"],
            fg="#cbd5e1",
            font=(FONT, 10),
        ).grid(row=2, column=2, sticky="w", padx=16, pady=(2, 18))

        search = ttk.Frame(self, style="Card.TFrame", padding=16)
        search.grid(row=1, column=0, sticky="ew", pady=(0, 18))
        search.columnconfigure(1, weight=1)

        tk.Frame(search, bg=COLORS["primary"], height=6).grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 12))
        ttk.Label(search, text="Session", style="Muted.TLabel").grid(row=1, column=0, sticky="w")
        self.session_combo = ttk.Combobox(search, textvariable=self.session_var, state="readonly", width=18)
        self.session_combo.grid(row=2, column=0, sticky="ew", padx=(0, 12), pady=(5, 0))

        ttk.Label(search, text="Roll Number", style="Muted.TLabel").grid(row=1, column=1, sticky="w")
        roll_entry = ttk.Entry(search, textvariable=self.roll_var, font=("Segoe UI", 10))
        roll_entry.grid(row=2, column=1, sticky="ew", padx=(0, 12), pady=(5, 0))
        roll_entry.bind("<Return>", lambda _event: self.search_result())

        ttk.Button(search, text="Search", style="Primary.TButton", command=self.search_result).grid(
            row=2, column=2, sticky="ew", padx=(0, 10), pady=(5, 0)
        )
        ttk.Button(search, text="Refresh", style="Ghost.TButton", command=self.reload_sessions).grid(
            row=2, column=3, sticky="ew", pady=(5, 0)
        )

        content = ttk.Frame(self, style="App.TFrame")
        content.grid(row=2, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)

        self._build_result_header(content)
        self._build_subject_table(content)

    def _build_result_header(self, parent):
        panel = ttk.Frame(parent, style="Card.TFrame", padding=18)
        panel.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        panel.columnconfigure((0, 1, 2, 3), weight=1, uniform="summary")

        tk.Frame(panel, bg=COLORS["secondary"], height=6).grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 12))
        ttk.Label(panel, textvariable=self.school_var, style="Section.TLabel").grid(
            row=1, column=0, columnspan=4, sticky="w", pady=(0, 12)
        )

        details = [
            ("Student", self.name_var),
            ("Father", self.father_var),
            ("Mother", self.mother_var),
            ("Class", self.class_var),
            ("DOB", self.dob_var),
            ("Total", self.total_var),
            ("Percentage", self.percent_var),
            ("Division", self.division_var),
        ]
        for index, (label, variable) in enumerate(details):
            row = 2 + (index // 4) * 2
            column = index % 4
            ttk.Label(panel, text=label.upper(), style="Muted.TLabel").grid(row=row, column=column, sticky="w", padx=(0, 14))
            ttk.Label(panel, textvariable=variable, style="TLabel").grid(
                row=row + 1, column=column, sticky="w", padx=(0, 14), pady=(3, 12)
            )

        ttk.Label(panel, text="RESULT", style="Muted.TLabel").grid(row=6, column=0, sticky="w")
        self.result_label = ttk.Label(panel, textvariable=self.result_var, style="SuccessBadge.TLabel", padding=(12, 6))
        self.result_label.grid(row=7, column=0, sticky="w")

        self.export_button = ttk.Button(panel, text="Download PDF", style="Primary.TButton", command=self.export_pdf, state="disabled")
        self.export_button.grid(row=7, column=3, sticky="e")

    def _build_subject_table(self, parent):
        panel = ttk.Frame(parent, style="Card.TFrame", padding=16)
        panel.grid(row=1, column=0, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(2, weight=1)

        tk.Frame(panel, bg=COLORS["accent"], height=6).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        ttk.Label(panel, text="Subjects", style="Section.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 12))

        columns = ("subject", "theory", "practical", "max", "obtained", "grade")
        self.subjects_tree = ttk.Treeview(panel, columns=columns, show="headings")
        headings = {
            "subject": "Subject",
            "theory": "Theory",
            "practical": "Practical",
            "max": "Max",
            "obtained": "Obtained",
            "grade": "Grade",
        }
        widths = {"subject": 320, "theory": 90, "practical": 100, "max": 80, "obtained": 100, "grade": 80}
        for column, heading in headings.items():
            self.subjects_tree.heading(column, text=heading)
            self.subjects_tree.column(column, width=widths[column], anchor="w")

        self.subjects_tree.grid(row=2, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(panel, orient="vertical", command=self.subjects_tree.yview)
        scrollbar.grid(row=2, column=1, sticky="ns")
        self.subjects_tree.configure(yscrollcommand=scrollbar.set)

    def reload_sessions(self):
        try:
            db = load_db()
        except DataStoreError as exc:
            self.status_var.set(str(exc))
            self.session_combo.configure(values=[])
            return

        sessions = sorted(db.keys(), reverse=True)
        self.session_combo.configure(values=sessions)
        if sessions and not self.session_var.get():
            self.session_var.set(sessions[0])
        self.status_var.set(f"{len(sessions)} session(s) available.")

    def search_result(self):
        session = self.session_var.get().strip()
        roll = self.roll_var.get().strip()
        if not session or not roll:
            messagebox.showerror("Search Failed", "Enter both session and roll number.")
            return

        try:
            record = get_student(session, roll)
        except DataStoreError as exc:
            messagebox.showerror("Search Failed", str(exc))
            return

        if not record:
            self.current_record = None
            self.export_button.configure(state="disabled")
            self.status_var.set("No result found.")
            messagebox.showerror("Not Found", "Result not found for this session and roll number.")
            return

        self.current_record = record
        self.current_roll = roll
        self.current_session = session
        self._render_record(record)
        self.export_button.configure(state="normal")
        self.status_var.set(f"Showing roll {roll} from {session}.")

    def _render_record(self, record):
        school = record.get("school", {})
        student = record.get("student", {})
        subjects = record.get("subjects", [])
        summary = calculate_summary(subjects)

        self.school_var.set(str(school.get("name", "School")))
        self.name_var.set(str(student.get("name", "-")))
        self.father_var.set(str(student.get("father", "-")))
        self.mother_var.set(str(student.get("mother", "-")))
        self.class_var.set(str(student.get("class", "-")))
        self.dob_var.set(str(student.get("dob", "-")))
        self.total_var.set(f"{summary['total_obtained']} / {summary['total_max']}")
        self.percent_var.set(f"{summary['percentage']:.2f}%")
        self.result_var.set(summary["result"])
        self.division_var.set(summary["division"])
        self.result_label.configure(style="SuccessBadge.TLabel" if summary["result"] == "PASS" else "DangerBadge.TLabel")

        for item in self.subjects_tree.get_children():
            self.subjects_tree.delete(item)

        for subject in subjects:
            obtained = subject_obtained(subject)
            max_marks = int(subject.get("max", 0) or 0)
            self.subjects_tree.insert(
                "",
                "end",
                values=(
                    subject.get("name", ""),
                    subject.get("theory", 0),
                    subject.get("practical", 0),
                    max_marks,
                    obtained,
                    get_grade(obtained, max_marks),
                ),
            )

    def export_pdf(self):
        if not self.current_record:
            messagebox.showerror("PDF Failed", "Search and load a result first.")
            return

        initial_path = default_output_path(self.current_session, self.current_roll)
        save_path = filedialog.asksaveasfilename(
            parent=self,
            title="Save Marksheet PDF",
            initialdir=str(initial_path.parent),
            initialfile=initial_path.name,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
        )
        if not save_path:
            return

        try:
            generated = generate_pdf(save_path, self.current_roll, self.current_record, session=self.current_session)
        except Exception as exc:
            messagebox.showerror("PDF Failed", str(exc))
            return

        self.status_var.set(f"Generated {generated}.")
        messagebox.showinfo("PDF Generated", f"PDF saved to:\n{generated}")


def start():
    root = tk.Tk()
    root.title("Student Result Portal")
    maximize(root)
    configure_style(root)
    set_window_icon(root)
    frame = UserViewFrame(root, on_back=root.destroy)
    frame.pack(fill="both", expand=True, padx=28, pady=24)
    root.mainloop()


if __name__ == "__main__":
    start()

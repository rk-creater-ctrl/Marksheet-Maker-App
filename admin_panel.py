from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from data_store import DataStoreError, default_output_path, get_student, list_records, save_student
from marksheet_utils import calculate_summary, get_grade, subject_obtained
from pdf_generator import generate_pdf
from ui_theme import COLORS, FONT, configure_style, create_logo_mark, maximize, set_window_icon


def _current_session():
    today = datetime.now()
    start_year = today.year if today.month >= 4 else today.year - 1
    return f"{start_year}-{str(start_year + 1)[-2:]}"


def _parse_int(value, label):
    try:
        number = int(str(value).strip())
    except ValueError as exc:
        raise ValueError(f"{label} must be a whole number.") from exc

    if number < 0:
        raise ValueError(f"{label} cannot be negative.")
    return number


class AdminPanelFrame(ttk.Frame):
    def __init__(self, parent, on_back):
        super().__init__(parent, style="App.TFrame")
        self.on_back = on_back
        self.subjects = []
        self.editing_subject_index = None
        self.record_index = {}
        self.status_var = tk.StringVar(value="")

        self.school_name_var = tk.StringVar(value="ABC PUBLIC SCHOOL")
        self.school_address_var = tk.StringVar(value="Rewa, Madhya Pradesh")
        self.session_var = tk.StringVar(value=_current_session())
        self.roll_var = tk.StringVar()
        self.class_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.father_var = tk.StringVar()
        self.mother_var = tk.StringVar()
        self.dob_var = tk.StringVar()

        self.subject_name_var = tk.StringVar()
        self.theory_var = tk.StringVar(value="0")
        self.practical_var = tk.StringVar(value="0")
        self.max_var = tk.StringVar(value="100")
        self.summary_var = tk.StringVar(value="No subjects added.")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build()
        self.reload_records()

    def _build(self):
        header = tk.Frame(self, bg=COLORS["brand"], highlightthickness=0)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        header.columnconfigure(2, weight=1)

        tk.Frame(header, bg=COLORS["secondary"], width=8).grid(row=0, column=0, rowspan=3, sticky="ns")
        ttk.Button(header, text="Back", style="Ghost.TButton", command=self.on_back).grid(
            row=0, column=1, columnspan=2, sticky="w", padx=22, pady=(18, 0)
        )
        create_logo_mark(header, size=56, background=COLORS["brand"]).grid(row=1, column=1, rowspan=2, padx=(22, 0), pady=(12, 18))
        tk.Label(
            header,
            text="Admin Panel",
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

        body = ttk.Frame(self, style="App.TFrame")
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_records_panel(body)
        self._build_editor_panel(body)

    def _build_records_panel(self, parent):
        panel = ttk.Frame(parent, style="Card.TFrame", padding=14)
        panel.grid(row=0, column=0, sticky="nsw", padx=(0, 16))
        panel.configure(width=330)
        panel.grid_propagate(False)
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(2, weight=1)

        tk.Frame(panel, bg=COLORS["primary"], height=6).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        title_row = ttk.Frame(panel, style="Surface.TFrame")
        title_row.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        title_row.columnconfigure(0, weight=1)
        ttk.Label(title_row, text="Saved Records", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Button(title_row, text="Refresh", style="Ghost.TButton", command=self.reload_records).grid(row=0, column=1)

        columns = ("session", "roll", "name")
        self.records_tree = ttk.Treeview(panel, columns=columns, show="headings", height=18)
        self.records_tree.heading("session", text="Session")
        self.records_tree.heading("roll", text="Roll")
        self.records_tree.heading("name", text="Name")
        self.records_tree.column("session", width=82, anchor="w")
        self.records_tree.column("roll", width=68, anchor="w")
        self.records_tree.column("name", width=150, anchor="w")
        self.records_tree.grid(row=2, column=0, sticky="nsew")
        self.records_tree.bind("<Double-1>", lambda _event: self.load_selected_record())

        scrollbar = ttk.Scrollbar(panel, orient="vertical", command=self.records_tree.yview)
        scrollbar.grid(row=2, column=1, sticky="ns")
        self.records_tree.configure(yscrollcommand=scrollbar.set)

        ttk.Button(panel, text="Load Selected", style="Primary.TButton", command=self.load_selected_record).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(14, 0)
        )

    def _build_editor_panel(self, parent):
        panel = ttk.Frame(parent, style="Card.TFrame", padding=16)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)

        tk.Frame(panel, bg=COLORS["accent"], height=6).grid(row=0, column=0, sticky="ew", pady=(0, 12))

        notebook = ttk.Notebook(panel)
        notebook.grid(row=1, column=0, sticky="nsew")

        details_tab = ttk.Frame(notebook, style="Surface.TFrame", padding=16)
        subjects_tab = ttk.Frame(notebook, style="Surface.TFrame", padding=16)
        notebook.add(details_tab, text="Student Details")
        notebook.add(subjects_tab, text="Subjects and Marks")

        self._build_details_tab(details_tab)
        self._build_subjects_tab(subjects_tab)

        actions = ttk.Frame(panel, style="Surface.TFrame")
        actions.grid(row=2, column=0, sticky="ew", pady=(16, 0))
        actions.columnconfigure(0, weight=1)

        ttk.Button(actions, text="New Student", style="Ghost.TButton", command=self.clear_form).grid(row=0, column=0, sticky="w")
        ttk.Button(actions, text="Save Student", style="Primary.TButton", command=self.save_current_student).grid(
            row=0, column=1, padx=(10, 0)
        )
        ttk.Button(actions, text="Generate PDF", style="Accent.TButton", command=self.export_current_pdf).grid(
            row=0, column=2, padx=(10, 0)
        )

    def _build_details_tab(self, parent):
        parent.columnconfigure((0, 1, 2), weight=1, uniform="details")

        ttk.Label(parent, text="School Information", style="Section.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 12)
        )
        self._field(parent, "School Name", self.school_name_var, 1, 0, columnspan=2)
        self._field(parent, "Address", self.school_address_var, 1, 2)
        self._field(parent, "Session", self.session_var, 3, 0)
        self._field(parent, "Class", self.class_var, 3, 1)
        self._field(parent, "Roll Number", self.roll_var, 3, 2)

        ttk.Separator(parent).grid(row=5, column=0, columnspan=3, sticky="ew", pady=22)
        ttk.Label(parent, text="Student Information", style="Section.TLabel").grid(
            row=6, column=0, columnspan=3, sticky="w", pady=(0, 12)
        )
        self._field(parent, "Student Name", self.name_var, 7, 0)
        self._field(parent, "Father Name", self.father_var, 7, 1)
        self._field(parent, "Mother Name", self.mother_var, 7, 2)
        self._field(parent, "Date of Birth", self.dob_var, 9, 0)

    def _build_subjects_tab(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)

        ttk.Label(parent, text="Subject Entry", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 12))

        entry_grid = ttk.Frame(parent, style="Surface.TFrame")
        entry_grid.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        entry_grid.columnconfigure(0, weight=2)
        entry_grid.columnconfigure((1, 2, 3), weight=1)

        self._field(entry_grid, "Subject", self.subject_name_var, 0, 0)
        self._field(entry_grid, "Theory", self.theory_var, 0, 1)
        self._field(entry_grid, "Practical", self.practical_var, 0, 2)
        self._field(entry_grid, "Max Marks", self.max_var, 0, 3)

        button_row = ttk.Frame(entry_grid, style="Surface.TFrame")
        button_row.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        self.subject_button = ttk.Button(button_row, text="Add Subject", style="Primary.TButton", command=self.add_or_update_subject)
        self.subject_button.pack(side="left")
        ttk.Button(button_row, text="Clear Subject", style="Ghost.TButton", command=self.clear_subject_fields).pack(
            side="left", padx=(10, 0)
        )
        ttk.Button(button_row, text="Remove Selected", style="Danger.TButton", command=self.remove_selected_subject).pack(
            side="left", padx=(10, 0)
        )

        columns = ("subject", "theory", "practical", "max", "obtained", "grade")
        self.subjects_tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)
        headings = {
            "subject": "Subject",
            "theory": "Theory",
            "practical": "Practical",
            "max": "Max",
            "obtained": "Obtained",
            "grade": "Grade",
        }
        widths = {"subject": 260, "theory": 80, "practical": 90, "max": 70, "obtained": 90, "grade": 70}
        for column, heading in headings.items():
            self.subjects_tree.heading(column, text=heading)
            self.subjects_tree.column(column, width=widths[column], anchor="w")
        self.subjects_tree.grid(row=2, column=0, sticky="nsew")
        self.subjects_tree.bind("<<TreeviewSelect>>", self.select_subject)

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.subjects_tree.yview)
        scrollbar.grid(row=2, column=1, sticky="ns")
        self.subjects_tree.configure(yscrollcommand=scrollbar.set)

        tk.Label(
            parent,
            textvariable=self.summary_var,
            bg=COLORS["accent_soft"],
            fg=COLORS["accent_dark"],
            font=(FONT, 10, "bold"),
            padx=12,
            pady=8,
        ).grid(row=3, column=0, sticky="ew", pady=(12, 0))

    def _field(self, parent, label, variable, row, column, columnspan=1):
        ttk.Label(parent, text=label, style="Muted.TLabel").grid(row=row, column=column, sticky="w", padx=(0, 12))
        entry = ttk.Entry(parent, textvariable=variable, font=("Segoe UI", 10))
        entry.grid(row=row + 1, column=column, columnspan=columnspan, sticky="ew", padx=(0, 12), pady=(5, 12))
        return entry

    def reload_records(self):
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)

        self.record_index.clear()
        try:
            records = list_records()
        except DataStoreError as exc:
            self.status_var.set(str(exc))
            return

        for index, record in enumerate(records):
            item_id = f"record-{index}"
            self.record_index[item_id] = (record["session"], record["roll"])
            self.records_tree.insert("", "end", iid=item_id, values=(record["session"], record["roll"], record["name"]))

        self.status_var.set(f"{len(records)} saved record(s) available.")

    def clear_form(self):
        self.session_var.set(_current_session())
        self.roll_var.set("")
        self.class_var.set("")
        self.name_var.set("")
        self.father_var.set("")
        self.mother_var.set("")
        self.dob_var.set("")
        self.subjects = []
        self.clear_subject_fields()
        self._refresh_subject_tree()
        self.status_var.set("Ready for a new student record.")

    def clear_subject_fields(self):
        self.editing_subject_index = None
        self.subject_name_var.set("")
        self.theory_var.set("0")
        self.practical_var.set("0")
        self.max_var.set("100")
        self.subject_button.configure(text="Add Subject")
        self.subjects_tree.selection_remove(self.subjects_tree.selection())

    def add_or_update_subject(self):
        try:
            subject = self._subject_from_form()
        except ValueError as exc:
            messagebox.showerror("Invalid Subject", str(exc))
            return

        duplicate = next(
            (
                index
                for index, existing in enumerate(self.subjects)
                if existing["name"].lower() == subject["name"].lower() and index != self.editing_subject_index
            ),
            None,
        )
        if duplicate is not None:
            messagebox.showerror("Duplicate Subject", "This subject is already in the marksheet.")
            return

        if self.editing_subject_index is None:
            self.subjects.append(subject)
        else:
            self.subjects[self.editing_subject_index] = subject

        self.clear_subject_fields()
        self._refresh_subject_tree()

    def _subject_from_form(self):
        name = self.subject_name_var.get().strip().upper()
        if not name:
            raise ValueError("Subject name is required.")

        theory = _parse_int(self.theory_var.get(), "Theory marks")
        practical = _parse_int(self.practical_var.get(), "Practical marks")
        max_marks = _parse_int(self.max_var.get(), "Max marks")

        if max_marks <= 0:
            raise ValueError("Max marks must be greater than zero.")
        if theory + practical > max_marks:
            raise ValueError("Theory plus practical marks cannot exceed max marks.")

        return {"name": name, "theory": theory, "practical": practical, "max": max_marks}

    def select_subject(self, _event=None):
        selected = self.subjects_tree.selection()
        if not selected:
            return

        index = int(selected[0])
        subject = self.subjects[index]
        self.editing_subject_index = index
        self.subject_name_var.set(subject["name"])
        self.theory_var.set(str(subject["theory"]))
        self.practical_var.set(str(subject["practical"]))
        self.max_var.set(str(subject["max"]))
        self.subject_button.configure(text="Update Subject")

    def remove_selected_subject(self):
        selected = self.subjects_tree.selection()
        if not selected:
            messagebox.showinfo("Remove Subject", "Select a subject first.")
            return

        index = int(selected[0])
        del self.subjects[index]
        self.clear_subject_fields()
        self._refresh_subject_tree()

    def _refresh_subject_tree(self):
        for item in self.subjects_tree.get_children():
            self.subjects_tree.delete(item)

        for index, subject in enumerate(self.subjects):
            obtained = subject_obtained(subject)
            self.subjects_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    subject["name"],
                    subject["theory"],
                    subject["practical"],
                    subject["max"],
                    obtained,
                    get_grade(obtained, subject["max"]),
                ),
            )

        summary = calculate_summary(self.subjects)
        if self.subjects:
            self.summary_var.set(
                f"Total {summary['total_obtained']} / {summary['total_max']} | "
                f"{summary['percentage']:.2f}% | {summary['result']} | {summary['division']}"
            )
        else:
            self.summary_var.set("No subjects added.")

    def _record_from_form(self):
        required = [
            ("School name", self.school_name_var.get()),
            ("Session", self.session_var.get()),
            ("Roll number", self.roll_var.get()),
            ("Class", self.class_var.get()),
            ("Student name", self.name_var.get()),
        ]
        missing = [label for label, value in required if not value.strip()]
        if missing:
            raise ValueError(f"Fill required field(s): {', '.join(missing)}.")
        if not self.subjects:
            raise ValueError("Add at least one subject.")

        return {
            "school": {
                "name": self.school_name_var.get().strip(),
                "address": self.school_address_var.get().strip(),
            },
            "student": {
                "name": self.name_var.get().strip(),
                "father": self.father_var.get().strip(),
                "mother": self.mother_var.get().strip(),
                "class": self.class_var.get().strip(),
                "dob": self.dob_var.get().strip(),
                "session": self.session_var.get().strip(),
                "type": "REGULAR",
            },
            "subjects": [subject.copy() for subject in self.subjects],
        }

    def save_current_student(self):
        try:
            record = self._record_from_form()
            save_student(self.session_var.get(), self.roll_var.get(), record)
        except (ValueError, DataStoreError) as exc:
            messagebox.showerror("Save Failed", str(exc))
            return

        self.reload_records()
        self.status_var.set(f"Saved {self.name_var.get().strip()} ({self.roll_var.get().strip()}).")
        messagebox.showinfo("Saved", "Student record saved successfully.")

    def export_current_pdf(self):
        try:
            record = self._record_from_form()
        except ValueError as exc:
            messagebox.showerror("PDF Failed", str(exc))
            return

        initial_path = default_output_path(self.session_var.get(), self.roll_var.get())
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
            generated = generate_pdf(save_path, self.roll_var.get().strip(), record, session=self.session_var.get().strip())
        except Exception as exc:
            messagebox.showerror("PDF Failed", str(exc))
            return

        self.status_var.set(f"Generated {generated}.")
        messagebox.showinfo("PDF Generated", f"PDF saved to:\n{generated}")

    def load_selected_record(self):
        selected = self.records_tree.selection()
        if not selected:
            messagebox.showinfo("Load Record", "Select a saved record first.")
            return

        session, roll = self.record_index[selected[0]]
        try:
            record = get_student(session, roll)
        except DataStoreError as exc:
            messagebox.showerror("Load Failed", str(exc))
            return

        if not record:
            messagebox.showerror("Load Failed", "The selected record was not found.")
            self.reload_records()
            return

        self._fill_form(session, roll, record)
        self.status_var.set(f"Loaded {roll} from {session}.")

    def _fill_form(self, session, roll, record):
        school = record.get("school", {})
        student = record.get("student", {})

        self.school_name_var.set(str(school.get("name", "")))
        self.school_address_var.set(str(school.get("address") or school.get("sub_title") or ""))
        self.session_var.set(str(session))
        self.roll_var.set(str(roll))
        self.class_var.set(str(student.get("class", "")))
        self.name_var.set(str(student.get("name", "")))
        self.father_var.set(str(student.get("father", "")))
        self.mother_var.set(str(student.get("mother", "")))
        self.dob_var.set(str(student.get("dob", "")))

        self.subjects = []
        for subject in record.get("subjects", []):
            try:
                self.subjects.append(
                    {
                        "name": str(subject.get("name", "")).upper(),
                        "theory": _parse_int(subject.get("theory", 0), "Theory marks"),
                        "practical": _parse_int(subject.get("practical", 0), "Practical marks"),
                        "max": _parse_int(subject.get("max", 100), "Max marks"),
                    }
                )
            except ValueError:
                continue

        self.clear_subject_fields()
        self._refresh_subject_tree()


def start():
    root = tk.Tk()
    root.title("Admin Panel - School Marksheet System")
    maximize(root)
    configure_style(root)
    set_window_icon(root)
    frame = AdminPanelFrame(root, on_back=root.destroy)
    frame.pack(fill="both", expand=True, padx=28, pady=24)
    root.mainloop()


if __name__ == "__main__":
    start()

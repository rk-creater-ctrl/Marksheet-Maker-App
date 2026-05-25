import json
import os
import re
import sys
from pathlib import Path


class DataStoreError(RuntimeError):
    pass


def _app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


APP_DIR = _app_dir()
DB_FILE = APP_DIR / "students.json"
OUTPUT_DIR = APP_DIR / "output"


def resource_path(relative_path):
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).resolve().parent / relative_path


ASSETS_DIR = resource_path("assets")


def load_db():
    if not DB_FILE.exists():
        return {}

    try:
        with DB_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise DataStoreError(
            f"{DB_FILE.name} is not valid JSON at line {exc.lineno}, column {exc.colno}."
        ) from exc
    except OSError as exc:
        raise DataStoreError(f"Could not read {DB_FILE.name}: {exc}") from exc

    if not isinstance(data, dict):
        raise DataStoreError(f"{DB_FILE.name} must contain a JSON object.")

    return data


def save_db(data):
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_file = DB_FILE.with_suffix(".tmp")

    try:
        with temp_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
            file.write("\n")
        os.replace(temp_file, DB_FILE)
    except OSError as exc:
        raise DataStoreError(f"Could not save {DB_FILE.name}: {exc}") from exc


def normalize_key(value):
    return str(value or "").strip()


def get_student(session, roll):
    db = load_db()
    return db.get(normalize_key(session), {}).get(normalize_key(roll))


def save_student(session, roll, record):
    session_key = normalize_key(session)
    roll_key = normalize_key(roll)

    if not session_key or not roll_key:
        raise DataStoreError("Session and roll number are required.")

    db = load_db()
    db.setdefault(session_key, {})[roll_key] = record
    save_db(db)


def _session_sort_value(session):
    match = re.search(r"\d{4}", str(session))
    return int(match.group(0)) if match else 0


def list_records():
    db = load_db()
    records = []

    for session, students in db.items():
        if not isinstance(students, dict):
            continue

        for roll, record in students.items():
            if not isinstance(record, dict):
                continue

            student = record.get("student", {})
            school = record.get("school", {})
            records.append(
                {
                    "session": str(session),
                    "roll": str(roll),
                    "name": str(student.get("name", "")),
                    "class": str(student.get("class", "")),
                    "school": str(school.get("name", "")),
                }
            )

    return sorted(
        records,
        key=lambda item: (-_session_sort_value(item["session"]), item["session"], item["roll"]),
    )


def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def default_output_path(session, roll):
    ensure_output_dir()
    safe_session = re.sub(r"[^A-Za-z0-9_-]+", "_", normalize_key(session))
    safe_roll = re.sub(r"[^A-Za-z0-9_-]+", "_", normalize_key(roll))
    return OUTPUT_DIR / f"Marksheet_{safe_session}_{safe_roll}.pdf"

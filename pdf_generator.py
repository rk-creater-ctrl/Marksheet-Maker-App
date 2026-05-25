from datetime import datetime
from pathlib import Path

from marksheet_utils import calculate_summary, get_grade, subject_obtained


def _fit_text(canvas, text, max_width, font_name, font_size):
    value = str(text or "")
    if canvas.stringWidth(value, font_name, font_size) <= max_width:
        return value

    suffix = "..."
    while value and canvas.stringWidth(value + suffix, font_name, font_size) > max_width:
        value = value[:-1]
    return value + suffix if value else suffix


def _draw_label_value(canvas, x, y, label, value, max_width):
    label_font = "Helvetica-Bold"
    value_font = "Helvetica"
    canvas.setFont(label_font, 9)
    canvas.drawString(x, y, f"{label}:")
    canvas.setFont(value_font, 9)
    canvas.drawString(x + 74, y, _fit_text(canvas, value, max_width - 74, value_font, 9))


def generate_pdf(save_path, roll, record, session=""):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise RuntimeError("ReportLab is required to generate PDFs. Install it with: pip install reportlab") from exc

    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    school = record.get("school", {})
    student = record.get("student", {})
    subjects = record.get("subjects", [])
    summary = calculate_summary(subjects)

    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    margin = 42
    inner_width = width - (margin * 2)

    primary = colors.HexColor("#1f6f8b")
    text = colors.HexColor("#172033")
    muted = colors.HexColor("#637083")
    border = colors.HexColor("#d8e0ea")
    surface = colors.HexColor("#f4f7fb")
    success = colors.HexColor("#19764a")
    danger = colors.HexColor("#b42318")

    c.setTitle(f"Marksheet {roll}")
    c.setAuthor(str(school.get("name", "School Marksheet System")))

    c.setFillColor(primary)
    c.rect(0, height - 14, width, 14, fill=1, stroke=0)

    c.setStrokeColor(border)
    c.setLineWidth(1.2)
    c.roundRect(margin / 2, margin / 2, width - margin, height - margin, 8, stroke=1, fill=0)

    y = height - 56
    c.setFillColor(text)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, y, _fit_text(c, school.get("name", "School Name"), inner_width, "Helvetica-Bold", 20))

    y -= 18
    c.setFont("Helvetica", 10)
    c.setFillColor(muted)
    address = school.get("address") or school.get("sub_title") or ""
    c.drawCentredString(width / 2, y, _fit_text(c, address, inner_width, "Helvetica", 10))

    y -= 26
    c.setFillColor(primary)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(width / 2, y, "ACADEMIC MARKSHEET")

    y -= 12
    c.setStrokeColor(border)
    c.line(margin, y, width - margin, y)

    details_top = y - 28
    details_height = 98
    c.setFillColor(surface)
    c.roundRect(margin, details_top - details_height, inner_width, details_height, 8, stroke=0, fill=1)
    c.setStrokeColor(border)
    c.roundRect(margin, details_top - details_height, inner_width, details_height, 8, stroke=1, fill=0)

    details = [
        ("Name", student.get("name", "")),
        ("Roll No", roll),
        ("Father", student.get("father", "")),
        ("Class", student.get("class", "")),
        ("Mother", student.get("mother", "")),
        ("Session", session or student.get("session", "")),
        ("DOB", student.get("dob", "")),
        ("Result Type", student.get("type", "Regular")),
    ]

    left_x = margin + 18
    right_x = margin + (inner_width / 2) + 10
    row_y = details_top - 24
    for index, (label, value) in enumerate(details):
        x = left_x if index % 2 == 0 else right_x
        row = index // 2
        _draw_label_value(c, x, row_y - (row * 20), label, value, (inner_width / 2) - 28)

    table_top = details_top - details_height - 34
    table_x = margin
    column_widths = [36, 190, 58, 58, 52, 68, 49]
    headers = ["S.No", "Subject", "Theory", "Practical", "Max", "Obtained", "Grade"]
    row_height = 24

    c.setFillColor(primary)
    c.roundRect(table_x, table_top - row_height, inner_width, row_height, 6, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 8.5)

    x = table_x
    for header, column_width in zip(headers, column_widths):
        c.drawString(x + 6, table_top - 16, header)
        x += column_width

    y = table_top - row_height
    c.setFont("Helvetica", 9)
    c.setFillColor(text)

    for index, subject in enumerate(subjects, 1):
        y -= row_height
        if index % 2 == 0:
            c.setFillColor(colors.HexColor("#f8fafc"))
            c.rect(table_x, y, inner_width, row_height, stroke=0, fill=1)
            c.setFillColor(text)

        theory = int(subject.get("theory", 0) or 0)
        practical = int(subject.get("practical", 0) or 0)
        max_marks = int(subject.get("max", 0) or 0)
        obtained = subject_obtained(subject)
        values = [
            str(index),
            _fit_text(c, subject.get("name", ""), column_widths[1] - 12, "Helvetica", 9),
            str(theory),
            str(practical),
            str(max_marks),
            str(obtained),
            get_grade(obtained, max_marks),
        ]

        x = table_x
        for value, column_width in zip(values, column_widths):
            c.drawString(x + 6, y + 8, value)
            x += column_width

        c.setStrokeColor(border)
        c.line(table_x, y, table_x + inner_width, y)

    c.setStrokeColor(border)
    c.rect(table_x, y, inner_width, table_top - y, stroke=1, fill=0)

    summary_y = max(y - 70, 120)
    c.setFillColor(surface)
    c.roundRect(margin, summary_y, inner_width, 48, 8, stroke=0, fill=1)
    c.setStrokeColor(border)
    c.roundRect(margin, summary_y, inner_width, 48, 8, stroke=1, fill=0)

    summary_items = [
        ("Total", f"{summary['total_obtained']} / {summary['total_max']}"),
        ("Percentage", f"{summary['percentage']:.2f}%"),
        ("Result", summary["result"]),
        ("Division", summary["division"]),
    ]
    item_width = inner_width / len(summary_items)
    for index, (label, value) in enumerate(summary_items):
        x = margin + (index * item_width) + 12
        c.setFillColor(muted)
        c.setFont("Helvetica", 8)
        c.drawString(x, summary_y + 30, label.upper())
        c.setFillColor(success if label == "Result" and value == "PASS" else danger if label == "Result" else text)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x, summary_y + 13, _fit_text(c, value, item_width - 18, "Helvetica-Bold", 11))

    c.setStrokeColor(border)
    c.line(margin + 14, 86, margin + 142, 86)
    c.line((width / 2) - 64, 86, (width / 2) + 64, 86)
    c.line(width - margin - 142, 86, width - margin - 14, 86)

    c.setFillColor(text)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(margin + 78, 70, "Class Teacher")
    c.drawCentredString(width / 2, 70, "Principal")
    c.drawCentredString(width - margin - 78, 70, "Head Examiner")

    c.setFont("Helvetica", 8)
    c.setFillColor(muted)
    c.drawCentredString(width / 2, 40, f"Generated on {datetime.now().strftime('%d/%m/%Y')}")
    c.drawCentredString(width / 2, 28, "This is a computer generated marksheet.")

    c.save()
    return str(path)

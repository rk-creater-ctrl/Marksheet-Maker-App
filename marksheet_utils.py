def subject_obtained(subject):
    return int(subject.get("theory", 0) or 0) + int(subject.get("practical", 0) or 0)


def get_grade(obtained, max_marks=100):
    if max_marks <= 0:
        return "F"

    percent = (obtained / max_marks) * 100
    if percent >= 90:
        return "A1"
    if percent >= 80:
        return "A2"
    if percent >= 70:
        return "B1"
    if percent >= 60:
        return "B2"
    if percent >= 50:
        return "C1"
    if percent >= 40:
        return "C2"
    if percent >= 33:
        return "D"
    return "F"


def calculate_summary(subjects):
    total_obtained = 0
    total_max = 0
    failed_subjects = 0

    for subject in subjects:
        max_marks = int(subject.get("max", 0) or 0)
        obtained = subject_obtained(subject)

        total_obtained += obtained
        total_max += max_marks

        if max_marks <= 0 or ((obtained / max_marks) * 100) < 33:
            failed_subjects += 1

    percentage = (total_obtained / total_max) * 100 if total_max else 0
    passed = bool(subjects) and percentage >= 33 and failed_subjects == 0

    if not passed:
        division = "Needs Improvement"
    elif percentage >= 60:
        division = "First Division"
    elif percentage >= 45:
        division = "Second Division"
    else:
        division = "Third Division"

    return {
        "total_obtained": total_obtained,
        "total_max": total_max,
        "percentage": percentage,
        "result": "PASS" if passed else "FAIL",
        "division": division,
        "failed_subjects": failed_subjects,
    }

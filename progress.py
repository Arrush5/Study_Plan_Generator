from datetime import date

def compute_days_left(end_date_iso: str) -> int:
    end_date = date.fromisoformat(end_date_iso)
    today = date.today()
    return max((end_date - today).days, 0)

def compute_status(total_tasks: int, done_tasks: int, days_left: int):
    if total_tasks == 0:
        return 0.0, "No Tasks", "Create a plan to start."

    percent = round((done_tasks / total_tasks) * 100, 2)

    # Simple expected trend baseline
    # If days_left is high, expected is low; as days reduce, expected rises
    expected = 100 - (days_left * (100 / (days_left + 1)))

    if percent >= expected + 10:
        status = "Ahead"
        suggestion = "You are ahead! Use extra time for revision or practice."
    elif percent >= expected:
        status = "On Track"
        suggestion = "Good pace! Keep going consistently."
    else:
        status = "Behind"
        suggestion = "You are behind. Add 30–45 minutes or one extra study day this week."

    return percent, status, suggestion

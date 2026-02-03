def generate_plan_fallback(goal, duration_days, intensity="moderate"):
    weeks = max(1, (duration_days + 6) // 7)

    week_themes = [
        "Introduction & Foundations",
        "Core Concepts",
        "Important Areas / High-weight topics",
        "Advanced / Applied Concepts",
        "Practice & PYQs",
        "Revision & Mock Tests"
    ]

    plan = {"weeks": []}

    for w in range(1, weeks + 1):
        theme = week_themes[(w - 1) % len(week_themes)]

        milestone = f"{goal}: {theme}"

        # Last week = forced revision focus
        if w == weeks:
            subtopics = [
                f"{goal} - Full syllabus revision",
                f"{goal} - Mock test / timed practice",
                f"{goal} - Error analysis & weak areas",
                f"{goal} - Final summary & quick recall"
            ]
        else:
            subtopics = [
                f"{goal} - {theme}: Concept overview",
                f"{goal} - {theme}: Key points & notes",
                f"{goal} - {theme}: Important facts / examples",
                f"{goal} - {theme}: Practice questions",
                f"{goal} - {theme}: Revision checklist"
            ]

        plan["weeks"].append({
            "week_no": w,
            "milestone": milestone,
            "subtopics": subtopics
        })

    return plan

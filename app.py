import streamlit as st
from datetime import date, timedelta

from dotenv import load_dotenv
load_dotenv()

from models import (
    init_db, create_plan, add_tasks, get_tasks_by_date,
    update_task_status, get_progress_counts, get_all_tasks,
    reset_all_data, get_latest_plan_id, get_all_tasks_detailed
)

from planner_hf import generate_plan_hf
from planner_fallback import generate_plan_fallback
from progress import compute_days_left, compute_status


st.set_page_config(page_title="Study Plan Generator & Tracker", layout="wide")
init_db()

st.title("📘 AI Study Plan Generator & Tracker (Hugging Face)")

if "plan_id" not in st.session_state:
    st.session_state.plan_id = get_latest_plan_id()


def get_revision_days(duration_days: int) -> int:
    rev = round(duration_days * 0.10)
    return max(2, min(14, int(rev)))


def convert_plan_to_tasks(ai_plan, start_date: date, duration_days: int, intensity: str, preferred_days: list, goal_type: str):
    # intensity -> minutes
    mins = 75
    if intensity == "light":
        mins = 55
    elif intensity == "intensive":
        mins = 105

    # preferred days mapping
    day_map = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
    preferred_idx = set(day_map[d] for d in preferred_days) if preferred_days else set(range(7))

    # dynamic revision window: 10% of duration, min 2, max 14
    revision_days = max(2, min(14, int(round(duration_days * 0.10))))

    weeks = ai_plan.get("weeks", [])
    if not weeks:
        weeks = [{"week_no": 1, "milestone": "Foundations", "subtopics": ["Basics", "Core concepts", "Practice", "Revision"]}]

    def get_week_obj(week_no: int):
        return next((w for w in weeks if int(w.get("week_no", 1)) == week_no), None)

    def looks_generic(subtopics: list) -> bool:
        generic_keywords = [
            "fundamentals", "core theory", "terminology", "types", "categories",
            "examples", "applications", "faqs", "common mistakes", "overview",
            "key concepts", "important points", "practice set", "quick revision"
        ]
        text = " ".join(s.lower() for s in (subtopics or []))
        return any(k in text for k in generic_keywords)

    tasks = []

    for day_offset in range(duration_days):
        d = start_date + timedelta(days=day_offset)
        if d.weekday() not in preferred_idx:
            continue

        week_no = (day_offset // 7) + 1
        week_obj = get_week_obj(week_no)

        milestone = (week_obj.get("milestone") if week_obj else f"Week {week_no} milestone")
        subtopics = (week_obj.get("subtopics") if week_obj else [])

        # If subtopics are missing or too generic, generate a goal-type-aware fallback subtopic list
        if not subtopics or looks_generic(subtopics):
            if goal_type == "Exam preparation":
                subtopics = [
                    f"{milestone} - Key concepts & notes",
                    f"{milestone} - High-yield points",
                    f"{milestone} - PYQ practice",
                    f"{milestone} - Mock-style questions",
                    f"{milestone} - Revision & recall",
                ]
            elif goal_type == "Certification":
                subtopics = [
                    f"{milestone} - Concepts for exam objectives",
                    f"{milestone} - Hands-on labs/tasks",
                    f"{milestone} - Scenario-based questions",
                    f"{milestone} - Practice test set",
                    f"{milestone} - Review weak areas",
                ]
            else:  # Skill/topic completion
                subtopics = [
                    f"{milestone} - Learn core concepts",
                    f"{milestone} - Guided implementation",
                    f"{milestone} - Mini-exercise / coding task",
                    f"{milestone} - Build a small project piece",
                    f"{milestone} - Debug + reflect + improve",
                ]

        # Count how many tasks already assigned in this week (handles skipped days)
        week_start = (week_no - 1) * 7
        prior_in_week = 0
        for t in tasks:
            td = date.fromisoformat(t["task_date"])
            offset = (td - start_date).days
            if week_start <= offset < week_start + 7:
                prior_in_week += 1

        subtopic = subtopics[prior_in_week % len(subtopics)]

        # Task labeling + details based on goal type
        if day_offset >= duration_days - revision_days:
            # Revision period
            title = "Revision & Mock Practice" if goal_type != "Skill/topic completion" else "Review & Improve"

            if goal_type == "Exam preparation":
                details = f"Revise: {subtopic} + timed PYQs/mock + analyze mistakes."
            elif goal_type == "Certification":
                details = f"Revise: {subtopic} + practice test + review weak areas."
            else:
                details = f"Review: {subtopic} + refactor + fix gaps + summarize learnings."

        else:
            cycle = prior_in_week % 5

            if cycle in [0, 1]:
                title = f"Learn: {subtopic}"
                details = "Learn concepts + make short notes." if goal_type != "Skill/topic completion" else "Learn + follow a guided example."

            elif cycle in [2, 3]:
                title = f"Practice: {subtopic}"

                if goal_type == "Exam preparation":
                    details = "Solve PYQs + practice questions + review errors."
                elif goal_type == "Certification":
                    details = "Do hands-on tasks + scenario questions + review errors."
                else:
                    details = "Implement/coding task + test + fix bugs."

            else:
                title = f"Revise: {subtopic}" if goal_type != "Skill/topic completion" else f"Improve: {subtopic}"
                details = "Quick revision + 10-minute recall test." if goal_type != "Skill/topic completion" else "Improve solution + clean code + add notes."

        tasks.append({
            "task_date": d.isoformat(),
            "week_no": week_no,
            "title": title,
            "details": details,
            "estimated_minutes": mins
        })

    return tasks

tab1, tab2, tab3, tab4 = st.tabs(["🧩 Create Plan", "✅ Tasks", "📊 Dashboard", "📅 Full Plan"])

with tab1:
    st.subheader("Create your personalized study plan")

    colR1, colR2 = st.columns([1, 3])
    with colR1:
        if st.button("🗑️ Start New Plan (Reset)", use_container_width=True):
            reset_all_data()
            st.session_state.plan_id = None
            st.success("Old plan cleared. Create a new plan now ✅")

    col1, col2 = st.columns(2)

    with col1:
        goal_type = st.selectbox("Goal type", ["Exam preparation", "Skill/topic completion", "Certification"], index=0)
        goal = st.text_input("Learning goal / Subject", placeholder="e.g., CDS History / SQL / Python")
        start_date = st.date_input("Start date", value=date.today())
        duration_days = st.number_input("Duration (days)", min_value=7, max_value=365, value=30, step=1)

    with col2:
        hours_per_week = st.slider("Hours per week", min_value=1, max_value=40, value=10)
        preferred_days = st.multiselect(
            "Preferred study days",
            ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            default=["Mon", "Tue", "Wed", "Thu", "Fri"]
        )
        intensity = st.selectbox("Study intensity", ["light", "moderate", "intensive"], index=1)
        learning_pref = st.selectbox("Learning preference", ["reading", "practice", "mixed"], index=2)

    if st.button("🚀 Generate Plan", use_container_width=True):
        if not goal.strip():
            st.error("Please enter a learning goal/subject.")
        else:
            goal_for_ai = f"{goal} ({goal_type})"
            end_date = start_date + timedelta(days=int(duration_days))

            plan_id = create_plan({
                "goal": goal_for_ai,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "duration_days": int(duration_days),
                "hours_per_week": float(hours_per_week),
                "preferred_days": ",".join(preferred_days),
                "intensity": intensity,
                "learning_pref": learning_pref
            })
            st.session_state.plan_id = plan_id

            planner_used = "Hugging Face"
            ai_error = None

            try:
                ai_plan = generate_plan_hf(goal_for_ai, int(duration_days), float(hours_per_week), intensity, learning_pref)
            except Exception as e:
                planner_used = "Fallback"
                ai_error = str(e)
                ai_plan = generate_plan_fallback(goal_for_ai, int(duration_days), intensity=intensity)

            st.caption(f"🧠 Planner used: **{planner_used}**")
            if ai_error:
                st.caption(f"⚠️ AI error (why fallback): {ai_error[:180]}")

            tasks = convert_plan_to_tasks(
                ai_plan,
                start_date,
                int(duration_days),
                intensity=intensity,
                preferred_days=preferred_days,
                goal_type=goal_type
            )

            add_tasks(plan_id, tasks)

            st.success("✅ Plan created successfully!")

            st.write("### ✅ Plan Preview (First 10 Tasks)")
            for t in tasks[:10]:
                st.write(f"- {t['task_date']} | Week {t['week_no']} | {t['title']} (~{t['estimated_minutes']} mins)")


with tab2:
    st.subheader("Tasks")

    if not st.session_state.plan_id:
        st.warning("Create a plan first in the **Create Plan** tab.")
    else:
        selected_date = st.date_input("Pick a date to view tasks", value=date.today())
        target_date = selected_date.isoformat()
        rows = get_tasks_by_date(st.session_state.plan_id, target_date)

        if not rows:
            st.info("No tasks scheduled for this date. Try another date or check Dashboard for upcoming tasks.")
        else:
            for task_id, title, details, mins, status in rows:
                checked = (status == "done")
                new_val = st.checkbox(f"{title}  •  ~{mins} mins", value=checked, key=task_id)
                if new_val and status != "done":
                    update_task_status(task_id, "done")
                elif (not new_val) and status == "done":
                    update_task_status(task_id, "pending")

                if details:
                    st.caption(details)


with tab3:
    st.subheader("Progress Dashboard")

    if not st.session_state.plan_id:
        st.warning("Create a plan first in the **Create Plan** tab.")
    else:
        total, done = get_progress_counts(st.session_state.plan_id)
        all_tasks = get_all_tasks(st.session_state.plan_id)

        last_day = all_tasks[-1][1] if all_tasks else date.today().isoformat()
        days_left = compute_days_left(last_day)
        percent, status, suggestion = compute_status(total, done, days_left)

        c1, c2, c3 = st.columns(3)
        c1.metric("Completed", f"{done}/{total}")
        c2.metric("Completion %", f"{percent}%")
        c3.metric("Days Left", f"{days_left}")

        st.progress(min(int(percent), 100))
        st.write(f"**Status:** {status}")
        st.info(suggestion)

        st.divider()
        st.write("### Weekly Milestone Progress")

        by_week = {}
        for _, task_date, week_no, title, t_status in all_tasks:
            by_week.setdefault(week_no, {"done": 0, "total": 0})
            by_week[week_no]["total"] += 1
            if t_status == "done":
                by_week[week_no]["done"] += 1

        for w in sorted(by_week.keys()):
            d = by_week[w]["done"]
            t = by_week[w]["total"]
            wp = round((d / t) * 100, 2) if t else 0
            st.write(f"**Week {w}** — {d}/{t} completed ({wp}%)")
            st.progress(int(wp))

with tab4:
    st.subheader("📅 Full Plan")

    if not st.session_state.plan_id:
        st.warning("Create a plan first in the **Create Plan** tab.")
    else:
        all_tasks = get_all_tasks_detailed(st.session_state.plan_id)

        if not all_tasks:
            st.info("No tasks found. Generate a plan first.")
        else:
            view_mode = st.radio("View Mode", ["Week-wise", "Date-wise"], horizontal=True)

            # Optional filter
            show_done = st.checkbox("Show completed tasks", value=True)

            def render_task(task_date, week_no, title, details, mins, status):
                if (not show_done) and status == "done":
                    return
                badge = "✅" if status == "done" else "🕒"
                st.markdown(f"{badge} **{task_date}** (Week {week_no}) — **{title}**  ·  _~{mins} mins_")
                if details:
                    st.caption(details)

            if view_mode == "Week-wise":
                by_week = {}
                for task_id, task_date, week_no, title, details, mins, status in all_tasks:
                    by_week.setdefault(week_no, [])
                    by_week[week_no].append((task_date, week_no, title, details, mins, status))

                for w in sorted(by_week.keys()):
                    st.markdown(f"### Week {w}")
                    for item in by_week[w]:
                        render_task(*item)

            else:
                st.markdown("### All Tasks by Date")
                for task_id, task_date, week_no, title, details, mins, status in all_tasks:
                    render_task(task_date, week_no, title, details, mins, status)

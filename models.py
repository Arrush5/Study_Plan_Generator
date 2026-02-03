from db import get_connection
from datetime import datetime
import uuid

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS plans (
        plan_id TEXT PRIMARY KEY,
        goal TEXT,
        start_date TEXT,
        end_date TEXT,
        duration_days INTEGER,
        hours_per_week REAL,
        preferred_days TEXT,
        intensity TEXT,
        learning_pref TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        task_id TEXT PRIMARY KEY,
        plan_id TEXT,
        task_date TEXT,
        week_no INTEGER,
        title TEXT,
        details TEXT,
        estimated_minutes INTEGER,
        status TEXT,
        completed_at TEXT
    )
    """)

    conn.commit()
    conn.close()

def reset_all_data():
    """One-plan mode: clear everything."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks")
    cur.execute("DELETE FROM plans")
    conn.commit()
    conn.close()

def get_latest_plan_id():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT plan_id FROM plans ORDER BY created_at DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def create_plan(plan_data: dict) -> str:
    plan_id = str(uuid.uuid4())
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO plans(plan_id, goal, start_date, end_date, duration_days,
                          hours_per_week, preferred_days, intensity, learning_pref, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        plan_id,
        plan_data["goal"],
        plan_data["start_date"],
        plan_data["end_date"],
        plan_data["duration_days"],
        plan_data["hours_per_week"],
        plan_data["preferred_days"],
        plan_data["intensity"],
        plan_data["learning_pref"],
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()
    return plan_id

def add_tasks(plan_id: str, tasks: list):
    conn = get_connection()
    cur = conn.cursor()

    for t in tasks:
        task_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO tasks(task_id, plan_id, task_date, week_no, title, details,
                              estimated_minutes, status, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id,
            plan_id,
            t["task_date"],
            t["week_no"],
            t["title"],
            t["details"],
            t["estimated_minutes"],
            "pending",
            None
        ))

    conn.commit()
    conn.close()

def get_tasks_by_date(plan_id: str, date_str: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT task_id, title, details, estimated_minutes, status
        FROM tasks
        WHERE plan_id=? AND task_date=?
        ORDER BY week_no ASC, title ASC
    """, (plan_id, date_str))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_all_tasks(plan_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT task_id, task_date, week_no, title, status
        FROM tasks
        WHERE plan_id=?
        ORDER BY task_date ASC
    """, (plan_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def update_task_status(task_id: str, status: str):
    conn = get_connection()
    cur = conn.cursor()
    completed_at = datetime.utcnow().isoformat() if status == "done" else None
    cur.execute("""
        UPDATE tasks SET status=?, completed_at=?
        WHERE task_id=?
    """, (status, completed_at, task_id))
    conn.commit()
    conn.close()

def get_progress_counts(plan_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tasks WHERE plan_id=?", (plan_id,))
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tasks WHERE plan_id=? AND status='done'", (plan_id,))
    done = cur.fetchone()[0]
    conn.close()
    return total, done

def get_all_tasks_detailed(plan_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT task_id, task_date, week_no, title, details, estimated_minutes, status
        FROM tasks
        WHERE plan_id=?
        ORDER BY task_date ASC
    """, (plan_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

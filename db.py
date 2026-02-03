import sqlite3

DB_NAME = "study_plan.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

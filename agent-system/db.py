import sqlite3
from datetime import datetime

DB_PATH = "agent_history.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            task TEXT,
            worker_output TEXT,
            review_status TEXT,
            feedback TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_execution(task: str, worker_output: str, review_status: str, feedback: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO executions (timestamp, task, worker_output, review_status, feedback)
        VALUES (?, ?, ?, ?, ?)
    """,
        (datetime.utcnow().isoformat(), task, worker_output, review_status, feedback),
    )
    conn.commit()
    conn.close()

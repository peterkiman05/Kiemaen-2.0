import sqlite3
import datetime

DB_PATH = "history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            task TEXT,
            status TEXT,
            iterations INTEGER,
            final_output TEXT,
            review_feedback TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_run(task, status, iterations, final_output, review_feedback):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO runs (timestamp, task, status, iterations, final_output, review_feedback)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (now, task, status, iterations, final_output, review_feedback))
    conn.commit()
    conn.close()

def get_all_runs():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, timestamp, task, status, iterations, final_output, review_feedback FROM runs ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "timestamp": r[1],
            "task": r[2],
            "status": r[3],
            "iterations": r[4],
            "final_output": r[5],
            "review_feedback": r[6]
        })
    return result

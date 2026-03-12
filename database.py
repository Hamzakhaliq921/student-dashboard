import sqlite3

import os
DB = os.environ.get("DB_PATH", "assignments.db")

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Assignments table
    c.execute("""
    CREATE TABLE IF NOT EXISTS assignments(
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        course    TEXT,
        title     TEXT,
        deadline  TEXT,
        status    TEXT,
        days_left INTEGER
    )""")

    # Attendance table
    c.execute("""
    CREATE TABLE IF NOT EXISTS attendance(
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        code         TEXT,
        title        TEXT,
        teacher      TEXT,
        present_hrs  REAL,
        absent_hrs   REAL,
        total_hrs    REAL,
        percentage   REAL,
        scraped_at   TEXT DEFAULT (datetime('now','localtime'))
    )""")

    # Scraper status table  (tracks whether a scraper is running)
    c.execute("""
    CREATE TABLE IF NOT EXISTS scraper_status(
        key   TEXT PRIMARY KEY,
        value TEXT
    )""")

    conn.commit()
    conn.close()


# ─── ASSIGNMENTS ───────────────────────────────────────────────

def clear_assignments():
    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM assignments")
    conn.commit(); conn.close()

def save_assignment(course, title, deadline, status, days_left=None):
    conn = sqlite3.connect(DB)
    conn.execute(
        "INSERT INTO assignments(course,title,deadline,status,days_left) VALUES(?,?,?,?,?)",
        (course, title, deadline, status, days_left)
    )
    conn.commit(); conn.close()

def get_assignments():
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT course,title,deadline,status,days_left FROM assignments ORDER BY status ASC, days_left ASC"
    ).fetchall()
    conn.close()
    return rows

def get_stats():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    total    = c.execute("SELECT COUNT(*) FROM assignments").fetchone()[0]
    upcoming = c.execute("SELECT COUNT(*) FROM assignments WHERE status='UPCOMING'").fetchone()[0]
    passed   = c.execute("SELECT COUNT(*) FROM assignments WHERE status='PASSED'").fetchone()[0]
    urgent   = c.execute("SELECT COUNT(*) FROM assignments WHERE status='UPCOMING' AND days_left<=3").fetchone()[0]
    conn.close()
    return {"total": total, "upcoming": upcoming, "passed": passed, "urgent": urgent}


# ─── ATTENDANCE ────────────────────────────────────────────────

def clear_attendance():
    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM attendance")
    conn.commit(); conn.close()

def save_attendance(code, title, teacher, present_hrs, absent_hrs, total_hrs, percentage):
    conn = sqlite3.connect(DB)
    conn.execute(
        "INSERT INTO attendance(code,title,teacher,present_hrs,absent_hrs,total_hrs,percentage) VALUES(?,?,?,?,?,?,?)",
        (code, title, teacher, present_hrs, absent_hrs, total_hrs, percentage)
    )
    conn.commit(); conn.close()

def get_attendance():
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT code,title,teacher,present_hrs,absent_hrs,total_hrs,percentage FROM attendance ORDER BY id ASC"
    ).fetchall()
    conn.close()
    return rows

def get_attendance_scraped_at():
    conn = sqlite3.connect(DB)
    row = conn.execute("SELECT scraped_at FROM attendance ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return row[0] if row else None


# ─── SCRAPER STATUS ────────────────────────────────────────────

def set_scraper_status(key, value):
    conn = sqlite3.connect(DB)
    conn.execute("INSERT OR REPLACE INTO scraper_status(key,value) VALUES(?,?)", (key, value))
    conn.commit(); conn.close()

def get_scraper_status(key):
    conn = sqlite3.connect(DB)
    row = conn.execute("SELECT value FROM scraper_status WHERE key=?", (key,)).fetchone()
    conn.close()
    return row[0] if row else None

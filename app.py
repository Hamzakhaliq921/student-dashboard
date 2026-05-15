from flask import Flask, render_template, request, redirect, session, jsonify
from database import (
    get_assignments, get_stats, get_attendance,
    get_attendance_scraped_at, get_scraper_status,
    set_scraper_status, init_db
)
import subprocess
import sys
import os

# Use persistent disk on Render, local path otherwise
if os.path.exists("/app/data"):
    os.environ.setdefault("DB_PATH", "/app/data/assignments.db")

app = Flask(__name__)
app.secret_key = "assignment_dashboard_secret_2024"

USERNAME = "admin"
PASSWORD = "admin"


# ─── AUTH ──────────────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form["username"] == USERNAME and request.form["password"] == PASSWORD:
            session["user"] = request.form["username"]
            return redirect("/dashboard")
        error = "Invalid username or password"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# ─── DASHBOARD ─────────────────────────────────────────────────

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    init_db()
    return render_template(
        "dashboard.html",
        assignments=get_assignments(),
        stats=get_stats()
    )


# ─── ASSIGNMENT SCRAPER ────────────────────────────────────────

@app.route("/run-scraper", methods=["POST"])
def run_scraper():
    if "user" not in session:
        return jsonify({"status": "error", "message": "Not authenticated"}), 401
    try:
        set_scraper_status("assignment_scraper", "running")
        path = os.path.join(os.path.dirname(__file__), "scraper.py")
        subprocess.Popen([sys.executable, path])
        return jsonify({"status": "success", "message": "Scraper started! Checking for results..."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/scraper-status")
def scraper_status_api():
    """Poll endpoint — frontend checks this to know when scraper is done"""
    if "user" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    status = get_scraper_status("assignment_scraper") or "idle"

    if status == "done":
        # Reset so next run works
        set_scraper_status("assignment_scraper", "idle")
        assignments = get_assignments()
        stats = get_stats()
        data = [{"course": a[0], "title": a[1], "deadline": a[2],
                 "status": a[3], "days_left": a[4]} for a in assignments]
        return jsonify({"status": "done", "assignments": data, "stats": stats})

    return jsonify({"status": status})


# ─── ATTENDANCE SCRAPER ────────────────────────────────────────

@app.route("/run-attendance-scraper", methods=["POST"])
def run_attendance_scraper():
    if "user" not in session:
        return jsonify({"status": "error", "message": "Not authenticated"}), 401
    try:
        set_scraper_status("attendance_scraper", "running")
        path = os.path.join(os.path.dirname(__file__), "attendance_scraper.py")
        subprocess.Popen([sys.executable, path])
        return jsonify({"status": "success", "message": "Attendance scraper started!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/attendance-status")
def attendance_status_api():
    """Poll endpoint — frontend checks this to know when attendance scraper is done"""
    if "user" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    status = get_scraper_status("attendance_scraper") or "idle"

    if status == "done":
        set_scraper_status("attendance_scraper", "idle")
        rows = get_attendance()
        courses = []
        for i, r in enumerate(rows):
            courses.append({
                "num":         i + 1,
                "code":        r[0],
                "title":       r[1],
                "teacher":     r[2],
                "present":     r[3],
                "absent":      r[4],
                "total":       r[5],
                "percentage":  r[6]
            })
        scraped_at = get_attendance_scraped_at()
        return jsonify({"status": "done", "courses": courses, "scraped_at": scraped_at})

    if status and status.startswith("error"):
        set_scraper_status("attendance_scraper", "idle")
        return jsonify({"status": "error", "message": status})

    return jsonify({"status": status})


@app.route("/api/attendance")
def api_attendance():
    """Return current saved attendance data"""
    if "user" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    rows = get_attendance()
    courses = []
    for i, r in enumerate(rows):
        courses.append({
            "num":        i + 1,
            "code":       r[0],
            "title":      r[1],
            "teacher":    r[2],
            "present":    r[3],
            "absent":     r[4],
            "total":      r[5],
            "percentage": r[6]
        })
    return jsonify({"courses": courses, "scraped_at": get_attendance_scraped_at()})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)

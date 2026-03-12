# 📚 Assignment Dashboard

A Flask + Selenium dashboard that scrapes your Bahria University CMS/LMS
assignments and displays them in a beautiful web interface.

---

## 📁 Project Structure

```
assignment_dashboard/
│
├── app.py           → Flask web server
├── scraper.py       → Selenium bot (scrapes CMS/LMS)
├── database.py      → SQLite database helper
├── requirements.txt → Python dependencies
├── assignments.db   → Auto-created database
│
├── templates/
│   ├── login.html      → Login page
│   └── dashboard.html  → Main dashboard
│
└── static/
    └── style.css        → Styles (dark theme)
```

---

## ⚙️ Setup

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Edit your credentials in scraper.py
```python
ENROLLMENT = "your-enrollment-number"
PASSWORD = "your-password"
```

### Step 3 — Run the scraper
```bash
python scraper.py
```
This opens Chrome, logs into CMS → LMS, and saves all assignments to the database.

### Step 4 — Run the web app
```bash
python app.py
```

### Step 5 — Open in browser
```
http://127.0.0.1:5000
```

Login:
- Username: `admin`
- Password: `admin`

---

## ✨ Features

- 🔐 Login protected dashboard
- 📊 Stats cards (Total / Upcoming / Passed / Urgent)
- 🔴🟢 Color-coded assignment status
- ⏳ Days left countdown for upcoming assignments
- 🔥 Urgent highlight for assignments due ≤ 3 days
- 🤖 "Run Scraper" button triggers Selenium from the website
- 🔔 Desktop notifications for urgent deadlines
- 📱 Mobile responsive design
- 🌙 Dark theme UI

---

## 🔧 Changing Login Password

Edit `app.py`:
```python
USERNAME = "your_username"
PASSWORD = "your_password"
```

---

## ⚠️ Notes

- Chrome must be installed for Selenium to work
- Run `scraper.py` before `app.py` for first-time data
- The "Run Scraper" button in the dashboard re-runs the bot live

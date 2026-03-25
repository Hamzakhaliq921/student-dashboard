<img width="1331" height="575" alt="0" src="https://github.com/user-attachments/assets/2e0feaba-d912-4e28-bf0a-aafcd0d05e6c" />
<img width="1346" height="606" alt="2" src="https://github.com/user-attachments/assets/53d1f7e0-bc18-4f98-ad8a-1fa40a94f5fa" />
<img width="1320" height="598" alt="3" src="https://github.com/user-attachments/assets/d04e6b47-a25e-45b7-841c-a49e425d9d6f" />
<img width="1325" height="597" alt="5" src="https://github.com/user-attachments/assets/fab198be-6135-4308-8d72-d0e8d7769575" />
<img width="1219" height="533" alt="6" src="https://github.com/user-attachments/assets/56e71efa-9d68-4dad-b558-c3b5487e894c" />
<img width="1328" height="499" alt="7" src="https://github.com/user-attachments/assets/08acbfb5-794f-4cbf-ad62-2ef3e83bddde" />
<img width="1336" height="525" alt="8" src="https://github.com/user-attachments/assets/247876d5-ad0f-434e-b5e4-63349ed276c9" />








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

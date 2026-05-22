# 📚 Student Dashboard — Bahria University CMS/LMS Tracker
https://github.com/user-attachments/assets/243c578b-276f-4c7c-bb08-7469001bdb39

A comprehensive web-based dashboard that automatically scrapes and tracks **assignments** and **attendance** from Bahria University's CMS and LMS portals. Built with Flask, Selenium, and SQLite.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.x-green)
![Selenium](https://img.shields.io/badge/Selenium-4.x-yellow)
![License](https://img.shields.io/badge/License-MIT-brightgreen)

---

## 🎯 Features

### 📋 Assignment Tracker
- ✅ Automatically scrapes assignments from Bahria University LMS
- ✅ Shows deadlines with smart urgency indicators (Today, Tomorrow, 3+ days)
- ✅ Categorizes assignments as **Upcoming** or **Passed**
- ✅ Desktop notifications for urgent deadlines (using `plyer`)
- ✅ Real-time stats: Total, Upcoming, Passed, Urgent (≤3 days)
- ✅ Filter assignments by status

### 📊 Attendance Tracker
- ✅ Scrapes attendance data from Bahria CMS
- ✅ Shows Present/Absent hours and percentage for each course
- ✅ Color-coded status indicators:
  - 🟢 **Safe** (≥75%)
  - 🟡 **Warning** (60-74%)
  - 🔴 **Danger** (<60%)
- ✅ Visual progress bars for quick status overview
- ✅ Filter courses by attendance level

### 🔐 Additional Features
- ✅ Secure login system with session management
- ✅ Responsive UI with modern glassmorphism design
- ✅ Tab-based interface for easy navigation
- ✅ Real-time scraper status monitoring
- ✅ SQLite database for persistent storage
- ✅ Works on both Windows (local) and Linux (deployment)

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Google Chrome** browser installed
- **ChromeDriver** (auto-installed by webdriver-manager)
- Bahria University CMS/LMS credentials

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/student-dashboard.git
cd student-dashboard
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure your credentials**

Edit `scraper.py` and `attendance_scraper.py`:
```python
# Line 24-25 in both files
ENROLLMENT = ""  # ← Your enrollment number
PASSWORD   = ""   # ← Your CMS password
```

Edit `app.py`:
```python
# Line 14-15
USERNAME = "admin"     # ← Your dashboard username
PASSWORD = "admin"     # ← Your dashboard password
```

4. **Run the application**
```bash
python app.py
```

5. **Access the dashboard**
- Open your browser: http://127.0.0.1:5000
- Login with credentials you set in `app.py`
- Click **🤖 Refresh Assignments** or **🤖 Refresh Attendance**

---

## 📁 Project Structure

```
ASSIGNMENT_DASHBOARD/
│
├── app.py                      # Flask backend server
├── scraper.py                  # Assignment scraper (Selenium)
├── attendance_scraper.py       # Attendance scraper (Selenium)
├── database.py                 # SQLite database functions
│
├── templates/
│   ├── login.html              # Login page
│   └── dashboard.html          # Main dashboard UI
│
├── static/
│   └── style.css               # Styling (glassmorphism theme)
│
├── assignments.db              # SQLite database (auto-created)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── Dockerfile                  # Docker configuration (optional)
├── render.yaml                 # Render deployment config
└── .gitignore                  # Git ignore rules
```

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Flask (Python) |
| **Web Scraping** | Selenium WebDriver |
| **Database** | SQLite3 |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Notifications** | Plyer (cross-platform) |
| **Deployment** | Render / Docker |

---

## 📋 Requirements

```txt
flask==2.3.2
selenium==4.15.2
webdriver-manager==4.0.1
plyer==2.1.0
```

---

## 🔧 Configuration

### Changing Login Credentials

**Dashboard Login** (`app.py`):
```python
USERNAME = "your_username"  # Change this
PASSWORD = "your_password"  # Change this
```

**CMS/LMS Credentials** (`scraper.py` & `attendance_scraper.py`):
```python
ENROLLMENT = "02-131232-059"  # Your enrollment
PASSWORD   = "your_cms_pass"   # Your CMS password
```

### Headless Mode (No Browser Window)

Uncomment line 37 in both scrapers:
```python
chrome_options.add_argument("--headless")  # Uncomment this
```

---

## 🐛 Troubleshooting

### ❌ Error: `[WinError 193] %1 is not a valid Win32 application`

**Solution:** ChromeDriver binary is corrupted or incompatible.

```bash
# Option 1: Reinstall dependencies
pip uninstall selenium webdriver-manager -y
pip install selenium==4.15.2 webdriver-manager

# Option 2: Manual ChromeDriver installation
# 1. Check Chrome version: chrome://version/
# 2. Download matching ChromeDriver: https://googlechromelabs.github.io/chrome-for-testing/
# 3. Extract to C:\chromedriver\
# 4. Update code:
service = Service('C:\\chromedriver\\chromedriver.exe')
```

### ❌ Scraper hangs or times out

**Possible causes:**
- CMS/LMS is down or slow
- Incorrect credentials
- UI structure changed

**Solution:**
- Check your enrollment/password in the scraper files
- Run scraper manually to see browser: comment out `--headless`
- Check CMS/LMS is accessible in your browser

### ❌ No assignments/attendance showing

**Solution:**
- Click the refresh button to trigger the scraper
- Check terminal for error messages
- Ensure Chrome browser is installed
- Verify your CMS credentials are correct

---

## 🎨 Customization

### Change Theme Colors

Edit `static/style.css`:
```css
:root {
    --primary: #6366f1;      /* Change primary color */
    --success: #10b981;      /* Success green */
    --warning: #f59e0b;      /* Warning orange */
    --danger: #ef4444;       /* Danger red */
}
```

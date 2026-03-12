"""
attendance_scraper.py
─────────────────────
Logs into Bahria University CMS, navigates to the Attendance page,
scrapes the StudentWiseAttendance table, and saves results to the DB.

Run standalone:   python attendance_scraper.py
Or triggered via: Flask /run-attendance-scraper route
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from database import init_db, clear_attendance, save_attendance, set_scraper_status
import time
import re

# ==============================
# ✅ YOUR CMS LOGIN DETAILS
# ==============================
ENROLLMENT = "enrollmemt"
PASSWORD   = "pass"

# ==============================
# ✅ BROWSER SETUP
# ==============================
import os as _os
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

if _os.path.exists("/usr/bin/chromium"):
    chrome_options.binary_location = "/usr/bin/chromium"
    driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=chrome_options)
else:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 25)

# Mark scraper as running
init_db()
set_scraper_status("attendance_scraper", "running")

print("=" * 60)
print("📊 ATTENDANCE SCRAPER STARTED")
print("=" * 60)

try:
    # ==============================
    # 1. LOGIN TO CMS
    # ==============================
    print("🔹 Opening CMS login page...")
    driver.get("https://cms.bahria.edu.pk/Logins/Student/Login.aspx")
    time.sleep(2)

    enroll_input = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//input[contains(@placeholder,'Enrollment') or contains(@id,'Enrollment') or @name='Enrollment']")
    ))
    enroll_input.clear()
    enroll_input.send_keys(ENROLLMENT)

    pass_input = driver.find_element(By.XPATH, "//input[@type='password']")
    pass_input.clear()
    pass_input.send_keys(PASSWORD)

    try:
        institute_select = Select(driver.find_element(By.XPATH, "//select[contains(@name,'Institute') or contains(@id,'Institute')]"))
        institute_select.select_by_visible_text("Karachi Campus")
    except:
        print("⚠️ Institute dropdown not found")

    try:
        role_select = Select(driver.find_element(By.XPATH, "//select[contains(@name,'Role') or contains(@id,'Role')]"))
        role_select.select_by_visible_text("Student")
    except:
        print("⚠️ Role dropdown not found")

    # Click login
    login_button = None
    for selector in [
        "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sign in')]",
        "//button[contains(text(),'Login')]",
        "//input[@type='submit']"
    ]:
        try:
            btn = driver.find_element(By.XPATH, selector)
            if btn.is_displayed():
                login_button = btn
                break
        except:
            continue

    if login_button:
        login_button.click()
    else:
        pass_input.send_keys(Keys.RETURN)

    time.sleep(4)
    print("✅ CMS login submitted")

    # ==============================
    # 2. NAVIGATE TO ATTENDANCE PAGE
    # ==============================
    print("🔹 Navigating to attendance page...")

    attendance_url = "https://cms.bahria.edu.pk/Sys/Student/ClassAttendance/StudentWiseAttendance.aspx"
    driver.get(attendance_url)
    time.sleep(4)

    # If redirected to login, re-login
    if "login" in driver.current_url.lower() or "Login" in driver.current_url:
        print("⚠️ Redirected to login, re-logging in...")
        enroll_input = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[contains(@placeholder,'Enrollment') or contains(@id,'Enrollment')]")
        ))
        enroll_input.clear()
        enroll_input.send_keys(ENROLLMENT)
        pass_input = driver.find_element(By.XPATH, "//input[@type='password']")
        pass_input.clear()
        pass_input.send_keys(PASSWORD)
        try:
            institute_select = Select(driver.find_element(By.XPATH, "//select[contains(@name,'Institute') or contains(@id,'Institute')]"))
            institute_select.select_by_visible_text("Karachi Campus")
        except:
            pass
        try:
            role_select = Select(driver.find_element(By.XPATH, "//select[contains(@name,'Role') or contains(@id,'Role')]"))
            role_select.select_by_visible_text("Student")
        except:
            pass
        pass_input.send_keys(Keys.RETURN)
        time.sleep(4)
        driver.get(attendance_url)
        time.sleep(4)

    print(f"📍 Current URL: {driver.current_url}")

    # ==============================
    # 3. SCRAPE THE ATTENDANCE TABLE
    # ==============================
    print("🔍 Looking for attendance table...")

    # Wait for table to load
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
    except:
        print("⚠️ Timed out waiting for table")

    time.sleep(2)

    # Find the main attendance table
    attendance_table = None
    tables = driver.find_elements(By.TAG_NAME, "table")

    for table in tables:
        if not table.is_displayed():
            continue
        text = table.text.lower()
        # Look for keywords that indicate it's the attendance table
        if ("present" in text or "absent" in text or "attendance" in text) and "course" in text:
            attendance_table = table
            print("✅ Found attendance table")
            break

    if not attendance_table:
        # Try finding by common CMS grid IDs
        for grid_id in ["GridView1", "gvAttendance", "ctl00_ContentPlaceHolder1_GridView1"]:
            try:
                attendance_table = driver.find_element(By.ID, grid_id)
                print(f"✅ Found table by ID: {grid_id}")
                break
            except:
                continue

    if not attendance_table:
        print("❌ Attendance table not found. Trying to print page structure...")
        print("Page title:", driver.title)
        print("Page URL:", driver.current_url)
        # Last resort: grab any visible table with numbers
        for table in tables:
            if table.is_displayed() and len(table.find_elements(By.TAG_NAME, "tr")) > 3:
                attendance_table = table
                print("⚠️ Using first visible table with rows")
                break

    if not attendance_table:
        raise Exception("Could not find attendance table on the page")

    # ==============================
    # 4. PARSE TABLE ROWS
    # ==============================
    print("📋 Parsing attendance rows...")

    rows = attendance_table.find_elements(By.TAG_NAME, "tr")
    scraped_courses = []

    # Detect header row to find column indices
    header_map = {}
    for row in rows:
        headers = row.find_elements(By.TAG_NAME, "th")
        if not headers:
            headers = row.find_elements(By.TAG_NAME, "td")

        if headers and len(headers) >= 4:
            for i, h in enumerate(headers):
                text = h.text.strip().lower()
                if "code" in text:
                    header_map["code"] = i
                elif "course" in text or "title" in text or "registered" in text:
                    header_map["title"] = i
                elif "teacher" in text or "instructor" in text:
                    header_map["teacher"] = i
                elif "present" in text:
                    header_map["present"] = i
                elif "absent" in text:
                    header_map["absent"] = i
                elif "total" in text:
                    header_map["total"] = i
            if header_map:
                print(f"✅ Detected columns: {header_map}")
                break

    # Default fallback column positions (matches the CMS screenshot)
    # #  | Code | Registered Course Title | Credit Hours | Majors | Offered Course | Class | Teacher | Fee | Present | Absent | Total | Actions
    # 0     1         2                      3               4          5              6        7      8      9        10       11      12
    if not header_map:
        print("⚠️ Could not detect headers, using default CMS column positions")
        header_map = {
            "code":    1,
            "title":   2,
            "teacher": 7,
            "present": 9,
            "absent":  10,
            "total":   11
        }

    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) < 4:
            continue

        try:
            # Skip header-like rows
            first_cell = cells[0].text.strip()
            if not first_cell.isdigit():
                continue

            def get_cell(key, fallback=""):
                idx = header_map.get(key)
                if idx is not None and idx < len(cells):
                    return cells[idx].text.strip()
                return fallback

            code    = get_cell("code",    f"COURSE{first_cell}")
            title   = get_cell("title",   f"Course {first_cell}")
            teacher = get_cell("teacher", "N/A")

            # Parse numeric values — handle "19.0 :90.48%" format from CMS
            def parse_num(raw):
                if not raw:
                    return 0.0
                # Extract first number from string like "19.0 :90.48%"
                match = re.search(r'[\d.]+', raw)
                return float(match.group()) if match else 0.0

            present_raw = get_cell("present", "0")
            absent_raw  = get_cell("absent",  "0")
            total_raw   = get_cell("total",   "0")

            present_hrs = parse_num(present_raw)
            absent_hrs  = parse_num(absent_raw)
            total_hrs   = parse_num(total_raw)

            # Calculate percentage
            if total_hrs > 0:
                percentage = round((present_hrs / total_hrs) * 100, 2)
            else:
                percentage = 0.0

            # Some CMS cells embed percentage like "19.0 :90.48%"
            pct_match = re.search(r'([\d.]+)%', present_raw)
            if pct_match:
                percentage = float(pct_match.group(1))

            course_data = {
                "code":        code,
                "title":       title,
                "teacher":     teacher,
                "present_hrs": present_hrs,
                "absent_hrs":  absent_hrs,
                "total_hrs":   total_hrs,
                "percentage":  percentage
            }
            scraped_courses.append(course_data)

            status = "✅ SAFE" if percentage >= 75 else ("⚠️ WARNING" if percentage >= 60 else "🚨 DANGER")
            print(f"  [{first_cell}] {code} — {title[:40]}")
            print(f"       Present:{present_hrs}  Absent:{absent_hrs}  Total:{total_hrs}  → {percentage}%  {status}")

        except Exception as e:
            print(f"  ⚠️ Skipping row: {e}")
            continue

    # ==============================
    # 5. SAVE TO DATABASE
    # ==============================
    if scraped_courses:
        print(f"\n💾 Saving {len(scraped_courses)} courses to database...")
        clear_attendance()
        for c in scraped_courses:
            save_attendance(
                code        = c["code"],
                title       = c["title"],
                teacher     = c["teacher"],
                present_hrs = c["present_hrs"],
                absent_hrs  = c["absent_hrs"],
                total_hrs   = c["total_hrs"],
                percentage  = c["percentage"]
            )
        print("✅ Attendance saved to database!")
        set_scraper_status("attendance_scraper", "done")
    else:
        print("❌ No courses found — nothing saved")
        set_scraper_status("attendance_scraper", "error:no_courses")

    print("\n" + "=" * 60)
    print(f"✅ ATTENDANCE SCRAPE COMPLETE — {len(scraped_courses)} courses")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ SCRAPER ERROR: {e}")
    import traceback
    traceback.print_exc()
    set_scraper_status("attendance_scraper", f"error:{str(e)}")

finally:
    time.sleep(5)
    # Don't close — let user see browser
    # driver.quit()

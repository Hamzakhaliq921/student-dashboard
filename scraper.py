from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from database import init_db, save_assignment, clear_assignments, set_scraper_status
import time
import re
import os

try:
    from plyer import notification
    NOTIFICATIONS_ENABLED = True
except ImportError:
    NOTIFICATIONS_ENABLED = False
    print("⚠️ plyer not installed - desktop notifications disabled")

# ==============================
# ✅ NOTIFICATION FUNCTION
# ==============================
def send_notification(title, message, urgent=False):
    if not NOTIFICATIONS_ENABLED:
        return
    try:
        notification.notify(
            title=title,
            message=message,
            timeout=10 if urgent else 7,
            app_name="Assignment Reminder"
        )
        print(f"🔔 Notification: {title}")
    except Exception as e:
        print(f"⚠️ Notification failed: {e}")

# ==============================
# ✅ USER LOGIN DETAILS — EDIT THESE
# ==============================


# ==============================
# ✅ BROWSER SETUP (FIXED FOR WINDOWS)
# ==============================
chrome_options = Options()
#chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-gpu")  # Helps with Windows compatibility

# Detect environment: Linux server vs Windows local
if os.path.exists("/usr/bin/chromium"):
    # Linux server (Render)
    chrome_options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
else:
    # Windows local — use webdriver-manager with proper cleanup
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        # Force fresh download and installation
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver installed at: {driver_path}")
        service = Service(driver_path)
    except Exception as e:
        print(f"❌ ChromeDriver setup failed: {e}")
        print("\n🔧 MANUAL FIX:")
        print("1. Download ChromeDriver from: https://googlechromelabs.github.io/chrome-for-testing/")
        print("2. Match your Chrome version (chrome://version/)")
        print("3. Extract chromedriver.exe to C:\\chromedriver\\")
        print("4. Update code to use: Service('C:\\\\chromedriver\\\\chromedriver.exe')")
        exit(1)

# Initialize driver
try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 25)
    print("✅ Browser initialized successfully")
except Exception as e:
    print(f"❌ Failed to start Chrome: {e}")
    print("\n🔧 TROUBLESHOOTING:")
    print("1. Ensure Chrome browser is installed")
    print("2. Check Chrome version matches ChromeDriver")
    print("3. Try: pip uninstall selenium webdriver-manager")
    print("          pip install selenium==4.15.2 webdriver-manager")
    exit(1)

# ==============================
# ✅ FUNCTION TO PARSE DEADLINE DATE
# ==============================
def parse_deadline(deadline_text):
    if not deadline_text or deadline_text.strip() == "":
        return None

    deadline_text = deadline_text.strip()

    try:
        patterns = [
            r'(\d{1,2})\s+(\w+)\s+(\d{4})\s+(\d{1,2}):(\d{2})\s*(am|pm)',
            r'(\d{1,2})\s+(\w+)\s+(\d{4})-(\d{1,2}):(\d{2})\s*(am|pm)',
            r'(\d{1,2})\s+(\w+)\s+(\d{4}):\s*(\d{1,2}):(\d{2})\s*(am|pm)',
            r'(\d{1,2})\s+(\w+)\s+(\d{4})'
        ]

        for pattern in patterns:
            match = re.search(pattern, deadline_text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 3:
                    day = int(groups[0])
                    month_name = groups[1]
                    year = int(groups[2])

                    hour = 23
                    minute = 59
                    am_pm = 'pm'

                    if len(groups) >= 6:
                        hour = int(groups[3])
                        minute = int(groups[4])
                        am_pm = groups[5].lower() if len(groups) > 5 else 'pm'

                    month_dict = {
                        'january': 1, 'february': 2, 'march': 3, 'april': 4,
                        'may': 5, 'june': 6, 'july': 7, 'august': 8,
                        'september': 9, 'october': 10, 'november': 11, 'december': 12
                    }
                    month = month_dict.get(month_name.lower(), 1)

                    if am_pm == 'pm' and hour != 12:
                        hour += 12
                    elif am_pm == 'am' and hour == 12:
                        hour = 0

                    return datetime(year, month, day, hour, minute)
    except Exception as e:
        print(f"⚠️ Could not parse deadline: '{deadline_text}' - Error: {e}")

    return None

# ==============================
# ✅ INIT DATABASE
# ==============================
init_db()
clear_assignments()  # Clear old data before fresh scrape
print("🗄️ Database ready")

# ==============================
# ✅ 1. LOGIN TO CMS
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
    print("⚠️ Institute dropdown not found or already selected")

try:
    role_select = Select(driver.find_element(By.XPATH, "//select[contains(@name,'Role') or contains(@id,'Role')]"))
    role_select.select_by_visible_text("Student")
except:
    print("⚠️ Role dropdown not found or already selected")

try:
    login_button = None
    selectors = [
        "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sign in')]",
        "//button[contains(text(), 'Sign In')]",
        "//button[contains(text(), 'Login')]",
        "//input[@type='submit' and @value='Login']",
        "//input[@type='submit' and @value='Sign In']"
    ]

    for selector in selectors:
        try:
            login_button = driver.find_element(By.XPATH, selector)
            if login_button.is_displayed():
                break
        except:
            continue

    if login_button:
        login_button.click()
    else:
        pass_input.send_keys(Keys.RETURN)
except Exception as e:
    print(f"⚠️ Login button click issue: {e}")
    pass_input.send_keys(Keys.RETURN)

try:
    wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Dashboard')] | //h2[contains(text(), 'Dashboard')]")))
    print("✅ CMS login successful!")
    time.sleep(3)
except Exception as e:
    if "Dashboard" in driver.title or "dashboard" in driver.current_url.lower():
        print("✅ CMS login successful!")
        time.sleep(3)
    else:
        print("❌ CMS login failed")
        driver.quit()
        exit()

# ==============================
# ✅ 2. CLICK "To LMS" LINK
# ==============================
print("🔹 Looking for 'To LMS' link...")
lms_selectors = [
    "//a[contains(translate(text(), 'TOLMS', 'tolms'), 'to lms')]",
    "//a[contains(text(), 'LMS')]",
    "//a[contains(@href, 'lms')]",
    "//a[contains(@onclick, 'lms')]",
    "//div[contains(text(), 'To LMS')]/ancestor::a",
    "//*[contains(text(), 'To LMS')]"
]

lms_link = None
for selector in lms_selectors:
    try:
        elements = driver.find_elements(By.XPATH, selector)
        for element in elements:
            if element.is_displayed():
                lms_link = element
                print(f"✅ Found LMS link")
                break
        if lms_link:
            break
    except:
        continue

if lms_link:
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", lms_link)
        time.sleep(1)
        lms_url = lms_link.get_attribute('href')
        print(f"🔗 LMS URL: {lms_url}")
        driver.execute_script("arguments[0].click();", lms_link)
        print("✅ Clicked 'To LMS' link")
        time.sleep(5)
    except Exception as e:
        print(f"⚠️ Could not click LMS link: {e}")
else:
    print("⚠️ 'To LMS' link not found")

# ==============================
# ✅ 3. SWITCH TO LMS WINDOW/TAB
# ==============================
print(f"🔹 Checking windows... (Total: {len(driver.window_handles)})")

if len(driver.window_handles) > 1:
    driver.switch_to.window(driver.window_handles[-1])
    print("✅ Switched to new window/tab")
    time.sleep(2)

print(f"📍 Current URL: {driver.current_url}")

# ==============================
# ✅ 4. LOGIN TO LMS IF NEEDED
# ==============================
if "login" in driver.current_url.lower():
    print("🔹 LMS login page detected, logging in...")
    try:
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username_field.clear()
        username_field.send_keys(ENROLLMENT)

        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(PASSWORD)

        login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_btn.click()
        print("✅ Submitted LMS login form")
        time.sleep(5)
    except Exception as e:
        print(f"⚠️ LMS login form issue: {e}")

print(f"📍 Current URL after login: {driver.current_url}")

# ==============================
# ✅ 5. NAVIGATE TO ASSIGNMENTS
# ==============================
print("🔹 Looking for Assignments link...")

assignments_selectors = [
    "//a[contains(text(), 'Assignment')]",
    "//a[contains(@href, 'assignment')]",
    "//a[contains(@href, 'Assignment')]",
    "//*[contains(text(), 'Assignment')]/ancestor::a",
    "//li//a[contains(text(), 'Assignment')]"
]

assignments_link = None
for selector in assignments_selectors:
    try:
        elements = driver.find_elements(By.XPATH, selector)
        for element in elements:
            if element.is_displayed():
                assignments_link = element
                print(f"✅ Found Assignments link")
                break
        if assignments_link:
            break
    except:
        continue

if assignments_link:
    try:
        assignments_url = assignments_link.get_attribute('href')
        print(f"🔗 Assignments URL: {assignments_url}")
        driver.execute_script("arguments[0].click();", assignments_link)
        print("✅ Clicked Assignments link")
        time.sleep(5)
    except Exception as e:
        print(f"⚠️ Could not click Assignments link: {e}")
else:
    print("⚠️ Assignments link not found")
    print("📄 Page title:", driver.title)

print(f"📍 Final URL: {driver.current_url}")

if "assignment" not in driver.current_url.lower():
    print("\n" + "="*60)
    print("⚠️ MANUAL NAVIGATION NEEDED")
    print("="*60)
    print("Please manually click on 'Assignments' in the LMS")
    print("Then press ENTER here to continue...")
    input()
    print(f"📍 Current URL: {driver.current_url}")

time.sleep(2)

# ==============================
# ✅ 6. GET ALL COURSES
# ==============================
print("🔍 Getting all course names...")

def get_course_dropdown():
    dropdown_selectors = [
        "//select[contains(@name, 'course') or contains(@id, 'course')]",
        "//select[contains(@onchange, 'course')]",
        "//select[option[contains(text(), 'Select Course')]]",
        "//td[contains(text(), 'Course:')]/following-sibling::td/select",
        "//select"
    ]

    for selector in dropdown_selectors:
        try:
            dropdown = driver.find_element(By.XPATH, selector)
            if dropdown.is_displayed():
                return dropdown
        except:
            continue
    return None

course_dropdown = get_course_dropdown()
if not course_dropdown:
    print("❌ Course dropdown not found")
    driver.quit()
    exit()

select = Select(course_dropdown)
courses = []

for option in select.options:
    course_name = option.text.strip()
    course_value = option.get_attribute('value')
    if course_name and "select" not in course_name.lower() and course_value:
        courses.append({'name': course_name, 'value': course_value})

print(f"📚 Found {len(courses)} courses to check")
print("Courses:", [c['name'] for c in courses])
print("=" * 60)

all_assignments = []

# ==============================
# ✅ 7. CHECK EACH COURSE
# ==============================
for course_index, course_info in enumerate(courses, 1):
    course_name = course_info['name']
    course_value = course_info['value']

    print(f"\n[{course_index}/{len(courses)}] 📖 Checking: {course_name}")

    try:
        course_dropdown = get_course_dropdown()
        if not course_dropdown:
            print(f"  ⚠️ Could not find dropdown for {course_name}")
            continue

        select = Select(course_dropdown)
        select.select_by_value(course_value)
        time.sleep(4)

        assignments_table = None
        tables = driver.find_elements(By.TAG_NAME, "table")

        for table in tables:
            if table.is_displayed():
                table_text = table.text.lower()
                if "assign" in table_text or "deadline" in table_text or "submission" in table_text:
                    assignments_table = table
                    break

        if not assignments_table:
            print(f"  📭 No assignments found")
            continue

        rows = assignments_table.find_elements(By.TAG_NAME, "tr")
        course_assignments = []

        for row in rows:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 3:
                    assign_no = cells[0].text.strip()

                    if assign_no and assign_no.isdigit():
                        title = cells[1].text.strip() if len(cells) > 1 else f"Assignment {assign_no}"

                        deadline_text = ""
                        for cell in cells:
                            cell_text = cell.text.strip()
                            if re.search(r'\d{1,2}\s+\w+\s+\d{4}', cell_text):
                                deadline_text = cell_text
                                break

                        if not deadline_text:
                            row_text = row.text
                            deadline_match = re.search(r'\d{1,2}\s+\w+\s+\d{4}[\s:\-]*\d{1,2}:\d{2}\s*(am|pm)?', row_text, re.IGNORECASE)
                            if deadline_match:
                                deadline_text = deadline_match.group(0)

                        deadline_dt = parse_deadline(deadline_text)

                        if deadline_dt:
                            is_passed = deadline_dt < datetime.now()
                            days_left = (deadline_dt - datetime.now()).days if not is_passed else 0

                            assignment_info = {
                                'course': course_name,
                                'assignment_no': assign_no,
                                'title': title,
                                'deadline_text': deadline_text,
                                'deadline_dt': deadline_dt,
                                'is_passed': is_passed,
                                'days_left': days_left
                            }
                            course_assignments.append(assignment_info)
                            all_assignments.append(assignment_info)

                            # Save to DB
                            save_assignment(
                                course=course_name,
                                title=f"Assignment #{assign_no}: {title}",
                                deadline=deadline_text,
                                status="PASSED" if is_passed else "UPCOMING",
                                days_left=days_left if not is_passed else None
                            )
            except Exception:
                continue

        if course_assignments:
            print(f"  ✅ Found {len(course_assignments)} assignments")
            for assign in course_assignments:
                status = "🔴 PASSED" if assign['is_passed'] else "🟢 UPCOMING"
                print(f"    #{assign['assignment_no']}: {assign['title']} - {assign['deadline_text']} ({status})")
        else:
            print(f"  📭 No assignments with deadlines")

    except Exception as e:
        print(f"  ⚠️ Error: {e}")
        continue

# ==============================
# ✅ 8. SUMMARY + NOTIFICATIONS
# ==============================
print("\n" + "="*60)
print("🎯 COMPLETE ASSIGNMENT ANALYSIS")
print("="*60)

if not all_assignments:
    print("❌ No assignments found in any course")
    send_notification("Assignment Check", "No assignments found", False)
else:
    upcoming = [a for a in all_assignments if not a['is_passed']]
    passed = [a for a in all_assignments if a['is_passed']]

    print(f"\n📊 SUMMARY:")
    print(f"  📈 Upcoming: {len(upcoming)}")
    print(f"  📉 Passed: {len(passed)}")

    send_notification(
        "📋 Assignment Summary",
        f"Upcoming: {len(upcoming)} | Passed: {len(passed)}",
        False
    )

    if upcoming:
        upcoming.sort(key=lambda x: x['deadline_dt'])
        print("\n🚨 UPCOMING DEADLINES:")
        print("-" * 50)

        for i, assignment in enumerate(upcoming, 1):
            days_left = (assignment['deadline_dt'] - datetime.now()).days

            if days_left == 0:
                urgency = "🔴 CRITICAL - DUE TODAY!"
                send_notification("🚨 DUE TODAY!", f"{assignment['course']}\n{assignment['title']}", True)
            elif days_left <= 1:
                urgency = "🟠 HIGH - DUE TOMORROW!"
                send_notification("⚠️ Due Tomorrow", f"{assignment['course']} - {assignment['title']}", True)
            elif days_left <= 3:
                urgency = "🟡 MEDIUM"
                send_notification("📚 Upcoming Assignment", f"{assignment['course']}\nDue in {days_left} days", False)
            else:
                urgency = "🟢 LOW"

            print(f"\n{i}. {urgency}")
            print(f"   📚 {assignment['course']}")
            print(f"   📝 Assignment #{assignment['assignment_no']}: {assignment['title']}")
            print(f"   📅 {assignment['deadline_text']}")
            print(f"   ⏳ {days_left} days left")

print("\n" + "="*60)
print("✅ SCAN COMPLETE! Open http://127.0.0.1:5000 to view dashboard")
print("="*60)

send_notification("✅ Scan Complete", "Assignment check finished. Open your dashboard!", False)
set_scraper_status("assignment_scraper", "done")
time.sleep(10)
driver.quit()
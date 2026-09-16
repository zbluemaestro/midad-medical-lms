import os
import shutil
import requests
import sqlite3

BASE_URL = "http://127.0.0.1:8080"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")
LMS_APP_DIR = os.path.join(PROJECT_DIR, "lms_app")
DB_PATH = os.path.join(LMS_APP_DIR, "data", "lms.db")

os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(os.path.join(DOCS_DIR, "static", "images"), exist_ok=True)

# 1. Sync Static Assets
print("[1/4] Syncing static images & assets...")
src_logo = os.path.join(LMS_APP_DIR, "static", "images", "midad_logo.svg")
dst_logo = os.path.join(DOCS_DIR, "static", "images", "midad_logo.svg")
if os.path.exists(src_logo):
    shutil.copy2(src_logo, dst_logo)

# Also copy uploads if needed
src_uploads = os.path.join(LMS_APP_DIR, "uploads")
dst_uploads = os.path.join(DOCS_DIR, "uploads")
if os.path.exists(src_uploads):
    shutil.copytree(src_uploads, dst_uploads, dirs_exist_ok=True)

# 2. Get list of courses to export
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
courses = conn.execute("SELECT id, title, slug FROM courses WHERE is_published = 1").fetchall()
conn.close()

def clean_html(html):
    # Adjust relative paths for GitHub Pages
    html = html.replace('href="/static/', 'href="./static/')
    html = html.replace('src="/static/', 'src="./static/')
    html = html.replace('src="/media/', 'src="./uploads/')
    html = html.replace('href="/login"', 'href="./login.html"')
    html = html.replace('href="/register"', 'href="./register.html"')
    html = html.replace('href="/"', 'href="./index.html"')
    for c in courses:
        slug = c["slug"]
        html = html.replace(f'href="/course/{slug}"', f'href="./course_{slug}.html"')
    return html

# 3. Export Main Pages
pages = [
    ("/", "index.html"),
    ("/login", "login.html"),
    ("/register", "register.html"),
]

print("[2/4] Exporting main portal pages...")
for path, filename in pages:
    try:
        r = requests.get(f"{BASE_URL}{path}", timeout=10)
        if r.status_code == 200:
            target = os.path.join(DOCS_DIR, filename)
            with open(target, "w", encoding="utf-8") as f:
                f.write(clean_html(r.text))
            print(f" [+] Exported {path} -> {filename}")
        else:
            print(f" [!] Failed {path}: HTTP {r.status_code}")
    except Exception as e:
        print(f" [!] Error exporting {path}: {e}")

# 4. Export Course Detail Pages
print("[3/4] Exporting course pages...")
for c in courses:
    slug = c["slug"]
    try:
        r = requests.get(f"{BASE_URL}/course/{slug}", timeout=10)
        if r.status_code == 200:
            filename = f"course_{slug}.html"
            target = os.path.join(DOCS_DIR, filename)
            with open(target, "w", encoding="utf-8") as f:
                f.write(clean_html(r.text))
            print(f" [+] Exported /course/{slug} -> {filename}")
    except Exception as e:
        print(f" [!] Error exporting course {slug}: {e}")

print("[4/4] Creating .nojekyll in docs/...")
with open(os.path.join(DOCS_DIR, ".nojekyll"), "w") as f:
    f.write("")

print("[+] All pages exported successfully into docs/!")

import sqlite3
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "lms.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Settings Table (Super Admin only)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """)

    # 3. Courses Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        description TEXT,
        instructor_id INTEGER NOT NULL,
        cover_image TEXT,
        category TEXT DEFAULT 'Technology',
        price REAL DEFAULT 0.0,
        is_published INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (instructor_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # 4. Lessons Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        order_index INTEGER DEFAULT 1,
        video_url TEXT,
        notes TEXT,
        pdf_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
    )
    """)

    # 5. Quizzes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        lesson_id INTEGER,
        title TEXT NOT NULL,
        passing_percentage INTEGER DEFAULT 70,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
        FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE SET NULL
    )
    """)

    # 6. Quiz Questions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        options_json TEXT NOT NULL,
        correct_option_index INTEGER NOT NULL DEFAULT 0,
        explanation TEXT,
        points INTEGER DEFAULT 10,
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
    )
    """)

    # 7. Enrollments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_lessons_json TEXT DEFAULT '[]',
        UNIQUE(user_id, course_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
    )
    """)

    # 8. Quiz Submissions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        quiz_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        total_points INTEGER NOT NULL,
        passed INTEGER NOT NULL,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
    )
    """)

    # Initialize Default Settings
    default_settings = {
        "site_name": "Midad Academy LMS",
        "tagline": "أكاديمية مداد التعليمية • Modern High-Performance Learning Platform",
        "hero_badge": "Next-Generation Learning",
        "hero_heading": "Build Skills, Build Courses, Lead the Future",
        "hero_subheading": "An independent, unrestricted learning management platform featuring video courses, interactive exams, and certified progression.",
        "primary_color": "#2563eb",
        "accent_color": "#3b82f6",
        "footer_text": "© 2026 Midad Academy LMS. All rights reserved. Self-Hosted & Unrestricted."
    }

    for k, v in default_settings.items():
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))

    # Initialize Master Super Admin User if not exists
    cursor.execute("SELECT id FROM users WHERE role = 'super_admin' LIMIT 1")
    super_admin = cursor.fetchone()
    if not super_admin:
        admin_email = "admin@lms.local"
        admin_name = "Omar Duhaim"
        admin_pass_hash = generate_password_hash("AdminPass2026!")
        cursor.execute(
            "INSERT INTO users (email, name, password_hash, role) VALUES (?, ?, ?, 'super_admin')",
            (admin_email, admin_name, admin_pass_hash)
        )
        admin_id = cursor.lastrowid
        print(f"[+] Initialized Master Super Admin: {admin_name} <{admin_email}> (Password: AdminPass2026!)")

        # Create Showcase Course
        cursor.execute("""
        INSERT INTO courses (title, slug, description, instructor_id, cover_image, category, price, is_published)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            "Full-Stack AI Systems & Autonomous Agents",
            "full-stack-ai-systems",
            "A comprehensive masterclass exploring LLM application design, vector databases, multi-agent frameworks, and production deployment.",
            admin_id,
            "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1200&auto=format&fit=crop&q=80",
            "Artificial Intelligence",
            0.0
        ))
        course_id = cursor.lastrowid

        # Lessons for Showcase Course
        cursor.execute("""
        INSERT INTO lessons (course_id, title, order_index, video_url, notes, pdf_url)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            course_id,
            "Lesson 1: Foundations of Autonomous Multi-Agent Architectures",
            1,
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "In this foundational lecture, we examine how autonomous agents perceive environment states, maintain conversation memory, formulate action plans, and call tools dynamically.",
            None
        ))
        lesson1_id = cursor.lastrowid

        cursor.execute("""
        INSERT INTO lessons (course_id, title, order_index, video_url, notes, pdf_url)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            course_id,
            "Lesson 2: Real-Time Tool Execution & API Integration",
            2,
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            "Deep dive into structured function calling, JSON schema validation, error recovery, and asynchronous execution.",
            None
        ))
        lesson2_id = cursor.lastrowid

        # Quiz for Lesson 1
        cursor.execute("""
        INSERT INTO quizzes (course_id, lesson_id, title, passing_percentage)
        VALUES (?, ?, ?, ?)
        """, (
            course_id,
            lesson1_id,
            "Knowledge Check: Multi-Agent Foundations",
            70
        ))
        quiz_id = cursor.lastrowid

        questions = [
            (
                quiz_id,
                "What is the primary role of a tool-calling mechanism in an autonomous agent?",
                json.dumps([
                    "To allow the language model to execute external actions and retrieve real-time data",
                    "To format plain text into Markdown",
                    "To slow down the inference speed for safety",
                    "To encrypt the database queries"
                ]),
                0,
                "Tool calling bridges the reasoning engine with external APIs, databases, and filesystem actions.",
                10
            ),
            (
                quiz_id,
                "Which memory pattern is most appropriate for retaining user preferences across long sessions?",
                json.dumps([
                    "Volatile cache only",
                    "Persistent database memory with semantic retrieval",
                    "Clearing memory after every 2 turns",
                    "Hardcoding memory in CSS"
                ]),
                1,
                "Persistent storage combined with vector/semantic search enables contextual recall across sessions.",
                10
            ),
            (
                quiz_id,
                "In a multi-tenant LMS SaaS, what is the best practice for tenant database security?",
                json.dumps([
                    "Store all passwords in plain text",
                    "Use separate databases or strict schema isolation per tenant",
                    "Allow any student to access any course",
                    "Disable database indexing"
                ]),
                1,
                "Data isolation prevents unauthorized cross-tenant data leakage.",
                10
            )
        ]

        for q in questions:
            cursor.execute("""
            INSERT INTO quiz_questions (quiz_id, question_text, options_json, correct_option_index, explanation, points)
            VALUES (?, ?, ?, ?, ?, ?)
            """, q)

    conn.commit()
    conn.close()

# Helper accessors
def get_settings():
    conn = get_db_connection()
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    conn.close()
    return {row["key"]: row["value"] for row in rows}

def update_settings(settings_dict):
    conn = get_db_connection()
    for k, v in settings_dict.items():
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))
    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user

def create_user(email, name, password, role="student"):
    conn = get_db_connection()
    pass_hash = generate_password_hash(password)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, name, password_hash, role) VALUES (?, ?, ?, ?)",
            (email.strip().lower(), name.strip(), pass_hash, role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id, None
    except sqlite3.IntegrityError:
        conn.close()
        return None, "Email address is already registered."

def update_user_role(user_id, new_role):
    valid_roles = ["super_admin", "instructor", "student"]
    if new_role not in valid_roles:
        return False, "Invalid role specified."
    conn = get_db_connection()
    conn.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    conn.commit()
    conn.close()
    return True, None

def get_all_users():
    conn = get_db_connection()
    users = conn.execute("SELECT id, email, name, role, created_at FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return users

if __name__ == "__main__":
    init_db()
    print("[+] Database initialized successfully.")

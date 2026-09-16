import os
import re
import json
import mimetypes
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, Response, send_from_directory, abort
)
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash

import database as db

# Initialize Flask
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
VIDEOS_DIR = os.path.join(UPLOADS_DIR, "videos")
PHOTOS_DIR = os.path.join(UPLOADS_DIR, "photos")
DOCS_DIR = os.path.join(UPLOADS_DIR, "documents")

for d in [VIDEOS_DIR, PHOTOS_DIR, DOCS_DIR]:
    os.makedirs(d, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "lms-midad-academy-super-secret-key-2026")

# Unrestricted Upload Limit (None = unlimited body size)
app.config["MAX_CONTENT_LENGTH"] = None
app.config["UPLOAD_FOLDER"] = UPLOADS_DIR

# Ensure DB is initialized
db.init_db()


# ------------------------------------------------------------------------------
# Context Processor for Global Template Data
# ------------------------------------------------------------------------------
@app.context_processor
def inject_global_data():
    settings = db.get_settings()
    current_user = None
    if "user_id" in session:
        current_user = db.get_user_by_id(session["user_id"])
    return dict(settings=settings, current_user=current_user)


# ------------------------------------------------------------------------------
# Authentication & RBAC Decorators
# ------------------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def super_admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in as Super Admin.", "warning")
            return redirect(url_for("login", next=request.url))
        user = db.get_user_by_id(session["user_id"])
        if not user or user["role"] != "super_admin":
            abort(403, description="Access Restricted: Only the Master Super Admin can modify website settings or manage user roles.")
        return f(*args, **kwargs)
    return decorated_function


def instructor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to access the Creator Studio.", "warning")
            return redirect(url_for("login", next=request.url))
        user = db.get_user_by_id(session["user_id"])
        if not user or user["role"] not in ["instructor", "super_admin"]:
            abort(403, description="Access Restricted: Only designated Course Creators can access the studio.")
        return f(*args, **kwargs)
    return decorated_function


# ------------------------------------------------------------------------------
# Error Handlers
# ------------------------------------------------------------------------------
@app.errorhandler(403)
def forbidden(e):
    return render_template("error.html", error_code=403, title="Permission Denied", message=e.description), 403

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", error_code=404, title="Page Not Found", message="The requested course or page could not be located."), 404


# ------------------------------------------------------------------------------
# Authentication Routes
# ------------------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = db.get_user_by_email(email)

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_role"] = user["role"]
            flash(f"Welcome back, {user['name']}!", "success")
            next_url = request.args.get("next")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            if user["role"] == "super_admin":
                return redirect(url_for("admin_users"))
            elif user["role"] == "instructor":
                return redirect(url_for("studio"))
            return redirect(url_for("index"))
        else:
            flash("Invalid email address or password.", "error")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.", "error")
            return render_template("register.html")

        user_id, err = db.create_user(email, name, password, role="student")
        if err:
            flash(err, "error")
            return render_template("register.html")

        session["user_id"] = user_id
        session["user_name"] = name
        session["user_role"] = "student"
        flash("Account created successfully! Welcome to the Academy.", "success")
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("index"))


# ------------------------------------------------------------------------------
# Super Admin Only: Website Customizer & User Role Management
# ------------------------------------------------------------------------------
@app.route("/admin/users")
@super_admin_only
def admin_users():
    users = db.get_all_users()
    return render_template("admin_users.html", users=users)


@app.route("/admin/users/<int:user_id>/role", methods=["POST"])
@super_admin_only
def change_user_role(user_id):
    new_role = request.form.get("role")
    target_user = db.get_user_by_id(user_id)

    if not target_user:
        flash("User not found.", "error")
        return redirect(url_for("admin_users"))

    # Protect self demotion
    if target_user["id"] == session["user_id"] and new_role != "super_admin":
        flash("Cannot demote your own Super Admin account.", "error")
        return redirect(url_for("admin_users"))

    ok, err = db.update_user_role(user_id, new_role)
    if ok:
        role_label = "Course Creator / Instructor" if new_role == "instructor" else ("Student" if new_role == "student" else "Super Admin")
        flash(f"Successfully updated {target_user['name']} to {role_label}.", "success")
    else:
        flash(err, "error")

    return redirect(url_for("admin_users"))


@app.route("/admin/settings", methods=["GET", "POST"])
@super_admin_only
def admin_settings():
    if request.method == "POST":
        new_settings = {
            "site_name": request.form.get("site_name", "").strip(),
            "tagline": request.form.get("tagline", "").strip(),
            "hero_heading": request.form.get("hero_heading", "").strip(),
            "hero_subheading": request.form.get("hero_subheading", "").strip(),
            "primary_color": request.form.get("primary_color", "#2563eb"),
            "footer_text": request.form.get("footer_text", "").strip(),
        }
        db.update_settings(new_settings)
        flash("Website settings and branding updated successfully!", "success")
        return redirect(url_for("admin_settings"))

    return render_template("admin_settings.html")


# ------------------------------------------------------------------------------
# Course Creator & Super Admin Studio
# ------------------------------------------------------------------------------
@app.route("/studio")
@instructor_required
def studio():
    conn = db.get_db_connection()
    user = db.get_user_by_id(session["user_id"])

    if user["role"] == "super_admin":
        courses = conn.execute("""
            SELECT c.*, u.name as instructor_name,
                   (SELECT COUNT(*) FROM lessons WHERE course_id = c.id) as lesson_count,
                   (SELECT COUNT(*) FROM enrollments WHERE course_id = c.id) as student_count
            FROM courses c
            JOIN users u ON c.instructor_id = u.id
            ORDER BY c.created_at DESC
        """).fetchall()
    else:
        courses = conn.execute("""
            SELECT c.*, u.name as instructor_name,
                   (SELECT COUNT(*) FROM lessons WHERE course_id = c.id) as lesson_count,
                   (SELECT COUNT(*) FROM enrollments WHERE course_id = c.id) as student_count
            FROM courses c
            JOIN users u ON c.instructor_id = u.id
            WHERE c.instructor_id = ?
            ORDER BY c.created_at DESC
        """, (user["id"],)).fetchall()

    conn.close()
    return render_template("studio.html", courses=courses)


@app.route("/studio/course/new", methods=["GET", "POST"])
@instructor_required
def new_course():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "General").strip()
        price = float(request.form.get("price", 0.0) or 0.0)
        is_published = 1 if request.form.get("is_published") else 0
        cover_image = request.form.get("cover_image", "").strip()

        # Handle direct cover image file upload if provided
        file = request.files.get("cover_file")
        if file and file.filename != "":
            fname = secure_filename(f"cover_{int(datetime.now().timestamp())}_{file.filename}")
            fpath = os.path.join(PHOTOS_DIR, fname)
            file.save(fpath)
            cover_image = f"/media/photos/{fname}"

        if not cover_image:
            cover_image = "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1200&auto=format&fit=crop&q=80"

        slug = re.sub(r"[^\w-]", "-", title.lower()).strip("-")
        slug = f"{slug}-{int(datetime.now().timestamp()) % 10000}"

        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO courses (title, slug, description, instructor_id, cover_image, category, price, is_published)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, slug, description, session["user_id"], cover_image, category, price, is_published))
        conn.commit()
        course_id = cursor.lastrowid
        conn.close()

        flash(f"Course '{title}' created successfully! Now add your video lectures and quizzes.", "success")
        return redirect(url_for("edit_course", course_id=course_id))

    return render_template("course_editor.html", course=None)


@app.route("/studio/course/<int:course_id>/edit", methods=["GET", "POST"])
@instructor_required
def edit_course(course_id):
    conn = db.get_db_connection()
    course = conn.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()

    if not course:
        conn.close()
        abort(404)

    # Permission check: super_admin or course owner
    user = db.get_user_by_id(session["user_id"])
    if user["role"] != "super_admin" and course["instructor_id"] != user["id"]:
        conn.close()
        abort(403, description="You can only edit courses you have created.")

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "General").strip()
        price = float(request.form.get("price", 0.0) or 0.0)
        is_published = 1 if request.form.get("is_published") else 0
        cover_image = request.form.get("cover_image", course["cover_image"]).strip()

        file = request.files.get("cover_file")
        if file and file.filename != "":
            fname = secure_filename(f"cover_{int(datetime.now().timestamp())}_{file.filename}")
            fpath = os.path.join(PHOTOS_DIR, fname)
            file.save(fpath)
            cover_image = f"/media/photos/{fname}"

        conn.execute("""
            UPDATE courses SET title = ?, description = ?, category = ?, price = ?, cover_image = ?, is_published = ?
            WHERE id = ?
        """, (title, description, category, price, cover_image, is_published, course_id))
        conn.commit()
        conn.close()

        flash("Course details saved successfully!", "success")
        return redirect(url_for("edit_course", course_id=course_id))

    lessons = conn.execute("SELECT * FROM lessons WHERE course_id = ? ORDER BY order_index ASC", (course_id,)).fetchall()
    quizzes = conn.execute("SELECT * FROM quizzes WHERE course_id = ? ORDER BY created_at ASC", (course_id,)).fetchall()
    conn.close()

    return render_template("course_editor.html", course=course, lessons=lessons, quizzes=quizzes)


@app.route("/studio/course/<int:course_id>/delete", methods=["POST"])
@instructor_required
def delete_course(course_id):
    conn = db.get_db_connection()
    course = conn.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
    if not course:
        conn.close()
        abort(404)

    user = db.get_user_by_id(session["user_id"])
    if user["role"] != "super_admin" and course["instructor_id"] != user["id"]:
        conn.close()
        abort(403)

    conn.execute("DELETE FROM courses WHERE id = ?", (course_id,))
    conn.commit()
    conn.close()
    flash(f"Course '{course['title']}' was removed.", "info")
    return redirect(url_for("studio"))


# ------------------------------------------------------------------------------
# Lesson Management (Unrestricted Video & PDF Uploads)
# ------------------------------------------------------------------------------
@app.route("/studio/course/<int:course_id>/lesson/new", methods=["GET", "POST"])
@instructor_required
def new_lesson(course_id):
    conn = db.get_db_connection()
    course = conn.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
    if not course:
        conn.close()
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        order_index = int(request.form.get("order_index", 1) or 1)
        notes = request.form.get("notes", "").strip()
        video_url = request.form.get("video_url", "").strip()
        pdf_url = request.form.get("pdf_url", "").strip()

        # Handle Video Upload (Unrestricted Size)
        video_file = request.files.get("video_file")
        if video_file and video_file.filename != "":
            vname = secure_filename(f"vid_{int(datetime.now().timestamp())}_{video_file.filename}")
            vpath = os.path.join(VIDEOS_DIR, vname)
            video_file.save(vpath)
            video_url = f"/media/videos/{vname}"

        # Handle PDF Upload
        pdf_file = request.files.get("pdf_file")
        if pdf_file and pdf_file.filename != "":
            pname = secure_filename(f"doc_{int(datetime.now().timestamp())}_{pdf_file.filename}")
            ppath = os.path.join(DOCS_DIR, pname)
            pdf_file.save(ppath)
            pdf_url = f"/media/documents/{pname}"

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO lessons (course_id, title, order_index, video_url, notes, pdf_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (course_id, title, order_index, video_url, notes, pdf_url))
        conn.commit()
        conn.close()

        flash(f"Lesson '{title}' saved successfully!", "success")
        return redirect(url_for("edit_course", course_id=course_id))

    conn.close()
    return render_template("lesson_editor.html", course=course, lesson=None)


@app.route("/studio/lesson/<int:lesson_id>/edit", methods=["GET", "POST"])
@instructor_required
def edit_lesson(lesson_id):
    conn = db.get_db_connection()
    lesson = conn.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,)).fetchone()
    if not lesson:
        conn.close()
        abort(404)

    course = conn.execute("SELECT * FROM courses WHERE id = ?", (lesson["course_id"],)).fetchone()
    user = db.get_user_by_id(session["user_id"])
    if user["role"] != "super_admin" and course["instructor_id"] != user["id"]:
        conn.close()
        abort(403)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        order_index = int(request.form.get("order_index", 1) or 1)
        notes = request.form.get("notes", "").strip()
        video_url = request.form.get("video_url", lesson["video_url"]).strip()
        pdf_url = request.form.get("pdf_url", lesson["pdf_url"]).strip()

        video_file = request.files.get("video_file")
        if video_file and video_file.filename != "":
            vname = secure_filename(f"vid_{int(datetime.now().timestamp())}_{video_file.filename}")
            vpath = os.path.join(VIDEOS_DIR, vname)
            video_file.save(vpath)
            video_url = f"/media/videos/{vname}"

        pdf_file = request.files.get("pdf_file")
        if pdf_file and pdf_file.filename != "":
            pname = secure_filename(f"doc_{int(datetime.now().timestamp())}_{pdf_file.filename}")
            ppath = os.path.join(DOCS_DIR, pname)
            pdf_file.save(ppath)
            pdf_url = f"/media/documents/{pname}"

        conn.execute("""
            UPDATE lessons SET title = ?, order_index = ?, video_url = ?, notes = ?, pdf_url = ?
            WHERE id = ?
        """, (title, order_index, video_url, notes, pdf_url, lesson_id))
        conn.commit()
        conn.close()

        flash(f"Lesson '{title}' updated successfully!", "success")
        return redirect(url_for("edit_course", course_id=course["id"]))

    conn.close()
    return render_template("lesson_editor.html", course=course, lesson=lesson)


@app.route("/studio/lesson/<int:lesson_id>/delete", methods=["POST"])
@instructor_required
def delete_lesson(lesson_id):
    conn = db.get_db_connection()
    lesson = conn.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,)).fetchone()
    if not lesson:
        conn.close()
        abort(404)
    course_id = lesson["course_id"]
    conn.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))
    conn.commit()
    conn.close()
    flash("Lesson removed.", "info")
    return redirect(url_for("edit_course", course_id=course_id))


# ------------------------------------------------------------------------------
# Quiz Builder & Auto-Grader
# ------------------------------------------------------------------------------
@app.route("/studio/course/<int:course_id>/quiz/new", methods=["GET", "POST"])
@instructor_required
def new_quiz(course_id):
    conn = db.get_db_connection()
    course = conn.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
    if not course:
        conn.close()
        abort(404)

    lessons = conn.execute("SELECT id, title FROM lessons WHERE course_id = ?", (course_id,)).fetchall()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        lesson_id = request.form.get("lesson_id") or None
        passing_percentage = int(request.form.get("passing_percentage", 70) or 70)

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO quizzes (course_id, lesson_id, title, passing_percentage)
            VALUES (?, ?, ?, ?)
        """, (course_id, lesson_id, title, passing_percentage))
        quiz_id = cursor.lastrowid

        # Process questions submitted dynamically
        questions_raw = request.form.get("questions_payload", "[]")
        try:
            questions = json.loads(questions_raw)
            for q in questions:
                q_text = q.get("question_text", "").strip()
                opts = q.get("options", [])
                correct = int(q.get("correct_option_index", 0))
                expl = q.get("explanation", "").strip()
                pts = int(q.get("points", 10))

                if q_text and opts:
                    cursor.execute("""
                        INSERT INTO quiz_questions (quiz_id, question_text, options_json, correct_option_index, explanation, points)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (quiz_id, q_text, json.dumps(opts), correct, expl, pts))
        except Exception as ex:
            print(f"[!] Error parsing quiz questions payload: {ex}")

        conn.commit()
        conn.close()

        flash(f"Quiz '{title}' created and saved successfully!", "success")
        return redirect(url_for("edit_course", course_id=course_id))

    conn.close()
    return render_template("quiz_editor.html", course=course, lessons=lessons, quiz=None, questions=[])


@app.route("/studio/quiz/<int:quiz_id>/edit", methods=["GET", "POST"])
@instructor_required
def edit_quiz(quiz_id):
    conn = db.get_db_connection()
    quiz = conn.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    if not quiz:
        conn.close()
        abort(404)

    course = conn.execute("SELECT * FROM courses WHERE id = ?", (quiz["course_id"],)).fetchone()
    lessons = conn.execute("SELECT id, title FROM lessons WHERE course_id = ?", (quiz["course_id"],)).fetchall()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        lesson_id = request.form.get("lesson_id") or None
        passing_percentage = int(request.form.get("passing_percentage", 70) or 70)

        conn.execute("""
            UPDATE quizzes SET title = ?, lesson_id = ?, passing_percentage = ? WHERE id = ?
        """, (title, lesson_id, passing_percentage, quiz_id))

        # Re-save questions
        conn.execute("DELETE FROM quiz_questions WHERE quiz_id = ?", (quiz_id,))
        questions_raw = request.form.get("questions_payload", "[]")
        try:
            questions = json.loads(questions_raw)
            for q in questions:
                q_text = q.get("question_text", "").strip()
                opts = q.get("options", [])
                correct = int(q.get("correct_option_index", 0))
                expl = q.get("explanation", "").strip()
                pts = int(q.get("points", 10))

                if q_text and opts:
                    conn.execute("""
                        INSERT INTO quiz_questions (quiz_id, question_text, options_json, correct_option_index, explanation, points)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (quiz_id, q_text, json.dumps(opts), correct, expl, pts))
        except Exception as ex:
            print(f"[!] Error updating quiz questions: {ex}")

        conn.commit()
        conn.close()

        flash(f"Quiz '{title}' saved successfully!", "success")
        return redirect(url_for("edit_course", course_id=course["id"]))

    questions_rows = conn.execute("SELECT * FROM quiz_questions WHERE quiz_id = ?", (quiz_id,)).fetchall()
    questions = []
    for r in questions_rows:
        questions.append({
            "question_text": r["question_text"],
            "options": json.loads(r["options_json"]),
            "correct_option_index": r["correct_option_index"],
            "explanation": r["explanation"],
            "points": r["points"]
        })

    conn.close()
    return render_template("quiz_editor.html", course=course, lessons=lessons, quiz=quiz, questions=questions)


@app.route("/studio/quiz/<int:quiz_id>/delete", methods=["POST"])
@instructor_required
def delete_quiz(quiz_id):
    conn = db.get_db_connection()
    quiz = conn.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    if not quiz:
        conn.close()
        abort(404)
    course_id = quiz["course_id"]
    conn.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
    conn.commit()
    conn.close()
    flash("Quiz removed.", "info")
    return redirect(url_for("edit_course", course_id=course_id))


# ------------------------------------------------------------------------------
# Student Catalog & Course Player
# ------------------------------------------------------------------------------
@app.route("/")
def index():
    conn = db.get_db_connection()
    courses = conn.execute("""
        SELECT c.*, u.name as instructor_name,
               (SELECT COUNT(*) FROM lessons WHERE course_id = c.id) as lesson_count
        FROM courses c
        JOIN users u ON c.instructor_id = u.id
        WHERE c.is_published = 1
        ORDER BY c.created_at DESC
    """).fetchall()
    conn.close()
    return render_template("index.html", courses=courses)


@app.route("/course/<slug>")
def course_detail(slug):
    conn = db.get_db_connection()
    course = conn.execute("""
        SELECT c.*, u.name as instructor_name, u.email as instructor_email
        FROM courses c
        JOIN users u ON c.instructor_id = u.id
        WHERE c.slug = ?
    """, (slug,)).fetchone()

    if not course:
        conn.close()
        abort(404)

    lessons = conn.execute("SELECT id, title, order_index FROM lessons WHERE course_id = ? ORDER BY order_index ASC", (course["id"],)).fetchall()
    quizzes = conn.execute("SELECT id, title, passing_percentage FROM quizzes WHERE course_id = ?", (course["id"],)).fetchall()

    is_enrolled = False
    if "user_id" in session:
        enrollment = conn.execute("SELECT id FROM enrollments WHERE user_id = ? AND course_id = ?", (session["user_id"], course["id"])).fetchone()
        is_enrolled = (enrollment is not None)

    conn.close()
    return render_template("course_detail.html", course=course, lessons=lessons, quizzes=quizzes, is_enrolled=is_enrolled)


@app.route("/course/<slug>/enroll", methods=["POST"])
@login_required
def enroll_course(slug):
    conn = db.get_db_connection()
    course = conn.execute("SELECT id, title FROM courses WHERE slug = ?", (slug,)).fetchone()
    if not course:
        conn.close()
        abort(404)

    try:
        conn.execute("INSERT OR IGNORE INTO enrollments (user_id, course_id) VALUES (?, ?)", (session["user_id"], course["id"]))
        conn.commit()
        flash(f"Enrolled in '{course['title']}'! Happy learning.", "success")
    except Exception as e:
        flash(f"Enrollment error: {e}", "error")

    conn.close()
    return redirect(url_for("learn_course", slug=slug))


@app.route("/learn/<slug>")
@login_required
def learn_course(slug):
    conn = db.get_db_connection()
    course = conn.execute("SELECT * FROM courses WHERE slug = ?", (slug,)).fetchone()
    if not course:
        conn.close()
        abort(404)

    lessons = conn.execute("SELECT * FROM lessons WHERE course_id = ? ORDER BY order_index ASC", (course["id"],)).fetchall()
    quizzes = conn.execute("SELECT * FROM quizzes WHERE course_id = ?", (course["id"],)).fetchall()

    if not lessons:
        conn.close()
        flash("This course does not have any lessons published yet.", "warning")
        return redirect(url_for("course_detail", slug=slug))

    active_lesson_id = request.args.get("lesson_id")
    active_lesson = None
    if active_lesson_id:
        active_lesson = conn.execute("SELECT * FROM lessons WHERE id = ? AND course_id = ?", (active_lesson_id, course["id"])).fetchone()

    if not active_lesson:
        active_lesson = lessons[0]

    # Associated quiz for this lesson if any
    lesson_quiz = conn.execute("SELECT * FROM quizzes WHERE lesson_id = ? LIMIT 1", (active_lesson["id"],)).fetchone()
    conn.close()

    return render_template(
        "course_player.html",
        course=course,
        lessons=lessons,
        quizzes=quizzes,
        active_lesson=active_lesson,
        lesson_quiz=lesson_quiz
    )


@app.route("/my-learning")
@login_required
def my_learning():
    conn = db.get_db_connection()
    courses = conn.execute("""
        SELECT c.*, e.enrolled_at,
               (SELECT COUNT(*) FROM lessons WHERE course_id = c.id) as lesson_count
        FROM courses c
        JOIN enrollments e ON c.id = e.course_id
        WHERE e.user_id = ?
        ORDER BY e.enrolled_at DESC
    """, (session["user_id"],)).fetchall()
    conn.close()
    return render_template("my_learning.html", courses=courses)


# ------------------------------------------------------------------------------
# Interactive Quiz Taker & Instant Auto-Grading
# ------------------------------------------------------------------------------
@app.route("/quiz/<int:quiz_id>", methods=["GET", "POST"])
@login_required
def take_quiz(quiz_id):
    conn = db.get_db_connection()
    quiz = conn.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    if not quiz:
        conn.close()
        abort(404)

    course = conn.execute("SELECT * FROM courses WHERE id = ?", (quiz["course_id"],)).fetchone()
    questions_rows = conn.execute("SELECT * FROM quiz_questions WHERE quiz_id = ?", (quiz_id,)).fetchall()

    questions = []
    for r in questions_rows:
        questions.append({
            "id": r["id"],
            "question_text": r["question_text"],
            "options": json.loads(r["options_json"]),
            "correct_option_index": r["correct_option_index"],
            "explanation": r["explanation"],
            "points": r["points"]
        })

    if request.method == "POST":
        total_points = sum(q["points"] for q in questions)
        user_score = 0
        feedback = []

        for q in questions:
            selected = request.form.get(f"q_{q['id']}")
            is_correct = False
            selected_idx = None
            if selected is not None:
                try:
                    selected_idx = int(selected)
                    if selected_idx == q["correct_option_index"]:
                        user_score += q["points"]
                        is_correct = True
                except ValueError:
                    pass

            feedback.append({
                "question_text": q["question_text"],
                "options": q["options"],
                "selected_index": selected_idx,
                "correct_index": q["correct_option_index"],
                "is_correct": is_correct,
                "explanation": q["explanation"],
                "points_earned": q["points"] if is_correct else 0,
                "max_points": q["points"]
            })

        percent = int((user_score / total_points * 100)) if total_points > 0 else 100
        passed = 1 if percent >= quiz["passing_percentage"] else 0

        # Save submission
        conn.execute("""
            INSERT INTO quiz_submissions (user_id, quiz_id, score, total_points, passed)
            VALUES (?, ?, ?, ?, ?)
        """, (session["user_id"], quiz_id, user_score, total_points, passed))
        conn.commit()
        conn.close()

        return render_template(
            "quiz_result.html",
            quiz=quiz,
            course=course,
            user_score=user_score,
            total_points=total_points,
            percent=percent,
            passed=passed,
            feedback=feedback
        )

    conn.close()
    return render_template("quiz_taker.html", quiz=quiz, course=course, questions=questions)


# ------------------------------------------------------------------------------
# HTTP 206 Partial Content Video Streaming & Media Delivery
# ------------------------------------------------------------------------------
@app.route("/media/<folder>/<filename>")
def stream_media(folder, filename):
    safe_folder = secure_filename(folder)
    target_dir = os.path.join(UPLOADS_DIR, safe_folder)
    safe_name = secure_filename(filename)
    filepath = os.path.join(target_dir, safe_name)

    if not os.path.exists(filepath):
        abort(404)

    # For videos, implement full HTTP 206 Range request handling
    range_header = request.headers.get("Range", None)
    if not range_header or not safe_name.lower().endswith((".mp4", ".webm", ".mov", ".mkv")):
        return send_from_directory(target_dir, safe_name)

    size = os.path.getsize(filepath)
    byte1, byte2 = 0, None

    m = re.search(r"(\d+)-(\d*)", range_header)
    g = m.groups()

    if g[0]:
        byte1 = int(g[0])
    if g[1]:
        byte2 = int(g[1])

    length = size - byte1
    if byte2 is not None:
        length = byte2 - byte1 + 1

    with open(filepath, "rb") as f:
        f.seek(byte1)
        data = f.read(length)

    rv = Response(data, 206, mimetype=mimetypes.guess_type(filepath)[0] or "video/mp4", direct_passthrough=True)
    rv.headers.add("Content-Range", f"bytes {byte1}-{byte1 + length - 1}/{size}")
    rv.headers.add("Accept-Ranges", "bytes")
    rv.headers.add("Content-Length", str(length))
    return rv


# ------------------------------------------------------------------------------
# Main Entrypoint
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print("==================================================================")
    print(f" Midad Academy LMS Platform Active!")
    print(f" URL: http://localhost:{port}")
    print(f" Master Super Admin: admin@lms.local (Password: AdminPass2026!)")
    print("==================================================================")
    app.run(host="0.0.0.0", port=port, debug=True)

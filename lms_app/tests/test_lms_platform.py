import os
import sys
import unittest
import json
from io import BytesIO

# Add app directory to sys.path
APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from app import app
import database as db

class TestLMSPlatform(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        db.init_db()

    def setUp(self):
        self.client = app.test_client()

    def test_01_super_admin_login(self):
        response = self.client.post("/login", data={
            "email": "admin@lms.local",
            "password": "AdminPass2026!"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Master Administrator", response.data)

    def test_02_student_registration_and_restrictions(self):
        # Register student
        reg_response = self.client.post("/register", data={
            "name": "Jane Learner",
            "email": "jane@learner.com",
            "password": "JanePassword123!"
        }, follow_redirects=True)
        self.assertEqual(reg_response.status_code, 200)
        self.assertIn(b"Account created successfully", reg_response.data)

        # Student should NOT access Creator Studio (403)
        studio_response = self.client.get("/studio")
        self.assertEqual(studio_response.status_code, 403)
        self.assertIn(b"Access Restricted", studio_response.data)

        # Student should NOT access Super Admin Settings (403)
        admin_response = self.client.get("/admin/settings")
        self.assertEqual(admin_response.status_code, 403)

    def test_03_super_admin_promotes_student_to_instructor(self):
        # Login as Super Admin
        self.client.post("/login", data={
            "email": "admin@lms.local",
            "password": "AdminPass2026!"
        })

        target_user = db.get_user_by_email("jane@learner.com")
        self.assertIsNotNone(target_user)
        self.assertEqual(target_user["role"], "student")

        # Promote to instructor
        promote_resp = self.client.post(f"/admin/users/{target_user['id']}/role", data={
            "role": "instructor"
        }, follow_redirects=True)
        self.assertEqual(promote_resp.status_code, 200)
        self.assertIn(b"Successfully updated", promote_resp.data)

        updated_user = db.get_user_by_email("jane@learner.com")
        self.assertEqual(updated_user["role"], "instructor")

    def test_04_instructor_permissions_scoped(self):
        # Login as Jane (now Instructor)
        self.client.get("/logout")
        login_resp = self.client.post("/login", data={
            "email": "jane@learner.com",
            "password": "JanePassword123!"
        }, follow_redirects=True)
        self.assertEqual(login_resp.status_code, 200)

        # Instructor CAN access Creator Studio!
        studio_resp = self.client.get("/studio")
        self.assertEqual(studio_resp.status_code, 200)
        self.assertIn(b"Creator Studio", studio_resp.data)

        # Instructor CANNOT access Website Customizer Settings! (403 Forbidden)
        admin_resp = self.client.get("/admin/settings")
        self.assertEqual(admin_resp.status_code, 403)
        self.assertIn(b"Access Restricted", admin_resp.data)

        # Instructor CANNOT access User Management! (403 Forbidden)
        users_resp = self.client.get("/admin/users")
        self.assertEqual(users_resp.status_code, 403)

    def test_05_course_and_lesson_creation(self):
        # Login as Jane (Instructor)
        self.client.post("/login", data={
            "email": "jane@learner.com",
            "password": "JanePassword123!"
        })

        # Create Course
        course_resp = self.client.post("/studio/course/new", data={
            "title": "Quantum Physics for Beginners",
            "description": "Introduction to wave-particle duality and state vectors.",
            "category": "Physics",
            "price": "0.0",
            "is_published": "1"
        }, follow_redirects=True)
        self.assertEqual(course_resp.status_code, 200)
        self.assertIn(b"Quantum Physics for Beginners", course_resp.data)

        # Check DB
        conn = db.get_db_connection()
        course = conn.execute("SELECT * FROM courses WHERE title = 'Quantum Physics for Beginners'").fetchone()
        self.assertIsNotNone(course)

        # Add Lesson with Video File
        video_dummy = (BytesIO(b"FAKE_VIDEO_CONTENT_BYTE_STREAM_1234567890"), "lecture1.mp4")
        lesson_resp = self.client.post(f"/studio/course/{course['id']}/lesson/new", data={
            "title": "Wavefunction Mechanics",
            "order_index": "1",
            "notes": "Key concept: Schrödinger equation describes wave propagation.",
            "video_file": video_dummy
        }, follow_redirects=True)
        self.assertEqual(lesson_resp.status_code, 200)

        lesson = conn.execute("SELECT * FROM lessons WHERE course_id = ?", (course["id"],)).fetchone()
        self.assertIsNotNone(lesson)
        self.assertTrue(lesson["video_url"].startswith("/media/videos/"))
        conn.close()

    def test_06_quiz_auto_grading(self):
        # Login as student
        self.client.get("/logout")
        self.client.post("/register", data={
            "name": "Bob Test",
            "email": "bob@test.com",
            "password": "BobPassword123!"
        })

        conn = db.get_db_connection()
        quiz = conn.execute("SELECT * FROM quizzes LIMIT 1").fetchone()
        questions = conn.execute("SELECT * FROM quiz_questions WHERE quiz_id = ?", (quiz["id"],)).fetchall()
        conn.close()

        # Submit all correct answers
        form_data = {}
        for q in questions:
            form_data[f"q_{q['id']}"] = str(q["correct_option_index"])

        submit_resp = self.client.post(f"/quiz/{quiz['id']}", data=form_data)
        self.assertEqual(submit_resp.status_code, 200)
        self.assertIn(b"Congratulations, You Passed!", submit_resp.data)
        self.assertIn(b"100%", submit_resp.data)

    def test_07_http_206_video_streaming(self):
        conn = db.get_db_connection()
        lesson = conn.execute("SELECT video_url FROM lessons WHERE video_url LIKE '/media/videos/%' LIMIT 1").fetchone()
        conn.close()

        if lesson and lesson["video_url"]:
            # Request byte range 0-10
            response = self.client.get(lesson["video_url"], headers={"Range": "bytes=0-10"})
            self.assertEqual(response.status_code, 206)
            self.assertIn("Content-Range", response.headers)
            self.assertEqual(response.headers["Accept-Ranges"], "bytes")

if __name__ == "__main__":
    unittest.main()

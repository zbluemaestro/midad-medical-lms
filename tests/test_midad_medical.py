import os
import sys
import unittest

class TestMidadMedicalLMS(unittest.TestCase):
    def setUp(self):
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def test_brand_logo_svg(self):
        logo_path = os.path.join(self.root, "midad_theme", "midad_brand_logo.svg")
        self.assertTrue(os.path.isfile(logo_path), "midad_brand_logo.svg must exist")
        with open(logo_path, "r", encoding="utf-8") as f:
            svg = f.read()
            self.assertIn("<svg", svg)
            self.assertIn("goldCrescent", svg, "Logo must contain golden crescent")
            self.assertIn("penBody", svg, "Logo must contain fountain pen")
            self.assertIn("wavyInk", svg, "Logo must contain wavy golden-brown ink stream")
            self.assertIn("MIDAD", svg)

    def test_dark_blue_theme(self):
        css_path = os.path.join(self.root, "midad_theme", "midad_dark_blue.css")
        self.assertTrue(os.path.isfile(css_path), "midad_dark_blue.css must exist")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
            self.assertIn("#070D1E", css, "Must contain deep midnight blue")
            self.assertIn("Plus Jakarta Sans", css, "Must contain modern font Plus Jakarta Sans")
            self.assertIn("F59E0B", css, "Must contain gold accents")

    def test_content_security_script(self):
        sec_path = os.path.join(self.root, "midad_theme", "content_security.js")
        self.assertTrue(os.path.isfile(sec_path), "content_security.js must exist")
        with open(sec_path, "r", encoding="utf-8") as f:
            js = f.read()
            self.assertIn("contextmenu", js, "Must intercept right-click")
            self.assertIn("nodownload", js, "Must strip download controls")
            self.assertIn("watermark", js, "Must contain dynamic watermark logic")

    def test_upload_capacity_10gb(self):
        # Check Nginx config
        nginx_path = os.path.join(self.root, "cloud", "nginx.conf")
        with open(nginx_path, "r", encoding="utf-8") as f:
            conf = f.read()
            self.assertIn("client_max_body_size 10G;", conf)
            self.assertIn("proxy_request_buffering off;", conf)
            self.assertIn("1800s", conf)

        # Check site_config.json
        site_cfg = os.path.join(self.root, "docker", "site_config.json")
        with open(site_cfg, "r", encoding="utf-8") as f:
            cfg = f.read()
            self.assertIn("10737418240", cfg, "max_file_size must be 10 GB in bytes")

    def test_medical_courses_seeder(self):
        seeder_path = os.path.join(self.root, "seeder", "seed_midad_medical.py")
        self.assertTrue(os.path.isfile(seeder_path), "seed_midad_medical.py must exist")
        
        # Import and verify course data
        sys.path.insert(0, os.path.join(self.root, "seeder"))
        import seed_midad_medical as smm
        courses = {c["title"]: c for c in smm.MEDICAL_COURSES}

        # Course 1: Anatomy & Histology
        self.assertIn("Anatomy and Histology Module", courses)
        anatomy = courses["Anatomy and Histology Module"]
        self.assertEqual(anatomy["course_price"], 300.00)
        self.assertEqual(anatomy["currency"], "EGP")
        self.assertEqual(anatomy["paid_course"], 1)

        # Course 2: General Physiology
        self.assertIn("General Physiology Module", courses)
        physio = courses["General Physiology Module"]
        self.assertEqual(physio["course_price"], 250.00)
        self.assertEqual(physio["currency"], "EGP")
        self.assertEqual(physio["paid_course"], 1)

        # Course 3: Microbiology
        self.assertIn("Microbiology Module", courses)
        micro = courses["Microbiology Module"]
        self.assertEqual(micro["course_price"], 0.00)
        self.assertEqual(micro["currency"], "EGP")
        self.assertEqual(micro["paid_course"], 0)

    def test_preview_server_files(self):
        preview_html = os.path.join(self.root, "preview_server", "static", "index.html")
        preview_server = os.path.join(self.root, "preview_server", "server.py")
        self.assertTrue(os.path.isfile(preview_html))
        self.assertTrue(os.path.isfile(preview_server))

if __name__ == "__main__":
    unittest.main()

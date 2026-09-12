import os
import sys
import unittest

class TestFrappeLMSSaaSConfig(unittest.TestCase):
    def setUp(self):
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def test_directory_structure(self):
        expected_dirs = ["docker", "saas", "cloud", "windows", "seeder", "tests"]
        for d in expected_dirs:
            p = os.path.join(self.root, d)
            self.assertTrue(os.path.isdir(p), f"Directory {d} should exist")

    def test_docker_compose_files(self):
        dev_compose = os.path.join(self.root, "docker", "docker-compose.yml")
        prod_compose = os.path.join(self.root, "cloud", "docker-compose.prod.yml")
        self.assertTrue(os.path.isfile(dev_compose), "Dev docker-compose.yml must exist")
        self.assertTrue(os.path.isfile(prod_compose), "Prod docker-compose.prod.yml must exist")

        with open(dev_compose, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("mariadb:", content)
            self.assertIn("redis:", content)
            self.assertIn("frappe:", content)
            self.assertIn(":8000", content)

    def test_scripts_exist_and_non_empty(self):
        critical_scripts = [
            ("docker", "init-bench.sh"),
            ("saas", "create-tenant.sh"),
            ("saas", "create-tenant.ps1"),
            ("saas", "list-tenants.sh"),
            ("saas", "backup-tenants.sh"),
            ("cloud", "deploy-vps.sh"),
            ("cloud", "nginx.conf"),
            ("windows", "setup-windows.ps1"),
            ("windows", "share-tunnel.ps1"),
            ("seeder", "seed_saas_showcase.py")
        ]
        for folder, file in critical_scripts:
            p = os.path.join(self.root, folder, file)
            self.assertTrue(os.path.isfile(p), f"Script {folder}/{file} must exist")
            self.assertGreater(os.path.getsize(p), 50, f"Script {folder}/{file} must not be empty")

    def test_env_templates(self):
        env_ex = os.path.join(self.root, "docker", ".env.example")
        self.assertTrue(os.path.isfile(env_ex), ".env.example must exist")
        with open(env_ex, "r", encoding="utf-8") as f:
            c = f.read()
            self.assertIn("DB_ROOT_PASSWORD=", c)
            self.assertIn("ADMIN_PASSWORD=", c)
            self.assertIn("SITE_NAME=", c)

if __name__ == "__main__":
    unittest.main()

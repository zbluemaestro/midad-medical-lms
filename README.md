# Pulse & Midad LMS Platform 🚀

A complete, production-grade, full-stack Learning Management System (LMS) with **Role-Based Access Control (RBAC)**, **unrestricted media uploads**, and **interactive quiz auto-grading**.

* **GitHub Repository**: [https://github.com/zbluemaestro/midad-medical-lms](https://github.com/zbluemaestro/midad-medical-lms)
* **GitHub Pages Preview**: [https://zbluemaestro.github.io/midad-medical-lms/](https://zbluemaestro.github.io/midad-medical-lms/)

---

## 🌟 Key Capabilities

1. **Master Super Admin Control**:
   * Master access to customize website branding, title, tagline, logo, colors, and landing page.
   * **User Management Dashboard**: 1-Click promotion of signed-up students to **Course Creators / Instructors**.
2. **Scoped Course Creator Permissions**:
   * Promoted instructors can create courses, upload video lectures, attach lecture notes, and design quizzes.
   * **Strictly Protected**: Course creators are restricted from editing the website itself, platform branding, or other instructors' content (403 Forbidden).
3. **Unrestricted Media Uploads**:
   * Removed arbitrary cloud size limits (`MAX_CONTENT_LENGTH = None`).
   * Native **HTTP 206 Partial Content video streaming** for smooth, instantaneous video scrubbing.
4. **Explicit "Save" & "Publish" Controls**:
   * Conspicuous save buttons across all course, lesson, and quiz editors with instant confirmation.
5. **Interactive Quiz Engine**:
   * Build exams with multiple choices, point allocations, and explanation feedback.
   * Instant server-side auto-grading with percentage score cards and detailed breakdowns.

---

## 📂 Repository Structure

```
├── lms_app/                     # Full-Stack Application (Flask + SQLite + RBAC)
│   ├── app.py                   # Core Flask app with streaming and role decorators
│   ├── database.py              # SQLite schema, migrations & seed data
│   ├── templates/               # 15 Responsive Jinja2 templates (Dark navy UI)
│   ├── uploads/                 # Local media storage (videos, photos, documents)
│   ├── tests/                   # Automated unit & integration tests (7/7 passing)
│   ├── run_website.bat          # 1-Click local Windows launcher (http://localhost:8080)
│   └── share_online.bat         # 1-Click Cloudflare Tunnel sharing for friends
│
├── docs/                        # Static GitHub Pages deployment
│   ├── index.html               # Live frontend showcase
│   └── static/                  # Brand assets and sample lecture notes
│
├── .github/workflows/           # CI/CD Automation
│   └── deploy.yml               # Automated testing & GitHub Pages deployment
│
└── SAAS_FOUNDER_GUIDE.md        # Comprehensive multi-tenancy & business playbook
```

---

## ⚡ 1-Click Quick Start

### 1. Run Locally (Windows)
Double-click `lms_app\run_website.bat` or run:
```powershell
python lms_app\app.py
```
Open your browser at **[http://localhost:8080](http://localhost:8080)**.

* **Master Super Admin Login**: `admin@lms.local` / `AdminPass2026!`

### 2. Share Live with Your Friend
Double-click `lms_app\share_online.bat`.
* Generates a free, public HTTPS link (e.g. `https://xxx.trycloudflare.com`) with zero port forwarding!

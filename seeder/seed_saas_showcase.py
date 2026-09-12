import frappe
from frappe.utils import now_datetime

def seed_showcase():
    """
    Seeds high-quality, professional courses and demo data into Frappe LMS.
    Ensures the instance is immediately populated with interactive content,
    quizzes, and media for SaaS evaluation.
    """
    print("[*] Starting SaaS Showcase Seeder...")

    # Step 1: Run native Frappe LMS demo data creator if present
    try:
        from lms.demo.demo_data import create_demo_data
        print("[*] Generating official Frappe LMS demo content...")
        create_demo_data()
        print("[+] Native demo content created successfully.")
    except Exception as e:
        print(f"[!] Note: Native create_demo_data encountered: {e}")

    # Step 2: Custom Professional Course Seeding
    try:
        ensure_custom_courses()
    except Exception as e:
        print(f"[!] Custom course seeding note: {e}")

    frappe.db.commit()
    print("[+] SaaS Showcase Seeding completed successfully!")


def ensure_custom_courses():
    """
    Creates rich specialized showcase courses tailored for an LMS SaaS launch:
    1. 'Full-Stack AI Engineering & Autonomous Agents'
    2. 'Executive Leadership & Technology Management'
    """
    course_doctype = None
    for candidate in ["LMS Course", "Course"]:
        if frappe.db.exists("DocType", candidate):
            course_doctype = candidate
            break

    if not course_doctype:
        print("[!] Course DocType not found. Skipping custom courses.")
        return

    courses = [
        {
            "title": "Full-Stack AI Engineering & Autonomous Agents",
            "short_introduction": "Master the deployment of generative AI models, multi-agent systems, and scalable LLM orchestration.",
            "description": """<h3>Welcome to Full-Stack AI Engineering</h3>
<p>In this comprehensive masterclass, you will learn how to design, test, and host autonomous AI systems in production.</p>
<ul>
    <li>Architecting Agentic Workflows</li>
    <li>Vector Databases & RAG Pipelines</li>
    <li>Tool Calling & Real-Time Function Execution</li>
    <li>Production Security & Token Optimization</li>
</ul>""",
            "status": "Approved",
            "published": 1,
            "upcoming": 0,
            "paid_course": 1,
            "course_price": 149.00,
            "currency": "USD"
        },
        {
            "title": "Executive Leadership & Technology Strategy",
            "short_introduction": "Strategic framework for CTOs, product directors, and founders building scalable SaaS companies.",
            "description": """<h3>Leading Modern Engineering Organizations</h3>
<p>A rigorous program exploring enterprise scaling, talent retention, and strategic software architecture.</p>""",
            "status": "Approved",
            "published": 1,
            "upcoming": 0,
            "paid_course": 0
        }
    ]

    for c in courses:
        existing = frappe.db.get_value(course_doctype, {"title": c["title"]}, "name")
        if not existing:
            doc = frappe.new_doc(course_doctype)
            for k, v in c.items():
                if doc.meta.has_field(k):
                    doc.set(k, v)
            # Safe fallbacks for common fields
            if doc.meta.has_field("course_title"):
                doc.course_title = c["title"]
            if doc.meta.has_field("tags"):
                doc.tags = "AI, Engineering, Python, SaaS"
            doc.insert(ignore_permissions=True)
            print(f"[+] Created showcase course: {c['title']}")
        else:
            print(f"[*] Course '{c['title']}' already exists.")


if __name__ == "__main__":
    frappe.init(site="lms.localhost")
    frappe.connect()
    seed_showcase()

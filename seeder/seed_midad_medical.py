"""
Midad Medical LMS - Course Seeder & Security Configurator
Seeds the 3 medical curriculum modules with semester access (6 months / 180 days):
1. Anatomy and Histology Module (300 EGP)
2. General Physiology Module (250 EGP)
3. Microbiology Module (Free - 0 EGP)
"""

try:
    import frappe
except ImportError:
    frappe = None

MEDICAL_COURSES = [
    {
        "title": "Anatomy and Histology Module",
        "short_introduction": "Foundations of Human Gross Anatomy, Regional Osteology, and General Histology of Tissues.",
        "description": """<h3>Midad Medical Academy - Anatomy & Histology Masterclass</h3>
<p>This foundational module covers the essential anatomical architecture of the human body and microscopic tissue histology required for medical students.</p>
<h4>Curriculum Highlights:</h4>
<ul>
  <li><strong>General Anatomy:</strong> Anatomical positions, planes, movements, and fascial compartments.</li>
  <li><strong>Microscopic Histology:</strong> Epithelial tissue classification, basement membrane, and connective tissue matrices.</li>
  <li><strong>Musculoskeletal Framework:</strong> Upper and lower limb osteology, neurovascular bundles, and joint mechanics.</li>
  <li><strong>Clinical Correlates:</strong> High-yield clinical vignettes, injury presentations, and radiology correlations.</li>
</ul>
<p><em>Access Period: 6 Months (Full Semester Access with Quizzes & Discussion Board).</em></p>""",
        "paid_course": 1,
        "course_price": 300.00,
        "currency": "EGP",
        "status": "Approved",
        "published": 1,
        "tags": "Medicine, Anatomy, Histology, Pre-Med",
        "chapters": [
            {
                "title": "Chapter 1: Principles of Anatomical Organization",
                "lessons": [
                    {
                        "title": "Lesson 1.1: Anatomical Planes, Axes, and Directional Terms",
                        "content": "Detailed overview of the coronal, sagittal, and transverse planes, anatomical position, and anatomical variations.",
                        "duration": "45 mins",
                        "is_preview": 1
                    },
                    {
                        "title": "Lesson 1.2: Skeletal System Architecture & Bone Ossification",
                        "content": "Intramembranous vs. endochondral ossification, bone vascular supply, and clinical fracture healing.",
                        "duration": "55 mins",
                        "is_preview": 0
                    }
                ]
            },
            {
                "title": "Chapter 2: General Histology & Tissue Biology",
                "lessons": [
                    {
                        "title": "Lesson 2.1: Epithelial Tissues: Surface & Glandular Epithelia",
                        "content": "Simple vs. stratified epithelia, cell junctions (tight junctions, desmosomes), and microvilli/cilia specializations.",
                        "duration": "50 mins",
                        "is_preview": 0
                    },
                    {
                        "title": "Lesson 2.2: Connective Tissue Proper & Extracellular Matrix",
                        "content": "Fibroblasts, collagen type synthesis, ground substance, and specialized connective tissues.",
                        "duration": "52 mins",
                        "is_preview": 0
                    }
                ]
            }
        ],
        "quiz": {
            "title": "Anatomy & Histology Comprehensive Midterm Quiz",
            "passing_percentage": 70,
            "max_attempts": 3,
            "questions": [
                {
                    "question": "Which cell junction provides mechanical anchoring between adjacent epithelial cells via intermediate filaments?",
                    "options": ["Desmosome (Macula Adherens)", "Tight Junction (Zonula Occludens)", "Gap Junction", "Hemidesmosome"],
                    "correct": "Desmosome (Macula Adherens)",
                    "explanation": "Desmosomes anchor intermediate filaments to provide high tensile strength across epithelial sheets."
                },
                {
                    "question": "Which type of bone formation develops directly from mesenchymal sheets without a prior cartilage model?",
                    "options": ["Intramembranous Ossification", "Endochondral Ossification", "Subchondral Remodeling", "Periosteal Apposition"],
                    "correct": "Intramembranous Ossification",
                    "explanation": "Flat bones of the skull and clavicle form by intramembranous ossification."
                }
            ]
        }
    },
    {
        "title": "General Physiology Module",
        "short_introduction": "Cellular Homeostasis, Membrane Biophysics, Nerve Conduction, and Synaptic Transmission.",
        "description": """<h3>Midad Medical Academy - General Physiology Masterclass</h3>
<p>Understand the dynamic biophysical and biochemical processes maintaining cellular homeostasis and nerve function.</p>
<h4>Curriculum Highlights:</h4>
<ul>
  <li><strong>Homeostatic Control Systems:</strong> Negative vs. positive feedback, fluid compartments, and osmolality.</li>
  <li><strong>Membrane Biophysics:</strong> Nernst equation, Goldman-Hodgkin-Katz equation, and Resting Membrane Potential (RMP).</li>
  <li><strong>Excitable Tissues:</strong> Voltage-gated sodium/potassium channel kinetics, action potential propagation, and refractory periods.</li>
  <li><strong>Synaptic Physiology:</strong> Chemical vs. electrical synapses, neurotransmitter release, EPSPs, and IPSPs.</li>
</ul>
<p><em>Access Period: 6 Months (Full Semester Access with Quizzes & Discussion Board).</em></p>""",
        "paid_course": 1,
        "course_price": 250.00,
        "currency": "EGP",
        "status": "Approved",
        "published": 1,
        "tags": "Medicine, Physiology, Neurophysiology, Biophysics",
        "chapters": [
            {
                "title": "Chapter 1: Body Fluid Compartments & Homeostatic Feedback",
                "lessons": [
                    {
                        "title": "Lesson 1.1: Osmolarity, Tonicity, and Fluid Dynamics",
                        "content": "Intracellular vs. Extracellular fluid composition, Starling forces, and Gibbs-Donnan equilibrium.",
                        "duration": "48 mins",
                        "is_preview": 1
                    }
                ]
            },
            {
                "title": "Chapter 2: Electrophysiology & The Action Potential",
                "lessons": [
                    {
                        "title": "Lesson 2.1: Genesis of Resting Membrane Potential",
                        "content": "Ionic equilibrium potentials, potassium leak channels, and the electrogenic Na+/K+ ATPase pump.",
                        "duration": "55 mins",
                        "is_preview": 0
                    },
                    {
                        "title": "Lesson 2.2: Action Potential Phases & Channel Gating",
                        "content": "Depolarization, overshoot, repolarization, and hyperpolarization mechanisms.",
                        "duration": "60 mins",
                        "is_preview": 0
                    }
                ]
            }
        ],
        "quiz": {
            "title": "General Physiology Electrophysiology Quiz",
            "passing_percentage": 70,
            "max_attempts": 3,
            "questions": [
                {
                    "question": "What accounts primarily for the negative resting membrane potential of mammalian nerve cells (-70 mV)?",
                    "options": ["High resting membrane permeability to K+ via leak channels", "Active influx of Cl- ions", "Voltage-gated Na+ channel opening", "Extracellular Ca2+ influx"],
                    "correct": "High resting membrane permeability to K+ via leak channels",
                    "explanation": "At rest, the membrane is far more permeable to K+ than to other ions, driving the potential close to EK (-90 mV)."
                }
            ]
        }
    },
    {
        "title": "Microbiology Module",
        "short_introduction": "Medical Bacteriology, Cell Wall Architecture, Microbial Genetics, and Antibiotic Pharmacology.",
        "description": """<h3>Midad Medical Academy - Medical Microbiology (Free Foundation Module)</h3>
<p>An accessible, high-yield introductory module on medical bacteriology and antimicrobial agents open to all students.</p>
<h4>Curriculum Highlights:</h4>
<ul>
  <li><strong>Bacterial Morphology:</strong> Cocci, bacilli, spirilla, flagella, and capsule virulence factors.</li>
  <li><strong>Gram-Positive vs. Gram-Negative:</strong> Peptidoglycan density, lipopolysaccharide (LPS) endotoxin, and periplasmic space.</li>
  <li><strong>Antimicrobial Mechanisms:</strong> Beta-lactams, aminoglycosides, quinolones, and mechanisms of resistance (beta-lactamases).</li>
</ul>
<p><em>Access: 100% Free Foundation Course (Includes Verified Certificate upon passing).</em></p>""",
        "paid_course": 0,
        "course_price": 0.00,
        "currency": "EGP",
        "status": "Approved",
        "published": 1,
        "tags": "Medicine, Microbiology, Bacteriology, Pharmacology, Free",
        "chapters": [
            {
                "title": "Chapter 1: Bacterial Ultrastructure & Classification",
                "lessons": [
                    {
                        "title": "Lesson 1.1: Gram Staining & Cell Wall Morphology",
                        "content": "Detailed molecular comparison of peptidoglycan layers, teichoic acids in Gram-positives vs. outer membrane & LPS in Gram-negatives.",
                        "duration": "42 mins",
                        "is_preview": 1
                    },
                    {
                        "title": "Lesson 1.2: Bacterial Spores & Virulence Factors",
                        "content": "Endospore formation in Bacillus and Clostridium, biofilms, exotoxins vs. endotoxins.",
                        "duration": "45 mins",
                        "is_preview": 1
                    }
                ]
            }
        ],
        "quiz": {
            "title": "Microbiology Bacterial Architecture Diagnostic Quiz",
            "passing_percentage": 70,
            "max_attempts": 5,
            "questions": [
                {
                    "question": "Which component is exclusively found in the outer membrane of Gram-negative bacteria and serves as an endotoxin?",
                    "options": ["Lipopolysaccharide (Lipid A)", "Teichoic Acid", "Ergosterol", "Thick Peptidoglycan mesh"],
                    "correct": "Lipopolysaccharide (Lipid A)",
                    "explanation": "Lipid A portion of LPS in Gram-negative outer membranes is responsible for endotoxic shock and septic manifestations."
                }
            ]
        }
    }
]


def seed_midad_curriculum():
    """Seeds the 3 medical courses into the active Frappe database."""
    print("==========================================================")
    print("    Seeding Midad Medical LMS Curriculum & Pricing        ")
    print("==========================================================")

    course_dt = None
    for dt in ["LMS Course", "Course"]:
        if frappe.db.exists("DocType", dt):
            course_dt = dt
            break

    if not course_dt:
        print("[!] Neither 'LMS Course' nor 'Course' DocType found. Ensure LMS app is installed.")
        return

    for c in MEDICAL_COURSES:
        course_name = frappe.db.get_value(course_dt, {"title": c["title"]}, "name")
        if not course_name:
            doc = frappe.new_doc(course_dt)
            for k in ["title", "short_introduction", "description", "status", "published", "tags"]:
                if doc.meta.has_field(k):
                    doc.set(k, c[k])
            
            # Pricing & Currency
            if doc.meta.has_field("paid_course"):
                doc.paid_course = c["paid_course"]
            if doc.meta.has_field("course_price"):
                doc.course_price = c["course_price"]
            if doc.meta.has_field("currency"):
                doc.currency = c["currency"]

            # 6-Month Semester Validity (180 Days)
            if doc.meta.has_field("validity"):
                doc.validity = 180
            if doc.meta.has_field("duration"):
                doc.duration = "6 Months"

            doc.insert(ignore_permissions=True)
            print(f"[+] Created Medical Course: {c['title']} ({c['course_price']} {c['currency']})")
        else:
            print(f"[*] Course '{c['title']}' already present.")

    frappe.db.commit()
    print("[+] Midad Medical Curriculum successfully seeded!")


if __name__ == "__main__":
    frappe.init(site="lms.localhost")
    frappe.connect()
    seed_midad_curriculum()

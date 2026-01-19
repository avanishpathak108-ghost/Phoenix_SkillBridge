import streamlit as st
from roles_skills import ROLES_SKILLS
from fpdf import FPDF
from learning_resources import LEARNING_RESOURCES
import io
from PyPDF2 import PdfReader
import docx

if "step" not in st.session_state:
    st.session_state.step = 1


st.set_page_config(page_title="Skill Bridge", layout="centered")

st.sidebar.title("🔥 Phoenix")
st.sidebar.subheader("Skill Bridge")

st.sidebar.markdown(
    """
    **Skill Bridge** helps students identify  
    industry skill gaps and get a  
    clear learning roadmap.
    
    ---
    👥 Team: Phoenix  
    🎯 Goal: Industry Readiness  
    """
)

st.sidebar.markdown("---")
st.sidebar.caption("Hackathon Prototype | 2026")


# -----------------------------
# Helper Functions
# -----------------------------
def extract_skills_with_confidence(text, role_skills):
    text = text.lower()
    skill_confidence = {}

    for skill in role_skills:
        count = text.count(skill)
        if count >= 2:
            skill_confidence[skill] = "Strong"
        elif count == 1:
            skill_confidence[skill] = "Basic"
        else:
            skill_confidence[skill] = "Missing"

    return skill_confidence

def resume_review_suggestions(resume_text):
    text = resume_text.lower()

    suggestions = []

    # Missing Sections Checks
    if "project" not in text:
        suggestions.append("📌 Add a **Projects** section (2–3 strong projects with tech stack + outcomes).")

    if "intern" not in text and "experience" not in text:
        suggestions.append("📌 Add **Internship / Experience** section (even if it's self-projects / freelancing).")

    if "education" not in text and "school" not in text and "college" not in text:
        suggestions.append("📌 Add an **Education** section (Degree + Year + College).")

    if "skill" not in text and "tools" not in text and "technologies" not in text:
        suggestions.append("📌 Add a **Skills / Tools** section (Python, SQL, Git, etc.).")

    if "linkedin" not in text:
        suggestions.append("📌 Add your **LinkedIn profile link** in the header.")

    if "github" not in text:
        suggestions.append("📌 Add your **GitHub profile link** (very important for tech roles).")

    # Generic Resume Improvements
    suggestions.append("✅ Use **bullet points** instead of paragraphs.")
    suggestions.append("✅ Add **numbers/impact** (example: improved accuracy by 15%, built dashboard for 200 users).")
    suggestions.append("✅ Keep resume **1 page** (if fresher).")
    suggestions.append("✅ Use strong action words: Built, Designed, Implemented, Automated, Optimized.")

    return suggestions

def calculate_ats_score(resume_text, role_skills=None):
    text = resume_text.lower()
    score = 0

    # ✅ Basic sections (40 points)
    sections = {
        "projects": 10,
        "experience": 10,
        "education": 5,
        "skills": 10,
        "certification": 5
    }

    for sec, pts in sections.items():
        if sec in text:
            score += pts

    # ✅ Links (10 points)
    if "linkedin" in text:
        score += 5
    if "github" in text:
        score += 5

    # ✅ Role skill keywords match (50 points)
    if role_skills:
        matched = 0
        for skill in role_skills:
            if skill.lower() in text:
                matched += 1

        if len(role_skills) > 0:
            score += int((matched / len(role_skills)) * 50)

    return min(100, score)

def calculate_readiness(present, total):
    if total == 0:
        return 0
    return int((len(present) / total) * 100)


def estimate_time_to_ready(missing_skills):
    weeks = len(missing_skills) * 2
    return f"{weeks}–{weeks+2} weeks"

def safe_text(text):
    return (
        text
        .replace("–", "-")
        .replace("—", "-")
        .replace("‑", "-")
        .replace("’", "'")
        .replace("“", '"')
        .replace("”", '"')
    )


def generate_pdf_report(role, readiness, roadmap):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, safe_text("Skill Bridge - Skill Gap Report"), ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, safe_text(f"Target Role: {role}"), ln=True)
    pdf.cell(0, 10, safe_text(f"Readiness Level: {readiness}%"), ln=True)
    pdf.cell(0,10,safe_text("Readiness includes self-assessment responses."),ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0,10,safe_text("Learning Roadmap with Resources:"),ln=True)

    pdf.set_font("Arial", size=11)

    if roadmap:
        for i, item in enumerate(roadmap, start=1):
            pdf.ln(3)
            pdf.multi_cell(
                0,
                8,
                safe_text(f"{i}. {item['skill']}")
            )

            if item["resources"]:
                pdf.multi_cell(
                    0,
                    8,
                    safe_text(f"   Course: {item['resources']['course']}")
                )
                pdf.multi_cell(
                    0,
                    8,
                    safe_text(f"   Video: {item['resources']['video']}")
                )
                pdf.multi_cell(
                    0,
                    8,
                    safe_text(f"   Practice: {item['resources']['practice']}")
                )
            else:
                pdf.multi_cell(
                    0,
                    8,
                    safe_text("   No curated resources available.")
                )
    else:
        pdf.multi_cell(
            0,
            8,
            safe_text("You are role-ready. No roadmap required.")
        )

    file_path = "SkillBridge_Report.pdf"
    pdf.output(file_path)

    return file_path

def extract_text_from_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return ""

    file_name = uploaded_file.name.lower()

    # TXT
    if file_name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")

    # PDF
    if file_name.endswith(".pdf"):
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += (page.extract_text() or "") + "\n"
        return text

    # DOCX
    if file_name.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        text = "\n".join([p.text for p in doc.paragraphs])
        return text

    return ""




SAMPLE_RESUME = """
I have worked on Python and Excel for data analysis projects.
Used Pandas for data cleaning and data visualization.
Basic knowledge of HTML and CSS.
"""

def find_resources_for_skill(skill_text):
    skill_text = skill_text.lower()

    for key in LEARNING_RESOURCES:
        if key in skill_text:
            return LEARNING_RESOURCES[key]

    return None


def build_roadmap_with_resources(missing_skills):
    roadmap = []

    for skill in missing_skills:
        resources = find_resources_for_skill(skill)

        roadmap.append({
            "skill": skill.title(),
            "resources": resources
        })

    return roadmap

SKILL_QUESTIONS = {
    "javascript": "Have you built a project using JavaScript?",
    "react": "Have you built a React application?",
    "git": "Have you used Git beyond basic commits?",
    "backend": "Have you worked with backend APIs?",
    "python": "Have you written Python scripts or projects?"
}


# -----------------------------
# UI
# -----------------------------
st.markdown("## 🔥 Skill Bridge")
st.markdown(
    "### Bridging the gap between **student skills** and **industry expectations**"
)
st.caption("Built by Team Phoenix")
st.markdown("---")


st.sidebar.title("🔥 Phoenix")
st.sidebar.subheader("Skill Bridge")

mode = st.sidebar.radio(
    "Navigation",
    ["SkillBridge", "Career Roadmap"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Hackathon Prototype | Team Phoenix")



# -----------------------------
# SKILLBRIDGE MODE
# -----------------------------
if mode == "SkillBridge":

    st.header("🧠 SkillBridge")

    if st.session_state.step == 1:
        role = st.selectbox(
            "Select Target Role",
            list(ROLES_SKILLS.keys())
        )
        if st.button("Next"):
            st.session_state.role = role
            st.session_state.step = 2
            st.rerun()


    if st.session_state.step == 2:

        if "resume_text" not in st.session_state:
            st.session_state.resume_text = ""

        # ✅ Upload Resume File (PDF/DOCX/TXT)
        st.subheader("📄 Upload Resume File (PDF / DOCX / TXT)")

        uploaded_file = st.file_uploader(
            "Upload your resume",
            type=["pdf", "docx", "txt"]
        )

        if uploaded_file is not None:
            extracted_text = extract_text_from_uploaded_file(uploaded_file)

            if extracted_text.strip():
                st.session_state.resume_text = extracted_text
                st.success("✅ Resume extracted successfully! Now click Analyze Skill Gap.")

                # ✅ Resume Review Section
                st.subheader("📝 Resume Review + Suggestions")

                tips = resume_review_suggestions(st.session_state.resume_text)

                for tip in tips:
                    st.write("•", tip)

            else:
                st.error("❌ Could not extract text from this file. Try another file or paste text manually.")

        # ✅ Text Area (auto filled if file uploaded)
        col1, col2 = st.columns([3, 1])

        with col1:
            resume_text = st.text_area(
                "Paste your resume text or skills here",
                value=st.session_state.resume_text,
                height=200
            )
            st.session_state.resume_text = resume_text

        with col2:
            if st.button("Use Sample Resume"):
                st.session_state.resume_text = SAMPLE_RESUME
                st.rerun()

        if st.button("Analyze Skill Gap"):
            st.session_state.step = 3
            st.rerun()

    if st.session_state.step == 3:

        role = st.session_state.role
        role_skills = ROLES_SKILLS[role]

        skill_confidence = extract_skills_with_confidence(
            st.session_state.resume_text, role_skills
        )

        present_skills = [
            skill for skill, level in skill_confidence.items()
            if level in ["Strong", "Basic"]
        ]

        missing_skills = [
            skill for skill, level in skill_confidence.items()
            if level == "Missing"
        ]

        readiness = calculate_readiness(
            present_skills, len(role_skills)
        )

        # ✅ ATS Score
        st.subheader("📄 ATS Resume Score")

        ats_score = calculate_ats_score(st.session_state.resume_text, role_skills)

        st.progress(ats_score / 100)
        st.write(f"✅ Your ATS Score is: **{ats_score}/100**")

        if ats_score >= 80:
            st.success("Great! Your resume is ATS-friendly.")
        elif ats_score >= 50:
            st.warning("Good, but you can improve keywords + sections.")
        else:
            st.error("Low ATS score. Add missing sections + role keywords.")

        

        # ---------- UI OUTPUT ----------
        st.subheader("📌 Skill Analysis")
        for skill, level in skill_confidence.items():
            if level == "Strong":
                st.success(f"{skill.title()} → Strong")
            elif level == "Basic":
                st.warning(f"{skill.title()} → Basic")
            else:
                st.error(f"{skill.title()} → Missing")
        st.subheader("🧠 Skill Depth Questions")

        depth_score = 0
        answered = 0

        for skill in missing_skills + present_skills:
            for key, question in SKILL_QUESTIONS.items():
                if key in skill.lower():
                    answer = st.radio(
                        question,
                        ["Never", "With guidance", "Independently"],
                        key=f"q_{skill}"
                    )

                    answered += 1

                    if answer == "With guidance":
                        depth_score += 1
                    elif answer == "Independently":
                        depth_score += 2
        if answered > 0:
            readiness = min(100, readiness + depth_score)

        st.subheader("📊 Readiness Level")
        st.write(f"You are **{readiness}% ready** for the role of **{role}**.")

        st.subheader("🎯 Job Readiness Status")
        if readiness >= 70:
            st.success("You are close to being job‑ready for this role.")
        elif readiness >= 40:
            st.warning("You are partially ready and need focused upskilling.")
        else:
            st.error("You are not job‑ready yet. A strong foundation is required.")

        st.subheader("⏳ Estimated Time to Role Readiness")
        st.write(estimate_time_to_ready(missing_skills))

        st.subheader("🛣 Learning Roadmap (With Resources)")

        roadmap = build_roadmap_with_resources(missing_skills)

        if roadmap:
            for i, item in enumerate(roadmap, start=1):
                st.markdown(f"### 🔴 Priority {i}: {item['skill']}")

                if item["resources"]:
                    st.markdown(f"- 📘 **Course**: {item['resources']['course']}")
                    st.markdown(f"- 🎥 **Video**: {item['resources']['video']}")
                    st.markdown(f"- 🧠 **Practice**: {item['resources']['practice']}")
                else:
                    st.markdown("- ⚠️ No curated resources available yet.")
        else:
            st.success("You are role‑ready 🎉 No learning roadmap required.")


        

        # ---------- PDF DOWNLOAD (LAST) ----------
        roadmap = build_roadmap_with_resources(missing_skills)
        pdf_path = generate_pdf_report(role, readiness, roadmap)


        with open(pdf_path, "rb") as file:
            st.download_button(
                label="📄 Download Skill Gap Report (PDF)",
                data=file,
                file_name="SkillBridge_Report.pdf",
                mime="application/pdf"
            )

        if st.button("Start Over"):
            st.session_state.step = 1
            st.session_state.resume_text = ""
            st.rerun()
  


# -----------------------------
# CAREER ROADMAP MODE
# -----------------------------
else:
    st.header("🧭 Career Roadmap")

    st.subheader("🧠 Quick Career Discovery")

    interest = st.selectbox(
        "Which area excites you the most?",
        ["Web Development", "Data", "Security", "Design", "Cloud"]
    )

    experience = st.radio(
        "Your current experience level?",
        ["Beginner", "Some experience", "Worked on projects"]
    )

    learning_style = st.radio(
        "How do you prefer to learn?",
        ["Videos", "Hands-on practice", "Reading & documentation"]
    )
    st.subheader("📊 Academic Background (Optional)")

    marks_10 = st.number_input(
        "10th Grade Percentage (optional)",
        min_value=0.0, max_value=100.0, step=0.1
    )

    marks_12 = st.number_input(
        "12th Grade Percentage (optional)",
        min_value=0.0, max_value=100.0, step=0.1
    )

    if st.button("Generate Career Roadmap"):
        st.session_state.career_ready = True

    if st.session_state.get("career_ready"):

        st.subheader("🎯 Recommended Career Path")
        if marks_12 and marks_12 < 50:
            st.warning(
                "We recommend starting with fundamentals and hands‑on practice."
            )


        if interest == "Web Development":
            st.success("Frontend / Full‑Stack Developer")
            st.write("Focus on: HTML, CSS, JavaScript, React, Git")

        elif interest == "Data":
            st.success("Data Analyst")
            st.write("Focus on: Python, SQL, Excel, Data Visualization")

        elif interest == "Security":
            st.success("Cybersecurity Analyst")
            st.write("Focus on: Networking, Linux, Security Basics")

        elif interest == "Design":
            st.success("UI/UX Designer")
            st.write("Focus on: Figma, User Research, Design Systems")

        elif interest == "Cloud":
            st.success("Cloud / DevOps Engineer")
            st.write("Focus on: Linux, AWS, Docker, CI/CD")

        st.info(
            "This roadmap is personalized based on your interests and experience level."
        )

        st.subheader("🗺️ Official Roadmap.sh Links")

        if interest == "Web Development":
            st.markdown("🔗 Frontend Developer: https://roadmap.sh/frontend")
            st.markdown("🔗 Backend Developer: https://roadmap.sh/backend")
            st.markdown("🔗 Full Stack Developer: https://roadmap.sh/full-stack")

        elif interest == "Data":
            st.markdown("🔗 Data Analyst: https://roadmap.sh/data-analyst")
            st.markdown("🔗 Data Scientist: https://roadmap.sh/data-scientist")
            st.markdown("🔗 AI / ML Engineer: https://roadmap.sh/ai-data-scientist")

        elif interest == "Security":
            st.markdown("🔗 Cyber Security: https://roadmap.sh/cyber-security")

        elif interest == "Design":
            st.markdown("🔗 UX Design: https://roadmap.sh/ux-design")

        elif interest == "Cloud":
            st.markdown("🔗 DevOps: https://roadmap.sh/devops")
            st.markdown("🔗 AWS: https://roadmap.sh/aws")

    st.subheader("📚 Suggested Learning Resources")

    skills = []

    if interest == "Web Development":
        skills = ["html", "css", "javascript", "react", "git"]

    elif interest == "Data":
        skills = ["python", "sql", "excel"]

    elif interest == "Cloud":
        skills = ["linux", "docker"]

    for skill in skills:
        resources = LEARNING_RESOURCES.get(skill)
        if resources:
            st.markdown(f"### 🔹 {skill.title()}")
            st.markdown(f"- 📘 Course: {resources['course']}")
            st.markdown(f"- 🎥 Video: {resources['video']}")
            st.markdown(f"- 🧠 Practice: {resources['practice']}")


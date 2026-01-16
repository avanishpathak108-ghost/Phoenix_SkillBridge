import streamlit as st
from roles_skills import ROLES_SKILLS

st.set_page_config(page_title="Skill Bridge", layout="centered")

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


def calculate_readiness(present, total):
    if total == 0:
        return 0
    return int((len(present) / total) * 100)


def estimate_time_to_ready(missing_skills):
    weeks = len(missing_skills) * 2
    return f"{weeks}–{weeks+2} weeks"

SAMPLE_RESUME = """
I have worked on Python and Excel for data analysis projects.
Used Pandas for data cleaning and data visualization.
Basic knowledge of HTML and CSS.
"""

# -----------------------------
# UI
# -----------------------------
st.title("🔥 Skill Bridge")
st.caption("Built by Team Phoenix | Skill Gap Translator for Industry Readiness")

mode = st.radio(
    "Choose Mode",
    ["SkillBridge (Skill Gap Analysis)", "Career Roadmap (Basic)"]
)

# -----------------------------
# SKILLBRIDGE MODE
# -----------------------------
if mode == "SkillBridge (Skill Gap Analysis)":

    st.header("🧠 SkillBridge")

    role = st.selectbox(
        "Select Target Role",
        list(ROLES_SKILLS.keys())
    )

    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""
    
    col1, col2 = st.columns([3, 1])

    with col1:
        resume_text = st.text_area(
            "Paste your resume text or skills here",
            value=st.session_state.resume_text,
            height=200
        )

    with col2:
        if st.button("Use Sample Resume"):
            st.session_state.resume_text = SAMPLE_RESUME
            st.rerun()




    if st.button("Analyze Skill Gap"):

        role_skills = ROLES_SKILLS[role]

        skill_confidence = extract_skills_with_confidence(
            resume_text, role_skills
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

        # --- Skill Analysis ---
        st.subheader("📌 Skill Analysis")
        for skill, level in skill_confidence.items():
            if level == "Strong":
                st.success(f"{skill.title()} → Strong")
            elif level == "Basic":
                st.warning(f"{skill.title()} → Basic")
            else:
                st.error(f"{skill.title()} → Missing")

        # --- Readiness ---
        st.subheader("📊 Readiness Level")
        st.write(f"You are **{readiness}% ready** for the role of **{role}**.")

        # --- Job Ready Status ---
        st.subheader("🎯 Job Readiness Status")
        if readiness >= 70:
            st.success("You are close to being job‑ready for this role.")
        elif readiness >= 40:
            st.warning("You are partially ready and need focused upskilling.")
        else:
            st.error("You are not job‑ready yet. A strong foundation is required.")

        # --- Time Estimate ---
        st.subheader("⏳ Estimated Time to Role Readiness")
        st.write(estimate_time_to_ready(missing_skills))

        # --- Roadmap ---
        st.subheader("🛣 Learning Roadmap (Priority‑Based)")
        if missing_skills:
            for i, skill in enumerate(missing_skills, start=1):
                st.write(f"🔴 Priority {i}: Learn {skill.title()}")
        else:
            st.success("No roadmap needed — you are role‑ready 🎉")

# -----------------------------
# CAREER ROADMAP MODE
# -----------------------------
else:
    st.header("🧭 Career Roadmap")

    interest = st.selectbox(
        "What are you most interested in?",
        ["Data", "Web Development", "Security", "Design", "Cloud"]
    )

    st.subheader("Suggested Career Options")

    if interest == "Data":
        st.write("- Data Analyst")
        st.write("- Business Analyst")
    elif interest == "Web Development":
        st.write("- Web Developer")
        st.write("- Frontend Engineer")
    elif interest == "Security":
        st.write("- Cybersecurity Analyst")
        st.write("- SOC Analyst")
    elif interest == "Design":
        st.write("- UI/UX Designer")
        st.write("- Product Designer")
    elif interest == "Cloud":
        st.write("- Cloud Engineer")
        st.write("- DevOps Engineer")

    st.info("You can continue to SkillBridge for detailed skill analysis.")

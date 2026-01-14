import streamlit as st
from roles_skills import ROLES_SKILLS

st.set_page_config(page_title="Phoenix", layout="centered")

# -----------------------------
# Helper Functions
# -----------------------------
def extract_skills(text, role_skills):
    text = text.lower()
    extracted = []
    for skill in role_skills:
        if skill in text:
            extracted.append(skill)
    return list(set(extracted))


def calculate_readiness(present, total):
    if total == 0:
        return 0
    return int((len(present) / total) * 100)


def generate_basic_roadmap(missing_skills):
    roadmap = []
    week = 1
    for skill in missing_skills:
        roadmap.append(f"Week {week}–{week+1}: Learn {skill.title()}")
        week += 2
    return roadmap


# -----------------------------
# UI Starts Here
# -----------------------------
st.title("🔥 Phoenix")
st.subheader("Skill Gap Translator for Industry Readiness")

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

    resume_text = st.text_area(
        "Paste your resume text or skills here",
        height=200
    )

    if st.button("Analyze Skill Gap"):

        role_skills = ROLES_SKILLS[role]
        user_skills = extract_skills(resume_text, role_skills)

        missing_skills = [
            skill for skill in role_skills if skill not in user_skills
        ]

        readiness = calculate_readiness(user_skills, len(role_skills))

        st.subheader("✅ Present Skills")
        if user_skills:
            st.write([skill.title() for skill in user_skills])
        else:
            st.write("No matching skills detected.")

        st.subheader("❌ Missing Skills")
        if missing_skills:
            st.write([skill.title() for skill in missing_skills])
        else:
            st.write("No missing skills 🎉")

        st.subheader("📊 Readiness Level")
        st.write(f"You are **{readiness}% ready** for the role of **{role}**.")

        st.subheader("🛣 Learning Roadmap")
        roadmap = generate_basic_roadmap(missing_skills)

        if roadmap:
            for step in roadmap:
                st.write(step)
        else:
            st.write("You are job-ready for this role.")

# -----------------------------
# CAREER ROADMAP MODE (BASIC)
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

import streamlit as st
from prompts import *
from utils import get_llm_response

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="TalentScout AI Assistant", page_icon="🤖", layout="wide")

# ---------------- STYLING ----------------
st.markdown("""
<style>
.main { background-color: #f8f9fc; }
h1 { color: #6C63FF; }
.stChatMessage { border-radius: 12px; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<h1 style='text-align:center;'>🤖 TalentScout AI Hiring Assistant</h1>
<p style='text-align:center;'>Smart AI-powered screening for tech candidates 🚀</p>
""", unsafe_allow_html=True)

st.info("🔒 Your data is used only for screening and is not stored permanently.")

# ---------------- SESSION ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "stage" not in st.session_state:
    st.session_state.stage = "start"

if "candidate" not in st.session_state:
    st.session_state.candidate = {}

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("📋 Candidate Summary")
    c = st.session_state.candidate
    st.write(f"👤 Name: {c.get('name', '-')}")
    st.write(f"📧 Email: {c.get('email', '-')}")
    st.write(f"📞 Phone: {c.get('phone', '-')}")
    st.write(f"💼 Role: {c.get('role', '-')}")
    st.write(f"📍 Location: {c.get('location', '-')}")
    st.write(f"🛠 Tech Stack: {c.get('tech_stack', '-')}")

# ---------------- PROGRESS ----------------
stage_map = {
    "collect_name": 1,
    "collect_email": 2,
    "collect_phone": 3,
    "collect_experience": 4,
    "collect_role": 5,
    "collect_location": 6,
    "tech_stack": 7,
    "questions": 8,
    "review": 9
}
st.progress(stage_map.get(st.session_state.stage, 0) / 9)

# ---------------- GREETING ----------------
if len(st.session_state.messages) == 0:
    greeting = """
Hello! Welcome to TalentScout 🤖

I am your AI Hiring Assistant. I will:
- Collect your basic details
- Understand your tech skills
- Ask relevant technical questions

👉 Please type your answers in the chat box below.

Let’s begin! What is your full name?
"""
    st.session_state.messages.append(("assistant", greeting))
    st.session_state.stage = "collect_name"

# ---------------- DISPLAY CHAT ----------------
for role, msg in st.session_state.messages:
    with st.chat_message(role):
        st.write(msg)

# ---------------- INPUT ----------------
user_input = st.chat_input("Type your response here...")

if user_input:

    st.session_state.messages.append(("user", user_input))

    if st.session_state.stage == "collect_name":
        st.session_state.candidate["name"] = user_input
        st.session_state.stage = "collect_email"
        st.session_state.messages.append(("assistant", "📧 Please provide your email address."))

    elif st.session_state.stage == "collect_email":
        st.session_state.candidate["email"] = user_input
        st.session_state.stage = "collect_phone"
        st.session_state.messages.append(("assistant", "📞 Please provide your phone number."))

    elif st.session_state.stage == "collect_phone":
        st.session_state.candidate["phone"] = user_input
        st.session_state.stage = "collect_experience"
        st.session_state.messages.append(("assistant", "💼 How many years of experience do you have?"))

    elif st.session_state.stage == "collect_experience":
        st.session_state.candidate["experience"] = user_input
        st.session_state.stage = "collect_role"
        st.session_state.messages.append(("assistant", "🎯 What role are you applying for?"))

    elif st.session_state.stage == "collect_role":
        st.session_state.candidate["role"] = user_input
        st.session_state.stage = "collect_location"
        st.session_state.messages.append(("assistant", "📍 Where are you currently located?"))

    elif st.session_state.stage == "collect_location":
        st.session_state.candidate["location"] = user_input
        st.session_state.stage = "tech_stack"
        st.session_state.messages.append(("assistant", "🛠 Enter your tech stack (comma separated)"))

    elif st.session_state.stage == "tech_stack":
        tech_list = [t.strip() for t in user_input.split(",")]
        clean_tech = ", ".join(tech_list)

        st.session_state.candidate["tech_stack"] = clean_tech

        try:
            questions = get_llm_response(get_question_prompt(clean_tech))
        except:
            questions = "General:\n1. Describe a project.\n2. Challenges?\n3. Problem solving?"

        st.session_state.questions = questions
        st.session_state.stage = "questions"
        st.session_state.messages.append(("assistant", "Questions generated. Answer below 👇"))

    else:
        chat_history = "\n".join([f"{r}: {m}" for r, m in st.session_state.messages[-10:]])

        try:
            response = get_llm_response(
                get_fallback_prompt(
                    user_input,
                    st.session_state.stage,
                    chat_history,
                    str(st.session_state.candidate),
                    str(st.session_state.get("final_answers", {}))
                )
            )
        except:
            response = "I'm here to help. Please continue."

        st.session_state.messages.append(("assistant", response))

    st.rerun()

# ---------------- QUESTIONS ----------------
if st.session_state.stage == "questions":
    st.subheader("Answer Questions")

    if "answers" not in st.session_state:
        st.session_state.answers = {}

    for i, line in enumerate(st.session_state.questions.split("\n"), 1):
        if line.strip().startswith(("1", "2", "3")):
            st.write(line)
            st.session_state.answers[i] = st.text_area("Your Answer", key=i)

    if st.button("Submit"):
        st.session_state.final_answers = st.session_state.answers
        st.session_state.stage = "review"
        st.rerun()

# ---------------- REVIEW ----------------
if st.session_state.stage == "review":
    st.subheader("📋 Your Answers")

    for q, a in st.session_state.final_answers.items():
        st.write(f"Q{q}: {a}")

    if st.button("Finish"):
        name = st.session_state.candidate.get("name", "Candidate")
        st.session_state.messages.append(("assistant", f"Thank you {name}! We will contact you soon."))
        st.session_state.stage = "end"
        st.rerun()

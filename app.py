import streamlit as st
from prompts import *
from utils import get_llm_response

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="TalentScout AI Assistant", page_icon="🤖", layout="wide")

# ---------------- STYLING ----------------
st.markdown("""
<style>
.main { background-color: #f8f9fc; }

/* Chat bubble style */
[data-testid="stChatMessage"] {
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 8px;
}

/* Assistant */
[data-testid="stChatMessage"]:nth-child(odd) {
    background-color: #f1f3ff;
}

/* User */
[data-testid="stChatMessage"]:nth-child(even) {
    background-color: #e6f7ff;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<h1 style='text-align:center;'>🤖 TalentScout AI Hiring Assistant</h1>
<p style='text-align:center;'>Smart AI-powered screening for tech candidates 🚀</p>
""", unsafe_allow_html=True)

# ---------------- PRIVACY ----------------
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
    st.session_state.messages.append(("assistant", """
Hello! Welcome to TalentScout 🤖

I will:
- Collect your details
- Understand your skills
- Ask technical questions

👉 Please type answers in chat below.

What is your full name?
"""))
    st.session_state.stage = "collect_name"

# ---------------- USER INPUT ----------------
user_input = st.chat_input("Type your response here...")

if user_input:
    st.session_state.messages.append(("user", user_input))

    if user_input.lower() in ["exit", "quit", "bye"]:
        name = st.session_state.candidate.get("name", "Candidate")
        final_msg = get_llm_response(get_end_prompt(name))
        st.session_state.messages.append(("assistant", final_msg))
        st.session_state.stage = "end"
        st.rerun()

    elif st.session_state.stage == "collect_name":
        st.session_state.candidate["name"] = user_input
        st.session_state.stage = "collect_email"
        st.session_state.messages.append(("assistant", "📧 Please provide your email address."))
        st.rerun()

    elif st.session_state.stage == "collect_email":
        st.session_state.candidate["email"] = user_input
        st.session_state.stage = "collect_phone"
        st.session_state.messages.append(("assistant", "📞 Please provide your phone number."))
        st.rerun()

    elif st.session_state.stage == "collect_phone":
        st.session_state.candidate["phone"] = user_input
        st.session_state.stage = "collect_experience"
        st.session_state.messages.append(("assistant", "💼 How many years of experience do you have?"))
        st.rerun()

    elif st.session_state.stage == "collect_experience":
        st.session_state.candidate["experience"] = user_input
        st.session_state.stage = "collect_role"
        st.session_state.messages.append(("assistant", "🎯 What role are you applying for?"))
        st.rerun()

    elif st.session_state.stage == "collect_role":
        st.session_state.candidate["role"] = user_input
        st.session_state.stage = "collect_location"
        st.session_state.messages.append(("assistant", "📍 Where are you currently located?"))
        st.rerun()

    elif st.session_state.stage == "collect_location":
        st.session_state.candidate["location"] = user_input
        st.session_state.stage = "tech_stack"
        st.session_state.messages.append(("assistant", "🛠 Enter your tech stack."))
        st.rerun()

    elif st.session_state.stage == "tech_stack":
        st.session_state.candidate["tech_stack"] = user_input

        questions = get_llm_response(get_question_prompt(user_input))
        st.session_state.questions = questions

        st.session_state.messages.append(("assistant", "Questions generated. Answer below 👇"))
        st.session_state.stage = "questions"
        st.rerun()

    else:
        chat_history = "\n".join([f"{r}: {m}" for r, m in st.session_state.messages])

        response = get_llm_response(
            get_fallback_prompt(user_input, st.session_state.stage, chat_history)
        )
        st.session_state.messages.append(("assistant", response))
        st.rerun()

# ---------------- QUESTIONS ----------------
if st.session_state.stage == "questions":

    st.subheader("Answer Questions")

    if "answers" not in st.session_state:
        st.session_state.answers = {}

    questions_text = st.session_state.get("questions", "").split("\n")

    q_index = 1
    for line in questions_text:
        if line.strip().startswith(("1", "2", "3", "4", "5")):
            st.write(f"**Q{q_index}: {line}**")
            ans = st.text_area(f"Answer {q_index}", key=f"a{q_index}")
            st.session_state.answers[f"Q{q_index}"] = ans
            q_index += 1

    if st.button("✅ Submit Answers"):
        st.session_state.final_answers = st.session_state.answers.copy()
        st.session_state.stage = "review"
        st.rerun()

# ---------------- REVIEW ----------------
if st.session_state.stage == "review":

    st.subheader("📋 Your Submitted Answers")

    for q, ans in st.session_state.final_answers.items():
        st.write(f"**{q}**")
        st.write(ans if ans else "_No answer provided_")

    if st.button("🚀 Finish Interview"):
        name = st.session_state.candidate.get("name", "Candidate")
        final_msg = get_llm_response(get_end_prompt(name))
        st.session_state.messages.append(("assistant", final_msg))
        st.session_state.stage = "end"
        st.rerun()

# ---------------- CHAT (BOTTOM FIX) ----------------
st.divider()

for role, msg in st.session_state.messages:
    with st.chat_message(role):
        st.write(msg)

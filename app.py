import streamlit as st
from prompts import *
from utils import get_llm_response

st.set_page_config(page_title="TalentScout AI Assistant", layout="wide")

# ---------------- HEADER ----------------
st.title("🤖 TalentScout AI Hiring Assistant")
st.info("🔒 Your data is not stored permanently.")

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
    st.write(f"Name: {c.get('name', '-')}")
    st.write(f"Email: {c.get('email', '-')}")
    st.write(f"Phone: {c.get('phone', '-')}")
    st.write(f"Role: {c.get('role', '-')}")
    st.write(f"Location: {c.get('location', '-')}")
    st.write(f"Tech: {c.get('tech_stack', '-')}")

# ---------------- GREETING ----------------
if len(st.session_state.messages) == 0:
    st.session_state.messages.append(("bot", "Hello! What is your full name?"))
    st.session_state.stage = "collect_name"

# ---------------- INPUT ----------------
user_input = st.chat_input("Type your response...")

if user_input:
    st.session_state.messages.append(("user", user_input))

    if st.session_state.stage == "collect_name":
        st.session_state.candidate["name"] = user_input
        st.session_state.messages.append(("bot", "Enter your email"))
        st.session_state.stage = "collect_email"
        st.rerun()

    elif st.session_state.stage == "collect_email":
        st.session_state.candidate["email"] = user_input
        st.session_state.messages.append(("bot", "Enter phone number"))
        st.session_state.stage = "collect_phone"
        st.rerun()

    elif st.session_state.stage == "collect_phone":
        st.session_state.candidate["phone"] = user_input
        st.session_state.messages.append(("bot", "Years of experience?"))
        st.session_state.stage = "collect_exp"
        st.rerun()

    elif st.session_state.stage == "collect_exp":
        st.session_state.candidate["exp"] = user_input
        st.session_state.messages.append(("bot", "Desired role?"))
        st.session_state.stage = "collect_role"
        st.rerun()

    elif st.session_state.stage == "collect_role":
        st.session_state.candidate["role"] = user_input
        st.session_state.messages.append(("bot", "Current location?"))
        st.session_state.stage = "collect_loc"
        st.rerun()

    elif st.session_state.stage == "collect_loc":
        st.session_state.candidate["location"] = user_input
        st.session_state.messages.append(("bot", "Enter tech stack"))
        st.session_state.stage = "tech"
        st.rerun()

    elif st.session_state.stage == "tech":
        st.session_state.candidate["tech_stack"] = user_input

        questions = get_llm_response(get_question_prompt(user_input))
        st.session_state.questions = questions

        st.session_state.messages.append(("bot", "Questions generated. Answer below 👇"))
        st.session_state.stage = "questions"
        st.rerun()

    else:
        chat_history = "\n".join([f"{r}:{m}" for r, m in st.session_state.messages])

        response = get_llm_response(
            get_fallback_prompt(user_input, st.session_state.stage, chat_history)
        )

        st.session_state.messages.append(("bot", response))
        st.rerun()

# ---------------- QUESTIONS ----------------
if st.session_state.stage == "questions":
    st.subheader("Answer Questions")

    if "answers" not in st.session_state:
        st.session_state.answers = {}

    q_lines = st.session_state.questions.split("\n")

    qn = 1
    for line in q_lines:
        if line.strip().startswith(("1", "2", "3", "4", "5")):
            st.write(f"Q{qn}: {line}")
            ans = st.text_area("Your Answer", key=f"a{qn}")
            st.session_state.answers[f"Q{qn}"] = ans
            qn += 1

    if st.button("Submit Answers"):
        st.session_state.final_answers = st.session_state.answers.copy()
        st.session_state.stage = "review"
        st.rerun()

# ---------------- REVIEW ----------------
if st.session_state.stage == "review":
    st.subheader("Your Answers")

    for q, a in st.session_state.final_answers.items():
        st.write(q)
        st.write(a if a else "No answer")

# ---------------- CHAT (ALWAYS BOTTOM) ----------------
st.divider()

for role, msg in st.session_state.messages:
    if role == "user":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**Assistant:** {msg}")

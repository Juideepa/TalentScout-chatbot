import streamlit as st
from prompts import *
from utils import get_llm_response

# ---------------- CONFIG ----------------
st.set_page_config(page_title="TalentScout AI", page_icon="🤖", layout="wide")

st.title("🤖 TalentScout AI Hiring Assistant")
st.info("🔒 Your data is safe and not stored permanently.")

# ---------------- SESSION ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "stage" not in st.session_state:
    st.session_state.stage = "name"

if "candidate" not in st.session_state:
    st.session_state.candidate = {}

# ---------------- GREETING ----------------
if len(st.session_state.messages) == 0:
    st.session_state.messages.append(("assistant", """
Hello! Welcome to TalentScout 🤖

I will:
- Collect your details
- Ask technical questions

What is your full name?
"""))

# ---------------- DISPLAY CHAT ----------------
for role, msg in st.session_state.messages:
    with st.chat_message(role):
        st.write(msg)

# ---------------- INPUT ----------------
user_input = st.chat_input("Type here...")

if user_input:

    st.session_state.messages.append(("user", user_input))

    # ---------------- FLOW ----------------
    if st.session_state.stage == "name":
        st.session_state.candidate["name"] = user_input
        st.session_state.stage = "email"
        st.session_state.messages.append(("assistant", "Enter your email"))

    elif st.session_state.stage == "email":
        st.session_state.candidate["email"] = user_input
        st.session_state.stage = "role"
        st.session_state.messages.append(("assistant", "What role are you applying for?"))

    elif st.session_state.stage == "role":
        st.session_state.candidate["role"] = user_input
        st.session_state.stage = "tech"
        st.session_state.messages.append(("assistant", "Enter your tech stack (comma separated)"))

    elif st.session_state.stage == "tech":
        tech = ", ".join([t.strip() for t in user_input.split(",")])
        st.session_state.candidate["tech_stack"] = tech

        try:
            questions = get_llm_response(get_question_prompt(tech))
        except:
            questions = """General:
1. Tell me about your project
2. Challenges faced?
3. How do you solve problems?"""

        st.session_state.questions = questions
        st.session_state.stage = "questions"

        st.session_state.messages.append(("assistant", "Answer these questions below 👇"))

    # ---------------- FALLBACK ----------------
    else:
        try:
            response = get_llm_response(get_fallback_prompt(user_input))
        except:
            response = "Please continue."

        st.session_state.messages.append(("assistant", response))

    st.rerun()

# ---------------- QUESTIONS ----------------
if st.session_state.stage == "questions":

    st.subheader("Answer Questions")

    if "answers" not in st.session_state:
        st.session_state.answers = {}

    lines = st.session_state.questions.split("\n")

    i = 1
    for line in lines:
        if line.strip().startswith(("1", "2", "3")):
            st.write(line)
            st.session_state.answers[i] = st.text_area("Your Answer", key=i)
            i += 1

    if st.button("Submit"):
        st.session_state.final_answers = st.session_state.answers
        st.session_state.stage = "review"
        st.rerun()

# ---------------- REVIEW ----------------
if st.session_state.stage == "review":

    st.subheader("Your Answers")

    for k, v in st.session_state.final_answers.items():
        st.write(f"Q{k}: {v}")

    if st.button("Finish"):
        name = st.session_state.candidate.get("name", "Candidate")

        try:
            msg = get_llm_response(get_end_prompt(name))
        except:
            msg = f"Thank you {name}, we will contact you soon."

        st.session_state.messages.append(("assistant", msg))
        st.session_state.stage = "end"
        st.rerun()

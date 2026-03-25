import streamlit as st
from prompts import *
from utils import get_llm_response

st.set_page_config(page_title="TalentScout AI Assistant", layout="wide")

st.title("🤖 TalentScout AI Hiring Assistant")
st.info("🔒 Your data is used only for screening.")

# ---------------- SESSION ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "stage" not in st.session_state:
    st.session_state.stage = "name"

if "candidate" not in st.session_state:
    st.session_state.candidate = {}

# ---------------- GREETING ----------------
if len(st.session_state.messages) == 0:
    st.session_state.messages.append(("assistant", "Hello! What is your full name?"))

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
        st.rerun()

    elif st.session_state.stage == "email":
        st.session_state.candidate["email"] = user_input
        st.session_state.stage = "role"
        st.session_state.messages.append(("assistant", "What role are you applying for?"))
        st.rerun()

    elif st.session_state.stage == "role":
        st.session_state.candidate["role"] = user_input
        st.session_state.stage = "tech"
        st.session_state.messages.append(("assistant", "Enter your tech stack (comma separated)"))
        st.rerun()

    elif st.session_state.stage == "tech":

        tech_list = [t.strip() for t in user_input.split(",")]
        clean_tech = ", ".join(tech_list)

        st.session_state.candidate["tech_stack"] = clean_tech

        try:
            questions = get_llm_response(get_question_prompt(clean_tech))
        except:
            questions = """General:
1. Tell me about your project
2. What challenges did you face?
3. How do you solve problems?
"""

        st.session_state.questions = questions
        st.session_state.stage = "questions"

        st.session_state.messages.append(("assistant", "Here are your questions. Answer below 👇"))
        st.rerun()

    # ---------------- FALLBACK ----------------
    else:
        chat_history = "\n".join(
            [f"{r}: {m}" for r, m in st.session_state.messages[-10:]]
        )

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

    q_lines = st.session_state.questions.split("\n")

    qn = 1
    for line in q_lines:
        if line.strip().startswith(("1", "2", "3")):
            st.write(f"Q{qn}: {line}")
            ans = st.text_area("Your Answer", key=f"a{qn}")
            st.session_state.answers[f"Q{qn}"] = ans
            qn += 1

    if st.button("Submit"):
        st.session_state.final_answers = st.session_state.answers.copy()
        st.session_state.stage = "review"
        st.rerun()

# ---------------- REVIEW ----------------
if st.session_state.stage == "review":

    st.subheader("Your Answers")

    for q, a in st.session_state.final_answers.items():
        st.write(q)
        st.write(a)

    if st.button("Finish"):
        name = st.session_state.candidate.get("name", "Candidate")

        try:
            final_msg = get_llm_response(get_end_prompt(name))
        except:
            final_msg = f"Thank you {name}, we will contact you soon."

        st.session_state.messages.append(("assistant", final_msg))
        st.session_state.stage = "end"
        st.rerun()

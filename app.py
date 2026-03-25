import streamlit as st
from prompts import *
from utils import get_llm_response

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="TalentScout AI Assistant", layout="wide")

# ---------------- HEADER ----------------
st.title("🤖 TalentScout AI Hiring Assistant")
st.info("🔒 Your data is used only for screening and is not stored permanently.")

# ---------------- SESSION ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "post_chat" not in st.session_state:
    st.session_state.post_chat = []

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
    st.write(f"Tech Stack: {c.get('tech_stack', '-')}")

# ---------------- INITIAL GREETING ----------------
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

# ---------------- USER INPUT ----------------
user_input = st.chat_input("Type your response here...")

if user_input:

    # Decide where to store chat
    if st.session_state.stage in ["questions", "review"]:
        st.session_state.post_chat.append(("user", user_input))
    else:
        st.session_state.messages.append(("user", user_input))

    # EXIT
    if user_input.lower() in ["exit", "quit", "bye"]:
        name = st.session_state.candidate.get("name", "Candidate")
        final_msg = get_llm_response(get_end_prompt(name))

        if st.session_state.stage in ["questions", "review"]:
            st.session_state.post_chat.append(("assistant", final_msg))
        else:
            st.session_state.messages.append(("assistant", final_msg))

        st.session_state.stage = "end"
        st.rerun()

    # FLOW
    elif st.session_state.stage == "collect_name":
        st.session_state.candidate["name"] = user_input
        st.session_state.messages.append(("assistant", "📧 Please provide your email address."))
        st.session_state.stage = "collect_email"
        st.rerun()

    elif st.session_state.stage == "collect_email":
        st.session_state.candidate["email"] = user_input
        st.session_state.messages.append(("assistant", "📞 Please provide your phone number."))
        st.session_state.stage = "collect_phone"
        st.rerun()

    elif st.session_state.stage == "collect_phone":
        st.session_state.candidate["phone"] = user_input
        st.session_state.messages.append(("assistant", "💼 How many years of experience do you have?"))
        st.session_state.stage = "collect_experience"
        st.rerun()

    elif st.session_state.stage == "collect_experience":
        st.session_state.candidate["experience"] = user_input
        st.session_state.messages.append(("assistant", "🎯 What role are you applying for?"))
        st.session_state.stage = "collect_role"
        st.rerun()

    elif st.session_state.stage == "collect_role":
        st.session_state.candidate["role"] = user_input
        st.session_state.messages.append(("assistant", "📍 Where are you currently located?"))
        st.session_state.stage = "collect_location"
        st.rerun()

    elif st.session_state.stage == "collect_location":
        st.session_state.candidate["location"] = user_input
        st.session_state.messages.append(("assistant", "🛠 Please list your tech stack."))
        st.session_state.stage = "tech_stack"
        st.rerun()

    elif st.session_state.stage == "tech_stack":
        st.session_state.candidate["tech_stack"] = user_input

        questions = get_llm_response(get_question_prompt(user_input))
        st.session_state.questions = questions

        st.session_state.messages.append(("assistant", "I have generated technical questions. Please answer them below 👇"))
        st.session_state.stage = "questions"
        st.rerun()

    # FALLBACK
    else:
        chat_history = "\n".join([f"{r}: {m}" for r, m in st.session_state.messages])

        response = get_llm_response(
            get_fallback_prompt(
    user_input,
    st.session_state.stage,
    chat_history,
    st.session_state.candidate,
    st.session_state.get("final_answers", {})
)
        )

        if st.session_state.stage in ["questions", "review"]:
            st.session_state.post_chat.append(("assistant", response))
        else:
            st.session_state.messages.append(("assistant", response))

        st.rerun()

# ---------------- MAIN CHAT ----------------
for role, msg in st.session_state.messages:
    if role == "assistant":
        with st.chat_message("assistant"):
            st.write(msg)
    else:
        st.markdown(f"""
        <div style='background-color:#e6f7ff;padding:10px;border-radius:10px;margin-bottom:8px'>
        <b>You:</b> {msg}
        </div>
        """, unsafe_allow_html=True)

# ---------------- QUESTIONS ----------------
if st.session_state.stage == "questions":
    st.subheader("Answer the Questions Below")

    if "answers" not in st.session_state:
        st.session_state.answers = {}

    q_lines = st.session_state.get("questions", "").split("\n")

    qn = 1
    for line in q_lines:
        if line.strip().startswith(("1", "2", "3", "4", "5")):
            st.write(f"**Q{qn}: {line}**")
            ans = st.text_area(f"Your Answer {qn}", key=f"a{qn}")
            st.session_state.answers[f"Q{qn}"] = ans
            qn += 1

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

# ---------------- POST CHAT ----------------
if st.session_state.stage in ["questions", "review"]:
    st.divider()

    for role, msg in st.session_state.post_chat:
        if role == "assistant":
            with st.chat_message("assistant"):
                st.write(msg)
        else:
            st.markdown(f"""
            <div style='background-color:#e6f7ff;padding:10px;border-radius:10px;margin-bottom:8px'>
            <b>You:</b> {msg}
            </div>
            """, unsafe_allow_html=True)

# ---------------- FINAL BUTTON ----------------
if st.session_state.stage == "review":
    if st.button("🚀 Finish Interview"):
        name = st.session_state.candidate.get("name", "Candidate")
        final_msg = get_llm_response(get_end_prompt(name))

        st.session_state.post_chat.append(("assistant", final_msg))
        st.session_state.stage = "end"
        st.rerun()

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

# ---------------- DISPLAY CHAT ----------------
for role, msg in st.session_state.messages:
    with st.chat_message(role):
        st.write(msg)

# ---------------- USER INPUT ----------------
user_input = st.chat_input("Type your response here...")

if user_input:

    st.session_state.messages.append(("user", user_input))

    # EXIT
    if user_input.lower() in ["exit", "quit", "bye"]:
        name = st.session_state.candidate.get("name", "Candidate")
        final_msg = get_llm_response(get_end_prompt(name))
        st.session_state.messages.append(("assistant", final_msg))
        st.session_state.stage = "end"
        st.rerun()

    # ---------------- FLOW ----------------
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
        st.session_state.messages.append(("assistant", "🛠 Please list your tech stack (languages, frameworks, tools)."))
        st.rerun()

    # 🔥 FIXED TECH STACK
    elif st.session_state.stage == "tech_stack":

        tech_list = [t.strip() for t in user_input.split(",")]
        clean_tech = ", ".join(tech_list)

        st.session_state.candidate["tech_stack"] = clean_tech

        try:
            questions = get_llm_response(get_question_prompt(clean_tech))
        except:
            questions = """General:
1. Describe a project you worked on.
2. What challenges did you face?
3. How do you approach problem-solving?
"""

        st.session_state.questions = questions
        st.session_state.messages.append(("assistant", "I have generated technical questions. Please answer them below 👇"))

        st.session_state.stage = "questions"
        st.rerun()

    # 🔥 FIXED FALLBACK
    else:
        chat_history = "\n".join(
            [f"{r}: {m}" for r, m in st.session_state.messages[-10:]]
        )

        candidate_info = str(st.session_state.candidate)
        answers = str(st.session_state.get("final_answers", {}))[:500]

        try:
            response = get_llm_response(
                get_fallback_prompt(
                    user_input,
                    st.session_state.stage,
                    chat_history,
                    candidate_info,
                    answers
                )
            )
        except:
            if st.session_state.stage == "review":
                response = "Your responses have been recorded and will be reviewed by our team."
            elif st.session_state.stage == "questions":
                response = "Please complete the questions above. Let me know if you need help."
            else:
                response = "I'm here to assist you. Could you please clarify your question?"

        st.session_state.messages.append(("assistant", response))
        st.rerun()

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

    name = st.session_state.candidate.get("name", "Candidate")

    if st.button("🚀 Finish Interview"):
        final_msg = get_llm_response(get_end_prompt(name))
        st.session_state.messages.append(("assistant", final_msg))
        st.session_state.stage = "end"
        st.rerun()

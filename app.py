import streamlit as st
from prompts import (
    get_info_prompt,
    get_tech_stack_prompt,
    get_question_prompt,
    get_fallback_prompt
)
from utils import get_llm_response


# =========================
# SESSION STATE INIT
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "stage" not in st.session_state:
    st.session_state.stage = "info"

if "candidate_info" not in st.session_state:
    st.session_state.candidate_info = {
        "name": "",
        "email": "",
        "phone": "",
        "experience": "",
        "role": "",
        "location": ""
    }

if "tech_stack" not in st.session_state:
    st.session_state.tech_stack = ""

if "questions" not in st.session_state:
    st.session_state.questions = []

if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0

if "answers" not in st.session_state:
    st.session_state.answers = []


# =========================
# UI
# =========================
st.title("TalentScout Hiring Assistant 🤖")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# =========================
# HELPER
# =========================
def ask_llm(prompt):
    return get_llm_response(prompt)


def extract_questions(text):
    lines = text.split("\n")
    questions = []
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit():
            questions.append(line)
    return questions


# =========================
# INITIAL BOT MESSAGE
# =========================
if len(st.session_state.messages) == 0:
    first_q = ask_llm(get_info_prompt())
    st.session_state.messages.append({"role": "assistant", "content": first_q})
    st.rerun()


# =========================
# USER INPUT
# =========================
user_input = st.chat_input("Type your response...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    stage = st.session_state.stage

    # =========================
    # STAGE 1: INFO COLLECTION
    # =========================
    if stage == "info":
        info = st.session_state.candidate_info

        if info["name"] == "":
            info["name"] = user_input
        elif info["email"] == "":
            info["email"] = user_input
        elif info["phone"] == "":
            info["phone"] = user_input
        elif info["experience"] == "":
            info["experience"] = user_input
        elif info["role"] == "":
            info["role"] = user_input
        elif info["location"] == "":
            info["location"] = user_input
            st.session_state.stage = "tech_stack"

        bot_reply = ask_llm(get_info_prompt())

    # =========================
    # STAGE 2: TECH STACK
    # =========================
    elif stage == "tech_stack":
        if st.session_state.tech_stack == "":
            st.session_state.tech_stack = user_input

            # Generate questions
            questions_text = ask_llm(get_question_prompt(user_input))
            questions = extract_questions(questions_text)

            st.session_state.questions = questions
            st.session_state.stage = "questions"
            st.session_state.current_q_index = 0

            if questions:
                bot_reply = f"Let's start the interview 🚀\n\n{questions[0]}"
            else:
                bot_reply = "I couldn't generate questions. Please re-enter your tech stack."
                st.session_state.stage = "tech_stack"
        else:
            bot_reply = ask_llm(get_tech_stack_prompt())

    # =========================
    # STAGE 3: QUESTIONS (ONE BY ONE)
    # =========================
    elif stage == "questions":
        st.session_state.answers.append(user_input)
        st.session_state.current_q_index += 1

        if st.session_state.current_q_index < len(st.session_state.questions):
            next_q = st.session_state.questions[st.session_state.current_q_index]
            bot_reply = next_q
        else:
            st.session_state.stage = "review"
            bot_reply = "Your responses have been recorded and will be reviewed by our team. You will be contacted soon."

    # =========================
    # STAGE 4: REVIEW
    # =========================
    elif stage == "review":
        bot_reply = "Your responses have been recorded and will be reviewed by our team. You will be contacted soon."

    # =========================
    # FALLBACK
    # =========================
    else:
        bot_reply = ask_llm(
            get_fallback_prompt(
                user_input,
                st.session_state.stage,
                st.session_state.messages,
                st.session_state.candidate_info,
                st.session_state.answers
            )
        )

    # Save bot response
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # Display bot response
    with st.chat_message("assistant"):
        st.markdown(bot_reply)

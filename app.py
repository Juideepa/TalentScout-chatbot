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

if "questions_generated" not in st.session_state:
    st.session_state.questions_generated = False

if "answers" not in st.session_state:
    st.session_state.answers = []


# =========================
# UI
# =========================
st.title("TalentScout Hiring Assistant 🤖")

# Show previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# =========================
# USER INPUT
# =========================
user_input = st.chat_input("Type your response...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    stage = st.session_state.stage

    # =========================
    # STAGE 1: INFO
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

        bot_reply = get_llm_response(get_info_prompt())

    # =========================
    # STAGE 2: TECH STACK
    # =========================
    elif stage == "tech_stack":
        if st.session_state.tech_stack == "":
            st.session_state.tech_stack = user_input
            st.session_state.stage = "questions"

            bot_reply = get_llm_response(get_question_prompt(user_input))
            st.session_state.questions_generated = True
        else:
            bot_reply = get_llm_response(get_tech_stack_prompt())

    # =========================
    # STAGE 3: QUESTIONS
    # =========================
    elif stage == "questions":
        st.session_state.answers.append(user_input)

        if len(st.session_state.answers) >= 3:
            st.session_state.stage = "review"
            bot_reply = "Your responses have been recorded and will be reviewed by our team. You will be contacted soon."
        else:
            bot_reply = "Got it 👍 Please continue answering the remaining questions."

    # =========================
    # STAGE 4: REVIEW
    # =========================
    elif stage == "review":
        bot_reply = "Your responses have been recorded and will be reviewed by our team. You will be contacted soon."

    # =========================
    # FALLBACK
    # =========================
    else:
        bot_reply = get_llm_response(
            get_fallback_prompt(
                user_input,
                st.session_state.stage,
                st.session_state.messages,
                st.session_state.candidate_info,
                st.session_state.answers
            )
        )

    # Save + display bot response
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    with st.chat_message("assistant"):
        st.markdown(bot_reply)

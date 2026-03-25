# ---------------- QUESTION PROMPT ----------------
def get_question_prompt(tech_stack):
    return f"""
You are a technical interviewer.

Tech Stack: {tech_stack}

Generate EXACTLY 3 questions per technology.

Format:

Python:
1. Question
2. Question
3. Question

Rules:
- Questions must be specific to each technology
- No generic questions
- No explanations
- Only questions
"""


# ---------------- FALLBACK ----------------
def get_fallback_prompt(user_input, stage, chat_history):
    return f"""
User: {user_input}

Context: Hiring assistant conversation

Reply naturally and briefly.

If user asks about results:
Say "Your responses have been recorded and our team will get back to you soon."
"""


# ---------------- END ----------------
def get_end_prompt(name):
    return f"""
Thank {name} for their time.

Say:
- Responses are recorded
- Team will contact soon
"""

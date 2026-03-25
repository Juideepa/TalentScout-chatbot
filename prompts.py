def get_question_prompt(tech_stack):
    return f"""
You are a technical interviewer.

Candidate Tech Stack:
{tech_stack}

Generate 3-5 interview questions for each technology.

Format:

Python:
1. Question
2. Question
3. Question

Rules:
- Questions should be relevant to each technology
- Keep them clear and practical
- No explanations
"""


def get_fallback_prompt(user_input, stage, chat_history):
    return f"""
You are an AI Hiring Assistant.

User said:
{user_input}

Conversation:
{chat_history}

Rules:
- Answer the user's question clearly
- Do NOT restart the process
- Do NOT ask for details again
- If user asks about results, say:
  "Your responses have been recorded and our team will get back to you soon."
- Keep answer short and helpful
"""


def get_end_prompt(name):
    return f"""
Thank {name} for their time.

Tell them:
- Their responses are recorded
- The team will contact them soon

Keep it short and professional.
"""

def get_question_prompt(tech_stack):
    return f"""
You are an expert technical interviewer.

Candidate Tech Stack:
{tech_stack}

Task:
- Identify each technology
- Generate EXACTLY 3 questions per technology

STRICT FORMAT:

Python:
1. Question
2. Question
3. Question

Rules:
- Questions must be specific to each technology
- No generic questions
- No explanation
- Only questions
"""

def get_fallback_prompt(user_input, stage, chat_history, candidate_info, answers):
    return f"""
You are an AI Hiring Assistant.

Current Stage: {stage}

Candidate Info:
{candidate_info}

Answers:
{answers}

Conversation:
{chat_history}

User said: "{user_input}"

Instructions:
- DO NOT restart process
- DO NOT ask for details again
- If user asks about results → say:
  "Your responses have been recorded and will be reviewed by our team."
- Otherwise answer normally in short
"""

def get_end_prompt(name):
    return f"""
Thank {name} for their time.

Say:
- Responses are recorded
- Team will contact soon

Keep it short and professional.
"""

def get_question_prompt(tech_stack):
    return f"""
You are a technical interviewer.

Candidate Tech Stack: {tech_stack}

Generate 3 questions per technology.

Format:

Python:
1. Question
2. Question
3. Question

Rules:
- Questions must be specific to each technology
- No explanations
- Only questions
"""


def get_fallback_prompt(user_input):
    return f"""
User said: "{user_input}"

Reply naturally and briefly.
If they ask about results, say:
"Your responses have been recorded and will be reviewed by our team."
"""


def get_end_prompt(name):
    return f"""
Thank {name} for their time.
Tell them their responses are recorded and they will be contacted soon.
"""

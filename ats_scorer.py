from langchain_groq import ChatGroq
from config import GROQ_API_KEY


llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="openai/gpt-oss-20b"
)


def calculate_resume_score(resume_text):

    prompt = f"""
You are an expert ATS resume evaluator.

Evaluate the quality of the resume based ONLY on the
information present in the resume.

This is a GENERAL resume quality score, not a job-specific
matching score.

Give a score from 0 to 100 using these categories:

1. Resume Structure and Organization — 20 points
2. Skills Clarity — 20 points
3. Experience and Projects — 20 points
4. Achievements and Quantifiable Results — 15 points
5. Contact and Professional Information — 10 points
6. ATS-Friendly Content and Headings — 15 points

IMPORTANT:
- Do not invent information.
- Do not assume missing information exists.
- Missing information should reduce the relevant score.
- Explain why points were deducted.
- Do not claim that this score guarantees ATS selection.
- This is an estimated resume quality score.

Return:

OVERALL SCORE:
__/100

STRUCTURE SCORE:
__/20

SKILLS SCORE:
__/20

EXPERIENCE AND PROJECTS SCORE:
__/20

ACHIEVEMENTS SCORE:
__/15

CONTACT INFORMATION SCORE:
__/10

ATS CONTENT SCORE:
__/15

WHY THIS SCORE:
- ...

TOP IMPROVEMENTS:
- ...
- ...
- ...

RESUME:
{resume_text}
"""

    response = llm.invoke(prompt)

    return response.content
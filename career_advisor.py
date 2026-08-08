from langchain_groq import ChatGroq
import os


# ==================================================
# LLM
# ==================================================

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2,
    api_key=os.getenv("GROQ_API_KEY")
)


# ==================================================
# CAREER DECISION
# ==================================================

def analyze_job_suitability(
    resume_text,
    job_description
):

    prompt = f"""
You are an expert career advisor and recruitment
assistant.

Analyze whether the candidate should apply for the
given job based on the candidate's actual resume.

IMPORTANT RULES:

1. Never invent candidate skills.
2. Never assume experience that is not in the resume.
3. Do not reject a candidate only because they are missing
   optional skills.
4. Distinguish between required and preferred skills.
5. Identify transferable skills when reasonable.
6. Consider that the candidate may be a fresher/junior.
7. Give practical and honest advice.
8. Do not make decisions based on protected personal
   characteristics.
9. Do not claim guaranteed job selection.

--------------------------------------------------
CANDIDATE RESUME
--------------------------------------------------

{resume_text}

--------------------------------------------------
JOB DESCRIPTION
--------------------------------------------------

{job_description}

--------------------------------------------------
DECISION
--------------------------------------------------

Choose exactly one:

APPLY

MAYBE

NOT RECOMMENDED

--------------------------------------------------
OUTPUT FORMAT
--------------------------------------------------

DECISION:
<APPLY / MAYBE / NOT RECOMMENDED>

MATCH LEVEL:
<High / Medium / Low>

WHY:
- Give 3 to 5 clear reasons.

MATCHING SKILLS:
- List skills from the candidate resume that match
  the job.

MISSING IMPORTANT SKILLS:
- List important job requirements that are missing
  from the candidate resume.

TRANSFERABLE SKILLS:
- Mention relevant transferable skills if applicable.

CONCERNS:
- Mention important gaps or concerns.

RECOMMENDATION:
- Give practical advice about whether the candidate
  should apply.
- If APPLY, explain why applying makes sense.
- If MAYBE, explain what should be improved.
- If NOT RECOMMENDED, explain what type of role may
  be more suitable.

Do not add any skill to the candidate's resume.
"""

    response = llm.invoke(prompt)

    return response.content
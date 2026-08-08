from langchain_groq import ChatGroq
from config import GROQ_API_KEY


llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="openai/gpt-oss-20b"
)


def improve_resume(resume_text, job_description=""):

    prompt = f"""
You are an expert professional resume writer.

Improve the candidate's resume to make it more professional,
clear, ATS-friendly and relevant to the target job.

STRICT RULES:

1. NEVER invent skills.
2. NEVER invent companies.
3. NEVER invent projects.
4. NEVER invent experience.
5. NEVER invent certifications.
6. NEVER invent achievements.
7. NEVER change factual numbers.
8. Do not add technologies unless they already appear in
   the resume.
9. You may improve grammar, wording, structure and formatting.
10. Use strong professional action verbs.
11. Keep the resume suitable for a fresher/junior candidate.
12. If a job description is provided, prioritize relevant
    existing skills and experience.
13. Do not claim that the candidate has a skill just because
    the job description requires it.

Create an improved resume with these sections:

NAME

PROFESSIONAL SUMMARY

TECHNICAL SKILLS

PROFESSIONAL SKILLS

TOOLS

PROJECTS

EXPERIENCE

EDUCATION

CERTIFICATIONS

ACHIEVEMENTS

Use concise bullet points.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""

    response = llm.invoke(prompt)

    return response.content
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
# GENERATE JOB-SPECIFIC RESUME
# ==================================================

def generate_job_specific_resume(
    resume_text,
    job_description
):

    prompt = f"""
You are an expert ATS resume writer and career assistant.

Your task is to create a job-specific resume using ONLY
information that is actually present in the candidate's resume.

IMPORTANT RULES:

1. Never invent skills.
2. Never invent experience.
3. Never invent companies.
4. Never invent certifications.
5. Never invent projects.
6. Never claim the candidate knows a technology
   if it is not present in the resume.
7. You may identify transferable skills when reasonable.
8. If the job requires a missing skill, do NOT falsely add it.
9. Improve wording using professional action verbs.
10. Keep the resume ATS-friendly.
11. Prioritize skills relevant to the job description.
12. Keep the candidate's original facts accurate.

--------------------------------------------------
CANDIDATE RESUME
--------------------------------------------------

{resume_text}

--------------------------------------------------
JOB DESCRIPTION
--------------------------------------------------

{job_description}

--------------------------------------------------
OUTPUT FORMAT
--------------------------------------------------

Create the following:

CANDIDATE NAME

PROFESSIONAL SUMMARY

TECHNICAL SKILLS

PROFESSIONAL SKILLS

PROJECTS

EXPERIENCE

EDUCATION

CERTIFICATIONS

ACHIEVEMENTS

--------------------------------------------------

The professional summary should be tailored to the
job description but must remain factually accurate.

In TECHNICAL SKILLS, prioritize skills that actually
exist in the candidate's resume and are relevant to
the job.

Do not add missing technologies just because they
appear in the job description.

Use concise ATS-friendly bullet points.

Return only the final resume.
"""

    response = llm.invoke(prompt)

    return response.content
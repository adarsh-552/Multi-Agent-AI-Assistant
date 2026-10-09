"""The real agents of this app, as confirmed from the source files.

Seven specialists power the resume features. The supervisor/router agents are
a separate, unconnected group and are listed as legacy/experimental.
Models and temperatures below come straight from each module's ChatGroq setup;
if a module is already imported, its live model name is used instead.
"""

import sys

GPT_OSS = "openai/gpt-oss-20b"
LLAMA =  "openai/gpt-oss-20b"

AGENTS = [
    {
        "id": "analyzer", "name": "Resume Analyzer", "initials": "RA",
        "role": "Reads the resume and extracts a structured profile: skills, strengths, weaknesses, recommended roles and skill gaps.",
        "module": "resume_analyzer", "function": "analyze_resume", "file": "resume_analyzer.py",
        "model": GPT_OSS, "temperature": None,
        "input": "Resume text", "output": "Structured profile (ResumeAnalysis)", "needs_jd": False,
    },
    {
        "id": "ats", "name": "ATS Scorer", "initials": "AS",
        "role": "Estimates a general resume quality score out of 100, with six sub-scores and the reasons points were lost.",
        "module": "ats_scorer", "function": "calculate_resume_score", "file": "ats_scorer.py",
        "model": GPT_OSS, "temperature": None,
        "input": "Resume text", "output": "Score report (text)", "needs_jd": False,
    },
    {
        "id": "matcher", "name": "Job Matcher", "initials": "JM",
        "role": "Compares the resume with a job description and reports a match score, matching and missing skills, and gaps.",
        "module": "job_matcher", "function": "match_resume_with_job", "file": "job_matcher.py",
        "model": GPT_OSS, "temperature": None,
        "input": "Resume text + job description", "output": "Match report (text)", "needs_jd": True,
    },
    {
        "id": "improver", "name": "Resume Improver", "initials": "RI",
        "role": "Rewrites the resume to be clearer and more ATS-friendly, without inventing skills, projects or numbers.",
        "module": "resume_improver", "function": "improve_resume", "file": "resume_improver.py",
        "model": GPT_OSS, "temperature": None,
        "input": "Resume text + optional job description", "output": "Improved resume (text)", "needs_jd": False,
    },
    {
        "id": "tailor", "name": "Job-Specific Resume Writer", "initials": "JR",
        "role": "Builds a resume tailored to one job description, using only skills and experience already in the resume.",
        "module": "job_resume_generator", "function": "generate_job_specific_resume", "file": "job_resume_generator.py",
        "model": LLAMA, "temperature": 0.2,
        "input": "Resume text + job description", "output": "Tailored resume (text)", "needs_jd": True,
    },
    {
        "id": "advisor", "name": "Career Advisor", "initials": "CA",
        "role": "Decides whether you should apply for a job, with reasons, matching and missing skills, and concerns.",
        "module": "career_advisor", "function": "analyze_job_suitability", "file": "career_advisor.py",
        "model": LLAMA, "temperature": 0.2,
        "input": "Resume text + job description", "output": "Apply / Maybe / Not recommended, with reasons", "needs_jd": True,
    },
    {
        "id": "qa", "name": "Resume Q&A", "initials": "QA",
        "role": "Answers questions using only the resume passages that best match the question.",
        "module": "rag.rag_pipeline", "function": "ask_pdf", "file": "rag/rag_pipeline.py",
        "model": GPT_OSS, "temperature": None,
        "input": "Question + the 4 closest resume chunks", "output": "Answer (text)", "needs_jd": False,
    },
]

AGENT_BY_ID = {a["id"]: a for a in AGENTS}

# Retrieval settings as defined in rag/rag_pipeline.py.
RAG = {
    "embedding_model": "all-MiniLM-L6-v2",
    "index_type": "FAISS IndexFlatL2",
    "chunk_size": 300,
    "chunk_overlap": 50,
    "top_k": 4,
}

# Supervisor / router group: not connected to this app's interface.
LEGACY_AGENTS = [
    {"name": "Memory Agent", "file": "agents/memory_agent.py", "status": "Working, limited", "kind": "warn",
     "note": "Stores and recalls a name in a shared memory.json file. Nothing else."},
    {"name": "Search Agent", "file": "agents/search_agent.py", "status": "Stub", "kind": "idle",
     "note": "Echoes the query back. It does not search."},
    {"name": "Code Agent", "file": "agents/code_agent.py", "status": "Stub", "kind": "idle",
     "note": "Echoes the query back. It does not write or run code."},
    {"name": "Calculator Agent", "file": "agents/calculator_agent.py", "status": "Stub", "kind": "idle",
     "note": "Echoes the query back. It does not calculate."},
    {"name": "PDF Agent", "file": "agents/pdf_agent.py", "status": "Incomplete", "kind": "warn",
     "note": "Only a read_pdf helper exists; the pdf_agent function the supervisor imports is missing."},
]


def model_for(agent):
    """Model name for display. Prefers the live module setting when available."""
    module = sys.modules.get(agent["module"])
    llm = getattr(module, "llm", None)
    live = getattr(llm, "model_name", None) or getattr(llm, "model", None)
    return live or agent["model"]


def temperature_for(agent):
    return f'{agent["temperature"]}' if agent["temperature"] is not None else "Library default"

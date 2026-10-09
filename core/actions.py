"""Run specialists from session data. Backend functions are called unchanged."""

import hashlib
import os
import tempfile
import time
import traceback

import streamlit as st

from core.registry import AGENT_BY_ID, model_for
from core.runner import redact, timed_call

JD_AGENTS = ("matcher", "improver", "tailor", "advisor")


def _md5(*parts):
    return hashlib.md5("||".join(parts).encode("utf-8", "ignore")).hexdigest()


def input_sig(agent_id):
    text = st.session_state.resume_text
    if agent_id in JD_AGENTS:
        return _md5(text, st.session_state.job_description.strip())
    return _md5(text)


def get_result(agent_id):
    return st.session_state.results.get(agent_id)


def is_stale(agent_id):
    result = get_result(agent_id)
    return bool(result) and result["sig"] != input_sig(agent_id)


def _invoke(agent_id, text, jd):
    """Call the real backend function for this specialist (prompts untouched)."""
    if agent_id == "analyzer":
        from resume_analyzer import analyze_resume
        return analyze_resume(text)
    if agent_id == "ats":
        from ats_scorer import calculate_resume_score
        return calculate_resume_score(text)
    if agent_id == "matcher":
        from job_matcher import match_resume_with_job
        return match_resume_with_job(text, jd)
    if agent_id == "improver":
        from resume_improver import improve_resume
        return improve_resume(text, jd)
    if agent_id == "tailor":
        from job_resume_generator import generate_job_specific_resume
        return generate_job_specific_resume(text, jd)
    if agent_id == "advisor":
        from career_advisor import analyze_job_suitability
        return analyze_job_suitability(text, jd)
    raise ValueError(f"Unknown specialist: {agent_id}")


def run_action(agent_id):
    """Run a specialist with a live status panel. Returns True on success."""
    agent = AGENT_BY_ID[agent_id]
    ss = st.session_state

    if not ss.resume_processed:
        st.warning("Upload a resume first.")
        return False

    jd = ss.job_description.strip()
    if agent["needs_jd"] and not jd:
        st.warning("Add a job description first.")
        return False

    jd_used = jd if agent_id in JD_AGENTS else ""

    with st.status(f"{agent['name']} is working", expanded=True) as status:
        st.write("Resume context loaded")
        st.write(f"Sending the request to {model_for(agent)}")
        try:
            output, duration = timed_call(agent_id, _invoke, agent_id, ss.resume_text, jd_used)
        except Exception:
            ss.errors[agent_id] = {
                "message": (
                    "We couldn't complete this request. The AI service may be busy, "
                    "or the response was not in the expected format. Try again."
                ),
                "detail": redact(traceback.format_exc())[-2500:],
            }
            status.update(label=f"{agent['name']} could not finish", state="error", expanded=False)
            return False

        ss.errors.pop(agent_id, None)
        ss.results[agent_id] = {
            "output": output,
            "sig": input_sig(agent_id),
            "duration": duration,
            "ts": time.time(),
        }
        # keep the original session keys in sync
        if agent_id == "analyzer":
            ss.analysis = output
        elif agent_id == "improver":
            ss.improved_resume = output
        elif agent_id == "tailor":
            ss.tailored_resume = output

        status.update(label=f"{agent['name']} finished in {duration:.1f}s", state="complete", expanded=False)

    st.toast(f"{agent['name']} finished")
    return True


def get_docx(text):
    """DOCX bytes for a result, built once per text and cached in the session.

    Uses the existing create_resume_docx(text, path), writing to a private
    temp file instead of a shared uploads/ path.
    """
    key = _md5(text)
    cache = st.session_state.docx_cache
    if key not in cache:
        from docx_generator import create_resume_docx

        fd, path = tempfile.mkstemp(suffix=".docx")
        os.close(fd)
        try:
            create_resume_docx(text, path)
            with open(path, "rb") as handle:
                cache[key] = handle.read()
        finally:
            if os.path.exists(path):
                os.remove(path)
    return cache[key]


def build_report():
    """Markdown report made only from results that actually exist this session."""
    ss = st.session_state
    lines = [f"# Resume report: {ss.get('processed_file_name') or 'resume'}", ""]

    analysis = ss.analysis
    if analysis is not None:
        lines += [
            "## Profile",
            f"- Name: {analysis.name}",
            f"- Target role: {analysis.current_or_target_role}",
            f"- Domain: {analysis.professional_domain}",
            f"- Experience level: {analysis.experience_level}",
            "",
        ]
        for title, items in [
            ("Technical skills", analysis.technical_skills),
            ("Professional skills", analysis.professional_skills),
            ("Tools", analysis.tools),
            ("Strengths", analysis.strengths),
            ("Weaknesses", analysis.weaknesses),
            ("Recommended roles", analysis.recommended_roles),
            ("Skill gaps", analysis.skill_gaps),
            ("Resume improvements", analysis.resume_improvements),
        ]:
            if items:
                lines += [f"## {title}"] + [f"- {i}" for i in items] + [""]

    for agent_id, title in [("ats", "ATS score report"), ("matcher", "Job match report"), ("advisor", "Career advice")]:
        result = ss.results.get(agent_id)
        if result:
            lines += [f"## {title}", str(result["output"]).strip(), ""]

    if len(lines) <= 2:
        lines.append("No results yet.")
    return "\n".join(lines)

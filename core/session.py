"""Session state for AI Command Center.

Original keys are kept (resume_processed, resume_text, index, chunks, analysis,
improved_resume, tailored_resume, processed_file_name). The resume text is
still the chunk-joined text, exactly as before.
"""

import copy
import os
import tempfile
import traceback

import streamlit as st

APP_VERSION = "2.0.0"

SESSION_DEFAULTS = {
    "resume_processed": False,
    "resume_text": "",
    "index": None,
    "chunks": None,
    "analysis": None,
    "improved_resume": None,
    "tailored_resume": None,
    "job_description": "",
    "ws_section": "Analyze",   # which Resume Workspace section is open
    "results": {},        # agent_id -> {output, sig, duration, ts}
    "errors": {},         # agent_id -> {message, detail}
    "qa_messages": [],
    "runs": [],           # one record per real specialist call
    "docx_cache": {},
    "upload_nonce": 0,
    "resume_file_size": None,
    "upload_error": None,
    "failed_upload": None,
}

PREF_DEFAULTS = {"compact": False, "run_details": True, "timestamps": True}

RESUME_KEYS = [
    "resume_processed", "resume_text", "index", "chunks", "analysis", "improved_resume",
    "tailored_resume", "results", "errors", "qa_messages", "docx_cache",
    "resume_file_size", "upload_error", "failed_upload",
]


def init_session():
    """Create missing keys. Safe to call on every rerun."""
    for key, default in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = copy.deepcopy(default)
    if "prefs" not in st.session_state:
        st.session_state["prefs"] = dict(PREF_DEFAULTS)


def get_prefs():
    return st.session_state.get("prefs", PREF_DEFAULTS)


def reset_resume():
    """Remove the loaded resume and everything derived from it (run history stays)."""
    for key in RESUME_KEYS:
        st.session_state[key] = copy.deepcopy(SESSION_DEFAULTS[key])
    st.session_state.pop("processed_file_name", None)
    st.session_state["upload_nonce"] += 1


def reset_session():
    st.session_state.clear()
    init_session()


def process_uploaded_file(uploaded_file):
    """Read the PDF and build the vector store. Returns True on success.

    Same processing as the original app (create_vector_store, then
    "\\n\\n".join(chunks)). Two changes: the PDF is written to a private temp
    file instead of a shared uploads/<name> path, and failures become a
    friendly error instead of a traceback.
    """
    from core.runner import redact
    from rag.rag_pipeline import create_vector_store

    already = st.session_state.get("processed_file_name") == uploaded_file.name
    if already:
        return True

    marker = (uploaded_file.name, getattr(uploaded_file, "size", None))
    if st.session_state.get("failed_upload") == marker:
        return False

    tmp_path = None
    with st.status("Processing your resume", expanded=True) as status:
        try:
            st.write("Saving the file for this session")
            fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
            os.close(fd)
            with open(tmp_path, "wb") as handle:
                handle.write(uploaded_file.getbuffer())

            st.write("Reading the PDF and building the search index")
            index, chunks = create_vector_store(tmp_path)
        except Exception as exc:
            status.update(label="Could not process this resume", state="error", expanded=False)
            st.session_state.failed_upload = marker
            st.session_state.upload_error = {
                "title": "We couldn't read this resume",
                "message": (
                    "The PDF may be scanned, image-only, empty or damaged. "
                    "Try a PDF that contains selectable text."
                ),
                "detail": redact(traceback.format_exc())[-2500:] or str(exc),
            }
            return False
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

        # ---- save in session (same keys as the original app) ----
        st.session_state.index = index
        st.session_state.chunks = chunks
        st.session_state.resume_text = "\n\n".join(chunks)
        st.session_state.resume_processed = True
        st.session_state.processed_file_name = uploaded_file.name
        st.session_state.resume_file_size = getattr(uploaded_file, "size", None)

        # a new resume invalidates everything derived from the old one
        st.session_state.analysis = None
        st.session_state.improved_resume = None
        st.session_state.tailored_resume = None
        st.session_state.results = {}
        st.session_state.errors = {}
        st.session_state.qa_messages = []
        st.session_state.docx_cache = {}
        st.session_state.upload_error = None
        st.session_state.failed_upload = None

        status.update(label="Resume ready", state="complete", expanded=False)
    return True


def groq_key_configured():
    """True if a Groq key exists. The key itself is never read out."""
    if os.getenv("GROQ_API_KEY"):
        return True
    try:
        return bool(st.secrets.get("GROQ_API_KEY"))
    except Exception:
        return False


def resume_status():
    chunks = st.session_state.get("chunks")
    return {
        "loaded": bool(st.session_state.get("resume_processed")),
        "file_name": st.session_state.get("processed_file_name"),
        "file_size": st.session_state.get("resume_file_size"),
        "analysis_done": st.session_state.get("analysis") is not None,
        "chunk_count": len(chunks) if chunks else 0,
        "characters": len(st.session_state.get("resume_text") or ""),
    }

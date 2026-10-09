"""Overview: greeting, ask box, clickable starter tiles, session status, workflow, activity."""

import streamlit as st

from core import parsing
from core.actions import get_result
from core.runner import agent_stats
from core.session import get_prefs, resume_status
from ui import components as ui

ss = st.session_state
status = resume_status()
prefs = get_prefs()


def open_workspace(section, question=None):
    """Jump to a Resume Workspace section (optionally with a question to ask)."""
    ss.ws_section = section
    ss.pop("ws_section_w", None)  # let the section switcher re-seed from ws_section
    if question:
        ss.qa_pending = question
    st.switch_page("views/workspace.py")


# ---------------- greeting + ask box ----------------
welcome = "Welcome back to" if (status["loaded"] or ss.runs) else "Welcome to"
ui.html(
    f'<div class="acc-greet">{welcome} <span class="acc-accent">AI Command Center</span></div>'
    '<div class="acc-greet-sub">What would you like to work on today?</div>'
)

with st.container(key="ask_box"):
    with st.form("ask_form", clear_on_submit=True):
        field, send = st.columns([6, 1])
        with field:
            typed = st.text_input(
                "Ask about your resume",
                placeholder=(
                    "Ask a question about your resume..." if status["loaded"]
                    else "Upload a resume to ask questions about it"
                ),
                label_visibility="collapsed",
                disabled=not status["loaded"],
            )
        with send:
            submitted = st.form_submit_button("Ask", type="primary", use_container_width=True, disabled=not status["loaded"])

if submitted and typed.strip():
    open_workspace("Ask Resume", typed.strip())

if status["loaded"]:
    ui.html('<div class="acc-center-note">Answers come from your resume only, with the source passages shown.</div>')
else:
    ui.html('<div class="acc-center-note">No resume yet. Open any card below to get started.</div>')

# ---------------- starter tiles (each one is a real link) ----------------
ui.html('<div class="acc-starters-title">Start here</div>')

tiles = [
    ("analyze", "Resume Analysis", "Your profile, skills, score and feedback in one view.", "blue", "file", "Analyze"),
    ("ats", "ATS Score", "Check your resume quality out of 100.", "purple", "score", "ATS"),
    ("improve", "Improve Resume", "Rewrite it to be clearer and more ATS-friendly.", "green", "zap", "Improve"),
    ("tailor", "Tailor Resume", "Match it to one specific job description.", "orange", "target", "Tailor"),
    ("ask", "Ask Resume", "Ask questions and see exactly which passages answer.", "teal", "chat", "Ask Resume"),
    ("analytics", "Analytics", "Runs and response times for this session.", "pink", "bars", None),
]
for row in (tiles[:3], tiles[3:]):
    for column, (key, title, text, color, icon_name, section) in zip(st.columns(3), row):
        with column:
            if ui.tile(key, title, text, color, icon_name):
                if section:
                    open_workspace(section)
                else:
                    st.switch_page("views/analytics.py")

st.write("")

# ---------------- status cards (real values only) ----------------
ui.section("Your resume at a glance")
ats = get_result("ats")
ats_parsed = parsing.parse_ats(ats["output"]) if ats else None
match = get_result("matcher")
match_parsed = parsing.parse_match(match["output"]) if match else None

c1, c2, c3, c4 = st.columns(4)
with c1:
    if status["loaded"]:
        ui.kpi_with_pill("Resume", ui.pill("Loaded", "ok"), status["file_name"])
    else:
        ui.kpi_with_pill("Resume", ui.pill("Not loaded", "idle"), "Upload a PDF to begin")
with c2:
    if status["analysis_done"]:
        ui.kpi_with_pill("Analysis", ui.pill("Complete", "ok"), f'{status["chunk_count"]} chunks indexed')
    elif "analyzer" in ss.errors:
        ui.kpi_with_pill("Analysis", ui.pill("Failed", "err"), "Open the workspace to retry")
    else:
        ui.kpi_with_pill("Analysis", ui.pill("Not started", "idle"), "Runs automatically after upload")
with c3:
    if ats_parsed and ats_parsed["score"] is not None:
        ui.kpi("ATS score", f'{ats_parsed["score"]:g} / {ats_parsed["max"]:g}', "AI-estimated quality score")
    else:
        ui.kpi("ATS score", "Not run", "Run the ATS Scorer in the workspace")
with c4:
    if match_parsed and match_parsed["score"] is not None:
        ui.kpi("Job match", f'{match_parsed["score"]:g}%', "Against your target job")
    else:
        ui.kpi("Job match", "Not run", "Needs a target job description")

st.write("")

# ---------------- workflow ----------------
with st.container(border=True):
    ui.section("Workflow", "Steps you have completed in this session. The highlighted step is the next one.")
    ui.workflow([
        ("Upload resume", status["loaded"]),
        ("Analyze", status["analysis_done"]),
        ("ATS", get_result("ats") is not None),
        ("Job match", get_result("matcher") is not None),
        ("Improve", get_result("improver") is not None),
        ("Tailor", get_result("tailor") is not None),
        ("Career advice", get_result("advisor") is not None),
        ("Ask resume", any(m["role"] == "assistant" and not m.get("error") for m in ss.qa_messages)),
    ])

st.write("")
with st.container(border=True):
    stats = agent_stats()
    ui.section("Recent activity", "The latest specialist runs in this session.")
    if stats["total"] == 0:
        ui.empty_state("No runs yet", "Specialist runs appear here as soon as you use the workspace.", "0")
    else:
        ui.activity_rows(list(reversed(ss.runs[-6:])), prefs.get("timestamps", True))

"""Resume Workspace: upload, target job, quick actions, then one tab per specialist."""

import time

import streamlit as st

from core import parsing
from core.actions import build_report, get_docx, get_result, is_stale, run_action
from core.registry import AGENT_BY_ID, model_for
from core.runner import redact, timed_call
from core.session import get_prefs, process_uploaded_file, reset_resume, resume_status
from ui import components as ui
from ui.theme import page_title

ss = st.session_state
prefs = get_prefs()

page_title(
    "Resume Workspace",
    "Upload a resume, add a target job if you have one, then run any specialist on it.",
)

# =========================================================
# UPLOAD CARD
# =========================================================

if not ss.resume_processed:
    with st.container(border=True):
        ui.section("Upload your resume", "PDF files only. The file is processed in this session.")
        uploaded = st.file_uploader(
            "Drop your resume PDF here",
            type=["pdf"],
            key=f"resume_pdf_upload_{ss.upload_nonce}",
            label_visibility="collapsed",
        )
        if uploaded is not None:
            if process_uploaded_file(uploaded):
                st.rerun()

    if ss.upload_error:
        ui.error_card(ss.upload_error["title"], ss.upload_error["message"], ss.upload_error["detail"])

    ui.empty_state(
        "Your specialists are waiting",
        "After you upload a resume you can analyze it, score it, match it to a job, "
        "improve it, tailor it, get career advice and ask questions about it.",
        "CV",
    )
    st.stop()

status = resume_status()
size = ui.human_size(status["file_size"])
meta_parts = [f'{status["chunk_count"]} chunks', f'{status["characters"]:,} characters']
if size:
    meta_parts.insert(0, size)

with st.container(border=True):
    left, right = st.columns([4, 1])
    with left:
        ui.file_chip(status["file_name"], " \u00b7 ".join(meta_parts))
        ui.html(ui.pill("Ready", "ok"))
    with right:
        st.button("Remove", key="remove_resume", icon=":material/delete:", on_click=reset_resume, use_container_width=True)

# automatic first analysis, as in the original app
if ss.analysis is None and "analyzer" not in ss.errors:
    run_action("analyzer")

# =========================================================
# TARGET JOB DESCRIPTION (shared by the job-based specialists)
# =========================================================

if "jd_input" not in ss:
    ss["jd_input"] = ss.job_description

with st.container(border=True):
    ui.section(
        "Target job description",
        "Used by Job Match, Tailor and Career Advisor. Optional for Improve.",
    )
    jd = st.text_area(
        "Job description",
        key="jd_input",
        height=120,
        placeholder="Paste the complete job description here...",
        label_visibility="collapsed",
    )
    ss.job_description = jd
has_jd = bool(jd.strip())

# =========================================================
# QUICK ACTIONS
# =========================================================

ui.section("Quick actions")
actions = [
    ("ats", "Score resume", ":material/speed:", False),
    ("matcher", "Match job", ":material/compare_arrows:", True),
    ("improver", "Improve resume", ":material/auto_fix_high:", False),
    ("tailor", "Tailor resume", ":material/tune:", True),
    ("advisor", "Career advice", ":material/explore:", True),
]
clicked = None
for column, (agent_id, label, icon, needs_jd) in zip(st.columns(len(actions)), actions):
    with column:
        if st.button(label, key=f"quick_{agent_id}", icon=icon, use_container_width=True, disabled=needs_jd and not has_jd):
            clicked = agent_id
if not has_jd:
    ui.note("Match job, Tailor resume and Career advice unlock once you add a job description.")
if clicked:
    if run_action(clicked):
        ui.note("Done. Open the matching section below to see the result.")

st.write("")

# =========================================================
# HELPERS
# =========================================================


def run_button(agent_id, label, again_label, key):
    agent = AGENT_BY_ID[agent_id]
    has_result = get_result(agent_id) is not None
    disabled = agent["needs_jd"] and not has_jd
    pressed = st.button(
        again_label if has_result else label,
        key=key,
        type="secondary" if has_result else "primary",
        disabled=disabled,
    )
    if disabled:
        ui.note("Add a target job description above to enable this.")
    if pressed:
        run_action(agent_id)


def show_error(agent_id):
    err = ss.errors.get(agent_id)
    if err:
        ui.error_card("Something went wrong", err["message"], err["detail"])


def show_meta(agent_id):
    result = get_result(agent_id)
    if not result:
        return
    if is_stale(agent_id):
        if AGENT_BY_ID[agent_id]["needs_jd"] or agent_id == "improver":
            ui.stale_note("The job description changed since this result was generated. Run it again to update.")
    if prefs.get("run_details"):
        ui.run_note(result, model_for(AGENT_BY_ID[agent_id]), prefs.get("timestamps"))


def document_tab(agent_id, title, filename, empty_title, empty_text, key):
    run_button(agent_id, f"Generate {title.lower()}", f"Regenerate {title.lower()}", f"run_{key}")
    show_error(agent_id)
    result = get_result(agent_id)
    if result is None:
        ui.empty_state(empty_title, empty_text, "DOC")
        return

    show_meta(agent_id)
    text = result["output"]

    if st.toggle("Compare with the extracted resume text", key=f"compare_{key}"):
        left, right = st.columns(2)
        with left:
            ui.section("Extracted resume text", "Exactly what the specialists received.")
            with st.container(height=520, border=True):
                st.text(ss.resume_text)
        with right:
            ui.section(title)
            with st.container(height=520, border=True):
                st.markdown(text)
    else:
        with st.container(border=True):
            st.markdown(text)

    ui.section("Download")
    left, right = st.columns(2)
    with left:
        st.download_button(
            "Download as text (.txt)", data=text, file_name=f"{filename}.txt", mime="text/plain",
            key=f"dl_txt_{key}", icon=":material/description:", use_container_width=True,
        )
    with right:
        try:
            st.download_button(
                "Download as Word (.docx)", data=get_docx(text), file_name=f"{filename}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"dl_docx_{key}", icon=":material/article:", use_container_width=True,
            )
        except Exception as exc:
            ui.error_card("Word download unavailable", "We couldn't build the .docx file. The text download still works.", str(exc))


# =========================================================
# SECTION SWITCHER (styled as tabs; the Overview tiles deep-link here)
# =========================================================

SECTIONS = ["Analyze", "ATS", "Job Match", "Improve", "Tailor", "Career Advisor", "Ask Resume"]
if ss.ws_section not in SECTIONS:
    ss.ws_section = "Analyze"
if "ws_section_w" not in ss:
    ss["ws_section_w"] = ss.ws_section


def _sync_section():
    ss.ws_section = ss["ws_section_w"]


section = st.radio(
    "Section", SECTIONS, key="ws_section_w", horizontal=True,
    label_visibility="collapsed", on_change=_sync_section,
)
ss.ws_section = section
st.write("")

# ---------------- Analyze (dashboard) ----------------
def analyze_section():
    # run before drawing so the ring shows the new score straight away
    if ss.get("an_ats"):
        run_action("ats")

    analysis = ss.analysis
    ats = get_result("ats")
    ats_p = parsing.parse_ats(ats["output"]) if ats else None
    match = get_result("matcher")
    match_p = parsing.parse_match(match["output"]) if match else None

    if analysis is None:
        show_error("analyzer")
        ui.empty_state("No analysis yet", "The Resume Analyzer builds a structured profile of your resume.", "RA")
        if st.button("Run analysis", key="run_analysis", type="primary"):
            run_action("analyzer")
            st.rerun()
        return

    left, right = st.columns([5, 6])

    with left:
        with st.container(border=True):
            if ats_p and ats_p["score"] is not None:
                ui.score_ring(ats_p["score"], ats_p["max"], large=True, suffix="ATS score")
            else:
                ui.empty_ring("Not scored yet")
            ui.html(
                f'<div class="acc-doc-title">{ui.esc(status["file_name"])}</div>'
                '<div class="acc-doc-sub">Your resume has been analyzed</div>'
            )
            if ats is None:
                st.button("Calculate ATS score", key="an_ats", type="primary", icon=":material/speed:", use_container_width=True)
            else:
                ui.note("AI-estimated quality score. It does not guarantee ATS selection.")
            st.download_button(
                "Download report", data=build_report(), file_name="resume_report.md", mime="text/markdown",
                key="dl_report", icon=":material/download:", use_container_width=True,
            )
            st.button("Upload new resume", key="an_upload_new", icon=":material/refresh:", on_click=reset_resume, use_container_width=True)

    with right:
        with st.container(border=True):
            ui.section("Keyword match", "How your resume lines up with the target job.")
            if match_p and match_p["score"] is not None:
                ui.bar_row("Job match", match_p["score"], match_p["max"])
                ui.html(
                    ui.chips([f'{len(match_p["matching_skills"])} matching skills'], "ok")
                    + ui.chips([f'{len(match_p["missing_skills"])} missing skills'], "warn")
                )
            else:
                ui.note("Add a target job description and run Job Match to see this.")
        with st.container(border=True):
            ui.section("Resume feedback", "From the resume analysis.")
            if analysis.strengths or analysis.weaknesses:
                ui.feedback_rows(analysis.strengths, analysis.weaknesses)
            else:
                ui.note("No feedback was returned.")

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            ui.section("Extracted skills", "Only skills explicitly found in the resume.")
            if analysis.technical_skills:
                ui.html(ui.chips(analysis.technical_skills, "accent"))
            if analysis.tools:
                st.markdown("**Tools**")
                ui.html(ui.chips(analysis.tools, "neutral"))
            if analysis.professional_skills:
                st.markdown("**Professional skills**")
                ui.html(ui.chips(analysis.professional_skills, "neutral"))
            if not (analysis.technical_skills or analysis.tools or analysis.professional_skills):
                ui.note("None identified.")
    with right:
        with st.container(border=True):
            if match_p and match_p["missing_skills"]:
                ui.section("Missing / recommended skills", "From Job Match, for your target job.")
                missing = match_p["missing_skills"]
            else:
                ui.section("Missing / recommended skills", "From the resume analysis.")
                missing = analysis.skill_gaps
            ui.html(ui.chips_or_list(missing, "warn", plus=True) or '<div class="acc-note">None identified.</div>')

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            ui.section("Profile")
            ui.html(
                f'<div class="acc-agent-name" style="font-size:1.15rem">{ui.esc(analysis.name)}</div>'
                f'<div class="acc-agent-role" style="margin-bottom:0.5rem">{ui.esc(analysis.current_or_target_role)}</div>'
                + ui.chips([analysis.professional_domain, analysis.experience_level], "accent")
            )
            if analysis.recommended_roles:
                st.markdown("**Recommended roles**")
                ui.html(ui.chips_or_list(analysis.recommended_roles, "neutral"))
    with right:
        with st.container(border=True):
            ui.section("Improvement suggestions")
            ui.html(ui.bullet_list(analysis.resume_improvements) or '<div class="acc-note">None identified.</div>')

    ui.note(
        "The analyzer extracts the fields above. Education, experience and project details "
        "are not extracted separately; they appear in the Improve and Tailor results."
    )


if section == "Analyze":
    analyze_section()

# ---------------- ATS ----------------
if section == "ATS":
    run_button("ats", "Calculate resume score", "Recalculate score", "run_ats")
    show_error("ats")
    result = get_result("ats")
    if result is None:
        ui.empty_state(
            "No score yet",
            "The ATS Scorer estimates resume quality out of 100 across structure, skills, "
            "experience, achievements, contact details and ATS-friendly content.",
            "ATS",
        )
    else:
        show_meta("ats")
        parsed = parsing.parse_ats(result["output"])
        if parsed["score"] is not None:
            left, right = st.columns([1, 2])
            with left:
                with st.container(border=True):
                    ui.score_ring(parsed["score"], parsed["max"], "Estimated resume quality score")
            with right:
                with st.container(border=True):
                    ui.section("Score breakdown")
                    if parsed["subs"]:
                        for sub in parsed["subs"]:
                            ui.bar_row(sub["label"], sub["value"], sub["max"])
                    else:
                        ui.note("No sub-scores were found in the report.")
            if parsed["why"]:
                with st.container(border=True):
                    ui.section("Why this score")
                    ui.html(ui.bullet_list(parsed["why"]))
            if parsed["improvements"]:
                with st.container(border=True):
                    ui.section("Top improvements")
                    ui.html(ui.bullet_list(parsed["improvements"]))
            ui.note("This is an AI-estimated quality score. It does not guarantee ATS selection.")
            with st.expander("View full report"):
                st.markdown(result["output"])
        else:
            ui.note("The score could not be read from the report, so the full report is shown.")
            with st.container(border=True):
                st.markdown(result["output"])

# ---------------- Job Match ----------------
if section == "Job Match":
    run_button("matcher", "Analyze job match", "Re-run job match", "run_match")
    show_error("matcher")
    result = get_result("matcher")
    if result is None:
        ui.empty_state(
            "No job match yet",
            "Add a target job description above, then compare it with your resume.",
            "JM",
        )
    else:
        show_meta("matcher")
        parsed = parsing.parse_match(result["output"])
        if parsed["score"] is not None:
            left, right = st.columns([1, 2])
            with left:
                with st.container(border=True):
                    ui.score_ring(parsed["score"], parsed["max"], "Job match score")
            with right:
                with st.container(border=True):
                    ui.section("Role suitability")
                    if parsed["suitability"]:
                        st.markdown(parsed["suitability"])
                    else:
                        ui.note("No suitability summary was found in the report.")
        else:
            ui.note("The match score could not be read from the report.")

        left, right = st.columns(2)
        with left:
            with st.container(border=True):
                ui.section("Matching skills")
                ui.html(ui.chips_or_list(parsed["matching_skills"], "ok") or '<div class="acc-note">None listed.</div>')
        with right:
            with st.container(border=True):
                ui.section("Missing / recommended skills")
                ui.html(ui.chips_or_list(parsed["missing_skills"], "warn", plus=True) or '<div class="acc-note">None listed.</div>')

        if parsed["matching_experience"]:
            with st.container(border=True):
                ui.section("Matching experience")
                ui.html(ui.bullet_list(parsed["matching_experience"]))
        if parsed["experience_gaps"]:
            with st.container(border=True):
                ui.section("Experience gaps")
                ui.html(ui.bullet_list(parsed["experience_gaps"]))
        if parsed["improvements"]:
            with st.container(border=True):
                ui.section("Recommendations for this job")
                ui.html(ui.bullet_list(parsed["improvements"]))

        with st.expander("View full report"):
            st.markdown(result["output"])

# ---------------- Improve ----------------
if section == "Improve":
    document_tab(
        "improver", "Improved resume", "improved_resume",
        "No improved resume yet",
        "Generate a clearer, more ATS-friendly version of your resume. "
        "A job description is optional. Nothing is invented: skills, projects and numbers stay as they are.",
        "improve",
    )

# ---------------- Tailor ----------------
if section == "Tailor":
    ui.note("Skills the job asks for but your resume doesn't show are not added.")
    document_tab(
        "tailor", "Tailored resume", "job_specific_resume",
        "No tailored resume yet",
        "Add a target job description above, then generate a resume tailored to that role "
        "using only what is already in your resume.",
        "tailor",
    )

# ---------------- Career Advisor ----------------
if section == "Career Advisor":
    run_button("advisor", "Analyze job suitability", "Re-run analysis", "run_advisor")
    show_error("advisor")
    result = get_result("advisor")
    if result is None:
        ui.empty_state(
            "No recommendation yet",
            "Add a target job description above to find out whether you should apply.",
            "CA",
        )
    else:
        show_meta("advisor")
        parsed = parsing.parse_advisor(result["output"])
        if parsed["decision"]:
            kind, mark, label = {
                "APPLY": ("ok", "\u2713", "Apply"),
                "MAYBE": ("warn", "!", "Maybe"),
                "NOT RECOMMENDED": ("err", "\u2715", "Not recommended"),
            }[parsed["decision"]]
            with st.container(border=True):
                level = f" {ui.pill(parsed['level'] + ' match', 'idle')}" if parsed["level"] else ""
                ui.html(
                    f'<div class="acc-decision acc-decision-{kind}"><span aria-hidden="true">{mark}</span>{label}</div>{level}'
                )
                if parsed["recommendation"]:
                    st.markdown(parsed["recommendation"])
            if parsed["why"]:
                with st.container(border=True):
                    ui.section("Why")
                    ui.html(ui.bullet_list(parsed["why"]))
            left, right = st.columns(2)
            with left:
                with st.container(border=True):
                    ui.section("Matching skills")
                    ui.html(ui.chips_or_list(parsed["matching_skills"], "ok") or '<div class="acc-note">None listed.</div>')
            with right:
                with st.container(border=True):
                    ui.section("Missing important skills")
                    ui.html(ui.chips_or_list(parsed["missing_skills"], "warn", plus=True) or '<div class="acc-note">None listed.</div>')
            if parsed["transferable"]:
                with st.container(border=True):
                    ui.section("Transferable skills")
                    ui.html(ui.chips_or_list(parsed["transferable"], "accent"))
            if parsed["concerns"]:
                with st.container(border=True):
                    ui.section("Concerns")
                    ui.html(ui.bullet_list(parsed["concerns"]))
            ui.note("This recommendation is based on resume and job matching. It does not guarantee job selection.")
            with st.expander("View full report"):
                st.markdown(result["output"])
        else:
            ui.note("The decision could not be read from the report, so the full report is shown.")
            with st.container(border=True):
                st.markdown(result["output"])

# ---------------- Ask Resume ----------------
if section == "Ask Resume":
    head, clear = st.columns([4, 1])
    with head:
        ui.note(
            "Each question is answered on its own, using the resume passages closest to it. "
            "Earlier questions are not remembered."
        )
    with clear:
        if ss.qa_messages and st.button("Clear chat", key="clear_chat", icon=":material/delete:"):
            ss.qa_messages = []
            st.rerun()

    def ask(question):
        ss["qa_pending"] = question

    if not ss.qa_messages:
        starters = ["What are my technical skills?", "Summarize my experience.", "Which projects are on my resume?"]
        for column, text in zip(st.columns(len(starters)), starters):
            with column:
                st.button(text, key=f"starter_{text}", on_click=ask, args=(text,), use_container_width=True)

    for message in ss.qa_messages:
        with st.chat_message(message["role"]):
            if message.get("error"):
                ui.error_card("Something went wrong", message["content"], message.get("detail"))
            else:
                st.markdown(message["content"])
            if prefs.get("timestamps"):
                ui.note(ui.clock(message["ts"]) + (f' \u00b7 {message["duration"]:.1f}s' if message.get("duration") else ""))
            if message.get("sources"):
                with st.expander(f"Sources used ({len(message['sources'])})"):
                    for i, chunk in enumerate(message["sources"], 1):
                        st.caption(f"Resume chunk {i}")
                        st.text(chunk)

    typed = st.chat_input("Ask a question about your resume")
    question = typed or ss.pop("qa_pending", None)

    if question:
        with st.chat_message("user"):
            st.markdown(question)
        ss.qa_messages.append({"role": "user", "content": question, "ts": time.time()})

        with st.chat_message("assistant"):
            with st.spinner("Searching your resume and writing an answer..."):
                try:
                    from rag.rag_pipeline import ask_pdf, search_document

                    answer, duration = timed_call("qa", ask_pdf, question, ss.index, ss.chunks)
                    sources = []
                    try:
                        for chunk in search_document(question, ss.index, ss.chunks):
                            if chunk not in sources:
                                sources.append(chunk)
                    except Exception:
                        sources = []
                    reply = {"role": "assistant", "content": answer, "ts": time.time(), "duration": duration, "sources": sources}
                except Exception as exc:
                    reply = {
                        "role": "assistant",
                        "error": True,
                        "content": "We couldn't answer this question. Try again in a moment.",
                        "detail": redact(f"{type(exc).__name__}: {exc}"),
                        "ts": time.time(),
                    }
            if reply.get("error"):
                ui.error_card("Something went wrong", reply["content"], reply["detail"])
            else:
                st.markdown(reply["content"])
                if reply["sources"]:
                    with st.expander(f"Sources used ({len(reply['sources'])})"):
                        for i, chunk in enumerate(reply["sources"], 1):
                            st.caption(f"Resume chunk {i}")
                            st.text(chunk)
        ss.qa_messages.append(reply)

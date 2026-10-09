"""Agents: the seven real specialists, then the legacy supervisor group."""

import streamlit as st

from core.registry import AGENTS, LEGACY_AGENTS, RAG, model_for, temperature_for
from core.runner import agent_stats
from ui import components as ui
from ui.theme import page_title

ss = st.session_state

page_title(
    "Agents",
    "Seven AI specialists power the resume features. Each one does a single job and runs when you ask for it.",
)

# ---------------- how it fits together ----------------
with st.container(border=True):
    ui.section("How the specialists work together")
    ui.stages([
        ("Resume PDF", "You upload one PDF."),
        ("Shared context", f'Split into chunks, embedded with {RAG["embedding_model"]}, indexed in FAISS.'),
        ("Specialists", "You choose which one to run. Each gets the resume text."),
        ("Results", "Scores, reports, rewritten resumes and answers."),
    ])
    ui.note("There is no automatic orchestrator in this app. Each specialist runs only when you trigger it.")

st.write("")
ui.section("Resume specialists")

# ---------------- specialist cards ----------------
for row_start in range(0, len(AGENTS), 2):
    columns = st.columns(2)
    for column, agent in zip(columns, AGENTS[row_start:row_start + 2]):
        stats = agent_stats(agent["id"])
        if stats["total"] == 0:
            state = ui.pill("Not run this session", "idle")
        elif stats["last"]["ok"]:
            state = ui.pill("Last run succeeded", "ok")
        else:
            state = ui.pill("Last run failed", "err")

        with column:
            with st.container(border=True):
                ui.html(
                    f'<div class="acc-agent-head"><div class="acc-agent-id">'
                    f'<div class="acc-avatar" aria-hidden="true">{ui.esc(agent["initials"])}</div>'
                    f'<div class="acc-agent-name">{ui.esc(agent["name"])}</div></div><div>{state}</div></div>'
                    f'<div class="acc-agent-role">{ui.esc(agent["role"])}</div>'
                    + ui.chips([model_for(agent)], "accent")
                )
                if stats["total"]:
                    rate = round(stats["ok"] / stats["total"] * 100)
                    ui.html(
                        f'<div class="acc-stats"><span><b>{stats["total"]}</b> runs</span>'
                        f'<span><b>{rate}%</b> succeeded</span>'
                        f'<span><b>{stats["avg"]:.1f}s</b> average</span>'
                        f'<span>last run <b>{ui.clock(stats["last"]["ts"])}</b></span></div>'
                    )
                else:
                    ui.note("No runs yet in this session.")
                with st.expander("Technical details"):
                    ui.html(
                        '<div class="acc-note">'
                        f'Function: {ui.esc(agent["function"])} in {ui.esc(agent["file"])}<br>'
                        f'Model: {ui.esc(model_for(agent))}<br>'
                        f'Temperature: {ui.esc(temperature_for(agent))}<br>'
                        f'Input: {ui.esc(agent["input"])}<br>'
                        f'Output: {ui.esc(agent["output"])}<br>'
                        "External tools: none</div>"
                    )
                    if agent["id"] == "qa":
                        ui.html(
                            '<div class="acc-note">'
                            f'Retrieval: {RAG["index_type"]}, top {RAG["top_k"]} chunks '
                            f'({RAG["chunk_size"]} characters, {RAG["chunk_overlap"]} overlap)</div>'
                        )

# ---------------- legacy ----------------
st.write("")
st.write("")
with st.container(border=True):
    ui.section(
        "Legacy / Experimental Supervisor Agents",
        "A keyword-based supervisor routes to these agents. It is not connected to this app's interface "
        "and is not part of the resume workflow.",
    )
    rows = []
    for agent in LEGACY_AGENTS:
        rows.append(
            f'<div class="acc-row"><div><div class="acc-row-main">{ui.esc(agent["name"])}</div>'
            f'<div class="acc-row-meta">{ui.esc(agent["file"])} &middot; {ui.esc(agent["note"])}</div></div>'
            f'<div>{ui.pill(agent["status"], agent["kind"])}</div></div>'
        )
    ui.html("".join(rows))

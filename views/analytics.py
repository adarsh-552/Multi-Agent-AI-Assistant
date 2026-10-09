"""Current Session Analytics. Built only from recorded specialist runs."""

import pandas as pd
import streamlit as st

from core.runner import agent_stats
from ui import components as ui
from ui.theme import page_title

ss = st.session_state

page_title(
    "Analytics",
    "Current session analytics. These numbers come from the specialist runs made since this session "
    "started and reset when it ends.",
)

stats = agent_stats()

if stats["total"] == 0:
    ui.empty_state(
        "No runs to analyze yet",
        "Run a specialist in the Resume Workspace and its timing and outcome will appear here.",
        "0",
    )
    st.page_link("views/workspace.py", label="Open Resume Workspace", icon=":material/description:")
    st.stop()

runs = pd.DataFrame(ss.runs)
questions = int((runs["agent_id"] == "qa").sum())
rate = round(stats["ok"] / stats["total"] * 100)

# ---------------- KPI cards ----------------
c1, c2, c3, c4 = st.columns(4)
with c1:
    ui.kpi("Specialist runs", stats["total"], "Model calls made this session")
with c2:
    ui.kpi("Success rate", f"{rate}%", f'{stats["ok"]} succeeded, {stats["failed"]} failed')
with c3:
    ui.kpi("Average response time", f'{stats["avg"]:.1f}s', "From request to response")
with c4:
    ui.kpi("Questions asked", questions, "In Ask Resume")

st.write("")

# ---------------- main chart + success ring ----------------
left, right = st.columns([2, 1])
with left:
    with st.container(border=True):
        ui.section("Runs by specialist", "How many times each specialist ran.")
        st.bar_chart(runs.groupby("agent").size().rename("Runs"), color="#6C47FF")
with right:
    with st.container(border=True):
        ui.section("Success rate")
        ui.score_ring(stats["ok"], stats["total"], f'{stats["ok"]} of {stats["total"]} runs succeeded', large=True, suffix="runs ok")

left, right = st.columns(2)
with left:
    with st.container(border=True):
        ui.section("Response time per run", "Seconds, in the order the runs happened.")
        st.bar_chart(runs[["n", "duration"]].rename(columns={"n": "Run", "duration": "Seconds"}), x="Run", y="Seconds", color="#6C47FF")
with right:
    with st.container(border=True):
        ui.section("Average response time by specialist", "Seconds.")
        st.bar_chart(runs.groupby("agent")["duration"].mean().rename("Seconds"), color="#6C47FF")

with st.container(border=True):
    ui.section("Not tracked")
    ui.note(
        "Token usage and cost are not shown. The specialists return only the answer text, "
        "so the app never receives token counts. Nothing here is estimated."
    )

with st.expander("Run log"):
    log = runs.assign(
        Time=runs["ts"].map(ui.clock),
        Status=runs["ok"].map({True: "Succeeded", False: "Failed"}),
        Seconds=runs["duration"].round(2),
    )[["n", "Time", "agent", "model", "Status", "Seconds", "error"]].rename(
        columns={"n": "Run", "agent": "Specialist", "model": "Model", "error": "Error"}
    )
    st.dataframe(log, hide_index=True, use_container_width=True)

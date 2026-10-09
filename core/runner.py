"""Run tracking. Every number in Analytics comes from these records."""

import os
import re
import time

import streamlit as st

from core.registry import AGENT_BY_ID, model_for


def redact(text):
    """Remove API keys from anything shown in the UI."""
    text = str(text)
    for secret in (os.getenv("GROQ_API_KEY"), os.getenv("TAVILY_API_KEY")):
        if secret:
            text = text.replace(secret, "[redacted]")
    return re.sub(r"(gsk_|tvly-)[A-Za-z0-9_\-]{8,}", "[redacted]", text)


def record_run(agent_id, ok, duration, error=None):
    agent = AGENT_BY_ID[agent_id]
    runs = st.session_state.setdefault("runs", [])
    runs.append({
        "n": len(runs) + 1,
        "agent_id": agent_id,
        "agent": agent["name"],
        "model": model_for(agent),
        "ok": ok,
        "duration": duration,
        "error": redact(error) if error else None,
        "ts": time.time(),
    })


def timed_call(agent_id, fn, *args, **kwargs):
    """Call fn, record the run, return (output, seconds). Re-raises failures."""
    start = time.perf_counter()
    try:
        output = fn(*args, **kwargs)
    except Exception as exc:
        record_run(agent_id, False, time.perf_counter() - start, f"{type(exc).__name__}: {exc}")
        raise
    duration = time.perf_counter() - start
    record_run(agent_id, True, duration)
    return output, duration


def agent_stats(agent_id=None):
    runs = [r for r in st.session_state.get("runs", []) if agent_id in (None, r["agent_id"])]
    ok = [r for r in runs if r["ok"]]
    return {
        "total": len(runs),
        "ok": len(ok),
        "failed": len(runs) - len(ok),
        "avg": (sum(r["duration"] for r in runs) / len(runs)) if runs else None,
        "last": runs[-1] if runs else None,
    }

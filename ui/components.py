"""Reusable visual components. Everything shown comes from real values passed in."""

import html as _html
import time

import streamlit as st

from core.runner import redact
from ui.theme import status_pill

ACCENT = "#6C47FF"


def esc(value):
    return _html.escape(str(value), quote=True)


def html(markup):
    """Render HTML, collapsing indentation so Markdown never treats it as code."""
    flat = " ".join(line.strip() for line in markup.splitlines() if line.strip())
    st.markdown(flat, unsafe_allow_html=True)


def section(title, sub=None):
    markup = f'<div class="acc-section">{esc(title)}</div>'
    if sub:
        markup += f'<div class="acc-section-sub">{esc(sub)}</div>'
    html(markup)


def note(text):
    html(f'<div class="acc-note">{esc(text)}</div>')


def pill(label, kind="idle"):
    return status_pill(esc(label), kind)


def chips(items, kind="accent", plus=False):
    if not items:
        return ""
    cls = "acc-chip" if kind == "accent" else f"acc-chip acc-chip-{kind}"
    if plus:
        cls += " acc-chip-plus"
    body = "".join(f'<span class="{cls}">{esc(item)}</span>' for item in items)
    return f'<div class="acc-chips">{body}</div>'


def bullet_list(items):
    if not items:
        return ""
    return '<ul class="acc-list">' + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"


def chips_or_list(items, kind="accent", plus=False):
    """Short items read best as badges; long sentences as a list."""
    if items and all(len(i) <= 42 for i in items):
        return chips(items, kind, plus)
    return bullet_list(items)


def kpi(label, value, hint=None):
    hint_html = f'<div class="acc-kpi-hint">{esc(hint)}</div>' if hint else ""
    html(
        f'<div class="acc-kpi"><div class="acc-kpi-label">{esc(label)}</div>'
        f'<div class="acc-kpi-value">{esc(value)}</div>{hint_html}</div>'
    )


def kpi_with_pill(label, pill_html, hint=None):
    hint_html = f'<div class="acc-kpi-hint">{esc(hint)}</div>' if hint else ""
    html(
        f'<div class="acc-kpi"><div class="acc-kpi-label">{esc(label)}</div>'
        f'<div style="margin-top:0.2rem">{pill_html}</div>{hint_html}</div>'
    )


def score_ring(value, maximum, caption=None, large=False, suffix=None):
    pct = max(0.0, min(100.0, value / maximum * 100.0))
    cap = f'<div class="acc-ring-caption">{esc(caption)}</div>' if caption else ""
    size = " acc-ring-lg" if large else ""
    tail = esc(suffix) if suffix else f"out of {maximum:g}"
    html(
        f'<div class="acc-ring-wrap"><div class="acc-ring{size}" role="img" aria-label="Score {value:g} out of {maximum:g}" '
        f'style="background: conic-gradient({ACCENT} {pct:.1f}%, #E9ECF3 0);">'
        f'<div class="acc-ring-inner"><div class="acc-ring-val">{value:g}</div>'
        f'<div class="acc-ring-max">{tail}</div></div></div></div>{cap}'
    )


def bar_row(label, value, maximum):
    pct = max(0.0, min(100.0, value / maximum * 100.0))
    html(
        f'<div class="acc-bar-row"><div class="acc-bar-top"><span>{esc(label)}</span>'
        f'<span><b>{value:g}</b> / {maximum:g}</span></div>'
        f'<div class="acc-bar"><div style="width:{pct:.1f}%"></div></div></div>'
    )


def workflow(steps):
    """steps: list of (label, done). The first step not done is marked as next."""
    next_index = next((i for i, (_, done) in enumerate(steps) if not done), None)
    parts = []
    for i, (label, done) in enumerate(steps):
        if done:
            cls, mark = "acc-step acc-step-done", "\u2713"
        elif i == next_index:
            cls, mark = "acc-step acc-step-next", "\u25cf"
        else:
            cls, mark = "acc-step", "\u25cb"
        parts.append(f'<span class="{cls}"><span aria-hidden="true">{mark}</span>{esc(label)}</span>')
        if i < len(steps) - 1:
            parts.append('<span class="acc-arrow" aria-hidden="true">\u2192</span>')
    html('<div class="acc-flow">' + "".join(parts) + "</div>")


def stages(items):
    """items: list of (title, text) shown as equal boxes with arrows between."""
    parts = []
    for i, (title, text) in enumerate(items):
        parts.append(f'<div class="acc-stage"><b>{esc(title)}</b><span>{esc(text)}</span></div>')
        if i < len(items) - 1:
            parts.append('<span class="acc-arrow" aria-hidden="true">\u2192</span>')
    html('<div class="acc-flow">' + "".join(parts) + "</div>")


def empty_state(title, text, mark="AI"):
    html(
        f'<div class="acc-empty"><div class="acc-empty-icon" aria-hidden="true">{esc(mark)}</div>'
        f'<div class="acc-empty-title">{esc(title)}</div><div class="acc-empty-text">{esc(text)}</div></div>'
    )


def error_card(title, message, detail=None):
    html(
        f'<div class="acc-err" role="alert"><div class="acc-err-title">\u26a0 {esc(title)}</div>'
        f'<div class="acc-err-text">{esc(message)}</div></div>'
    )
    if detail:
        with st.expander("View technical details"):
            st.code(redact(detail), language=None)


def stale_note(text):
    html(f'<div class="acc-stale">{esc(text)}</div>')


def file_chip(name, meta):
    html(
        f'<div class="acc-file"><div class="acc-file-icon" aria-hidden="true">PDF</div>'
        f'<div><div class="acc-file-name">{esc(name)}</div><div class="acc-file-meta">{esc(meta)}</div></div></div>'
    )


def human_size(num_bytes):
    if not num_bytes:
        return None
    for unit in ("B", "KB", "MB"):
        if num_bytes < 1024 or unit == "MB":
            return f"{num_bytes:.0f} {unit}" if unit == "B" else f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024


def clock(ts):
    return time.strftime("%H:%M:%S", time.localtime(ts))


def activity_rows(runs, show_time=True):
    rows = []
    for r in runs:
        status = pill("Succeeded", "ok") if r["ok"] else pill("Failed", "err")
        when = f' &middot; {clock(r["ts"])}' if show_time else ""
        rows.append(
            f'<div class="acc-row"><div><div class="acc-row-main">{esc(r["agent"])}</div>'
            f'<div class="acc-row-meta">{esc(r["model"])}{when}</div></div>'
            f'<div style="text-align:right">{status}<div class="acc-row-meta">{r["duration"]:.1f}s</div></div></div>'
        )
    html("".join(rows))


def run_note(result, model, show_timestamp=True):
    """Small line under a result: which specialist/model ran, how long, when."""
    when = f" at {clock(result['ts'])}" if show_timestamp else ""
    note(f"Generated by {model} in {result['duration']:.1f}s{when}")


def empty_ring(caption, large=True):
    size = " acc-ring-lg" if large else ""
    html(
        f'<div class="acc-ring-wrap"><div class="acc-ring acc-ring-empty{size}" role="img" aria-label="No score yet">'
        f'<div class="acc-ring-inner"><div class="acc-ring-val">&ndash;</div>'
        f'<div class="acc-ring-max">{esc(caption)}</div></div></div></div>'
    )


def feedback_rows(good, warn, limit=3):
    """Green check rows for strengths, amber rows for things to improve."""
    rows = [f'<div class="acc-fb acc-fb-ok"><b aria-hidden="true">\u2713</b><span>{esc(t)}</span></div>' for t in good[:limit]]
    rows += [f'<div class="acc-fb acc-fb-warn"><b aria-hidden="true">\u25b2</b><span>{esc(t)}</span></div>' for t in warn[:limit]]
    html("".join(rows))


_ICONS = {
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>',
    "score": '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    "zap": '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "target": '<circle cx="12" cy="12" r="10"/><line x1="22" y1="12" x2="18" y2="12"/><line x1="6" y1="12" x2="2" y2="12"/><line x1="12" y1="6" x2="12" y2="2"/><line x1="12" y1="22" x2="12" y2="18"/>',
    "chat": '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>',
    "bars": '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
}


def icon(name, size=18):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        f'{_ICONS[name]}</svg>'
    )


def tile(key, title, text, color, icon_name):
    """A gradient card that is itself the button. Returns True when clicked.

    The visible card is HTML; a transparent button is stretched over it (see the
    st-key-tile_ rules in theme.py). If that CSS ever fails, the button simply
    shows under the card and still works.
    """
    with st.container(key=f"tile_{key}"):
        html(
            f'<div class="acc-tile acc-tile-{color}"><div class="acc-tile-icon">{icon(icon_name, 18)}</div>'
            f'<div class="acc-tile-title">{esc(title)}</div><div class="acc-tile-text">{esc(text)}</div></div>'
        )
        return st.button(f"Open {title}", key=f"tilebtn_{key}")

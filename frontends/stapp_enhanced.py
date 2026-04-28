#!/usr/bin/env python3
"""GenericAgent Web UI - enhanced solo mode."""

import os
import queue
import re
import sys
import threading
import time

import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from agentmain import GeneraticAgent
import chatapp_common  # noqa: F401  Activate /continue patch on GeneraticAgent.
from continue_cmd import (
    extract_ui_messages,
    handle_frontend_command,
    list_sessions,
    reset_conversation,
)
from frontends.chatapp_common import build_done_text
from frontends.themes import ALL_THEMES, DEFAULT_THEME, get_theme_colors, get_theme_css

THEME_LABELS = {theme.name: theme.label for theme in ALL_THEMES}


@st.cache_resource
def init_agent():
    agent = GeneraticAgent()
    if getattr(agent, "llmclient", None) is not None:
        threading.Thread(target=agent.run, daemon=True).start()
    return agent


def init_state():
    st.session_state.setdefault("theme_name", DEFAULT_THEME)
    st.session_state.setdefault(
        "messages",
        [
            {
                "role": "assistant",
                "content": "GenericAgent solo mode is ready. Use /new to reset or /continue to restore a prior session.",
            }
        ],
    )
    st.session_state.setdefault("last_reply_time", int(time.time()))


def current_model_label(agent):
    if getattr(agent, "llmclient", None) is None:
        return "No LLM configured"
    try:
        return agent.get_llm_name()
    except Exception:
        return "LLM ready"


def reset_ui_state():
    st.session_state.last_reply_time = int(time.time())


def handle_command(agent, prompt):
    cmd = (prompt or "").strip()
    if cmd == "/new":
        st.session_state.messages = [{"role": "assistant", "content": reset_conversation(agent)}]
        reset_ui_state()
        st.rerun()

    if not cmd.startswith("/continue"):
        return False

    matched = re.match(r"/continue\s+(\d+)\s*$", cmd)
    sessions = list_sessions(exclude_pid=os.getpid()) if matched else []
    target_path = None
    if matched:
        idx = int(matched.group(1)) - 1
        if 0 <= idx < len(sessions):
            target_path = sessions[idx][0]

    result = handle_frontend_command(agent, cmd)
    restored = extract_ui_messages(target_path) if target_path and result.startswith("✅") else None

    if restored:
        st.session_state.messages = restored + [{"role": "assistant", "content": result}]
    else:
        st.session_state.messages.append({"role": "assistant", "content": result})

    reset_ui_state()
    st.rerun()


def agent_backend_stream(agent, prompt):
    display_queue = agent.put_task(prompt, source="user")
    response = ""
    while True:
        try:
            item = display_queue.get(timeout=1)
        except queue.Empty:
            yield response
            continue

        if "next" in item:
            response = item["next"]
            yield response

        if "done" in item:
            yield item["done"]
            break


def normalize_assistant_text(raw_text, streaming=False):
    text = build_done_text(raw_text) if raw_text else ""
    text = re.sub(r"(?m)^\**LLM Running \(Turn \d+\) \.\.\.\**\s*$", "", text)
    text = re.sub(r"(?m)^\[Info\] Final response to user\.\s*$", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if text:
        return text
    return "Working..." if streaming else "..."


def render_header(agent):
    theme_name = st.session_state.theme_name
    st.markdown(get_theme_css(theme_name), unsafe_allow_html=True)

    st.markdown(
        '<div class="ga-topbar"><div class="ga-topbar-title">GenericAgent Solo</div><div class="ga-tool-tag">Enhanced UI</div></div>',
        unsafe_allow_html=True,
    )

    action_col, reset_col, info_col, theme_col = st.columns([0.8, 1.0, 2.4, 1.2])
    with action_col:
        if st.button("Stop", use_container_width=True, disabled=not getattr(agent, "is_running", False)):
            agent.abort()
            st.toast("Stop signal sent")
    with reset_col:
        if st.button("New Chat", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": reset_conversation(agent)}]
            reset_ui_state()
            st.rerun()
    with info_col:
        status = "Running" if getattr(agent, "is_running", False) else "Idle"
        st.markdown(
            f'<div class="ga-tool-tag">Model: {current_model_label(agent)} | Status: {status}</div>',
            unsafe_allow_html=True,
        )
    with theme_col:
        st.selectbox(
            "Theme",
            options=[theme.name for theme in ALL_THEMES],
            format_func=lambda name: THEME_LABELS.get(name, name),
            key="theme_name",
            label_visibility="collapsed",
        )


def render_history():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def main():
    st.set_page_config(
        page_title="GenericAgent",
        page_icon="●",
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={"Get Help": None, "Report a bug": None, "About": None},
    )
    init_state()
    agent = init_agent()

    render_header(agent)

    if getattr(agent, "llmclient", None) is None:
        st.error("No LLM interface is configured. Set up mykey.py before using the enhanced UI.")
        return

    render_history()

    if prompt := st.chat_input("Ask GenericAgent anything"):
        handle_command(agent, prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            final_raw = ""
            for raw in agent_backend_stream(agent, prompt):
                final_raw = raw
                live_text = normalize_assistant_text(raw, streaming=True)
                placeholder.markdown(live_text + (" ▌" if getattr(agent, "is_running", False) else ""))
            final_text = normalize_assistant_text(final_raw, streaming=False)
            placeholder.markdown(final_text)

        st.session_state.messages.append({"role": "assistant", "content": final_text})
        reset_ui_state()

    st.markdown(
        f'<div id="last-reply-time" style="display:none">{st.session_state.get("last_reply_time", int(time.time()))}</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

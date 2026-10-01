"""
Streamlit UI for the Human-in-the-Loop Agent.
Main application entry point.
"""

import uuid
import streamlit as st
import os
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from config import is_smtp_configured
from utils import get_reply_text
from graph import build_graph

# =================================================================
# PAGE SETUP
# =================================================================

st.set_page_config(page_title="Human-in-the-Loop Agent", page_icon="🧑‍⚖️")
st.title("🧑‍⚖️ Human-in-the-Loop Agent")
st.caption(
    "Claude pauses for your approval before risky actions — powered by LangGraph interrupt/resume"
)


if not is_smtp_configured():
    st.info(
        "SMTP credentials are not configured, so send_email will report a warning instead of "
        "actually sending mail. Set SMTP_USERNAME / SMTP_PASSWORD (and optionally SMTP_HOST, "
        "SMTP_PORT, SMTP_FROM) in a .env file to enable real sending.",
        icon="✉️",
    )


# =================================================================
# SESSION STATE INITIALIZATION
# =================================================================

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(
        uuid.uuid4()
    )  # identifies this conversation to the checkpointer
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pending_action" not in st.session_state:
    st.session_state.pending_action = (
        None  # holds the interrupted tool call awaiting a decision
    )


# Get or build the graph (cached across reruns)
@st.cache_resource
def get_graph():
    """
    Build and cache the graph. This is cached so it survives Streamlit reruns.

    Streamlit reruns the whole script top-to-bottom on every click —
    including Approve/Reject. If the graph were created fresh each time,
    every rerun would wipe the paused conversation right before we try to
    resume it. Caching keeps the SAME graph + checkpointer alive across
    reruns, which is what makes pause/resume possible.
    """
    return build_graph()


graph = get_graph()
graph_config = {"configurable": {"thread_id": st.session_state.thread_id}}


# =================================================================
# HELPER FUNCTIONS
# =================================================================


def run_graph(graph_input):
    """
    Runs (or resumes) the graph. Either it:
      a) hits interrupt() again -> we store the pending action to show the user, or
      b) finishes normally -> we show Claude's final reply.
    """
    result = graph.invoke(graph_input, graph_config)

    if "__interrupt__" in result:
        st.session_state.pending_action = result["__interrupt__"][0].value
    else:
        reply = get_reply_text(result["messages"][-1].content)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.session_state.pending_action = None


def handle_decision(approved: bool):
    """Resumes the paused graph with the user's Approve/Reject decision."""
    with st.spinner("Resuming..."):
        run_graph(Command(resume={"approved": approved}))
    st.rerun()


# =================================================================
# UI RENDERING
# =================================================================

# Replay the visible chat so far
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Either show a pending approval, OR accept a new message
if st.session_state.pending_action:

    action = st.session_state.pending_action
    st.warning(f"⚠️ Claude wants to run **{action['action']}**")
    st.json(action["args"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Approve", type="primary", use_container_width=True):
            handle_decision(approved=True)
    with col2:
        if st.button("❌ Reject", use_container_width=True):
            handle_decision(approved=False)

else:
    user_input = st.chat_input("Try: 'send an email to my boss saying I'll be late'")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.spinner("Thinking..."):
            run_graph({"messages": [HumanMessage(content=user_input)]})

        st.rerun()

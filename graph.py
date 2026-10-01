"""
Graph building for the Human-in-the-Loop Agent.
Handles the LangGraph state machine setup.
"""
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from models import MessagesState
from nodes import agent_node, approval_node, route_after_agent


def build_graph():
    """
    Build the LangGraph state machine.
    
    IMPORTANT: this must be cached with @st.cache_resource in the app.
    
    Streamlit reruns the whole script top-to-bottom on every click —
    including Approve/Reject. If MemorySaver() were created fresh each
    time, every rerun would wipe the paused conversation right before
    we try to resume it. Caching keeps the SAME graph + checkpointer
    alive across reruns, which is what makes pause/resume possible.
    """
    builder = StateGraph(MessagesState)
    builder.add_node("agent", agent_node)
    builder.add_node("approval", approval_node)
    builder.add_edge(START, "agent")
    builder.add_conditional_edges(
        "agent", route_after_agent, {"approval": "approval", END: END}
    )
    builder.add_edge("approval", "agent")

    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)

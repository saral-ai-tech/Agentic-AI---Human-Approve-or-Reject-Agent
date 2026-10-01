"""
Graph nodes for the Human-in-the-Loop Agent.
Defines the agent logic and approval logic.
"""
from langchain_core.messages import ToolMessage
from langgraph.types import interrupt, Command
from langgraph.graph import END

from llm import llm
from prompts import SYSTEM_PROMPT
from tools import TOOLS_BY_NAME
from models import MessagesState


def agent_node(state: MessagesState): # 
    """Claude looks at the conversation and either replies, or calls a tool."""
    response = llm.invoke(
        [{"role": "system", "content": SYSTEM_PROMPT}] + state["messages"]
    )
    return {"messages": [response]}


def route_after_agent(state: MessagesState):
    """After the agent replies: did it call a tool? If so, go get approval first."""
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "approval"
    return END


def approval_node(state: MessagesState):
    """
    This node is only reached when Claude wants to call a risky tool.
    interrupt() freezes the graph HERE and sends `payload` to the app.
    Nothing below that line runs until the app resumes with a decision.
    """
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[0]  # demo keeps it to one action at a time

    decision = interrupt(
        {
            "action": tool_call["name"],
            "args": tool_call["args"],
        }
    )

    if decision.get("approved"):
        result = TOOLS_BY_NAME[tool_call["name"]].invoke(tool_call["args"])
        outcome = f"✅ Approved. {result}"
    else:
        outcome = "❌ Rejected by user. This action was not performed."

    return {"messages": [ToolMessage(content=outcome, tool_call_id=tool_call["id"])]}



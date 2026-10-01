"""
LLM initialization for the Human-in-the-Loop Agent.
"""
from langchain_anthropic import ChatAnthropic

from config import MODEL
from tools import ALL_TOOLS

# Initialize LLM with tools bound
llm = ChatAnthropic(model=MODEL, max_tokens=1000).bind_tools(ALL_TOOLS)

__all__ = ["llm"]

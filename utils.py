"""
Utility functions for the Human-in-the-Loop Agent.
"""


def get_reply_text(content) -> str:
    """
    Claude's reply can come back as a plain string, OR as a list of
    content blocks (this happens after tool calls). This just always
    gives us plain text back, whichever form it is.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return str(content)

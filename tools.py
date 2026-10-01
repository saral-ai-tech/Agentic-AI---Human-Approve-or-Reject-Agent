"""
Tool definitions for the Human-in-the-Loop Agent.
Includes risky tools that require human approval.
"""
import smtplib
from email.mime.text import MIMEText
from langchain_core.tools import tool

from config import SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM


# =================================================================
# RISKY TOOLS (these need human approval before running)
# =================================================================


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email. This is a sensitive action requiring approval."""

    if not SMTP_USERNAME or not SMTP_PASSWORD:
        return "⚠️ Email NOT sent — SMTP_USERNAME/SMTP_PASSWORD " "are not configured."

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:

            server.login(SMTP_USERNAME, SMTP_PASSWORD)

            server.sendmail(SMTP_FROM, [to], msg.as_string())

        return f"📧 Email sent to {to} — " f"subject: '{subject}'"

    except Exception as e:
        return f"❌ Failed to send email to {to}: {e}"


@tool
def delete_file(filename: str) -> str:
    """Delete a file. This is a sensitive action requiring approval."""
    return f"🗑️ File deleted: {filename}"


@tool
def make_purchase(item: str, amount: float) -> str:
    """Make a purchase. This is a sensitive action requiring approval."""
    return f"💳 Purchased '{item}' for ${amount:.2f}"


# Tool registry
ALL_TOOLS = [send_email, delete_file, make_purchase]
TOOLS_BY_NAME = {t.name: t for t in ALL_TOOLS}

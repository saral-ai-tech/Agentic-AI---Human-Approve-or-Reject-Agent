"""
Configuration module for the Human-in-the-Loop Agent.
Handles environment variables and constants.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Model configuration
MODEL = "claude-haiku-4-5-20251001"

# SMTP configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USERNAME)

# Validation
def is_smtp_configured() -> bool:
    """Check if SMTP credentials are configured."""
    return bool(SMTP_USERNAME and SMTP_PASSWORD)

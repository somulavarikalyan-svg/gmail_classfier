"""
Configuration settings for the Gmail Cleanup Agent.
Defines constants, file paths, safety rules, and thresholds.
"""
import os
from typing import List, Final

# --- Paths ---
BASE_DIR: Final[str] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR: Final[str] = os.path.join(BASE_DIR, 'data')
LOGS_DIR: Final[str] = os.path.join(BASE_DIR, 'logs')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

CREDENTIALS_FILE: Final[str] = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_FILE: Final[str] = os.path.join(BASE_DIR, 'token.json')
SENDERS_FILE: Final[str] = os.path.join(DATA_DIR, 'senders.json')
LOG_FILE: Final[str] = os.path.join(LOGS_DIR, 'agent.log')

# --- Gmail Settings ---
SCOPES: Final[List[str]] = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.settings.basic'
]

# --- LLM Settings ---
OLLAMA_MODEL: str = "llama3"
OLLAMA_URL: str = "http://localhost:11434/api/generate"

# --- Thresholds ---
# Confidence score required to archive an email automatically
CONFIDENCE_ARCHIVE: float = 0.80

# Confidence score required to label an email for review (but keep in inbox)
CONFIDENCE_REVIEW: float = 0.55

# Number of times a sender must be classified as marketing to be "trusted"
TRUSTED_SENDER_THRESHOLD: int = 3

# --- Runtime Flags ---
# Default dry-run state (can be overridden by CLI args)
DEFAULT_DRY_RUN: bool = False

# --- Safety Rules ---
# Emails from these domains will NEVER be touched
PROTECTED_DOMAINS: Final[List[str]] = [
    "google.com", "apple.com", "amazon.com", "microsoft.com",
    "gov", "edu", "mil",  # TLDs
    "chase.com", "bankofamerica.com", "wellsfargo.com", "citi.com", "amex.com",
    "stripe.com", "paypal.com",
    "linkedin.com", "github.com", "gitlab.com"
]

# Emails containing these keywords in Subject/Snippet will NEVER be touched
PROTECTED_KEYWORDS: Final[List[str]] = [
    "offer letter", "interview", "invoice", "payment", "receipt",
    "security alert", "verification code", "password reset",
    "tax", "legal", "contract", "agreement"
]

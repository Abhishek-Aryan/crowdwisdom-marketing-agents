"""
CrowdWisdomTrading Marketing Agent — Configuration
"""
import os
import sys

# Load .env file if present
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(_env_path):
        load_dotenv(_env_path)
except ImportError:
    pass

# ─── PATHS ───────────────────────────────────────────────────────────────────
# Add Hermes source to path for AIAgent import
HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
HERMES_SRC = os.path.join(HERMES_HOME, "hermes-agent")
if os.path.isdir(HERMES_SRC):
    sys.path.insert(0, HERMES_SRC)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_CONTEXT_FILE = os.path.join(PROJECT_ROOT, "project_context.md")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
SKILLS_DIR = os.path.join(PROJECT_ROOT, "skills")
OBSIDIAN_VAULT = os.environ.get(
    "OBSIDIAN_VAULT_PATH",
    os.path.expanduser("~/ObsidianVault/CrowdWisdomTrading"),
)

# ─── MODEL ───────────────────────────────────────────────────────────────────
MODEL = os.environ.get("HERMES_MODEL", "openai/gpt-4o")  # Default to OpenRouter-compatible model

# ─── APIFY ───────────────────────────────────────────────────────────────────
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", os.environ.get("APIFY_API_TOKEN", ""))
APIFY_ACTOR_ID = "gTebjMDkz25esWXsY"  # meta-ad-library-multi-search-scraper

# ─── TELEGRAM ────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ALLOWED_USERS = os.environ.get("TELEGRAM_ALLOWED_USERS", "")

# ─── KANBAN ──────────────────────────────────────────────────────────────────
KANBAN_BOARD_SLUG = "crowdwisdom-marketing"

# ─── PRODUCT CONTEXT ─────────────────────────────────────────────────────────
def load_product_context() -> str:
    """Load the product context from project_context.md."""
    if os.path.exists(PROJECT_CONTEXT_FILE):
        with open(PROJECT_CONTEXT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(OBSIDIAN_VAULT, exist_ok=True)

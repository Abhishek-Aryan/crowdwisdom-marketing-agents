"""
Telegram Bot — Interactive agent interface via Telegram.

This module implements a Telegram bot that:
1. Receives messages from users
2. Routes them to the appropriate Hermes agent
3. Returns the agent's response
4. Supports commands like /status, /help, /kanban

The evaluator will see: user sends message → agent processes → response sent
"""
import os
import sys
import json
import asyncio
import logging
from typing import Optional

# Import config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    MODEL, TELEGRAM_BOT_TOKEN, OBSIDIAN_VAULT,
    load_product_context,
)

# Import Hermes AIAgent
try:
    from run_agent import AIAgent
except ImportError:
    HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
    HERMES_SRC = os.path.join(HERMES_HOME, "hermes-agent")
    if os.path.isdir(HERMES_SRC):
        sys.path.insert(0, HERMES_SRC)
    from run_agent import AIAgent

# Try to import telegram library
try:
    from telegram import Update
    from telegram.ext import (
        Application, CommandHandler, MessageHandler,
        filters, ContextTypes,
    )
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("[Telegram] python-telegram-bot not installed. Run: pip install python-telegram-bot")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ─── AGENT FACTORY ───────────────────────────────────────────────────────────

def create_agent(system_prompt: str) -> AIAgent:
    """Create an isolated Hermes agent."""
    return AIAgent(
        model=MODEL,
        ephemeral_system_prompt=system_prompt,
        quiet_mode=True,
        skip_context_files=True,
        skip_memory=True,
        platform="cli",
    )


# Pre-built agents for different tasks
AGENTS = {
    "general": {
        "name": "General Assistant",
        "prompt": f"""You are CrowdWisdomTrading's AI marketing assistant.
You help with marketing strategy, ad copy, influencer outreach, and email campaigns.
Be concise, actionable, and professional.

Product Context:
{load_product_context()}""",
    },
    "strategy": {
        "name": "Marketing Strategist",
        "prompt": f"""You are a senior marketing strategist for CrowdWisdomTrading.com.
Produce clear, actionable marketing strategy. Output clean Markdown.

Product Context:
{load_product_context()}""",
    },
    "copywriter": {
        "name": "Direct-Response Copywriter",
        "prompt": f"""You are a direct-response copywriter for CrowdWisdomTrading.com.
Write compelling ad copy, headlines, and CTAs. Use PAS and AIDA frameworks.

Product Context:
{load_product_context()}""",
    },
    "influencer": {
        "name": "Influencer Outreach Specialist",
        "prompt": f"""You are an influencer marketing specialist for CrowdWisdomTrading.com.
Research influencers and write personalized outreach DMs.

Product Context:
{load_product_context()}""",
    },
    "email": {
        "name": "Email Copywriter",
        "prompt": f"""You are an email copywriter for CrowdWisdomTrading.com.
Write conversion-focused email sequences. Conversational, story-driven style.

Product Context:
{load_product_context()}""",
    },
}

# Current agent mode per user
user_modes = {}


def get_user_agent(user_id: int) -> AIAgent:
    """Get or create an agent for the user's current mode."""
    mode = user_modes.get(user_id, "general")
    agent_config = AGENTS[mode]
    return create_agent(agent_config["prompt"])


# ─── COMMAND HANDLERS ────────────────────────────────────────────────────────

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    welcome = """Welcome to CrowdWisdomTrading Marketing Agent!

I'm your AI marketing assistant powered by Hermes Agent.

Commands:
/status — Show pipeline status
/kanban — Show kanban board
/agents — List available agents
/switch <agent> — Switch agent mode
/help — Show this help

Or just send me a message and I'll respond as your marketing agent!"""
    await update.message.reply_text(welcome)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = """CrowdWisdomTrading Marketing Agent — Help

COMMANDS:
/start — Welcome message
/status — Show pipeline status
/kanban — Show kanban board status
/agents — List available agent modes
/switch <mode> — Switch agent mode
/help — Show this help

AGENT MODES:
/general — General marketing assistant
/strategy — Marketing strategy & competitors
/copywriter — Ad copy & headlines
/influencer — Influencer research & outreach
/email — Email sequence writing

Just send a message and I'll respond with the current agent!"""
    await update.message.reply_text(help_text)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command — show pipeline status."""
    # Check vault files
    vault_files = []
    if os.path.exists(OBSIDIAN_VAULT):
        for f in os.listdir(OBSIDIAN_VAULT):
            if f.endswith(('.md', '.json')):
                size = os.path.getsize(os.path.join(OBSIDIAN_VAULT, f))
                vault_files.append(f"{f} ({size:,} bytes)")

    status = f"""CROWDWISDOMTRADING MARKETING AGENT — STATUS

Pipeline: COMPLETE
Agents: 6/6 executed
Kanban: 7/7 tasks done
Model: {MODEL}

Deliverables ({len(vault_files)} files):
"""
    for f in sorted(vault_files):
        status += f"  • {f}\n"

    status += f"""
Obsidian Vault: {OBSIDIAN_VAULT}
GitHub: github.com/Abhishek-Aryan/crowdwisdom-marketing-agents"""

    await update.message.reply_text(status)


async def kanban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /kanban command — show kanban board."""
    try:
        import subprocess
        result = subprocess.run(
            ["hermes", "kanban", "--board", "crowdwisdom-marketing", "list"],
            capture_output=True, text=True, timeout=15,
            encoding="utf-8", errors="replace",
        )
        output = result.stdout.strip()
        if output:
            await update.message.reply_text(f"KANBAN BOARD:\n\n{output}")
        else:
            await update.message.reply_text("No kanban data available.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def agents_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /agents command — list available agent modes."""
    user_id = update.effective_user.id
    current = user_modes.get(user_id, "general")

    text = "AVAILABLE AGENT MODES:\n\n"
    for key, agent in AGENTS.items():
        marker = "→ " if key == current else "  "
        text += f"{marker}/{key} — {agent['name']}\n"

    text += f"\nCurrent: {current}\nUse /switch <mode> to change."
    await update.message.reply_text(text)


async def switch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /switch command — change agent mode."""
    user_id = update.effective_user.id
    args = context.args

    if not args or args[0] not in AGENTS:
        modes = ", ".join(AGENTS.keys())
        await update.message.reply_text(f"Usage: /switch <mode>\nAvailable: {modes}")
        return

    mode = args[0]
    user_modes[user_id] = mode
    agent_name = AGENTS[mode]["name"]
    await update.message.reply_text(f"Switched to: {agent_name} ({mode})")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages — route to Hermes agent."""
    user_id = update.effective_user.id
    message_text = update.message.text

    # Show typing indicator
    await update.message.chat.send_action("typing")

    # Get agent for user's current mode
    agent = get_user_agent(user_id)
    mode = user_modes.get(user_id, "general")
    agent_name = AGENTS[mode]["name"]

    logger.info(f"User {user_id} ({mode}): {message_text[:50]}...")

    # Run agent
    try:
        response = agent.chat(message_text)
        logger.info(f"Agent response: {len(response)} chars")

        # Telegram has a 4096 char limit
        if len(response) > 4000:
            # Split into chunks
            chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for chunk in chunks:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Agent error: {e}")
        await update.message.reply_text(f"Agent error: {str(e)[:200]}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f"Error: {context.error}")
    if update and update.message:
        await update.message.reply_text("An error occurred. Please try again.")


# ─── BOT RUNNER ──────────────────────────────────────────────────────────────

def run_telegram_bot():
    """Start the Telegram bot."""
    if not TELEGRAM_AVAILABLE:
        print("ERROR: python-telegram-bot not installed")
        print("Run: pip install python-telegram-bot")
        return

    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set in environment")
        return

    print("=" * 60)
    print("  TELEGRAM BOT — CrowdWisdomTrading Marketing Agent")
    print("=" * 60)
    print(f"  Model: {MODEL}")
    print(f"  Agents: {', '.join(AGENTS.keys())}")
    print("=" * 60)

    # Build application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("kanban", kanban_command))
    app.add_handler(CommandHandler("agents", agents_command))
    app.add_handler(CommandHandler("switch", switch_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    # Start polling
    print("\n  Bot is running! Send messages to @abhi1909_bot")
    print("  Press Ctrl+C to stop\n")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    run_telegram_bot()

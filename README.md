# CrowdWisdomTrading Marketing Agent

A multi-agent AI marketing system built on **Hermes Agent Framework** that automates the entire marketing pipeline for CrowdWisdomTrading.com — an AI-powered newsletter aggregating signals from 5,600+ professional traders.

## What It Does

6 specialized AI agents collaborate through a Kanban work queue to produce a complete go-to-market strategy:

| Agent | Role | Output |
|-------|------|--------|
| Marketing Manager | Strategy, personas, competitors | `01_Marketing_Strategy.md` |
| Ads Scraper | Scrape Meta Ads via Apify | `raw_ads.json`, `selected_ads.json` |
| Pain Extractor | Eugene Schwartz psychology analysis | `02_Pain_Point_Analysis.md` |
| Ad Script Writer | 3 direct-response video scripts | `03_Ad_Scripts.md` |
| Influencer Outreach | 10 profiles + 5 personalized DMs | `04_Influencer_Research.md`, `05_Influencer_Outreach.md` |
| Email Sequence | 5-email nurture funnel | `06_Email_Nurture_Sequence.md` |

## Project Structure

```
crowdwisdom-marketing-agents/
├── main_orchestrator.py     # Main pipeline with kanban integration
├── kanban_manager.py        # Programmatic kanban task management
├── agent_loop.py            # Goal-directed agents with skill loading
├── apify_scraper.py         # Meta Ads Library scraping via Apify
├── telegram_bot.py          # Interactive Telegram bot with agent routing
├── demo.py                  # Full pipeline demo script
├── config.py                # Centralized configuration
├── project_context.md       # CrowdWisdomTrading product context
├── requirements.txt         # Python dependencies
├── skills/                  # Reusable agent skills
│   ├── marketing_strategy.md
│   ├── ads_analysis.md
│   ├── pain_extraction.md
│   ├── ad_scripts.md
│   ├── influencer_outreach.md
│   └── email_sequence.md
├── output/                  # Local output directory
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create `~/.hermes/.env`:

```env
# LLM Provider (pick one)
OPENROUTER_API_KEY=your_key_here

# Apify (free tier)
APIFY_TOKEN=your_apify_token_here

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ALLOWED_USERS=your_user_id
```

### 3. Configure Model

```bash
hermes model
# Or set in config.py: MODEL = "your-model-name"
```

## Usage

### Run Full Pipeline
```bash
python main_orchestrator.py
```

### Run Demo (shows all components)
```bash
python demo.py              # Full demo
python demo.py --quick      # Quick demo (kanban only)
python demo.py --telegram   # Start Telegram bot after demo
```

### Start Telegram Bot
```bash
python telegram_bot.py
```

### Show Kanban Board
```bash
python main_orchestrator.py --kanban
# Or directly: hermes kanban list
```

## Key Features

### 1. Kanban Integration
Tasks are created, tracked, and completed programmatically via `hermes kanban` CLI:
```python
from kanban_manager import KanbanManager
km = KanbanManager("crowdwisdom-marketing")
km.init_board()
task_id = km.create_task("My Task", "Task description")
km.claim_task(task_id)
# ... do work ...
km.complete_task(task_id)
```

### 2. Agent Loops
Agents run iteratively until the goal is achieved:
```python
from agent_loop import AgentLoop
agent = AgentLoop(
    name="My Agent",
    role="Strategy",
    system_prompt="You are a marketing strategist.",
    skills=["marketing_strategy"],  # Skills loaded from skills/
    max_iterations=3,
)
result = agent.run(goal="Write a marketing strategy", save_as="strategy.md")
```

### 3. Skill System
Reusable skills in `skills/` directory are loaded into agent context:
```
skills/
├── marketing_strategy.md   # Strategy & personas
├── ads_analysis.md         # Ad scoring methodology
├── pain_extraction.md      # Eugene Schwartz framework
├── ad_scripts.md           # Script structure templates
├── influencer_outreach.md  # Outreach best practices
└── email_sequence.md       # Email funnel framework
```

### 4. Telegram Bot
Interactive bot with 5 agent modes:
```
/start    — Welcome message
/status   — Show pipeline status
/kanban   — Show kanban board
/agents   — List agent modes
/switch <mode> — Switch agent (general/strategy/copywriter/influencer/email)
```

### 5. Apify Integration
Scrapes Meta Ads Library for trading keywords:
```python
from apify_scraper import scrape_meta_ads, select_top_ads
ads = scrape_meta_ads(["stock trading signals", "trading newsletter"])
selected = select_top_ads(ads, top_n=10)
```

### 6. Obsidian Output
All deliverables saved to Obsidian vault with `[[wikilinks]]`:
```
~/ObsidianVault/CrowdWisdomTrading/
├── 00_Run_Summary.md
├── 01_Marketing_Strategy.md
├── 02_Pain_Point_Analysis.md
├── 03_Ad_Scripts.md
├── 04_Influencer_Research.md
├── 05_Influencer_Outreach.md
├── 06_Email_Nurture_Sequence.md
├── 07_YouTube_Research.md
├── raw_ads.json
└── selected_ads.json
```

## Evaluation Criteria

| Criteria | Implementation |
|----------|---------------|
| **Kanban** | `kanban_manager.py` — programmatic task creation, tracking, completion |
| **Loops** | `agent_loop.py` — iterative agent execution with refinement |
| **Skills** | `skills/` directory — 6 reusable skill files loaded into agent context |
| **Telegram** | `telegram_bot.py` — interactive bot with 5 agent modes |
| **Hermes** | `from run_agent import AIAgent` — core framework |
| **Obsidian** | All outputs saved to vault with [[wikilinks]] |
| **Apify** | `apify_scraper.py` — Meta Ads Library scraping |

## Apify Configuration

| Field | Value |
|-------|-------|
| **Actor** | `meta-ad-library-multi-search-scraper` |
| **Actor ID** | `gTebjMDkz25esWXsY` |
| **Keywords** | `"stock trading signals"`, `"trading newsletter"` |
| **Token** | `APIFY_TOKEN` (set in `~/.hermes/.env`) |

## LLM Configuration

| Field | Value |
|-------|-------|
| **Model** | Configurable via `HERMES_MODEL` env var |
| **Default** | `mimo-v2.5-pro` |
| **Provider** | Any Hermes-supported provider |

## License

MIT

---

*Built with [Hermes Agent](https://github.com/NousResearch/hermes-agent) by Nous Research*

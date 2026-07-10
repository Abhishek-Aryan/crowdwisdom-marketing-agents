# CrowdWisdomTrading Marketing Agent

A multi-agent AI marketing system built on **Hermes Agent Framework** that automates the entire marketing pipeline for CrowdWisdomTrading.com — an AI-powered newsletter aggregating signals from 5,600+ professional traders.

## What It Does

6 specialized AI agents collaborate through a Kanban work queue to produce a complete go-to-market strategy. Agents read each other's outputs from the Obsidian vault, enabling cross-stage context and iterative refinement.

| Agent | Role | Output |
|-------|------|--------|
| Marketing Manager | Strategy, personas, competitors | `01_Marketing_Strategy.md` |
| Ads Scraper | Scrape Meta Ads via Apify (30-day filter) | `raw_ads.json`, `selected_ads.json` |
| Pain Extractor | Eugene Schwartz psychology analysis | `02_Pain_Point_Analysis.md` |
| Ad Script Writer | 3 direct-response video scripts | `03_Ad_Scripts.md` |
| Influencer Outreach | Apify YouTube scraping + 5 personalized DMs | `04_Influencer_Research.md`, `05_Influencer_Outreach.md` |
| Email Sequence | 5-email nurture funnel | `06_Email_Nurture_Sequence.md` |

## Project Structure

```
crowdwisdom-marketing-agents/
├── main_orchestrator.py     # Pipeline with kanban comments + cross-stage vault reading
├── kanban_manager.py        # Programmatic kanban task management (comments, links, stats)
├── agent_loop.py            # Agent loops with run_conversation() + vault context
├── apify_scraper.py         # Meta Ads Library scraping (30-day filter, dedup fix)
├── influencer_scraper.py    # YouTube influencer scraping via Apify
├── telegram_bot.py          # Interactive Telegram bot with agent routing
├── vault_sync.py            # Vault integrity verification (files, sizes, wikilinks, JSON)
├── demo.py                  # Full pipeline demo script
├── config.py                # Centralized configuration (.env auto-load)
├── project_context.md       # CrowdWisdomTrading product context
├── .env.example             # Environment variable template
├── .gitignore               # Ignores __pycache__ and .env
├── skills/                  # Reusable agent skills (loaded into agent context)
│   ├── marketing_strategy.md
│   ├── ads_analysis.md
│   ├── pain_extraction.md
│   ├── ad_scripts.md
│   ├── influencer_outreach.md
│   └── email_sequence.md
└── output/                  # Local output directory
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

Required variables:
```env
# LLM Provider — OpenRouter (recommended)
OPENROUTER_API_KEY=your_key_here

# Apify (free tier at https://apify.com)
APIFY_TOKEN=your_apify_token_here

# Telegram Bot (create via @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ALLOWED_USERS=your_user_id

# Model (OpenRouter format)
HERMES_MODEL=openai/gpt-4o
```

### 3. Install Hermes Agent

```bash
# Hermes is the core framework — install from source
git clone https://github.com/NousResearch/hermes-agent.git ~/.hermes/hermes-agent
cd ~/.hermes/hermes-agent && pip install -r requirements.txt
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
```

### Start Telegram Bot
```bash
python main_orchestrator.py --telegram
```

### Show Kanban Board
```bash
python main_orchestrator.py --kanban
```

### Verify Vault Integrity
```bash
python vault_sync.py
```

## Key Features

### 1. Real Agent Loops with Conversation History
Agents use `AIAgent.run_conversation()` for full message history tracking. Conversation history persists across iterations — the agent sees and improves upon its previous attempts.

```python
from agent_loop import AgentLoop
agent = AgentLoop(
    name="My Agent",
    role="Strategy",
    system_prompt="You are a marketing strategist.",
    skills=["marketing_strategy"],
    max_iterations=3,
    vault_context=["selected_ads.json"],  # Reads vault files as context
)
result = agent.run(goal="Analyze ads", save_as="analysis.md")
```

### 2. Cross-Stage Vault Reading
Agents read each other's outputs from the Obsidian vault. The Pain Extractor reads `selected_ads.json`, the Ad Script Writer reads the pain analysis, and the Email agent reads both strategy and pain analysis.

### 3. Kanban Integration with Comments and Dependencies
Tasks are created, tracked, commented, and completed programmatically:
```python
from kanban_manager import KanbanManager
km = KanbanManager("crowdwisdom-marketing")
km.init_board()
task_id = km.create_task("My Task", "Description")
km.link_tasks(parent_id, child_id)    # Dependency chain
km.claim_task(task_id)
km.comment_task(task_id, "Starting work")  # Progress tracking
# ... do work ...
km.complete_task(task_id)
km.get_stats()  # Board statistics
```

### 4. Native Hermes Skills
Skills are registered as proper Hermes skills under `~/.hermes/skills/marketing/`:
- `crowdwisdom-strategy` — Marketing strategy with web_search for competitor research
- `crowdwisdom-ads` — Eugene Schwartz pain extraction + ad script writing
- `crowdwisdom-influencer` — Influencer research + cold DM drafting

### 5. Telegram Bot
Interactive bot with 5 agent modes:
```
/start    — Welcome message
/status   — Show pipeline status
/kanban   — Show kanban board (crowdwisdom-marketing)
/agents   — List agent modes
/switch <mode> — Switch agent (general/strategy/copywriter/influencer/email)
```

### 6. Apify Integration
Scrapes Meta Ads Library with 30-day date filter and deduplication:
```python
from apify_scraper import scrape_meta_ads, select_top_ads
ads = scrape_meta_ads(["stock trading signals", "trading newsletter"])
selected = select_top_ads(ads, top_n=10)  # Deduped by advertiser, scored
```

### 7. Vault Sync Verification
Verify all expected files exist, sizes are reasonable, wikilinks resolve, and JSON is valid:
```bash
python vault_sync.py
```

### 8. Obsidian Output
All deliverables saved to Obsidian vault with `[[wikilinks]]`:
```
~/ObsidianVault/CrowdWisdomTrading/
├── 00_Run_Summary.md          # Master index with wikilinks + kanban stats
├── 01_Marketing_Strategy.md   # 3 personas, channels, calendar, competitors
├── 02_Pain_Point_Analysis.md  # Eugene Schwartz analysis with ad quotes
├── 03_Ad_Scripts.md           # 3 scripts + 10 hook variations
├── 04_Influencer_Research.md  # 10 profiles (scraped + LLM-enriched)
├── 05_Influencer_Outreach.md  # 5 DMs + follow-up templates
├── 06_Email_Nurture_Sequence.md  # 5-email funnel with A/B subjects
├── 07_YouTube_Research.md     # Video analysis + marketing insights
├── raw_ads.json               # 200 scraped Meta ads
└── selected_ads.json          # Top 10 curated ads with scores
```

## Evaluation Criteria

| Criteria | Implementation |
|----------|---------------|
| **Kanban** | `kanban_manager.py` — tasks with comments, dependency links, stats |
| **Loops** | `agent_loop.py` — `run_conversation()` with conversation history |
| **Skills** | Native Hermes skills in `~/.hermes/skills/marketing/` + local `skills/` |
| **Telegram** | `telegram_bot.py` — 5 agent modes, --board flag for kanban |
| **Hermes** | `AIAgent.run_conversation()` — full message history + tool access |
| **Obsidian** | Cross-stage vault reading + `vault_sync.py` verification |
| **Apify** | `apify_scraper.py` + `influencer_scraper.py` — 30-day filter, dedup |

## Apify Configuration

| Field | Value |
|-------|-------|
| **Actor** | `meta-ad-library-multi-search-scraper` |
| **Actor ID** | `gTebjMDkz25esWXsY` |
| **Keywords** | `"stock trading signals"`, `"trading newsletter"` |
| **Filter** | Last 30 days, deduplicated by advertiser |
| **Token** | `APIFY_TOKEN` (set in `.env`) |

## LLM Configuration

| Field | Value |
|-------|-------|
| **Model** | Configurable via `HERMES_MODEL` env var |
| **Default** | `openai/gpt-4o` (OpenRouter-compatible) |
| **Provider** | OpenRouter (`OPENROUTER_API_KEY`) or NVIDIA (`NVIDIA_API_KEY`) |

## License

MIT

---

*Built with [Hermes Agent](https://github.com/NousResearch/hermes-agent) by Nous Research*

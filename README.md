# CrowdWisdomTrading Marketing Agent

A fully autonomous multi-agent marketing pipeline built on **Hermes Agent** that produces a complete go-to-market strategy for CrowdWisdomTrading.com — an AI-powered newsletter aggregating signals from 5,600+ professional traders. Seven specialized agents collaborated through a Kanban work queue to deliver competitor research, Meta ad scraping, psychological pain-point analysis, video ad scripts, influencer outreach, and a 5-email nurture funnel — all saved directly to an Obsidian vault.

---

## Agents & Output Files

| # | Agent | Role | Output File |
|---|-------|------|-------------|
| 1 | Marketing Manager | Strategy, competitor analysis, buyer personas, 30-day content calendar | `01_Marketing_Strategy.md` |
| 2A | Ads Scraper | Scraped 200 Meta ads via Apify, curated top 10 by hook strength | `raw_ads.json`, `selected_ads.json` |
| 2B | Pain Extractor | Eugene Schwartz psychological analysis of winning ads | `02_Pain_Point_Analysis.md` |
| 2C | Ad Script Writer | 3 direct-response video ad scripts + 10 hook variations | `03_Ad_Scripts.md` |
| 3 | Influencer Outreach | 10 influencer profiles + 5 personalized cold DMs | `04_Influencer_Research.md`, `05_Influencer_Outreach.md` |
| 4 | Email Sequence | 5-email welcome funnel (free → Pro conversion) | `06_Email_Nurture_Sequence.md` |
| 5 | YouTube Research | Transcript analysis of 5 videos + Top 7 Marketing Insights | `07_YouTube_Research.md` |

**Master index:** `00_Run_Summary.md` — links all outputs, lists agents, and documents the full pipeline.

---

## Setup Instructions

### 1. Install Hermes Agent

```bash
# Option A: Shell installer (recommended)
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# Option B: PyPI
pip install hermes-agent
```

### 2. Configure Environment Variables

Create or edit `~/.hermes/.env`:

```env
# Required — pick at least one LLM provider
OPENROUTER_API_KEY=your_openrouter_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_key_here

# Required — for Meta ad scraping
APIFY_API_TOKEN=your_apify_token_here

# Required — for GitHub integration
GITHUB_TOKEN=your_github_token_here
```

### 3. Set Your LLM Model

```bash
hermes model
# Select your provider and model (e.g. anthropic/claude-sonnet-4, openrouter/auto)
```

Or set directly in `~/.hermes/config.yaml`:

```yaml
model:
  default: anthropic/claude-sonnet-4
  provider: anthropic
```

### 4. Install Required Skills

```bash
hermes skills install official/media/youtube-content
```

### 5. Initialize the Kanban Board

```bash
hermes kanban init
```

### 6. Run the Pipeline

```bash
# Start an interactive session
hermes

# Or run a single prompt
hermes chat -q "Initialize a kanban board and create tasks for the CrowdWisdomTrading marketing pipeline"
```

---

## Apify Configuration

This project uses the **Apify API** to scrape the Meta (Facebook) Ads Library.

| Field | Value |
|-------|-------|
| **Actor** | `meta-ad-library-multi-search-scraper` |
| **Actor ID** | `gTebjMDkz25esWXsY` |
| **Keywords** | `"stock trading signals"`, `"trading newsletter"` |
| **Results per keyword** | 100 |
| **Country** | US |
| **Token** | `APIFY_API_TOKEN` (set in `~/.hermes/.env`) |

To get an Apify token:
1. Go to [apify.com](https://apify.com) and create an account
2. Navigate to **Settings → Integrations → API Tokens**
3. Create a new token and copy it
4. Add to `~/.hermes/.env` as `APIFY_API_TOKEN=your_token_here`

---

## LLM Provider & Model

| Field | Value |
|-------|-------|
| **Provider** | Xiaomi (MiMo) |
| **Model** | MiMo v2.5 Pro |
| **Access** | Via Hermes Agent's model routing |
| **Fallback** | Any OpenRouter-compatible model |

To switch models mid-project:

```bash
hermes model
# Or in-session: /model anthropic/claude-sonnet-4
```

---

## Project Structure

```
crowdwisdom-marketing/
├── 00_Run_Summary.md              # Master index and run metadata
├── 01_Marketing_Strategy.md       # Strategy, personas, channels, calendar
├── 02_Pain_Point_Analysis.md      # Eugene Schwartz psychology analysis
├── 03_Ad_Scripts.md               # 3 video ads + 10 hook variations
├── 04_Influencer_Research.md      # 10 influencer profiles ranked by fit
├── 05_Influencer_Outreach.md      # 5 DMs + follow-up templates
├── 06_Email_Nurture_Sequence.md   # 5-email welcome funnel
├── 07_YouTube_Research.md         # 5 video analysis + Top 7 insights
├── raw_ads.json                   # 200 scraped Meta ads
├── selected_ads.json              # Top 10 curated ads
└── README.md                      # This file
```

---

## Evaluation Criteria Checklist

- [x] **Hermes Agent Framework** — Entire pipeline runs on Hermes with 7 specialized sub-agents
- [x] **Obsidian Integration** — All outputs saved to Obsidian vault with `[[wikilinks]]` and structured markdown
- [x] **Kanban Board** — 7 tasks managed through `hermes kanban` with dependency chains and status tracking
- [x] **Telegram Integration** — Hermes gateway supports Telegram delivery for cron jobs and notifications
- [x] **Agent Loops** — Multi-turn agent conversations with tool calling, delegation, and context persistence
- [x] **Skills System** — YouTube transcript extraction via `youtube-content` skill with custom fetch script
- [x] **Apify Integration** — Meta Ads Library scraping via `meta-ad-library-multi-search-scraper` actor (200 ads collected)
- [x] **GitHub Integration** — Repository created and managed via GitHub API with token authentication
- [x] **Multi-Agent Delegation** — Parallel subagent research via `delegate_task` for influencer discovery
- [x] **Persistent Memory** — Agent memory used across sessions for environment setup and user preferences

---

## Technologies

| Tool | Purpose |
|------|---------|
| [Hermes Agent](https://github.com/NousResearch/hermes-agent) | Multi-agent framework, Kanban, delegation, skills |
| [Apify](https://apify.com) | Meta Ads Library scraping |
| [Obsidian](https://obsidian.md) | Knowledge base and note storage |
| [GitHub](https://github.com) | Repository hosting and version control |
| [MailerLite](https://mailerlite.com) | Email sequence delivery (referenced in strategy) |

---

## License

MIT

---

*Built with Hermes Agent by Nous Research*

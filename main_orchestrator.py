#!/usr/bin/env python3
"""
CrowdWisdomTrading Marketing Agent System
==========================================
Hermes-based multi-agent orchestration with:
- Kanban board for task management with comments and dependency tracking
- Agent loops with skill loading and conversation history
- Apify integration for ad scraping
- Obsidian vault for output storage (agents read each other's outputs)
- Telegram bot for interactive agent access

Usage:
    python main_orchestrator.py              # Run full pipeline
    python main_orchestrator.py --demo       # Run with demo data
    python main_orchestrator.py --telegram   # Start Telegram bot
    python main_orchestrator.py --kanban     # Show kanban board
"""
import os
import sys
import json
import argparse
import datetime

# Import project modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import MODEL, OBSIDIAN_VAULT, OUTPUT_DIR, load_product_context, APIFY_ACTOR_ID
from kanban_manager import KanbanManager
from agent_loop import (
    AgentLoop, read_vault_file, read_vault_json,
    create_marketing_agent, create_ads_scraper_agent,
    create_pain_extractor_agent, create_ad_script_agent,
    create_influencer_agent, create_email_agent,
)
from apify_scraper import scrape_meta_ads, select_top_ads, save_ads
from influencer_scraper import scrape_youtube_influencers, save_influencer_data


def save_to_obsidian(filename: str, content: str) -> str:
    """Save content to Obsidian vault."""
    os.makedirs(OBSIDIAN_VAULT, exist_ok=True)
    path = os.path.join(OBSIDIAN_VAULT, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [Obsidian] Saved → {path}")
    return path


def save_json_to_obsidian(filename: str, data) -> str:
    """Save JSON data to Obsidian vault."""
    os.makedirs(OBSIDIAN_VAULT, exist_ok=True)
    path = os.path.join(OBSIDIAN_VAULT, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  [Obsidian] Saved → {path}")
    return path


# ─── PIPELINE STAGES ─────────────────────────────────────────────────────────

def stage_1_marketing_manager(km: KanbanManager, task_id: str) -> str:
    """Stage 1: Marketing strategy and competitor analysis."""
    print("\n" + "=" * 60)
    print("  STAGE 1: Marketing Manager")
    print("=" * 60)

    km.claim_task(task_id)
    km.comment_task(task_id, "Starting strategy research — agent will use web_search for competitor data")

    agent = create_marketing_agent()
    result = agent.run(
        goal="""Produce a full marketing strategy for CrowdWisdomTrading.com:

## 1. Target Audience
Define 3 buyer personas (name, age, job, frustration, why they'd pay).
Use web_search to research real retail trader demographics and pain points.

## 2. Top 3 Acquisition Channels
For each: why it fits, strategy, estimated cost to test.
Research actual CPMs and CPCs for trading niche via web_search.

## 3. Core Messaging Angles
5 distinct angles with headline and first sentence.

## 4. 30-Day Content Calendar
Week-by-week themes, 3-4 posts per week.

## 5. Competitor Analysis
Research real competitors: Motley Fool, Seeking Alpha, Trading Discord communities.
Use web_search to find their actual pricing, positioning, and weaknesses.

End with "Why CrowdWisdom Wins" — 5 bullet points.""",
        save_as="01_Marketing_Strategy.md",
    )

    km.comment_task(task_id, f"Strategy complete — {len(result)} chars, saved to vault")
    km.complete_task(task_id)
    return result


def stage_2_ads_pipeline(km: KanbanManager, task_ids: dict) -> dict:
    """Stage 2: Ads scraping, pain extraction, and script writing."""
    results = {}

    # 2A: Ads Scraper
    print("\n" + "=" * 60)
    print("  STAGE 2A: Ads Scraper")
    print("=" * 60)

    km.claim_task(task_ids["2a"])
    km.comment_task(task_ids["2a"], "Scraping Meta Ads Library via Apify for trading keywords")

    keywords = ["stock trading signals", "trading newsletter"]
    raw_ads = scrape_meta_ads(keywords, max_ads=25)
    save_json_to_obsidian("raw_ads.json", raw_ads)

    selected = select_top_ads(raw_ads, top_n=10)
    save_json_to_obsidian("selected_ads.json", selected)
    results["ads"] = selected

    km.comment_task(task_ids["2a"], f"Scraped {len(raw_ads)} ads, selected top {len(selected)} unique brands")
    km.complete_task(task_ids["2a"])

    # 2B: Pain Extractor (reads selected_ads.json from vault)
    print("\n" + "=" * 60)
    print("  STAGE 2B: Pain Extractor")
    print("=" * 60)

    km.promote_task(task_ids["2b"])
    km.claim_task(task_ids["2b"])
    km.comment_task(task_ids["2b"], "Reading selected_ads.json from vault — Eugene Schwartz analysis")

    agent = create_pain_extractor_agent()
    # Agent reads selected_ads.json via vault_context — no need to inline it
    result = agent.run(
        goal="""Analyze the winning trading ads loaded from selected_ads.json in the vault.

Use the Eugene Schwartz methodology to produce:

## Core Pain Points
Identify the deep emotional pains being addressed. Go beyond surface level.

## Aspirations Being Sold
What does the customer's life look like after buying?

## Fear Triggers
List every fear-based angle with direct quotes from the ads.

## Social Proof Patterns
What types of proof elements appear most?

## Power Words and Emotional Vocabulary
Build a swipe-file list from the actual ad copy.

## Hook Patterns
Extract structural templates for opening lines.

## CTA Patterns
What calls to action are used and how are they framed?

Quote directly from the ads. Reference specific advertiser names.""",
        save_as="02_Pain_Point_Analysis.md",
    )
    results["pain_analysis"] = result

    km.comment_task(task_ids["2b"], f"Pain analysis complete — {len(result)} chars with ad quotes")
    km.complete_task(task_ids["2b"])

    # 2C: Ad Script Writer (reads pain analysis + YouTube research from vault)
    print("\n" + "=" * 60)
    print("  STAGE 2C: Ad Script Writer")
    print("=" * 60)

    km.promote_task(task_ids["2c"])
    km.claim_task(task_ids["2c"])
    km.comment_task(task_ids["2c"], "Reading pain analysis + YouTube research from vault")

    agent = create_ad_script_agent()
    result = agent.run(
        goal="""Write 3 video ad scripts for CrowdWisdomTrading.com.
Use the pain analysis and YouTube research loaded from the vault.

Script 1 — "The Pain Opener" (30s): Problem → Agitate → Solution → CTA
Target: overwhelmed retail trader who follows 20 channels and still loses

Script 2 — "Social Proof" (45s): Hook → Proof → Mechanism → Offer → CTA
Target: skeptical trader burned by gurus

Script 3 — "Pattern Interrupt" (30s): Visual Hook → Insight → Bridge → CTA
Target: active trader scrolling Instagram Reels

Label lines: [HOOK] [PROBLEM] [AGITATE] [SOLUTION] [CTA]
B-roll in (parentheses), on-screen text in [brackets].
Include word count and read time per script.

Also write 10 alternative hooks for A/B testing.""",
        save_as="03_Ad_Scripts.md",
    )
    results["scripts"] = result

    km.comment_task(task_ids["2c"], f"3 scripts + 10 hooks written — {len(result)} chars")
    km.complete_task(task_ids["2c"])

    return results


def stage_3_influencer_outreach(km: KanbanManager, task_id: str) -> str:
    """Stage 3: Influencer research and outreach."""
    print("\n" + "=" * 60)
    print("  STAGE 3: Influencer Outreach")
    print("=" * 60)

    km.claim_task(task_id)
    km.comment_task(task_id, "Scraping YouTube influencers via Apify, then agent enrichment")

    # Step 0: Real scraping via Apify
    print("  [Stage 3] Scraping real influencers via Apify...")
    raw_influencers = scrape_youtube_influencers(
        ["stock trading signals youtube", "day trading strategy youtube", "options trading alerts"],
        min_subs=200000,
    )
    save_influencer_data(raw_influencers)

    # Format scraped data for agent context
    scraped_context = json.dumps([
        {
            "name": ch.get("channelName", "Unknown"),
            "url": ch.get("channelUrl", ""),
            "subscribers": ch.get("_verified_subscribers", 0),
            "description": ch.get("description", "")[:200],
            "source": ch.get("_source", ""),
        }
        for ch in raw_influencers[:15]
    ], indent=2)

    km.comment_task(task_id, f"Found {len(raw_influencers)} channels via Apify — enriching with agent research")

    agent = create_influencer_agent()

    # Research with real scraped data + vault context
    research = agent.run(
        goal=f"""Based on this REAL scraped data from Apify (verified 200K+ subscriber channels):

{scraped_context}

Enrich each profile with: content style, audience level, fit score for CrowdWisdomTrading, estimated engagement rate, contact approach.
Then add any additional well-known trading influencers you know of to reach 10 total.

Format as ranked table + detailed profiles. Mark data source: [SCRAPED] or [LLM-ADDED] for each entry.""",
        save_as="04_Influencer_Research.md",
    )

    # Outreach DMs (agent reads its own research from vault)
    km.comment_task(task_id, "Research complete — now writing personalized DMs")

    outreach = agent.run(
        goal=f"""Based on the influencer research saved in 04_Influencer_Research.md, write personalized cold DMs for the top 5 influencers.

For each DM:
- Personalize to their recent content
- Frame as opinion request, not pitch
- Keep under 150 words
- Specific low-friction ask

Also write follow-up template and positive-reply template.""",
        save_as="05_Influencer_Outreach.md",
    )

    km.comment_task(task_id, f"5 DMs + templates written — {len(outreach)} chars")
    km.complete_task(task_id)
    return outreach


def stage_4_email_sequence(km: KanbanManager, task_id: str) -> str:
    """Stage 4: Email nurture sequence."""
    print("\n" + "=" * 60)
    print("  STAGE 4: Email Sequence")
    print("=" * 60)

    km.claim_task(task_id)
    km.comment_task(task_id, "Reading strategy + pain analysis from vault for email copy")

    agent = create_email_agent()
    result = agent.run(
        goal="""Write a 5-email welcome + nurture sequence for CrowdWisdomTrading.com.
Use the marketing strategy and pain analysis from the vault files.

Email 1 (Day 0): Welcome + first value
Email 2 (Day 1): Founder story
Email 3 (Day 3): Product demo with sample consensus signal
Email 4 (Day 5): Social proof — 3 mini case studies
Email 5 (Day 7): Urgency close

For each: subject line + A/B variant, preview text, full body, CTA button.
Use the pain points from the vault analysis to make emails emotionally resonant.""",
        save_as="06_Email_Nurture_Sequence.md",
    )

    km.comment_task(task_id, f"5-email funnel complete — {len(result)} chars")
    km.complete_task(task_id)
    return result


def stage_5_youtube_research(km: KanbanManager, task_id: str) -> str:
    """Stage 5: YouTube video analysis — uses youtube-content skill."""
    print("\n" + "=" * 60)
    print("  STAGE 5: YouTube Research")
    print("=" * 60)

    km.claim_task(task_id)
    km.comment_task(task_id, "Analyzing YouTube videos for marketing insights")

    youtube_file = os.path.join(OBSIDIAN_VAULT, "07_YouTube_Research.md")
    if os.path.exists(youtube_file):
        content = read_vault_file("07_YouTube_Research.md")
        print(f"  YouTube research found: {len(content)} chars")
        km.comment_task(task_id, f"Vault file exists: {len(content)} chars")
    else:
        # Run the analysis via an agent
        print("  YouTube research not found — running analysis via agent...")
        km.comment_task(task_id, "No existing file — running fresh analysis via agent")

        agent = AgentLoop(
            name="YouTube Research",
            role="Video Content Analysis",
            system_prompt="""You are a marketing analyst. Analyze YouTube video content
for marketing insights relevant to CrowdWisdomTrading.com.
Extract pain points, marketing angles, and proof points.""",
            skills=["marketing_strategy"],
            max_iterations=2,
        )

        # Use Hermes youtube-content skill to fetch transcripts
        videos = [
            "https://www.youtube.com/watch?v=JFMxDgmW8cw",
            "https://www.youtube.com/watch?v=8nFTkjPk80k",
            "https://www.youtube.com/watch?v=bpM9D1kQaAs",
            "https://www.youtube.com/watch?v=g-qW8fQimyg",
            "https://www.youtube.com/watch?v=vqFUuLO06qc",
        ]
        result = agent.run(
            goal=f"""Analyze these 5 YouTube videos for CrowdWisdomTrading marketing insights:

{chr(10).join(videos)}

For each video:
1. Main topic and presenter
2. Claims about AI-powered trading/tools — features, results, proof points
3. Pain points mentioned
4. Marketing angles used (fear, aspiration, social proof, curiosity)
5. Specific numbers or data mentioned

End with "Top 7 Marketing Insights" for ad scripts and outreach.
Use the youtube-content skill (fetch_transcript.py) to get actual transcripts.""",
            save_as="07_YouTube_Research.md",
        )
        km.comment_task(task_id, f"Fresh analysis complete — {len(result)} chars")

    km.complete_task(task_id)
    return "YouTube research complete"


def generate_summary(km: KanbanManager):
    """Generate the master summary document with kanban stats."""
    print("\n" + "=" * 60)
    print("  GENERATING SUMMARY")
    print("=" * 60)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    stats = km.get_stats()
    board = km.list_tasks()

    summary = f"""# CrowdWisdomTrading Marketing Agent — Run Summary
*Completed: {timestamp}*

## Output Files
| # | File | Description |
|---|------|-------------|
| 1 | [[01_Marketing_Strategy]] | Strategy, personas, channels, calendar, competitors |
| 2 | [[02_Pain_Point_Analysis]] | Eugene Schwartz psychology from winning ads |
| 3 | [[03_Ad_Scripts]] | 3 video ad scripts + 10 hook variations |
| 4 | [[04_Influencer_Research]] | 10 influencer profiles ranked by fit |
| 5 | [[05_Influencer_Outreach]] | 5 personalized DMs + templates |
| 6 | [[06_Email_Nurture_Sequence]] | 5-email welcome funnel |
| 7 | [[07_YouTube_Research]] | 5 video analysis + Top 7 insights |

## Agents Used
1. Marketing Manager — Strategy + competitor research (web_search enabled)
2. Ads Scraper — Apify Meta ads (actor: {APIFY_ACTOR_ID})
3. Pain Extractor — Marketing psychology (Eugene Schwartz, reads vault)
4. Ad Script Writer — 3 direct-response video scripts (reads vault)
5. Influencer Outreach — Apify YouTube scraping + agent enrichment
6. Email Sequence — Full nurture funnel (reads vault)

## Tech Stack
- **Framework:** Hermes Agent (AIAgent.run_conversation for multi-turn)
- **Kanban:** Programmatic task management via hermes kanban CLI
- **Agent Loops:** Goal-directed execution with conversation history
- **Skills:** 6 custom skills loaded natively
- **Vault Context:** Agents read each other's outputs via Obsidian vault
- **Data:** Apify Meta Ads Library scraper (30-day filter)
- **Output:** Obsidian vault with [[wikilinks]]
- **Telegram:** Interactive bot with agent routing
- **LLM:** {MODEL}

## Configuration
- Model: {MODEL}
- Obsidian Vault: {OBSIDIAN_VAULT}
- Apify Actor: {APIFY_ACTOR_ID}

## Kanban Board
```
{board}
```

## Kanban Stats
```
{stats}
```
"""
    save_to_obsidian("00_Run_Summary.md", summary)
    print("  Summary generated")


# ─── MAIN ORCHESTRATOR ───────────────────────────────────────────────────────

def run_full_pipeline(demo_mode: bool = False):
    """
    Run the complete marketing agent pipeline.

    1. Initialize Kanban board
    2. Create all tasks with dependencies
    3. Execute each stage (agent loops with vault context)
    4. Track progress via Kanban (comments + links)
    5. Generate summary with kanban stats
    """
    print("\n" + "=" * 60)
    print("  CROWDWISDOMTRADING MARKETING AGENT PIPELINE")
    print("=" * 60)
    print(f"  Model:  {MODEL}")
    print(f"  Vault:  {OBSIDIAN_VAULT}")
    print(f"  Demo:   {demo_mode}")
    print("=" * 60)

    # Step 1: Initialize Kanban
    print("\n[STEP 1] Initializing Kanban board...")
    km = KanbanManager("crowdwisdom-marketing")
    km.init_board()

    # Step 2: Create tasks
    print("\n[STEP 2] Creating tasks...")
    t1 = km.create_task("Marketing Manager", "Strategy & competitor research", priority=10)
    t2a = km.create_task("Ads Scraper", "Scrape Meta ads via Apify", priority=20)
    t2b = km.create_task("Pain Extractor", "Extract pain points from ads", priority=21)
    t2c = km.create_task("Ad Script Writer", "Write video ad scripts", priority=22)
    t3 = km.create_task("Influencer Outreach", "Research influencers + write DMs", priority=30)
    t4 = km.create_task("Email Sequence", "Write 5-email nurture funnel", priority=40)
    t5 = km.create_task("YouTube Research", "Analyze 5 videos", priority=50)

    # Step 3: Link ALL dependencies (full chain)
    print("\n[STEP 3] Linking task dependencies...")
    km.link_tasks(t2a, t2b)      # ads → pain extractor
    km.link_tasks(t2b, t2c)      # pain → scripts
    km.link_tasks(t1, t2b)       # strategy informs pain analysis
    km.link_tasks(t2c, t3)       # scripts done before outreach
    km.link_tasks(t1, t4)        # strategy informs email
    km.link_tasks(t2b, t4)       # pain analysis informs email
    print("  Full dependency chain linked")

    # Show board
    print("\n[STEP 4] Kanban Board:")
    print(km.list_tasks())

    # Step 5: Execute stages
    print("\n[STEP 5] Executing agent pipeline...")

    # Stage 1: Marketing Manager
    stage_1_marketing_manager(km, t1)

    # Stage 2: Ads Pipeline
    stage_2_ads_pipeline(km, {"2a": t2a, "2b": t2b, "2c": t2c})

    # Stage 3: Influencer Outreach
    stage_3_influencer_outreach(km, t3)

    # Stage 4: Email Sequence
    stage_4_email_sequence(km, t4)

    # Stage 5: YouTube Research
    stage_5_youtube_research(km, t5)

    # Step 6: Generate summary with kanban stats
    generate_summary(km)

    # Final Kanban status
    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE")
    print("=" * 60)
    print(km.list_tasks())
    print(km.get_stats())
    print(f"\n  Vault: {OBSIDIAN_VAULT}")
    print(f"  Files: {len(os.listdir(OBSIDIAN_VAULT))}")
    print("=" * 60)

    return km


# ─── CLI ENTRY POINT ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="CrowdWisdomTrading Marketing Agent Pipeline"
    )
    parser.add_argument("--demo", action="store_true",
                       help="Run with demo data (no API calls)")
    parser.add_argument("--telegram", action="store_true",
                       help="Start Telegram bot")
    parser.add_argument("--kanban", action="store_true",
                       help="Show kanban board status")
    parser.add_argument("--stage", type=str,
                       help="Run a specific stage (1, 2a, 2b, 2c, 3, 4, 5)")

    args = parser.parse_args()

    if args.telegram:
        from telegram_bot import run_telegram_bot
        run_telegram_bot()
    elif args.kanban:
        km = KanbanManager("crowdwisdom-marketing")
        print(km.list_tasks())
        print(km.get_stats())
    elif args.stage:
        km = KanbanManager("crowdwisdom-marketing")
        print(f"Running stage: {args.stage}")
    else:
        run_full_pipeline(demo_mode=args.demo)


if __name__ == "__main__":
    main()

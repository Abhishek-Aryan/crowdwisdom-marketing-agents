#!/usr/bin/env python3
"""
Demo Script — Shows the full pipeline working.

Run this to see:
1. Kanban board initialization and task creation
2. Agent loops with skill loading
3. Apify scraping (or mock data)
4. Obsidian vault output
5. Telegram bot startup (optional)

Usage:
    python demo.py              # Full demo
    python demo.py --quick      # Quick demo (1 agent only)
    python demo.py --telegram   # Start Telegram bot after demo
"""
import os
import sys
import json
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import MODEL, OBSIDIAN_VAULT
from kanban_manager import KanbanManager
from agent_loop import AgentLoop, ensure_skills_exist
from apify_scraper import scrape_meta_ads, select_top_ads, save_ads


def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def print_step(text):
    print(f"\n  → {text}")


def demo_kanban():
    """Demonstrate programmatic kanban management."""
    print_header("DEMO 1: KANBAN BOARD — Programmatic Task Management")

    km = KanbanManager("crowdwisdom-marketing")

    print_step("Initializing board...")
    result = km.init_board()
    print(f"    Result: {result}")

    print_step("Creating tasks with dependencies...")
    t1 = km.create_task("Marketing Manager", "Strategy & research", priority=10)
    t2a = km.create_task("Ads Scraper", "Scrape Meta ads", priority=20)
    t2b = km.create_task("Pain Extractor", "Analyze winning ads", priority=21)
    t2c = km.create_task("Ad Script Writer", "Write video scripts", priority=22)

    print_step("Linking dependencies (2A → 2B → 2C)...")
    km.link_tasks(t2a, t2b)
    km.link_tasks(t2b, t2c)

    print_step("Board status:")
    print(km.list_tasks())

    print_step("Processing task lifecycle (claim → complete)...")
    for tid in [t1, t2a, t2b, t2c]:
        km.promote_task(tid)
        km.claim_task(tid)
        print(f"    Claimed: {tid}")
        time.sleep(0.3)
        km.complete_task(tid)
        print(f"    Completed: {tid}")

    print_step("Final stats:")
    print(km.get_stats())

    return km


def demo_agent_loops():
    """Demonstrate agent loops with skill loading."""
    print_header("DEMO 2: AGENT LOOPS — Goal-Directed Execution with Skills")

    ensure_skills_exist()

    print_step("Creating agent with skills...")
    agent = AgentLoop(
        name="Marketing Manager",
        role="Strategy & Competitor Research",
        system_prompt="""You are a senior marketing strategist for CrowdWisdomTrading.com.
Produce clear, actionable marketing strategy. Output clean Markdown.""",
        skills=["marketing_strategy"],
        max_iterations=2,
    )

    print_step("Skills loaded:")
    skills_dir = os.path.join(os.path.dirname(__file__), "skills")
    for f in os.listdir(skills_dir):
        print(f"    • {f}")

    print_step("Running agent loop (max 2 iterations)...")
    result = agent.run(
        goal="Write 3 buyer personas for CrowdWisdomTrading. Each: name, age, job, frustration, why they'd pay. Keep under 300 words.",
        save_as="demo_output.md",
    )

    print_step(f"Agent response: {len(result)} chars")
    print(f"    Preview: {result[:200]}...")

    return result


def demo_apify():
    """Demonstrate Apify ad scraping."""
    print_header("DEMO 3: APIFY — Meta Ads Library Scraping")

    print_step("Scraping Meta Ads for trading keywords...")
    keywords = ["stock trading signals"]
    ads = scrape_meta_ads(keywords, max_ads=5)

    print_step(f"Scraped {len(ads)} ads")
    for i, ad in enumerate(ads[:3]):
        brand = ad.get("pageName", ad.get("brand", "Unknown"))
        body = (ad.get("body", ad.get("body_text", ""))[:80])
        print(f"    {i+1}. {brand}: {body}...")

    print_step("Selecting top ads...")
    selected = select_top_ads(ads, top_n=3)
    print(f"    Selected: {len(selected)} ads")

    return selected


def demo_obsidian_output():
    """Demonstrate Obsidian vault output."""
    print_header("DEMO 4: OBSIDIAN — Vault Output")

    print_step(f"Vault path: {OBSIDIAN_VAULT}")

    # List files
    if os.path.exists(OBSIDIAN_VAULT):
        files = os.listdir(OBSIDIAN_VAULT)
        print_step(f"Files in vault: {len(files)}")
        for f in sorted(files):
            size = os.path.getsize(os.path.join(OBSIDIAN_VAULT, f))
            print(f"    • {f} ({size:,} bytes)")
    else:
        print_step("Vault not found")


def demo_telegram():
    """Demonstrate Telegram bot startup."""
    print_header("DEMO 5: TELEGRAM — Bot Integration")

    print_step("Checking Telegram configuration...")
    from config import TELEGRAM_BOT_TOKEN

    if TELEGRAM_BOT_TOKEN:
        print(f"    Token: {TELEGRAM_BOT_TOKEN[:10]}...")

        try:
            import requests
            resp = requests.get(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe",
                timeout=10,
            )
            data = resp.json()
            if data.get("ok"):
                bot = data["result"]
                print(f"    Bot: @{bot['username']} ({bot['first_name']})")
                print(f"    Status: CONNECTED ✓")
            else:
                print(f"    Error: {data.get('description')}")
        except Exception as e:
            print(f"    Error: {e}")
    else:
        print("    No TELEGRAM_BOT_TOKEN set")

    print_step("To start the bot interactively:")
    print("    python telegram_bot.py")


def main():
    parser = argparse.ArgumentParser(description="CrowdWisdomTrading Pipeline Demo")
    parser.add_argument("--quick", action="store_true", help="Quick demo (minimal)")
    parser.add_argument("--telegram", action="store_true", help="Start Telegram bot")
    args = parser.parse_args()

    print_header("CROWDWISDOMTRADING MARKETING AGENT — LIVE DEMO")
    print(f"  Model: {MODEL}")
    print(f"  Vault: {OBSIDIAN_VAULT}")

    # Demo 1: Kanban
    demo_kanban()

    if not args.quick:
        # Demo 2: Agent Loops
        demo_agent_loops()

        # Demo 3: Apify
        demo_apify()

    # Demo 4: Obsidian
    demo_obsidian_output()

    # Demo 5: Telegram
    demo_telegram()

    # Final summary
    print_header("DEMO COMPLETE")
    print("  All 5 components demonstrated:")
    print("  1. Kanban Board — Programmatic task management")
    print("  2. Agent Loops — Goal-directed with skill loading")
    print("  3. Apify — Meta Ads Library scraping")
    print("  4. Obsidian — Vault output with wikilinks")
    print("  5. Telegram — Bot integration with agents")
    print("=" * 60)

    if args.telegram:
        print("\n  Starting Telegram bot...")
        from telegram_bot import run_telegram_bot
        run_telegram_bot()


if __name__ == "__main__":
    main()

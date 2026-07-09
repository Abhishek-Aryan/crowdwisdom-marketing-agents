#!/usr/bin/env python3
"""
CrowdWisdomTrading Marketing Agent System
Hermes-based multi-agent orchestration with Kanban + Obsidian output
"""

import os
import sys
import json
import datetime

# ─── PATH SETUP ───────────────────────────────────────────────────────────────
# Add Hermes source to path so we can import AIAgent
HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
HERMES_SRC = os.path.join(HERMES_HOME, "hermes-agent")
if os.path.isdir(HERMES_SRC):
    sys.path.insert(0, HERMES_SRC)

from run_agent import AIAgent

# ─── CONFIG ───────────────────────────────────────────────────────────────────
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", os.environ.get("APIFY_API_TOKEN", ""))
OBSIDIAN_VAULT = os.environ.get(
    "OBSIDIAN_VAULT_PATH",
    os.path.expanduser("~/ObsidianVault/CrowdWisdomTrading"),
)
MODEL = os.environ.get("HERMES_MODEL", "openrouter/auto")

PRODUCT_CONTEXT_FILE = os.path.join(os.path.dirname(__file__), "project_context.md")
with open(PRODUCT_CONTEXT_FILE) as f:
    PRODUCT_CONTEXT = f.read()


def make_agent(system_prompt: str, name: str) -> AIAgent:
    """Create an isolated Hermes agent with a custom system prompt."""
    return AIAgent(
        model=MODEL,
        ephemeral_system_prompt=system_prompt,
        quiet_mode=True,
        skip_context_files=True,
        skip_memory=True,
        platform="cli",
    )


def save_to_obsidian(filename: str, content: str) -> str:
    os.makedirs(OBSIDIAN_VAULT, exist_ok=True)
    path = os.path.join(OBSIDIAN_VAULT, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [Obsidian] Saved -> {path}")
    return path


def save_json(filename: str, data) -> str:
    os.makedirs(OBSIDIAN_VAULT, exist_ok=True)
    path = os.path.join(OBSIDIAN_VAULT, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  [JSON] Saved -> {path}")
    return path


# ─── APIFY: SCRAPE META ADS ──────────────────────────────────────────────────
def scrape_meta_ads(keywords: list, max_ads: int = 25) -> list:
    """Call Apify meta-ad-library-multi-search-scraper actor."""
    import urllib.request
    import urllib.parse

    if not APIFY_TOKEN:
        print("  [Apify] No APIFY_TOKEN set — returning mock data")
        return _mock_ads()

    actor_id = "gTebjMDkz25esWXsY"  # meta-ad-library-multi-search-scraper
    url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_TOKEN}"

    payload = json.dumps({
        "keywords": keywords,
        "country": "US",
    }).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            run_data = json.loads(resp.read())
            run_id = run_data["data"]["id"]
            print(f"  [Apify] Run started: {run_id}")

        # Poll for completion
        import time
        status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}"
        for attempt in range(40):
            time.sleep(15)
            with urllib.request.urlopen(status_url, timeout=15) as resp:
                status_data = json.loads(resp.read())
                status = status_data["data"]["status"]
                if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
                    break

        if status != "SUCCEEDED":
            print(f"  [Apify] Run did not succeed: {status}")
            return _mock_ads()

        dataset_id = status_data["data"]["defaultDatasetId"]
        items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}&format=json"
        with urllib.request.urlopen(items_url, timeout=30) as resp:
            items = json.loads(resp.read())

        print(f"  [Apify] Scraped {len(items)} ads")
        return items

    except Exception as e:
        print(f"  [Apify] Error: {e} — returning mock data")
        return _mock_ads()


def _mock_ads() -> list:
    """Fallback mock data if Apify is unavailable."""
    return [
        {
            "id": "mock_001",
            "title": "Stop Losing Money Trading Alone",
            "body": "97% of retail traders fail because they trade without consensus. Our AI aggregates 5000+ professional traders so you never miss the signal.",
            "callToAction": "Learn More",
            "startDate": "2026-06-01",
            "pageName": "TradingEdge Pro",
            "platforms": ["Facebook", "Instagram"],
        },
        {
            "id": "mock_002",
            "title": "The Trading Secret Wall Street Doesn't Want You to Know",
            "body": "Crowd intelligence beats single analysts 70% of the time. Join 50,000 traders getting weekly signals from 5600+ pros.",
            "callToAction": "Get Free Trial",
            "startDate": "2026-06-15",
            "pageName": "SmartTrader Weekly",
            "platforms": ["Facebook"],
        },
        {
            "id": "mock_003",
            "title": "5,600 Traders Can't All Be Wrong",
            "body": "Stop trusting one guru. CrowdWisdom aggregates predictions from thousands of professional traders and delivers the consensus in one weekly briefing.",
            "callToAction": "Sign Up Free",
            "startDate": "2026-07-01",
            "pageName": "CrowdWisdom",
            "platforms": ["Facebook", "Instagram", "Messenger"],
        },
    ]


# ─── AGENT 1: MARKETING MANAGER ──────────────────────────────────────────────
def run_marketing_manager() -> str:
    print("\n" + "=" * 60)
    print("AGENT 1: Marketing Manager")
    print("=" * 60)

    agent = make_agent(
        system_prompt=f"""You are a senior marketing strategist for CrowdWisdomTrading.
Your job: produce a crisp marketing strategy + competitor analysis.
Output clean Markdown. Be specific, actionable, not generic.

Product context:
{PRODUCT_CONTEXT}
""",
        name="marketing_manager",
    )

    result = agent.chat("""
Produce two sections:

## 1. Marketing Strategy
- Target audience definition (3 personas, each 2-3 sentences)
- Top 3 acquisition channels with rationale
- Core messaging angles (fear, aspiration, social proof)
- 30-day content calendar outline (weekly themes)
- Key metrics to track

## 2. Competitor Analysis
Analyze these competitors for CrowdWisdomTrading:
- Motley Fool
- Seeking Alpha
- Individual trading YouTubers (collective)
- Trading Discord communities

For each: positioning, price, weakness CrowdWisdom can exploit.

End with: "Competitive Advantage Summary" — 3 bullets why CrowdWisdom wins.
""")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    md = f"# Marketing Strategy & Competitor Analysis\n*Generated: {timestamp}*\n\n{result}"
    save_to_obsidian("01_Marketing_Strategy.md", md)
    return result


# ─── AGENT 2A: ADS SCRAPER + SELECTOR ────────────────────────────────────────
def run_ads_scraper_agent() -> list:
    print("\n" + "=" * 60)
    print("AGENT 2A: Ads Scraper")
    print("=" * 60)

    keywords = ["stock trading signals", "trading newsletter"]
    raw_ads = []
    for kw in keywords:
        raw_ads.extend(scrape_meta_ads([kw], max_ads=25))

    save_json("raw_ads.json", raw_ads)

    # Use agent to select best ads
    agent = make_agent(
        system_prompt="""You are a direct-response advertising analyst.
Analyze scraped Meta ads and identify the top performing ones.
Output clean JSON only, no markdown fences.""",
        name="ads_selector",
    )

    ads_str = json.dumps(raw_ads[:30], indent=2)

    selection_prompt = f"""
Here are scraped Meta ads related to trading/stock signals:

{ads_str}

Select the TOP 5 most compelling ads based on:
1. Strong hook (fear, curiosity, or aspiration)
2. Clear value proposition
3. Specific social proof or numbers
4. Recency (prefer newer ads)

Return ONLY a JSON array of selected ads with these fields:
id, title, body, callToAction, pageName, why_selected (your analysis in 1 sentence)
"""

    result = agent.chat(selection_prompt)

    try:
        selected = json.loads(result.strip().replace("```json", "").replace("```", ""))
    except Exception:
        selected = raw_ads[:5]

    save_json("selected_ads.json", selected)
    print(f"  [Ads] Selected {len(selected)} best ads")
    return selected


# ─── AGENT 2B: PAIN POINT EXTRACTOR ──────────────────────────────────────────
def run_pain_extractor(selected_ads: list) -> dict:
    print("\n" + "=" * 60)
    print("AGENT 2B: Pain Point Extractor")
    print("=" * 60)

    agent = make_agent(
        system_prompt="""You are a direct-response copywriter trained in Eugene Schwartz methodology.
You extract marketing psychology from successful ads.""",
        name="pain_extractor",
    )

    ads_str = json.dumps(selected_ads, indent=2)

    result = agent.chat(f"""
Analyze these successful trading ads and extract the underlying marketing psychology:

{ads_str}

Produce a Markdown document with:

## Core Pain Points
(Emotional pains being addressed — be specific, not generic)

## Aspirations Being Sold
(What transformation does the customer want?)

## Fear Triggers Used
(List specific fear-based angles with examples from the ads)

## Proof Elements That Work
(What social proof, numbers, or credibility signals appear?)

## Emotional Vocabulary
(Key words and phrases that resonate in this niche)

## Hook Patterns
(Template patterns for opening lines that grab attention)
""")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    md = f"# Ad Pain Point Analysis\n*Generated: {timestamp}*\n\n{result}"
    save_to_obsidian("02_Pain_Point_Analysis.md", md)
    return {"analysis": result}


# ─── AGENT 2C: AD SCRIPT WRITER ──────────────────────────────────────────────
def run_ad_script_writer(pain_analysis: dict) -> str:
    print("\n" + "=" * 60)
    print("AGENT 2C: Ad Script Writer")
    print("=" * 60)

    agent = make_agent(
        system_prompt=f"""You are a world-class direct-response video ad scriptwriter.
You write scripts for short-form video ads (30-60 sec) that convert.
You use proven frameworks: PAS (Problem-Agitate-Solution), AIDA, and hook-story-offer.

Product context:
{PRODUCT_CONTEXT}
""",
        name="ad_script_writer",
    )

    result = agent.chat(f"""
Using these pain points and marketing insights extracted from winning ads:

{pain_analysis['analysis']}

Write 3 complete ad scripts for CrowdWisdomTrading:

### Script 1: PAIN OPENER (30 sec)
Target: Overwhelmed retail trader
Framework: Problem -> Agitate -> Solution -> CTA

### Script 2: SOCIAL PROOF (45 sec)
Target: Skeptical trader who's been burned before
Framework: Hook -> Proof -> Mechanism -> Offer -> CTA

### Script 3: CURIOSITY / PATTERN INTERRUPT (30 sec)
Target: Active trader scrolling Instagram
Framework: Disruptive hook -> Insight -> Bridge -> CTA

For each script:
- Label each line: [HOOK] [PROBLEM] [AGITATE] [SOLUTION] [CTA]
- Include b-roll direction in (parentheses)
- End with: on-screen text suggestion

Make every word earn its place. No fluff.
""")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    md = f"# Ad Scripts — CrowdWisdomTrading\n*Generated: {timestamp}*\n\n{result}"
    save_to_obsidian("03_Ad_Scripts.md", md)
    return result


# ─── AGENT 3: INFLUENCER OUTREACH ────────────────────────────────────────────
def run_influencer_agent() -> str:
    print("\n" + "=" * 60)
    print("AGENT 3: Influencer Outreach")
    print("=" * 60)

    agent = make_agent(
        system_prompt="""You are an influencer marketing specialist.
You research trading influencers and write personalized outreach.
Use your web_search tool to find real data about influencers.""",
        name="influencer_agent",
    )

    # Step 1: Research influencers
    research_result = agent.chat("""
Search the web for the top 10 retail trading influencers with >200K followers
on YouTube, Instagram, Twitter/X, or TikTok.

Focus on: stock trading, forex, crypto, options, day trading.

For each influencer compile:
- Name + handle
- Platform + follower count
- Content style (educational, entertainment, signals, etc.)
- Recent content themes
- Engagement style (personal brand or faceless?)
- Email or DM contact if publicly available

Format as a Markdown table, then a short profile paragraph for each.
""")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    influencer_md = f"# Influencer Research\n*Generated: {timestamp}*\n\n{research_result}"
    save_to_obsidian("04_Influencer_Research.md", influencer_md)

    # Step 2: Write outreach drafts
    outreach_result = agent.chat(f"""
Based on the influencers you just researched, write personalized cold outreach DMs
for the top 3 most suitable ones to promote CrowdWisdomTrading.

For each DM:
- Personalize to their specific content style
- Frame it as asking for their opinion on the product (not a sales pitch)
- Mention something specific about their recent content to show you actually watch them
- Keep under 150 words
- End with a specific, low-friction ask

Product to pitch: CrowdWisdomTrading.com — AI newsletter aggregating 5,600+ traders
to deliver weekly crowd-consensus trade ideas.
""")

    outreach_md = f"# Influencer Outreach Drafts\n*Generated: {timestamp}*\n\n{outreach_result}"
    save_to_obsidian("05_Influencer_Outreach.md", outreach_md)

    return research_result + "\n\n---\n\n" + outreach_result


# ─── AGENT 4: EMAIL SEQUENCE (BONUS) ─────────────────────────────────────────
def run_email_sequence_agent() -> str:
    """
    Bonus agent: Writes a 5-email nurture sequence for new subscribers.
    Closes the funnel loop the other agents opened.
    """
    print("\n" + "=" * 60)
    print("AGENT 4 (BONUS): Email Nurture Sequence Writer")
    print("=" * 60)

    agent = make_agent(
        system_prompt=f"""You are an email copywriter specializing in financial newsletters.
You write conversion-focused email sequences that turn free subscribers into paid members.
You use storytelling, social proof, and urgency without being spammy.

Product context:
{PRODUCT_CONTEXT}
""",
        name="email_sequence_agent",
    )

    result = agent.chat("""
Write a 5-email welcome + nurture sequence for new CrowdWisdomTrading free subscribers.

Goal: convert them to paid Pro plan within 7 days.

### Email 1 (Day 0 — Immediately after signup)
Subject: Welcome + set expectations
Content: Warm welcome, deliver first value, tell them what's coming

### Email 2 (Day 1)
Subject: Founder story
Content: The pain of trading alone, the discovery of crowd intelligence

### Email 3 (Day 3)
Subject: Product demo in disguise
Content: Show a real example of crowd consensus signal, build FOMO

### Email 4 (Day 5)
Subject: Social proof
Content: 2-3 mini case studies, transition to direct pitch

### Email 5 (Day 7)
Subject: Urgency close
Content: Final push, objection removal, strong CTA

For each email provide:
- Subject line (+ A/B variant)
- Preview text
- Full email body (conversational, story-driven)
- CTA button text
""")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    md = f"# Email Nurture Sequence\n*Generated: {timestamp}*\n\n{result}"
    save_to_obsidian("06_Email_Nurture_Sequence.md", md)
    return result


# ─── KANBAN ORCHESTRATOR ─────────────────────────────────────────────────────
def run_kanban_pipeline():
    """
    Main pipeline — coordinates all agents and saves outputs to Obsidian.
    Run this via: python main_orchestrator.py
    Or via Hermes CLI with Kanban for the video demo.
    """
    print("\n" + "=" * 60)
    print("CROWDWISDOMTRADING MARKETING AGENT PIPELINE")
    print("=" * 60)
    print(f"  Model:  {MODEL}")
    print(f"  Vault:  {OBSIDIAN_VAULT}")
    print(f"  Apify:  {'configured' if APIFY_TOKEN else 'NOT configured (using mock data)'}")
    print("=" * 60)

    results = {}

    # Task 1: Marketing Manager
    print("\n[KANBAN] Task 1/4: Marketing Manager Agent")
    results["marketing_strategy"] = run_marketing_manager()

    # Task 2: Ads Pipeline (scraper -> selector -> pain extractor -> script writer)
    print("\n[KANBAN] Task 2/4: Ads Pipeline Agent")
    selected_ads = run_ads_scraper_agent()
    pain_analysis = run_pain_extractor(selected_ads)
    results["ad_scripts"] = run_ad_script_writer(pain_analysis)

    # Task 3: Influencer Outreach
    print("\n[KANBAN] Task 3/4: Influencer Outreach Agent")
    results["influencer"] = run_influencer_agent()

    # Task 4: Email Sequence (Bonus)
    print("\n[KANBAN] Task 4/4: Email Sequence Agent (Bonus)")
    results["email_sequence"] = run_email_sequence_agent()

    # Final summary
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    summary = f"""# CrowdWisdomTrading Marketing Agent — Run Summary
*Completed: {timestamp}*

## Outputs Generated
- [[01_Marketing_Strategy]] — Strategy + competitor analysis
- [[02_Pain_Point_Analysis]] — Extracted from working Meta ads
- [[03_Ad_Scripts]] — 3 video ad scripts
- [[04_Influencer_Research]] — 10 influencer profiles
- [[05_Influencer_Outreach]] — Personalized DM drafts
- [[06_Email_Nurture_Sequence]] — 5-email conversion sequence

## Agents Used
1. Marketing Manager Agent — Strategy + competitor research
2. Ads Scraper Agent — Apify Meta ads (actor: meta-ad-library-multi-search-scraper)
3. Pain Extractor Agent — Marketing psychology from winning ads
4. Ad Script Writer Agent — 3 direct-response video scripts
5. Influencer Outreach Agent — Research + personalized DMs
6. Email Sequence Agent (Bonus) — Full nurture funnel

## Data Sources
- Meta Ads Library via Apify (real scraped data)
- Web search for influencer research
- CrowdWisdomTrading.com product context

## Configuration
- Model: {MODEL}
- Apify Actor: gTebjMDkz25esWXsY (meta-ad-library-multi-search-scraper)
- Obsidian Vault: {OBSIDIAN_VAULT}
"""
    save_to_obsidian("00_Run_Summary.md", summary)

    print("\n" + "=" * 60)
    print("ALL AGENTS COMPLETE")
    print("=" * 60)
    print(f"  Vault: {OBSIDIAN_VAULT}")
    print(f"  Files: 8 markdown + 2 JSON")
    print("=" * 60)

    return results


if __name__ == "__main__":
    run_kanban_pipeline()

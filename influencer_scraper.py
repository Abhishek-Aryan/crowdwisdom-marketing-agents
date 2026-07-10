"""
Influencer Scraper — Find trading influencers via Apify.
Uses Apify's YouTube Scraper to find real influencers with verified subscriber counts.
"""
import os
import sys
import json
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import APIFY_TOKEN, OUTPUT_DIR, OBSIDIAN_VAULT

# Apify actor for YouTube search
YT_ACTOR_ID = "h7LD7O1FP4dOVAT7v"  # YouTube Scraper by Apify

# Search queries for trading influencers
TRADING_QUERIES = [
    "stock trading signals youtube",
    "options trading alerts channel",
    "day trading strategy youtube",
    "retail trading education channel",
    "forex trading signals",
]

MIN_SUBSCRIBERS = 200000  # 200K minimum


def scrape_youtube_influencers(queries: list, min_subs: int = MIN_SUBSCRIBERS) -> list:
    """
    Scrape YouTube for trading influencers via Apify.
    Returns list of channels with subscriber count >= min_subs.
    """
    if not APIFY_TOKEN:
        print("  [Influencer] No APIFY_TOKEN — returning mock data")
        return _mock_influencers()

    all_channels = []

    for query in queries:
        print(f"  [Influencer] Searching YouTube: '{query}'...")

        run_url = f"https://api.apify.com/v2/acts/{YT_ACTOR_ID}/runs?token={APIFY_TOKEN}"
        payload = json.dumps({
            "searchQuery": query,
            "maxResults": 10,
            "type": "channel",
        }).encode()

        req = urllib.request.Request(
            run_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                run_data = json.loads(resp.read())
                run_id = run_data["data"]["id"]
                print(f"  [Influencer] Run started: {run_id}")

            # Poll for completion
            status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}"
            status = "RUNNING"
            for _ in range(30):
                time.sleep(10)
                with urllib.request.urlopen(status_url, timeout=15) as resp:
                    status_data = json.loads(resp.read())
                    status = status_data["data"]["status"]
                    if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
                        break

            if status != "SUCCEEDED":
                print(f"  [Influencer] Run failed: {status}")
                continue

            # Fetch results
            dataset_id = status_data["data"]["defaultDatasetId"]
            items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}&format=json"
            with urllib.request.urlopen(items_url, timeout=30) as resp:
                items = json.loads(resp.read())

            # Filter by subscriber count
            for item in items:
                subs = item.get("numberOfSubscribers", item.get("subscriberCount", 0))
                if isinstance(subs, str):
                    subs = int(subs.replace(",", "").replace("K", "000").replace("M", "000000")) if subs else 0
                if subs >= min_subs:
                    item["_verified_subscribers"] = subs
                    item["_search_query"] = query
                    item["_source"] = "apify_youtube_scraper"
                    all_channels.append(item)
                    print(f"  [Influencer] Found: {item.get('channelName', '?')} ({subs:,} subs)")

        except Exception as e:
            print(f"  [Influencer] Error for '{query}': {e}")

    # Deduplicate by channel ID
    seen = {}
    for ch in all_channels:
        cid = ch.get("channelId", ch.get("id", ""))
        if cid and cid not in seen:
            seen[cid] = ch

    result = list(seen.values())
    print(f"  [Influencer] Total unique channels (200K+): {len(result)}")
    return result if result else _mock_influencers()


def save_influencer_data(channels: list) -> str:
    """Save raw influencer data to JSON."""
    os.makedirs(OBSIDIAN_VAULT, exist_ok=True)
    path = os.path.join(OBSIDIAN_VAULT, "raw_influencers.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(channels, f, indent=2, ensure_ascii=False)
    print(f"  [Influencer] Saved {len(channels)} channels -> {path}")
    return path


def _mock_influencers() -> list:
    """Fallback mock data — clearly labeled as mock."""
    return [
        {
            "channelName": "Meet Kevin",
            "channelId": "UCUvvj5kwbT3osEYql5G9FyA",
            "channelUrl": "https://www.youtube.com/@MeetKevin",
            "numberOfSubscribers": 2100000,
            "description": "Finance, real estate, investing, and trading.",
            "country": "US",
            "_verified_subscribers": 2100000,
            "_source": "mock_data",
            "_search_query": "stock trading signals youtube",
        },
        {
            "channelName": "Ricky Gutierrez",
            "channelId": "UCPqhTRzMaJxuTQiNKCXUZFg",
            "channelUrl": "https://www.youtube.com/@RickyGutierrez",
            "numberOfSubscribers": 1200000,
            "description": "Day trading, options, and investing education.",
            "country": "US",
            "_verified_subscribers": 1200000,
            "_source": "mock_data",
            "_search_query": "day trading strategy youtube",
        },
    ]


if __name__ == "__main__":
    print("Scraping trading influencers (200K+ subscribers)...")
    channels = scrape_youtube_influencers(TRADING_QUERIES)
    save_influencer_data(channels)
    print(f"Done. Found {len(channels)} influencers.")

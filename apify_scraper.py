"""
Apify Scraper — Meta Ads Library scraping via Apify API.

This module handles:
1. Calling the Apify actor to scrape Meta Ads
2. Processing and filtering results
3. Selecting top ads by quality
"""
import os
import sys
import json
import time
import urllib.request
import urllib.parse
from typing import List, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import APIFY_TOKEN, APIFY_ACTOR_ID, OUTPUT_DIR, OBSIDIAN_VAULT


def scrape_meta_ads(keywords: List[str], max_ads: int = 25,
                    country: str = "US") -> List[Dict]:
    """
    Scrape Meta Ads Library via Apify.
    
    Args:
        keywords: Search keywords (e.g., ["stock trading signals"])
        max_ads: Maximum ads per keyword
        country: Country code
        
    Returns:
        List of ad dictionaries
    """
    if not APIFY_TOKEN:
        print("  [Apify] No APIFY_TOKEN set — returning mock data")
        return _mock_ads()

    all_ads = []

    for keyword in keywords:
        print(f"  [Apify] Scraping: '{keyword}'...")

        # Start actor run
        run_url = f"https://api.apify.com/v2/acts/{APIFY_ACTOR_ID}/runs?token={APIFY_TOKEN}"
        payload = json.dumps({
            "keywords": [keyword],
            "country": country,
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
                print(f"  [Apify] Run started: {run_id}")

            # Poll for completion
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
                continue

            # Fetch results
            dataset_id = status_data["data"]["defaultDatasetId"]
            items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}&format=json"
            with urllib.request.urlopen(items_url, timeout=30) as resp:
                items = json.loads(resp.read())

            for item in items:
                item["_search_keyword"] = keyword

            all_ads.extend(items)
            print(f"  [Apify] Got {len(items)} ads for '{keyword}'")

        except Exception as e:
            print(f"  [Apify] Error for '{keyword}': {e}")

    return all_ads if all_ads else _mock_ads()


def select_top_ads(ads: List[Dict], top_n: int = 10) -> List[Dict]:
    """
    Select top N ads by quality criteria.
    
    Args:
        ads: List of all scraped ads
        top_n: Number of top ads to select
        
    Returns:
        List of selected ads with 'why_selected' field
    """
    import re

    def score_ad(ad):
        score = 0
        body = (ad.get("body", ad.get("body_text", "")) or "").lower()

        # Hook strength
        hook_words = ["imagine", "what if", "stop", "never", "finally",
                      "discover", "secret", "here's why", "warning"]
        score += sum(2 for w in hook_words if w in body[:100])

        # Numbers and social proof
        numbers = re.findall(r'\$[\d,]+|[\d]+%|[\d]+k', body)
        score += min(len(numbers) * 2, 6)

        # Pain specificity
        pain_words = ["lose", "losing", "frustrated", "confused", "overwhelmed",
                      "tired of", "struggling", "fail", "bleeding"]
        score += sum(1 for w in pain_words if w in body)

        # Value proposition
        value_words = ["profit", "returns", "win rate", "accuracy", "signals",
                       "alerts", "portfolio", "grow", "wealth"]
        score += sum(1 for v in value_words if v in body)

        # Penalize very short
        if len(body) < 50:
            score -= 3

        return score

    # Deduplicate by brand/page
    seen = {}
    for ad in ads:
        brand = ad.get("pageName", ad.get("brand", "unknown"))
        if brand not in seen or score_ad(ad) > score_ad(seen[brand]):
            seen[brand] = ad

    # Score and sort
    unique_ads = list(seen.values())
    for ad in unique_ads:
        ad["_score"] = score_ad(ad)

    unique_ads.sort(key=lambda x: x["_score"], reverse=True)

    # Select top N
    selected = unique_ads[:top_n]

    # Add why_selected field
    for ad in selected:
        body = ad.get("body", ad.get("body_text", ""))[:200]
        ad["why_selected"] = f"Score {ad['_score']}: {body}..."

    return selected


def save_ads(raw_ads: List[Dict], selected_ads: List[Dict]):
    """Save ads to Obsidian vault and local output."""
    # Save raw ads
    raw_path = os.path.join(OBSIDIAN_VAULT, "raw_ads.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(raw_ads, f, indent=2, ensure_ascii=False)
    print(f"  [Obsidian] Saved → raw_ads.json ({len(raw_ads)} ads)")

    # Save selected ads
    sel_path = os.path.join(OBSIDIAN_VAULT, "selected_ads.json")
    with open(sel_path, "w", encoding="utf-8") as f:
        json.dump(selected_ads, f, indent=2, ensure_ascii=False)
    print(f"  [Obsidian] Saved → selected_ads.json ({len(selected_ads)} ads)")


def _mock_ads() -> List[Dict]:
    """Fallback mock data if Apify is unavailable."""
    return [
        {
            "id": "mock_001",
            "pageName": "TradingEdge Pro",
            "body": "Stop losing money trading alone. 97% of retail traders fail because they trade without consensus. Our AI aggregates 5000+ professional traders so you never miss the signal.",
            "startDate": "2026-06-01",
            "platforms": ["Facebook", "Instagram"],
        },
        {
            "id": "mock_002",
            "pageName": "SmartTrader Weekly",
            "body": "The trading secret Wall Street doesn't want you to know. Crowd intelligence beats single analysts 70% of the time. Join 50,000 traders getting weekly signals.",
            "startDate": "2026-06-15",
            "platforms": ["Facebook"],
        },
        {
            "id": "mock_003",
            "pageName": "CrowdWisdom",
            "body": "5,600 traders can't all be wrong. Stop trusting one guru. CrowdWisdom aggregates predictions from thousands of professional traders.",
            "startDate": "2026-07-01",
            "platforms": ["Facebook", "Instagram", "Messenger"],
        },
    ]

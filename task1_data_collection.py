import json
import os
import re
import time
from datetime import datetime

import requests


BASE_URL = "https://hacker-news.firebaseio.com/v0"
HEADERS = {"User-Agent": "TrendPulse/1.0"}
MAX_IDS = 500
MAX_PER_CATEGORY = 25


CATEGORIES = {
    "technology": ["AI", "software", "tech", "code", "computer", "data",
                   "cloud", "API", "GPU", "LLM"],
    "worldnews": ["war", "government", "country", "president", "election",
                  "climate", "attack", "global"],
    "sports": ["NFL", "NBA", "FIFA", "sport", "game", "team", "player",
               "league", "championship"],
    "science": ["research", "study", "space", "physics", "biology",
                "discovery", "NASA", "genome"],
    "entertainment": ["movie", "film", "music", "Netflix", "game", "book",
                      "show", "award", "streaming"],
}


def matches(title, keywords):

    for kw in keywords:
        if re.search(r"\b" + re.escape(kw) + r"\b", title, re.IGNORECASE):
            return True
    return False


def get_json(url):

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Request failed for {url}: {e}")
        return None


def main():

    ids = get_json(f"{BASE_URL}/topstories.json")
    if not ids:
        print("Could not fetch top story IDs. Exiting.")
        return
    ids = ids[:MAX_IDS]
    print(f"Fetched {len(ids)} story IDs. Fetching story details...")


    stories = []
    for story_id in ids:
        item = get_json(f"{BASE_URL}/item/{story_id}.json")
        if item and item.get("title"):
            stories.append(item)
    print(f"Retrieved details for {len(stories)} stories.")


    collected = []
    used_ids = set()
    for category, keywords in CATEGORIES.items():
        count = 0
        for item in stories:
            if count >= MAX_PER_CATEGORY:
                break
            if item["id"] in used_ids or not matches(item["title"], keywords):
                continue
            collected.append({
                "post_id": item.get("id"),
                "title": item.get("title"),
                "category": category,
                "score": item.get("score"),
                "num_comments": item.get("descendants", 0),
                "author": item.get("by"),
                "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
            used_ids.add(item["id"])
            count += 1
        print(f"  {category}: {count} stories")
        time.sleep(2)


    os.makedirs("data", exist_ok=True)
    filename = f"data/trends_{datetime.now().strftime('%Y%m%d')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(collected, f, indent=2, ensure_ascii=False)

    print(f"Collected {len(collected)} stories. Saved to {filename}")


if __name__ == "__main__":
    main()
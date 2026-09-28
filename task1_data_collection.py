import json
import os
import re
import time
from datetime import datetime

import requests

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
HEADERS = {"User-Agent": "TrendPulse/1.0"}

NUM_IDS_TO_FETCH = 500    
MAX_PER_CATEGORY = 25       
REQUEST_TIMEOUT = 10        


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


def build_patterns():
    """Pre-compile one case-insensitive regex per category.

    Word boundaries stop short keywords like "AI" from matching inside
    unrelated words (e.g. "said", "main"). An optional plural ending lets
    "sport" match "sports" and "study" match "studies" style variants.
    """
    patterns = {}
    for category, keywords in CATEGORIES.items():
        joined = "|".join(re.escape(k) for k in keywords)
        patterns[category] = re.compile(
            r"\b(?:" + joined + r")(?:s|es)?\b", re.IGNORECASE
        )
    return patterns


def fetch_json(url):
    """GET a URL and return parsed JSON, or None if the request fails."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as err:
        print(f"  Request failed for {url}: {err}")
        return None


def fetch_top_story_ids():
    """Step 1: return the first 500 top story IDs (empty list on failure)."""
    ids = fetch_json(TOP_STORIES_URL)
    if not ids:
        return []
    return ids[:NUM_IDS_TO_FETCH]


def fetch_stories(story_ids):
    """Step 2: fetch details for every story ID, skipping any that fail."""
    stories = []
    for i, story_id in enumerate(story_ids, start=1):
        story = fetch_json(ITEM_URL.format(id=story_id))
        
        if story and story.get("title") and not story.get("deleted") \
                and not story.get("dead"):
            stories.append(story)
        if i % 100 == 0:
            print(f"  Fetched {i}/{len(story_ids)} stories...")
    return stories


def extract_fields(story, category):
    """Keep only the 7 required fields for a story."""
    return {
        "post_id": story.get("id"),
        "title": story.get("title"),
        "category": category,
        "score": story.get("score", 0),
        "num_comments": story.get("descendants", 0), 
        "author": story.get("by"),
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }



def main():
    patterns = build_patterns()

    
    print("Fetching top story IDs...")
    story_ids = fetch_top_story_ids()
    if not story_ids:
        print("Could not fetch story IDs. Exiting.")
        return
    print(f"Got {len(story_ids)} story IDs.")

   
    print("Fetching story details (this may take a minute)...")
    stories = fetch_stories(story_ids)
    print(f"Retrieved {len(stories)} valid stories.")

    
    collected = []
    used_ids = set() 

    for category, pattern in patterns.items():
        count = 0
        for story in stories:
            if count >= MAX_PER_CATEGORY:
                break
            if story["id"] in used_ids:
                continue
            if pattern.search(story["title"]):
                collected.append(extract_fields(story, category))
                used_ids.add(story["id"])
                count += 1

        print(f"Category '{category}': {count} stories")
        time.sleep(2)  
        
   
    os.makedirs("data", exist_ok=True)
    filename = f"data/trends_{datetime.now().strftime('%Y%m%d')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(collected, f, indent=4, ensure_ascii=False)

    print(f"Collected {len(collected)} stories. Saved to {filename}")


if __name__ == "__main__":
    main()

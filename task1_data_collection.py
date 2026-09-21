"""
TrendPulse - Task 1: Fetch Data from API
------------------------------------------
Fetches top stories from the HackerNews public API, assigns each story to one
of 5 categories based on keyword matching in the title, and saves up to
25 stories per category (125 total) to a timestamped JSON file.

No API key / login required.
"""

import requests
import time
import json
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
HEADERS = {"User-Agent": "TrendPulse/1.0"}

NUM_TOP_IDS_TO_FETCH = 500       # how many top story IDs to pull
STORIES_PER_CATEGORY = 25        # cap per category
SLEEP_BETWEEN_CATEGORIES = 2     # seconds, once per category loop

# Category -> list of keywords (case-insensitive match against the title)
CATEGORY_KEYWORDS = {
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


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_top_story_ids(limit=NUM_TOP_IDS_TO_FETCH):
    """Fetch the list of top story IDs from HackerNews. Returns a list of ints."""
    try:
        response = requests.get(TOP_STORIES_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        ids = response.json()
        return ids[:limit]
    except requests.RequestException as e:
        print(f"Failed to fetch top story IDs: {e}")
        return []


def get_story_details(story_id):
    """Fetch a single story's details. Returns a dict, or None on failure."""
    url = ITEM_URL.format(id=story_id)
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Failed to fetch story {story_id}: {e}")
        return None


def match_category(title, category):
    """Return True if any of the category's keywords appear in the title
    (case-insensitive)."""
    if not title:
        return False
    title_lower = title.lower()
    keywords = CATEGORY_KEYWORDS[category]
    return any(keyword.lower() in title_lower for keyword in keywords)


def build_story_record(story, category):
    """Extract the 7 required fields from a raw HackerNews story object."""
    return {
        "post_id": story.get("id"),
        "title": story.get("title"),
        "category": category,
        "score": story.get("score", 0),
        "num_comments": story.get("descendants", 0),
        "author": story.get("by", "unknown"),
        "collected_at": datetime.now().isoformat(timespec="seconds"),
    }


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def collect_trends():
    story_ids = get_top_story_ids()

    if not story_ids:
        print("No story IDs retrieved. Exiting.")
        return []

    # Cache fetched story details so the same story isn't re-fetched
    # from the API multiple times while checking it against each category.
    story_cache = {}

    all_collected = []

    # Loop over each category. One sleep happens per category loop
    # (not per individual story fetch).
    for category in CATEGORY_KEYWORDS:
        category_stories = []

        for story_id in story_ids:
            # Stop once we've collected enough stories for this category
            if len(category_stories) >= STORIES_PER_CATEGORY:
                break

            # Use cached details if we already fetched this story for a
            # previous category, otherwise fetch it now.
            if story_id in story_cache:
                story = story_cache[story_id]
            else:
                story = get_story_details(story_id)
                story_cache[story_id] = story

            if story is None:
                # Fetch failed - already printed a message, just move on
                continue

            title = story.get("title", "")

            if match_category(title, category):
                record = build_story_record(story, category)
                category_stories.append(record)

        all_collected.extend(category_stories)
        print(f"Category '{category}': collected {len(category_stories)} stories.")

        # One sleep per category loop, as required
        time.sleep(SLEEP_BETWEEN_CATEGORIES)

    return all_collected


def save_to_json(stories):
    """Save the collected stories to data/trends_YYYYMMDD.json."""
    os.makedirs("data", exist_ok=True)

    filename = f"data/trends_{datetime.now().strftime('%Y%m%d')}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(stories, f, indent=2, ensure_ascii=False)

    print(f"Collected {len(stories)} stories. Saved to {filename}")


if __name__ == "__main__":
    stories = collect_trends()
    save_to_json(stories)

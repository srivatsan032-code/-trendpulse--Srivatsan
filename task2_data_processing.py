"""
TrendPulse - Task 2: Clean the Data and Save as CSV

NOTE ON SCOPE: no official Task 2 rubric/spec was provided beyond the
pipeline label "Clean CSV". The cleaning rules below are reasonable
assumptions, clearly commented, and should be adjusted if a real spec
becomes available.

Loads the most recent data/trends_*.json file produced by Task 1, cleans it,
and saves the result as data/trends_clean_YYYYMMDD.csv

Cleaning rules (assumed):
  - Load the most recently modified data/trends_*.json file
  - Drop rows with a missing/empty title or category
  - Drop duplicate post_id rows (keep the first occurrence)
  - Fill missing score / num_comments with 0 and cast to int
  - Strip leading/trailing whitespace from title and author
  - Fill missing author with "unknown"
  - Save as CSV with the same 7 columns, in a stable column order
"""

import csv
import glob
import json
import os
from datetime import datetime

DATA_DIR = "data"
REQUIRED_COLUMNS = [
    "post_id", "title", "category", "score",
    "num_comments", "author", "collected_at",
]


def find_latest_json():
    """Return the path to the most recently modified trends_*.json file."""
    pattern = os.path.join(DATA_DIR, "trends_*.json")
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def load_stories(path):
    """Load the JSON file into a list of story dicts."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def clean_stories(stories):
    """Apply cleaning rules and return (clean_list, stats dict)."""
    stats = {
        "input_count": len(stories),
        "dropped_missing_fields": 0,
        "dropped_duplicates": 0,
    }

    seen_ids = set()
    cleaned = []

    for story in stories:
        title = (story.get("title") or "").strip()
        category = (story.get("category") or "").strip()
        post_id = story.get("post_id")

        # Drop rows missing essential fields
        if not title or not category or post_id is None:
            stats["dropped_missing_fields"] += 1
            continue

        # Drop duplicate post_id rows (keep first occurrence)
        if post_id in seen_ids:
            stats["dropped_duplicates"] += 1
            continue
        seen_ids.add(post_id)

        author = (story.get("author") or "").strip() or "unknown"

        # Coerce numeric fields, defaulting to 0 if missing/invalid
        try:
            score = int(story.get("score") or 0)
        except (TypeError, ValueError):
            score = 0
        try:
            num_comments = int(story.get("num_comments") or 0)
        except (TypeError, ValueError):
            num_comments = 0

        cleaned.append({
            "post_id": post_id,
            "title": title,
            "category": category,
            "score": score,
            "num_comments": num_comments,
            "author": author,
            "collected_at": story.get("collected_at", ""),
        })

    stats["output_count"] = len(cleaned)
    return cleaned, stats


def save_csv(stories, path):
    """Write the cleaned stories to a CSV file with a fixed column order."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(stories)


def main():
    latest_json = find_latest_json()
    if not latest_json:
        print(f"No trends_*.json file found in {DATA_DIR}/. Run Task 1 first.")
        return

    print(f"Loading {latest_json}...")
    stories = load_stories(latest_json)

    cleaned, stats = clean_stories(stories)

    os.makedirs(DATA_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")

    csv_path = os.path.join(DATA_DIR, f"trends_clean_{date_str}.csv")
    save_csv(cleaned, csv_path)

    print(f"Input rows: {stats['input_count']}")
    print(f"Dropped (missing fields): {stats['dropped_missing_fields']}")
    print(f"Dropped (duplicates): {stats['dropped_duplicates']}")
    print(f"Cleaned rows: {stats['output_count']}")
    print(f"Saved cleaned CSV to {csv_path}")


if __name__ == "__main__":
    main()

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
   
    pattern = os.path.join(DATA_DIR, "trends_*.json")
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def load_stories(path):
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def clean_stories(stories):
    
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

        
        if not title or not category or post_id is None:
            stats["dropped_missing_fields"] += 1
            continue

        
        if post_id in seen_ids:
            stats["dropped_duplicates"] += 1
            continue
        seen_ids.add(post_id)

        author = (story.get("author") or "").strip() or "unknown"

        
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

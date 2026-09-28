import glob
import json
import os
from datetime import datetime

import numpy as np
import pandas as pd

DATA_DIR = "data"


def find_latest_csv():
    
    pattern = os.path.join(DATA_DIR, "trends_clean_*.csv")
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def load_dataframe(path):
    
    return pd.read_csv(path)


def analyse_stories(df):
    
    if df.empty:
        return {"total_stories": 0}

   
    df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0)
    df["num_comments"] = pd.to_numeric(
        df["num_comments"], errors="coerce"
    ).fillna(0)

    
    category_counts = df["category"].value_counts().to_dict()

    
    category_stats = {}
    for category, group in df.groupby("category"):
        category_stats[category] = {
            "count": int(len(group)),
            "mean_score": round(float(np.mean(group["score"])), 2),
            "median_score": round(float(np.median(group["score"])), 2),
            "mean_comments": round(float(np.mean(group["num_comments"])), 2),
            "median_comments": round(
                float(np.median(group["num_comments"])), 2
            ),
        }

    
    top_stories = (
        df.sort_values("score", ascending=False)
        .head(5)[["post_id", "title", "category", "score"]]
        .to_dict(orient="records")
    )

    
    author_counts = df["author"].value_counts()
    most_active_author = {
        "author": str(author_counts.index[0]),
        "story_count": int(author_counts.iloc[0]),
    } if not author_counts.empty else None

    return {
        "total_stories": int(len(df)),
        "stories_per_category": {k: int(v) for k, v in category_counts.items()},
        "stats_per_category": category_stats,
        "top_5_stories_by_score": top_stories,
        "most_active_author": most_active_author,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def save_summary(summary, path):
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)


def main():
    latest_csv = find_latest_csv()
    if not latest_csv:
        print(f"No trends_clean_*.csv file found in {DATA_DIR}/. Run Task 2 first.")
        return

    print(f"Loading {latest_csv}...")
    df = load_dataframe(latest_csv)

    summary = analyse_stories(df)

    os.makedirs(DATA_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    summary_path = os.path.join(DATA_DIR, f"trends_summary_{date_str}.json")
    save_summary(summary, summary_path)

    print(f"Analysed {summary.get('total_stories', 0)} stories.")
    print(f"Saved analysis summary to {summary_path}")


if __name__ == "__main__":
    main()

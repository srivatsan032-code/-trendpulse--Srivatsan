"""
TrendPulse - Task 3: NumPy/Pandas Analysis

NOTE ON SCOPE: no official Task 3 rubric/spec was provided beyond the
pipeline label "NumPy/Pandas". The analysis below is a reasonable,
clearly-commented set of assumptions and should be adjusted if a real
spec becomes available.

Loads the most recent data/trends_clean_*.csv file produced by Task 2,
runs a NumPy/Pandas analysis, and saves the results as
data/trends_summary_YYYYMMDD.json

Analysis performed (assumed):
  - Total story count
  - Story count per category
  - Mean and median score per category
  - Mean and median comment count per category
  - Top 5 stories overall by score
  - Most active author (most stories submitted) and their story count
"""

import glob
import json
import os
from datetime import datetime

import numpy as np
import pandas as pd

DATA_DIR = "data"


def find_latest_csv():
    """Return the path to the most recently modified trends_clean_*.csv file."""
    pattern = os.path.join(DATA_DIR, "trends_clean_*.csv")
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def load_dataframe(path):
    """Load the cleaned CSV into a pandas DataFrame."""
    return pd.read_csv(path)


def analyse_stories(df):
    """Run a NumPy/Pandas analysis on the cleaned stories DataFrame.

    Returns a JSON-serialisable dict of summary statistics.
    """
    if df.empty:
        return {"total_stories": 0}

    # Make sure numeric columns are actually numeric for NumPy/pandas ops
    df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0)
    df["num_comments"] = pd.to_numeric(
        df["num_comments"], errors="coerce"
    ).fillna(0)

    # --- Per-category counts -------------------------------------------
    category_counts = df["category"].value_counts().to_dict()

    # --- Per-category score / comment stats (mean + median via NumPy) --
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

    # --- Top 5 stories overall by score ---------------------------------
    top_stories = (
        df.sort_values("score", ascending=False)
        .head(5)[["post_id", "title", "category", "score"]]
        .to_dict(orient="records")
    )

    # --- Most active author ---------------------------------------------
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
    """Write the analysis summary to a JSON file."""
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

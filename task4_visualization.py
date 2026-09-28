import glob
import os
from datetime import datetime

import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt
import pandas as pd

DATA_DIR = "data"


def find_latest_csv():
    
    pattern = os.path.join(DATA_DIR, "trends_clean_*.csv")
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def load_dataframe(path):
    
    df = pd.read_csv(path)
    df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0)
    return df


def plot_stories_per_category(df, out_path):
    
    counts = df["category"].value_counts().sort_index()

    plt.figure(figsize=(8, 5))
    counts.plot(kind="bar", color="#4C72B0")
    plt.title("Number of Stories per Category")
    plt.xlabel("Category")
    plt.ylabel("Story Count")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_avg_score_per_category(df, out_path):
    
    avg_scores = df.groupby("category")["score"].mean().sort_index()

    plt.figure(figsize=(8, 5))
    avg_scores.plot(kind="bar", color="#DD8452")
    plt.title("Average Score per Category")
    plt.xlabel("Category")
    plt.ylabel("Average Score")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def main():
    latest_csv = find_latest_csv()
    if not latest_csv:
        print(f"No trends_clean_*.csv file found in {DATA_DIR}/. Run Task 2 first.")
        return

    print(f"Loading {latest_csv}...")
    df = load_dataframe(latest_csv)

    os.makedirs(DATA_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")

    stories_chart_path = os.path.join(
        DATA_DIR, f"chart_stories_per_category_{date_str}.png"
    )
    plot_stories_per_category(df, stories_chart_path)
    print(f"Saved chart: {stories_chart_path}")

    score_chart_path = os.path.join(
        DATA_DIR, f"chart_avg_score_per_category_{date_str}.png"
    )
    plot_avg_score_per_category(df, score_chart_path)
    print(f"Saved chart: {score_chart_path}")


if __name__ == "__main__":
    main()

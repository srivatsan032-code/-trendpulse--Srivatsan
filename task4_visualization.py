"""
TrendPulse - Task 4: Visualization
Builds two charts from the cleaned trending data:
 1. Bar chart of the latest snapshot's top trending coins by trend score
 2. Bar chart of how many times each coin has appeared in trending, overall
Saved as PNG files.
"""

import os
import sys

import matplotlib
matplotlib.use("Agg")  # safe for headless environments
import matplotlib.pyplot as plt
import pandas as pd

CLEAN_FILE = os.path.join("data", "cleaned_trending.csv")
OUTPUT_DIR = "visualizations"


def load_clean_data(path: str = CLEAN_FILE) -> pd.DataFrame:
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"{path} not found. Run task2_data_processing.py first."
        )
    return pd.read_csv(path, parse_dates=["collected_at"])


def plot_latest_snapshot(df: pd.DataFrame, output_dir: str = OUTPUT_DIR) -> str:
    latest_run = df["collected_at"].max()
    latest = (
        df[df["collected_at"] == latest_run]
        .sort_values("trend_score", ascending=False)
        .head(10)
    )

    plt.figure(figsize=(10, 6))
    plt.barh(latest["name"], latest["trend_score"], color="#4C72B0")
    plt.xlabel("Trend Score")
    plt.title(f"Top Trending Coins - {latest_run}")
    plt.gca().invert_yaxis()
    plt.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "latest_trending_snapshot.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def plot_trending_frequency(df: pd.DataFrame, output_dir: str = OUTPUT_DIR) -> str:
    freq = df.groupby("name").size().sort_values(ascending=False).head(10)

    plt.figure(figsize=(10, 6))
    freq.sort_values().plot(kind="barh", color="#DD8452")
    plt.xlabel("Times Appeared in Trending List")
    plt.title("Most Frequently Trending Coins (All Runs)")
    plt.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "trending_frequency.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def main():
    try:
        df = load_clean_data()
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    snapshot_path = plot_latest_snapshot(df)
    frequency_path = plot_trending_frequency(df)
    print(f"Saved chart: {snapshot_path}")
    print(f"Saved chart: {frequency_path}")


if __name__ == "__main__":
    main()

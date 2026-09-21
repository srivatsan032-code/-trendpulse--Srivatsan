"""
TrendPulse - Task 3: Analysis
Analyses the cleaned trending data and produces summary statistics:
 - most frequently trending coins across all collection runs
 - average market cap rank and score
 - the latest snapshot's top trending coins
Outputs a JSON summary plus a printed report.
"""

import json
import os
import sys

import pandas as pd

CLEAN_FILE = os.path.join("data", "cleaned_trending.csv")
SUMMARY_FILE = os.path.join("analysis", "summary.json")


def load_clean_data(path: str = CLEAN_FILE) -> pd.DataFrame:
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"{path} not found. Run task2_data_processing.py first."
        )
    return pd.read_csv(path, parse_dates=["collected_at"])


def analyse(df: pd.DataFrame) -> dict:
    latest_run = df["collected_at"].max()
    latest_snapshot = df[df["collected_at"] == latest_run].sort_values(
        "trend_score", ascending=False
    )

    most_frequent = (
        df.groupby(["id", "name", "symbol"])
        .size()
        .reset_index(name="times_trending")
        .sort_values("times_trending", ascending=False)
        .head(5)
    )

    summary = {
        "total_records": int(len(df)),
        "unique_coins": int(df["id"].nunique()),
        "collection_runs": int(df["collected_at"].nunique()),
        "average_market_cap_rank": round(float(df["market_cap_rank"].mean()), 2),
        "average_score": round(float(df["score"].mean()), 2),
        "latest_run_timestamp": str(latest_run),
        "top_5_latest_snapshot": latest_snapshot[
            ["name", "symbol", "market_cap_rank", "trend_score"]
        ].head(5).to_dict(orient="records"),
        "most_frequently_trending": most_frequent.to_dict(orient="records"),
    }
    return summary


def save_summary(summary: dict, path: str = SUMMARY_FILE) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"Saved analysis summary to {path}")


def print_report(summary: dict) -> None:
    print("\n=== TrendPulse Analysis Report ===")
    print(f"Total records analysed : {summary['total_records']}")
    print(f"Unique coins seen      : {summary['unique_coins']}")
    print(f"Collection runs        : {summary['collection_runs']}")
    print(f"Avg market cap rank    : {summary['average_market_cap_rank']}")
    print(f"Avg trending score     : {summary['average_score']}")
    print("\nTop trending coins (latest run):")
    for coin in summary["top_5_latest_snapshot"]:
        print(
            f"  - {coin['name']} ({coin['symbol']}) | "
            f"rank {coin['market_cap_rank']} | trend_score {coin['trend_score']}"
        )
    print("\nMost frequently trending coins overall:")
    for coin in summary["most_frequently_trending"]:
        print(f"  - {coin['name']} ({coin['symbol']}): trended {coin['times_trending']} time(s)")


def main():
    try:
        df = load_clean_data()
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    summary = analyse(df)
    save_summary(summary)
    print_report(summary)


if __name__ == "__main__":
    main()

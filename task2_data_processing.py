"""
TrendPulse - Task 2: Data Processing
Cleans and standardises the raw trending data collected in Task 1:
 - drops incomplete rows
 - fixes data types
 - removes duplicate coins from the same collection run
 - derives a few convenience columns
"""

import os
import sys

import pandas as pd

RAW_FILE = os.path.join("data", "raw_trending.csv")
CLEAN_FILE = os.path.join("data", "cleaned_trending.csv")


def load_raw_data(path: str = RAW_FILE) -> pd.DataFrame:
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"{path} not found. Run task1_data_collection.py first."
        )
    return pd.read_csv(path)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Drop rows missing an identifier or name - unusable for analysis
    df = df.dropna(subset=["id", "name", "symbol"])

    # Normalise text fields
    df["name"] = df["name"].str.strip()
    df["symbol"] = df["symbol"].str.upper().str.strip()

    # Coerce numeric columns; invalid values become NaN then get filled
    numeric_cols = ["market_cap_rank", "price_btc", "score"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Unranked coins get pushed to the bottom instead of being dropped
    df["market_cap_rank"] = df["market_cap_rank"].fillna(df["market_cap_rank"].max() + 1)
    df["price_btc"] = df["price_btc"].fillna(0.0)
    df["score"] = df["score"].fillna(0)

    # Remove duplicate coin entries collected within the same run
    df = df.drop_duplicates(subset=["collected_at", "id"])

    # Derived column: convenience rank score (higher = more trending)
    df["trend_score"] = df["score"].max() - df["score"] + 1

    df["collected_at"] = pd.to_datetime(df["collected_at"], errors="coerce")

    return df.reset_index(drop=True)


def save_clean_data(df: pd.DataFrame, path: str = CLEAN_FILE) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved {len(df)} cleaned records to {path}")


def main():
    try:
        raw_df = load_raw_data()
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    clean_df = clean_data(raw_df)
    save_clean_data(clean_df)


if __name__ == "__main__":
    main()

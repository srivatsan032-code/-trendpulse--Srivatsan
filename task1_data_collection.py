"""
TrendPulse - Task 1: Data Collection
Fetches live trending cryptocurrency data from the CoinGecko public API
(no API key required) and saves the raw results to a CSV file.
"""

import csv
import os
import sys
from datetime import datetime, timezone

import requests

API_URL = "https://api.coingecko.com/api/v3/search/trending"
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "raw_trending.csv")


def fetch_trending_data(url: str = API_URL, timeout: int = 15) -> list:
    """Fetch trending coin data from the CoinGecko API.

    Returns a list of dicts, one per trending coin.
    Raises requests.RequestException on network/API failure.
    """
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    coins = payload.get("coins", [])
    return [coin.get("item", {}) for coin in coins]


def save_raw_data(records: list, output_file: str = OUTPUT_FILE) -> None:
    """Append the fetched records to a CSV file, tagging each row with
    the UTC timestamp of collection so historical runs can be compared."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    if not records:
        print("No trending records returned; nothing to save.")
        return

    collected_at = datetime.now(timezone.utc).isoformat()
    fieldnames = [
        "collected_at", "id", "coin_id", "name", "symbol",
        "market_cap_rank", "price_btc", "score",
    ]

    file_exists = os.path.isfile(output_file)
    with open(output_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for item in records:
            writer.writerow({
                "collected_at": collected_at,
                "id": item.get("id"),
                "coin_id": item.get("coin_id"),
                "name": item.get("name"),
                "symbol": item.get("symbol"),
                "market_cap_rank": item.get("market_cap_rank"),
                "price_btc": item.get("price_btc"),
                "score": item.get("score"),
            })
    print(f"Saved {len(records)} trending records to {output_file}")


def main():
    try:
        records = fetch_trending_data()
    except requests.RequestException as exc:
        print(f"Failed to fetch trending data: {exc}", file=sys.stderr)
        sys.exit(1)

    save_raw_data(records)


if __name__ == "__main__":
    main()

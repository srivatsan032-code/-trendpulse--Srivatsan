import glob
import os

import pandas as pd


files = sorted(glob.glob("data/trends_*.json"))
if not files:
    raise SystemExit("No data/trends_*.json found. Run task1_data_collection.py first.")
json_file = files[-1]

df = pd.read_json(json_file)
print(f"Loaded {len(df)} stories from {json_file}\n")


df = df.drop_duplicates(subset="post_id")
print(f"After removing duplicates: {len(df)}")


df = df.dropna(subset=["post_id", "title", "score"])
print(f"After removing nulls: {len(df)}")


df["score"] = df["score"].astype(int)
df["num_comments"] = df["num_comments"].fillna(0).astype(int)


df = df[df["score"] >= 5]
print(f"After removing low scores: {len(df)}")


df["title"] = df["title"].str.strip().str.replace(r"\s+", " ", regex=True)


os.makedirs("data", exist_ok=True)
df.to_csv("data/trends_clean.csv", index=False)
print(f"\nSaved {len(df)} rows to data/trends_clean.csv")


print("\nStories per category:")
for category, count in df["category"].value_counts().items():
    print(f"  {category:<15}{count}")
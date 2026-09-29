import numpy as np
import pandas as pd


df = pd.read_csv("data/trends_clean.csv")
print(f"Loaded data: {df.shape}\n")
print("First 5 rows:")
print(df.head(), "\n")
print(f"Average score   : {df['score'].mean():,.0f}")
print(f"Average comments: {df['num_comments'].mean():,.0f}\n")


scores = df["score"].to_numpy()
print("--- NumPy Stats ---")
print(f"Mean score   : {np.mean(scores):,.0f}")
print(f"Median score : {np.median(scores):,.0f}")
print(f"Std deviation: {np.std(scores):,.0f}")
print(f"Max score    : {np.max(scores):,}")
print(f"Min score    : {np.min(scores):,}\n")


counts = df["category"].value_counts()
print(f"Most stories in: {counts.idxmax()} ({counts.max()} stories)\n")


top = df.iloc[np.argmax(df["num_comments"].to_numpy())]
print(f"Most commented story: \"{top['title']}\"  - {top['num_comments']:,} comments\n")


df["engagement"] = df["num_comments"] / (df["score"] + 1)
df["is_popular"] = df["score"] > df["score"].mean()


df.to_csv("data/trends_analysed.csv", index=False)
print("Saved to data/trends_analysed.csv")
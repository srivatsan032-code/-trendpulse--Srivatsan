import os

import matplotlib.pyplot as plt
import pandas as pd


df = pd.read_csv("data/trends_analysed.csv")
os.makedirs("outputs", exist_ok=True)


def shorten(title, n=50):

    return title if len(title) <= n else title[: n - 3] + "..."


def draw_top_stories(ax):

    top = df.nlargest(10, "score").iloc[::-1]
    ax.barh([shorten(t) for t in top["title"]], top["score"], color="steelblue")
    ax.set_title("Top 10 Stories by Score")
    ax.set_xlabel("Score (upvotes)")
    ax.set_ylabel("Story title")


def draw_categories(ax):

    counts = df["category"].value_counts()
    colours = ["#4c72b0", "#dd8452", "#55a868", "#c44e52", "#8172b3"]
    ax.bar(counts.index, counts.values, color=colours[: len(counts)])
    ax.set_title("Stories per Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Number of stories")
    ax.tick_params(axis="x", rotation=30)


def draw_scatter(ax):

    popular = df[df["is_popular"]]
    other = df[~df["is_popular"]]
    ax.scatter(other["score"], other["num_comments"], c="grey", alpha=0.6, label="Not popular")
    ax.scatter(popular["score"], popular["num_comments"], c="crimson", alpha=0.7, label="Popular")
    ax.set_title("Score vs Comments")
    ax.set_xlabel("Score (upvotes)")
    ax.set_ylabel("Number of comments")
    ax.legend()



charts = [
    (draw_top_stories, "outputs/chart1_top_stories.png", (11, 6)),
    (draw_categories, "outputs/chart2_categories.png", (8, 5)),
    (draw_scatter, "outputs/chart3_scatter.png", (8, 5)),
]
for draw, path, size in charts:
    fig, ax = plt.subplots(figsize=size)
    draw(ax)
    fig.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Saved {path}")


fig, axes = plt.subplots(1, 3, figsize=(24, 7))
draw_top_stories(axes[0])
draw_categories(axes[1])
draw_scatter(axes[2])
fig.suptitle("TrendPulse Dashboard", fontsize=20)
fig.tight_layout()
plt.savefig("outputs/dashboard.png", dpi=150)
print("Saved outputs/dashboard.png")
plt.show()
# TrendPulse: What's Actually Trending Right Now

A 4-step data pipeline that collects trending HackerNews stories, cleans them, analyses them and visualises the results.

```
Task 1 (JSON)  ->  Task 2 (CSV)  ->  Task 3 (Analysis)  ->  Task 4 (Charts)
```

## Setup

```bash
pip install requests pandas numpy matplotlib
```

## Run (in order)

| Step | Script | Input | Output |
|------|--------|-------|--------|
| 1 | `task1_data_collection.py` | HackerNews API | `data/trends_YYYYMMDD.json` |
| 2 | `task2_data_processing.py` | the JSON file | `data/trends_clean.csv` |
| 3 | `task3_analysis.py` | `trends_clean.csv` | `data/trends_analysed.csv` |
| 4 | `task4_visualization.py` | `trends_analysed.csv` | `outputs/*.png` |

```bash
python task1_data_collection.py
python task2_data_processing.py
python task3_analysis.py
python task4_visualization.py
```

## What each step does

1. **Collect** - Fetches the top 500 story IDs from the HackerNews API, then each story's details. Stories are grouped into `technology`, `worldnews`, `sports`, `science` and `entertainment` by keyword matching on the title (up to 25 per category). Each story is placed in one category only.
2. **Clean** - Removes duplicates, missing values and low-quality stories (score < 5), fixes data types and strips whitespace from titles.
3. **Analyse** - Computes mean, median, standard deviation, max and min score with NumPy, finds the top category and most-commented story, and adds `engagement` (comments per upvote) and `is_popular` (score above average) columns.
4. **Visualise** - Creates a top-10 stories bar chart, a stories-per-category bar chart, a score vs comments scatter plot, and a combined `dashboard.png`.

## Output files

```
data/
  trends_YYYYMMDD.json
  trends_clean.csv
  trends_analysed.csv
outputs/
  chart1_top_stories.png
  chart2_categories.png
  chart3_scatter.png
  dashboard.png
```

## Notes

- The HackerNews API needs no key or login.
- Task 1 waits 2 seconds between categories to be polite to the API.
- Category counts depend on what is trending at the time you run it, so some categories may have fewer than 25 stories.

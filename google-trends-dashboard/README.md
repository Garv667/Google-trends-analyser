# 📈 Google Search Trends Dashboard

A Streamlit dashboard that visualizes Google Trends data using [Pytrends](https://github.com/GeneralMills/pytrends),
the unofficial Python API for Google Trends.

## Features

- **Interest over time** — line chart of search popularity for up to 5 keywords
- **Interest by region** — bar chart + world choropleth map
- **Related queries** — top and rising queries for each keyword
- **Keyword suggestions** — related keyword ideas from Google

## Project structure

```
google-trends-dashboard/
├── app.py              # Main Streamlit app
├── requirements.txt    # Pinned Python dependencies
├── runtime.txt         # Pinned Python version (for Streamlit Cloud)
├── .gitignore
└── README.md
```

## Run locally

```bash
git clone <your-repo-url>
cd google-trends-dashboard
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## Deploy on Streamlit Community Cloud

1. Push this folder to a GitHub repository (see below).
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **New app**.
3. Select your repo, branch (`main`), and set **Main file path** to `app.py`.
4. Deploy. `requirements.txt` and `runtime.txt` are picked up automatically.

### Notes on deployment reliability

- `runtime.txt` pins the Python version to `3.12` so the cloud build matches what
  this project was tested against — avoids "works locally, breaks on deploy" issues
  caused by version drift.
- `requirements.txt` uses **exact pinned versions** (not ranges) for every dependency,
  including transitive ones prone to conflicts (`urllib3`, `numpy`). This avoids pip
  silently resolving to an incompatible combination on a fresh cloud build.
- Pytrends talks directly to Google Trends and has no official rate-limit guarantee.
  If you see `429` errors or empty results after repeated runs, wait a few minutes
  before retrying — this is a Google Trends-side limit, not a bug in the app.

## Uploading to GitHub

```bash
cd google-trends-dashboard
git init
git add .
git commit -m "Initial commit: Google Trends dashboard"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

## Data source

Built following the approach described in
[Google Search Analysis with Python (GeeksforGeeks)](https://www.geeksforgeeks.org/python/google-search-analysis-with-python/),
extended into a full interactive dashboard.

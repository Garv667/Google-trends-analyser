# 📈 Google Trends Analyzer

A Streamlit web app for exploring Google search interest data — built with [pytrends](https://github.com/GeneralMills/pytrends) (unofficial Google Trends API) and [Plotly](https://plotly.com/python/).

**🔗 Live demo:** _add your Streamlit Cloud link here after deploying_

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

- **Interest over time** — compare up to 5 keywords across a configurable timeframe (past hour to all-time), plotted as an interactive line chart
- **Interest by region** — see which countries, regions, or cities search a keyword most, with adjustable resolution and top-N filtering
- **Related queries & topics** — surface "top" and "rising" queries/topics Google associates with each keyword
- **Keyword suggestions** — get related keyword ideas straight from Google's autosuggest
- **CSV export** of the raw time-series data
- Cached API calls (`st.cache_data`) and a retry wrapper to soften Google Trends' rate limiting

## Screenshots

_Add 1–2 screenshots or a GIF here after running the app locally — this is the first thing recruiters look at._

```
![screenshot](assets/screenshot.png)
```

## Tech stack

- **Streamlit** — UI and app framework
- **pytrends** — unofficial Python client for Google Trends
- **Plotly Express** — interactive charts
- **Pandas** — data wrangling

## Getting started

### 1. Clone and install

```bash
git clone https://github.com/<your-username>/google-trends-analyzer.git
cd google-trends-analyzer
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run locally

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

### 3. Deploy on Streamlit Community Cloud (free)

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. Click **New app**, select this repo/branch, and set the main file to `app.py`.
4. Click **Deploy**. Add the resulting URL to this README's "Live demo" link.

## Project structure

```
google-trends-analyzer/
├── app.py              # Streamlit app (all logic + UI)
├── requirements.txt    # Python dependencies
├── .gitignore
└── README.md
```

## Notes & limitations

- Google Trends data is **relative search interest (0–100)**, not absolute search volume.
- `pytrends` scrapes an unofficial endpoint, so Google may rate-limit (HTTP 429) or occasionally change the response format — the app retries automatically but can still fail under heavy use.
- For production use at scale, consider a paid trends/search-data API instead.

## Possible extensions

- Add a world choropleth map for regional interest (Plotly `px.choropleth`)
- Schedule daily snapshots and store history in a database
- Add sentiment/news correlation for spikes in interest

## License

MIT — feel free to fork and adapt for your own portfolio.

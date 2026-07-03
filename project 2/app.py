"""
Google Trends Analyzer
A Streamlit dashboard for exploring Google search interest data using pytrends.
"""

import time

import pandas as pd
import plotly.express as px
import streamlit as st
from pytrends.request import TrendReq

# ------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Google Trends Analyzer",
    page_icon="📈",
    layout="wide",
)

TIMEFRAME_OPTIONS = {
    "Past hour": "now 1-H",
    "Past 4 hours": "now 4-H",
    "Past day": "now 1-d",
    "Past 7 days": "now 7-d",
    "Past 30 days": "today 1-m",
    "Past 90 days": "today 3-m",
    "Past 12 months": "today 12-m",
    "Past 5 years": "today 5-y",
    "2004 - present": "all",
}


# ------------------------------------------------------------------
# Cached pytrends helpers
# ------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_pytrends_client():
    return TrendReq(hl="en-US", tz=360)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_interest_over_time(keywords, timeframe, geo):
    pytrends = get_pytrends_client()
    pytrends.build_payload(keywords, timeframe=timeframe, geo=geo)
    df = pytrends.interest_over_time()
    if not df.empty and "isPartial" in df.columns:
        df = df.drop(columns=["isPartial"])
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_interest_by_region(keywords, timeframe, geo, resolution):
    pytrends = get_pytrends_client()
    pytrends.build_payload(keywords, timeframe=timeframe, geo=geo)
    df = pytrends.interest_by_region(resolution=resolution, inc_low_vol=True, inc_geo_code=True)
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_related_queries(keywords, timeframe, geo):
    pytrends = get_pytrends_client()
    pytrends.build_payload(keywords, timeframe=timeframe, geo=geo)
    return pytrends.related_queries()


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_related_topics(keywords, timeframe, geo):
    pytrends = get_pytrends_client()
    pytrends.build_payload(keywords, timeframe=timeframe, geo=geo)
    return pytrends.related_topics()


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_suggestions(keyword):
    pytrends = get_pytrends_client()
    return pytrends.suggestions(keyword=keyword)


def safe_call(fn, *args, retries=3, **kwargs):
    """Retry wrapper — Google Trends rate-limits aggressively (HTTP 429)."""
    last_err = None
    for attempt in range(retries + 1):
        try:
            return fn(*args, **kwargs), None
        except Exception as e:  # noqa: BLE001
            last_err = e
            if attempt < retries:
                time.sleep(3 * (attempt + 1))  # 3s, 6s, 9s backoff
    return None, last_err


# ------------------------------------------------------------------
# Sidebar controls
# ------------------------------------------------------------------
st.sidebar.title("📈 Google Trends Analyzer")
st.sidebar.caption("Search interest analysis powered by pytrends + Streamlit")

kw_input = st.sidebar.text_input(
    "Keywords (comma-separated, max 5)",
    value="Cloud Computing, Machine Learning",
)
keywords = [k.strip() for k in kw_input.split(",") if k.strip()][:5]

timeframe_label = st.sidebar.selectbox("Timeframe", list(TIMEFRAME_OPTIONS.keys()), index=6)
timeframe = TIMEFRAME_OPTIONS[timeframe_label]

geo = st.sidebar.text_input("Country code (blank = worldwide, e.g. US, IN, GB)", value="")

resolution = st.sidebar.selectbox("Region resolution", ["COUNTRY", "REGION", "CITY", "DMA"], index=0)

run = st.sidebar.button("Run analysis", type="primary", use_container_width=True)

st.sidebar.divider()
st.sidebar.markdown(
    "**About**\n\n"
    "This app queries Google Trends via the unofficial [pytrends](https://github.com/GeneralMills/pytrends) "
    "library. Data is on a relative 0–100 scale, not absolute search volume. "
    "Google may rate-limit frequent requests."
)

# ------------------------------------------------------------------
# Main area
# ------------------------------------------------------------------
st.title("Google Trends Analyzer")
st.write(
    "Explore search interest over time, by region, and related queries/topics for any keyword(s), "
    "using live data from Google Trends."
)

if not keywords:
    st.warning("Enter at least one keyword in the sidebar to get started.")
    st.stop()

if not run:
    st.info("Set your keywords and options in the sidebar, then click **Run analysis**.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Interest Over Time", "🌍 Interest By Region", "🔗 Related Queries & Topics", "💡 Suggestions"]
)

# --- Tab 1: Interest over time ---
with tab1:
    st.subheader(f"Interest over time — {timeframe_label}")
    data, err = safe_call(fetch_interest_over_time, tuple(keywords), timeframe, geo)
    if err:
        st.error(f"Couldn't fetch data (Google Trends may be rate-limiting requests). Details: {err}")
    elif data is None or data.empty:
        st.warning("No data returned for these keywords/timeframe.")
    else:
        fig = px.line(data, x=data.index, y=keywords, labels={"value": "Search interest", "date": "Date"})
        fig.update_layout(legend_title_text="Keyword", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Peak interest", int(data[keywords].values.max()))
        with col2:
            top_kw = data[keywords].mean().idxmax()
            st.metric("Highest average interest", top_kw)

        with st.expander("Raw data"):
            st.dataframe(data, use_container_width=True)
            st.download_button(
                "Download CSV",
                data.to_csv().encode("utf-8"),
                file_name="interest_over_time.csv",
                mime="text/csv",
            )

# --- Tab 2: Interest by region ---
with tab2:
    st.subheader("Interest by region")
    region_data, err = safe_call(fetch_interest_by_region, tuple(keywords), timeframe, geo, resolution)
    if err:
        if "429" in str(err):
            st.error(
                "Google Trends is rate-limiting requests right now (HTTP 429). "
                "This is a known limitation of the unofficial API — wait a minute or two and try again."
            )
        else:
            st.error(f"Couldn't fetch region data. Details: {err}")
    elif region_data is None or region_data.empty:
        st.warning("No regional data returned.")
    else:
        sort_kw = st.selectbox("Sort/plot by keyword", keywords)
        top_n = st.slider("Show top N regions", 5, 50, 15)
        plot_df = region_data.sort_values(sort_kw, ascending=False).head(top_n)
        fig = px.bar(plot_df, x=plot_df.index, y=sort_kw, labels={"x": "Region", sort_kw: "Interest"})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("Raw data"):
            st.dataframe(region_data, use_container_width=True)

# --- Tab 3: Related queries & topics ---
with tab3:
    st.subheader("Related queries and topics")
    rq, err1 = safe_call(fetch_related_queries, tuple(keywords), timeframe, geo)
    rt, err2 = safe_call(fetch_related_topics, tuple(keywords), timeframe, geo)

    for kw in keywords:
        st.markdown(f"### {kw}")
        c1, c2 = st.columns(2)

        with c1:
            st.caption("Related queries — Top")
            if rq and rq.get(kw) and rq[kw].get("top") is not None:
                st.dataframe(rq[kw]["top"], use_container_width=True, height=220)
            else:
                st.caption("No data.")
            st.caption("Related queries — Rising")
            if rq and rq.get(kw) and rq[kw].get("rising") is not None:
                st.dataframe(rq[kw]["rising"], use_container_width=True, height=220)
            else:
                st.caption("No data.")

        with c2:
            st.caption("Related topics — Top")
            if rt and rt.get(kw) and rt[kw].get("top") is not None:
                st.dataframe(rt[kw]["top"], use_container_width=True, height=220)
            else:
                st.caption("No data.")
            st.caption("Related topics — Rising")
            if rt and rt.get(kw) and rt[kw].get("rising") is not None:
                st.dataframe(rt[kw]["rising"], use_container_width=True, height=220)
            else:
                st.caption("No data.")

# --- Tab 4: Suggestions ---
with tab4:
    st.subheader("Keyword suggestions")
    for kw in keywords:
        st.markdown(f"**{kw}**")
        sug, err = safe_call(fetch_suggestions, kw)
        if err:
            st.error(f"Couldn't fetch suggestions for '{kw}'. Details: {err}")
        elif sug:
            st.dataframe(pd.DataFrame(sug), use_container_width=True)
        else:
            st.caption("No suggestions found.")

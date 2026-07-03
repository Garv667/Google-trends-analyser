"""
Google Search Trends Dashboard
--------------------------------
A Streamlit dashboard built on top of Pytrends (unofficial Google Trends API).
Features:
  - Interest over time (single or multiple keywords)
  - Interest by region (bar chart + choropleth map)
  - Related queries (top & rising)
  - Keyword suggestions
"""

import time

import pandas as pd
import plotly.express as px
import streamlit as st
from pytrends.request import TrendReq

# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Google Search Trends Dashboard",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Google Search Trends Dashboard")
st.caption("Explore keyword popularity, regional interest, and related searches — powered by Pytrends.")


# --------------------------------------------------------------------------
# Cached Pytrends session + data fetchers
# --------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_pytrends_client():
    return TrendReq(hl="en-US", tz=330)  # tz=330 -> IST offset in minutes


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_interest_over_time(keywords, timeframe, geo):
    pytrends = get_pytrends_client()
    pytrends.build_payload(kw_list=keywords, timeframe=timeframe, geo=geo)
    df = pytrends.interest_over_time()
    if not df.empty and "isPartial" in df.columns:
        df = df.drop(columns=["isPartial"])
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_interest_by_region(keywords, timeframe, geo, resolution):
    pytrends = get_pytrends_client()
    pytrends.build_payload(kw_list=keywords, timeframe=timeframe, geo=geo)
    df = pytrends.interest_by_region(resolution=resolution, inc_low_vol=True, inc_geo_code=True)
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_related_queries(keywords, timeframe, geo):
    pytrends = get_pytrends_client()
    pytrends.build_payload(kw_list=keywords, timeframe=timeframe, geo=geo)
    return pytrends.related_queries()


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_suggestions(keyword):
    pytrends = get_pytrends_client()
    return pytrends.suggestions(keyword=keyword)


# --------------------------------------------------------------------------
# Sidebar controls
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("Search settings")

    raw_keywords = st.text_input(
        "Keywords (comma-separated, up to 5)",
        value="Python, Streamlit",
        help="Google Trends allows a maximum of 5 keywords per request.",
    )
    keywords = [k.strip() for k in raw_keywords.split(",") if k.strip()][:5]

    timeframe_options = {
        "Past 7 days": "now 7-d",
        "Past 30 days": "today 1-m",
        "Past 90 days": "today 3-m",
        "Past 12 months": "today 12-m",
        "Past 5 years": "today 5-y",
    }
    timeframe_label = st.selectbox("Timeframe", list(timeframe_options.keys()), index=3)
    timeframe = timeframe_options[timeframe_label]

    geo = st.text_input(
        "Region code (blank = Worldwide)",
        value="",
        help="ISO-2 country code, e.g. IN, US, GB. Leave blank for worldwide.",
    )

    resolution = st.selectbox("Map resolution", ["COUNTRY", "REGION", "CITY", "DMA"], index=0)

    run_search = st.button("🔍 Run analysis", type="primary", use_container_width=True)

    st.divider()
    st.caption(
        "Note: Pytrends talks to Google Trends directly and has no official rate limit "
        "guarantee. If you see errors, wait a bit and try again with fewer keywords."
    )


# --------------------------------------------------------------------------
# Main content
# --------------------------------------------------------------------------
if not keywords:
    st.info("Enter at least one keyword in the sidebar to get started.")
    st.stop()

if not run_search:
    st.info("Set your keywords and options in the sidebar, then click **Run analysis**.")
    st.stop()

tab_trend, tab_region, tab_related, tab_suggest = st.tabs(
    ["📊 Interest over time", "🗺️ Interest by region", "🔗 Related queries", "💡 Suggestions"]
)

# ---- Interest over time ---------------------------------------------------
with tab_trend:
    st.subheader("Interest over time")
    try:
        with st.spinner("Fetching trend data..."):
            df_trend = fetch_interest_over_time(keywords, timeframe, geo)

        if df_trend.empty:
            st.warning("No trend data found for these keywords/timeframe.")
        else:
            fig = px.line(
                df_trend,
                x=df_trend.index,
                y=keywords,
                labels={"value": "Search interest (0-100)", "date": "Date"},
                title=f"Search interest over time ({timeframe_label})",
            )
            fig.update_layout(legend_title_text="Keyword")
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("Show raw data"):
                st.dataframe(df_trend, use_container_width=True)
                st.download_button(
                    "Download CSV",
                    df_trend.to_csv().encode("utf-8"),
                    file_name="interest_over_time.csv",
                    mime="text/csv",
                )
    except Exception as e:
        st.error(f"Could not fetch interest-over-time data: {e}")

# ---- Interest by region -----------------------------------------------
with tab_region:
    st.subheader("Interest by region")
    try:
        with st.spinner("Fetching regional data..."):
            df_region = fetch_interest_by_region(keywords, timeframe, geo, resolution)

        if df_region.empty:
            st.warning("No regional data found for these keywords/timeframe.")
        else:
            df_region_reset = df_region.reset_index()
            primary_kw = keywords[0]

            top_n = st.slider("Show top N regions", 5, 50, 20)
            df_top = df_region_reset.sort_values(primary_kw, ascending=False).head(top_n)

            bar_fig = px.bar(
                df_top,
                x=primary_kw,
                y="geoName",
                orientation="h",
                title=f"Top {top_n} regions for '{primary_kw}'",
                labels={primary_kw: "Search interest (0-100)", "geoName": "Region"},
            )
            bar_fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(bar_fig, use_container_width=True)

            if resolution == "COUNTRY" and "geoCode" in df_region_reset.columns:
                map_fig = px.choropleth(
                    df_region_reset,
                    locations="geoCode",
                    color=primary_kw,
                    hover_name="geoName",
                    color_continuous_scale="Blues",
                    title=f"World interest map — '{primary_kw}'",
                )
                st.plotly_chart(map_fig, use_container_width=True)
            else:
                st.caption("Switch map resolution to COUNTRY in the sidebar to see the world map.")

            with st.expander("Show raw data"):
                st.dataframe(df_region, use_container_width=True)
                st.download_button(
                    "Download CSV",
                    df_region.to_csv().encode("utf-8"),
                    file_name="interest_by_region.csv",
                    mime="text/csv",
                )
    except Exception as e:
        st.error(f"Could not fetch regional data: {e}")

# ---- Related queries -----------------------------------------------------
with tab_related:
    st.subheader("Related queries")
    try:
        with st.spinner("Fetching related queries..."):
            related = fetch_related_queries(keywords, timeframe, geo)

        for kw in keywords:
            st.markdown(f"**{kw}**")
            data = related.get(kw, {})
            col1, col2 = st.columns(2)

            top_df = data.get("top") if data else None
            rising_df = data.get("rising") if data else None

            with col1:
                st.caption("Top")
                if top_df is not None and not top_df.empty:
                    st.dataframe(top_df, use_container_width=True, hide_index=True)
                else:
                    st.caption("No data.")

            with col2:
                st.caption("Rising")
                if rising_df is not None and not rising_df.empty:
                    st.dataframe(rising_df, use_container_width=True, hide_index=True)
                else:
                    st.caption("No data.")
            st.divider()
    except Exception as e:
        st.error(f"Could not fetch related queries: {e}")

# ---- Suggestions -----------------------------------------------------
with tab_suggest:
    st.subheader("Keyword suggestions")
    try:
        with st.spinner("Fetching suggestions..."):
            for kw in keywords:
                suggestions = fetch_suggestions(kw)
                st.markdown(f"**{kw}**")
                if suggestions:
                    st.dataframe(pd.DataFrame(suggestions), use_container_width=True, hide_index=True)
                else:
                    st.caption("No suggestions found.")
                time.sleep(0.2)  # small buffer between requests
    except Exception as e:
        st.error(f"Could not fetch suggestions: {e}")

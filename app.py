"""Streamlit dashboard for the NASA FIRMS California pipeline.

Queries the local SQLite database and displays metrics, a map, and a data table.
"""

import sqlite3
from datetime import datetime

import pandas as pd
import pydeck as pdk
import streamlit as st

DB_PATH = "data/firms.db"


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


@st.cache_data
def load_detections() -> pd.DataFrame:
    """Load the detections table from SQLite."""
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT * FROM detections", conn)
    finally:
        conn.close()
    df["acq_date"] = pd.to_datetime(df["acq_date"])
    return df


def brightness_to_color(brightness: float, min_b: float, max_b: float) -> list:
    """Map brightness to an RGBA color."""
    if max_b <= min_b:
        norm = 0.5
    else:
        norm = (brightness - min_b) / (max_b - min_b)
        norm = max(0.0, min(1.0, norm))
    r = int(180 + 75 * norm)
    g = int(40 + 60 * (1 - norm))
    b = int(20)
    return [r, g, b, 200]


def main() -> None:
    st.set_page_config(
        page_title="FIRMS California Dashboard",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("🔥 NASA FIRMS California Dashboard")
    st.markdown(
        "Live pipeline dashboard. Data is loaded from the local SQLite database "
        "built by the ingest → clean → load stages."
    )

    try:
        df = load_detections()
    except Exception as e:
        st.error(f"Could not load database. Run `python -m src.pipeline` first.\n\n{e}")
        return

    if df.empty:
        st.warning("Database is empty. Run the pipeline to load data.")
        return

    # Sidebar filters
    st.sidebar.header("Filters")
    min_date = df["acq_date"].min().date()
    max_date = df["acq_date"].max().date()
    date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    frp_min = float(df["frp"].min())
    frp_max = float(df["frp"].max())
    min_frp = st.sidebar.slider("Minimum FRP", frp_min, frp_max, frp_min)

    intensities = ["All"] + sorted(df["intensity"].dropna().unique().tolist())
    intensity = st.sidebar.selectbox("Intensity", intensities)

    # Filter
    mask = (
        (df["acq_date"].dt.date >= start_date)
        & (df["acq_date"].dt.date <= end_date)
        & (df["frp"] >= min_frp)
    )
    if intensity != "All":
        mask &= df["intensity"] == intensity
    filtered = df.loc[mask].copy()

    # Metrics
    st.subheader("Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Detections", f"{len(filtered):,}")
    col2.metric("Avg FRP", f"{filtered['frp'].mean():.1f}" if len(filtered) else "—")
    col3.metric("Max FRP", f"{filtered['frp'].max():.1f}" if len(filtered) else "—")
    col4.metric("Avg Brightness", f"{filtered['bright_ti4'].mean():.1f}" if len(filtered) else "—")

    # Map
    st.subheader("Map")
    if filtered.empty:
        st.info("No detections match the current filters.")
    else:
        map_df = filtered.copy()
        map_df["acq_date"] = map_df["acq_date"].dt.strftime("%Y-%m-%d")
        b_min = float(map_df["bright_ti4"].min())
        b_max = float(map_df["bright_ti4"].max())
        map_df["color"] = map_df["bright_ti4"].apply(
            lambda b: brightness_to_color(b, b_min, b_max)
        )

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position="[longitude, latitude]",
            get_fill_color="color",
            get_radius=8000,
            radius_min_pixels=3,
            radius_max_pixels=15,
            pickable=True,
        )
        view_state = pdk.ViewState(
            latitude=float(map_df["latitude"].mean()),
            longitude=float(map_df["longitude"].mean()),
            zoom=5.5,
        )
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            )
        st.pydeck_chart(deck, use_container_width=True)
    # Table
    with st.expander("View detections"):
        display = filtered.copy()
        display["acq_date"] = display["acq_date"].dt.strftime("%Y-%m-%d")
        st.dataframe(display, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()

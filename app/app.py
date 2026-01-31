import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from pathlib import Path

# ================== PATHS ==================
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR.parent / "assets"
DATA_DIR = BASE_DIR.parent / "data"

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="FC Barcelona Performance Intelligence",
    layout="wide"
)

# ================== BACKGROUND ==================
def set_background(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    .block-container {{
        background-color: rgba(0, 0, 0, 0.80);
        padding: 2rem;
        border-radius: 18px;
    }}

    h1, h2, h3, h4 {{
        color: white;
    }}

    [data-testid="stMetricValue"] {{
        color: #FFD700;
        font-size: 28px;
    }}
    </style>
    """, unsafe_allow_html=True)

set_background(ASSETS_DIR / "barca_bg.png")

# ================== LOAD DATA ==================
@st.cache_data
def load_data():
    return pd.read_csv(DATA_DIR / "FC_Barcelona_Big_Dataset_TimeSeries.csv")

df = load_data()

# ================== HEADER ==================
col1, col2 = st.columns([1,6])
with col1:
    st.image(ASSETS_DIR / "barca_logo.png", width=95)

with col2:
    st.title("FC Barcelona Performance Intelligence Dashboard")
    st.caption("Multi-Season Match • Team • Player Analytics")

# ================== SIDEBAR FILTERS ==================
st.sidebar.header("🔎 Filters")

season_filter = st.sidebar.multiselect(
    "Season",
    sorted(df["season"].unique()),
    default=sorted(df["season"].unique())
)

player_filter = st.sidebar.multiselect(
    "Player",
    sorted(df["player"].unique()),
    default=sorted(df["player"].unique())
)

filtered = df[
    (df["season"].isin(season_filter)) &
    (df["player"].isin(player_filter))
]

# ================== KPIs ==================
st.markdown("## 📊 Key Performance Indicators")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Matches", filtered["match_id"].nunique())
k2.metric("Goals Scored", int(filtered["goals_for"].sum()))
k3.metric("Goals Conceded", int(filtered["goals_against"].sum()))
k4.metric("Avg Possession %", round(filtered["possession_pct"].mean(), 1))
k5.metric("Avg xG", round(filtered["xG"].mean(), 2))

st.divider()

# ================== TABS ==================
tab1, tab2, tab3, tab4 = st.tabs(
    ["🏟️ Overview", "📅 Seasons", "👤 Players", "🧠 Insights"]
)

# -------- TAB 1: OVERVIEW --------
with tab1:
    st.subheader("Goals Across Rounds")
    goals_round = filtered.groupby("round")["goals_for"].sum().reset_index()
    fig1 = px.line(goals_round, x="round", y="goals_for", markers=True)
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Home vs Away Performance")
    ha = filtered.groupby("home_away")[["goals_for","goals_against"]].mean().reset_index()
    fig2 = px.bar(ha, x="home_away", y=["goals_for","goals_against"], barmode="group")
    st.plotly_chart(fig2, use_container_width=True)

# -------- TAB 2: SEASONS --------
with tab2:
    st.subheader("Season Comparison")
    season_stats = filtered.groupby("season")[["goals_for","goals_against","xG"]].mean().reset_index()

    fig3 = px.bar(season_stats, x="season", y="goals_for")
    st.plotly_chart(fig3, use_container_width=True)

    fig4 = px.line(season_stats, x="season", y=["xG","goals_for"], markers=True)
    st.plotly_chart(fig4, use_container_width=True)

# -------- TAB 3: PLAYERS --------
with tab3:
    st.subheader("Player Contribution")
    player_stats = filtered.groupby("player")[["goals","assists","minutes_played","xG"]].sum().reset_index()

    fig5 = px.scatter(
        player_stats,
        x="minutes_played",
        y="goals",
        size="assists",
        hover_name="player"
    )
    st.plotly_chart(fig5, use_container_width=True)

    st.dataframe(player_stats.sort_values(by="goals", ascending=False))

# -------- TAB 4: INSIGHTS --------
with tab4:
    st.subheader("Correlation Insights")
    corr = filtered[["goals_for","shots","shots_on_target","possession_pct","xG"]].corr()
    fig6 = px.imshow(corr, text_auto=True, aspect="auto")
    st.plotly_chart(fig6, use_container_width=True)

    st.markdown("""
    ### Key Insights
    - Higher possession correlates with more goals.
    - Shots on target are critical for outcomes.
    - Some players outperform their expected goals (xG).
    """)

# ================== DATA PREVIEW ==================
st.divider()
st.subheader("Raw Data Preview")
st.dataframe(filtered.head(30))

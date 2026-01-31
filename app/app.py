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
    image_path = Path(image_path)
    if not image_path.exists():
        st.error(f"الصورة مش موجودة! تحقق من المسار: {image_path}")
        return
    
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
    h1,h2,h3,h4 {{ color:white; }}
    [data-testid="stMetricValue"] {{ font-size:28px; }}
    </style>
    """, unsafe_allow_html=True)

# استخدم الخلفية الموجودة
set_background(ASSETS_DIR / "barca_bg.png")

# ================== LOAD DATA ==================
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_DIR / "FC_Barcelona_Big_Dataset_TimeSeries.csv")

    # Rename columns for consistency
    df.rename(columns={
        "season_x": "season",
        "player": "player",
        "xG_x": "xg",
        "xG_y": "player_xg",
        "shots_x": "shots",
        "shots_y": "player_shots"
    }, inplace=True)

    # Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

df = load_data()

# ================== HEADER ==================
col_logo, col_title = st.columns([1,6])
with col_logo:
    st.image(ASSETS_DIR / "barca_logo.png", width=90)

with col_title:
    st.markdown(f"""
    <div style="
        background-color: rgba(0,0,0,0.7);
        padding: 15px 25px;
        border-radius:12px;
        text-align:center;
        margin-bottom:10px;
    ">
        <h1 style="color:#FFD700; margin:0; font-size:40px;">FC Barcelona Performance Intelligence Dashboard</h1>
        <p style="color:white; margin:0; font-size:18px;">Multi-Season Match • Team • Player Analytics</p>
    </div>
    """, unsafe_allow_html=True)

# ================== SIDEBAR FILTERS ==================
st.sidebar.header("🔎 Filters")

# ---- Season filter ----
season_options = sorted(df["season"].unique())
season_filter = st.sidebar.multiselect(
    "Season",
    options=season_options,
    default=season_options
)

# ---- Player filter (dynamic based on selected seasons) ----
filtered_for_players = df[df["season"].isin(season_filter)]
player_options = sorted(filtered_for_players["player"].unique())
player_filter = st.sidebar.multiselect(
    "Player",
    options=player_options,
    default=player_options
)

# ---- Final filtered dataframe ----
filtered = df[
    (df["season"].isin(season_filter)) &
    (df["player"].isin(player_filter))
]

# ================== KPIs ==================
st.markdown("## 📊 Key Performance Indicators")

kpi_data = {
    "Matches": filtered["match_id"].nunique(),
    "Goals Scored": int(filtered["goals_for"].sum()),
    "Goals Conceded": int(filtered["goals_against"].sum()),
    "Avg Possession %": round(filtered["possession_pct"].mean(),1),
    "Avg xG": round(filtered["xg"].mean(),2)
}

# ألوان مستوحاة من علم برشلونة: أحمر – أزرق – أصفر – ذهبي
kpi_colors = ["#A50044","#004C97","#FFD700","#A50044","#004C97"]

k1, k2, k3, k4, k5 = st.columns(5)

for col, (kpi_name, kpi_value), color in zip([k1,k2,k3,k4,k5], kpi_data.items(), kpi_colors):
    col.markdown(f"""
        <div style="
            background-color:{color};
            padding:20px;
            border-radius:15px;
            text-align:center;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
        ">
            <h4 style="color:white; margin-bottom:5px;">{kpi_name}</h4>
            <h2 style="color:white; margin-top:0;">{kpi_value}</h2>
        </div>
    """, unsafe_allow_html=True)

# ================== PLAYER OVERVIEW ==================
st.markdown("## 👤 Player Overview")
st.markdown("### عدد اللاعبين وإسهامهم في المباريات")

# عدد اللاعبين الفريدين
num_players = filtered["player"].nunique()
st.markdown(f"**عدد اللاعبين الفريدين في البيانات:** {num_players}")

# ترتيب اللاعبين حسب عدد المباريات
player_counts = filtered.groupby("player")["match_id"].nunique().reset_index()
player_counts.rename(columns={"match_id":"matches_played"}, inplace=True)
player_counts = player_counts.sort_values(by="matches_played", ascending=False)

# KPI أعلى 5 لاعبين حسب عدد المباريات
top_players = player_counts.head(5)
k1, k2, k3, k4, k5 = st.columns(5)
kpi_colors_players = ["#FFD700","#1E90FF","#FF4500","#32CD32","#FF69B4"]  # ذهبية - أزرق - أحمر - أخضر - وردي

for i, col in enumerate([k1,k2,k3,k4,k5]):
    if i < len(top_players):
        player = top_players.iloc[i]["player"]
        matches = top_players.iloc[i]["matches_played"]
        col.markdown(f"""
            <div style="background-color:{kpi_colors_players[i]}; padding: 10px; border-radius:10px; text-align:center;">
                <h4 style="color:white;margin:0">{player}</h4>
                <h2 style="color:white;margin:0">{matches} ⚽</h2>
            </div>
        """, unsafe_allow_html=True)

# Chart لكل اللاعبين
st.markdown("### توزيع عدد المباريات لكل اللاعبين")
fig_player = px.bar(
    player_counts,
    x="player",
    y="matches_played",
    color="matches_played",
    color_continuous_scale="Viridis",
    title="عدد المباريات لكل لاعب",
    labels={"matches_played":"عدد المباريات","player":"اللاعب"}
)
fig_player.update_layout(
    xaxis_tickangle=-45,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white")
)
st.plotly_chart(fig_player, use_container_width=True)

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
    season_stats = filtered.groupby("season")[["goals_for","goals_against","xg"]].mean().reset_index()

    fig3 = px.bar(season_stats, x="season", y="goals_for")
    st.plotly_chart(fig3, use_container_width=True)

    fig4 = px.line(season_stats, x="season", y=["xg","goals_for"], markers=True)
    st.plotly_chart(fig4, use_container_width=True)

# -------- TAB 3: PLAYERS --------
with tab3:
    st.subheader("Player Contribution")
    player_stats = filtered.groupby("player")[["goals","assists","minutes_played","player_xg"]].sum().reset_index()

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
    corr = filtered[["goals_for","shots","shots_on_target","possession_pct","xg"]].corr()
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

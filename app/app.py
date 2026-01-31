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
        background-color: rgba(0, 0, 0, 0.85);
        padding: 2rem;
        border-radius: 18px;
    }}
    h1,h2,h3,h4,p,span {{ color:#FFD700; }}  /* كل النصوص ذهبية */
    </style>
    """, unsafe_allow_html=True)

set_background(ASSETS_DIR / "barca_bg.png")

# ================== LOAD DATA ==================
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_DIR / "FC_Barcelona_Big_Dataset_TimeSeries.csv")
    df.rename(columns={
        "season_x": "season",
        "player": "player",
        "xG_x": "xg",
        "xG_y": "player_xg",
        "shots_x": "shots",
        "shots_y": "player_shots"
    }, inplace=True)
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
        <h1 style="margin:0; font-size:40px;">FC Barcelona Performance Intelligence Dashboard</h1>
        <p style="margin:0; font-size:18px;">Multi-Season Match • Team • Player Analytics</p>
    </div>
    """, unsafe_allow_html=True)

# ================== SIDEBAR FILTERS ==================
st.sidebar.header("🔎 Filters")

# كل المواسم الموجودة
season_options = sorted(df["season"].unique())
season_filter = st.sidebar.multiselect(
    "Season",
    options=season_options,
    default=season_options
)

# ✅ كل اللاعبين في الداتا الكبيرة (حتى لو مكرر في مواسم مختلفة)
player_options = sorted(df["player"].unique())
player_filter = st.sidebar.multiselect(
    "Player",
    options=player_options,
    default=player_options  # كل اللاعبين يظهرون تلقائيًا
)

# تطبيق الفلاتر
filtered = df[
    (df["season"].isin(season_filter)) &
    (df["player"].isin(player_filter))
]

# ================== DYNAMIC KPI CARDS ==================
st.markdown("## 📊 Key Performance Indicators - Dynamic")

kpi_data = [
    {"title": "Matches", "value": filtered["match_id"].nunique(), "icon": "🏟️", "color":"#A50044"},
    {"title": "Goals Scored", "value": int(filtered["goals_for"].sum()), "icon": "⚽", "color":"#004C97"},
    {"title": "Goals Conceded", "value": int(filtered["goals_against"].sum()), "icon": "🛡️", "color":"#FFD700"},
    {"title": "Avg Possession %", "value": round(filtered["possession_pct"].mean(),1), "icon": "📊", "color":"#A50044"},
    {"title": "Avg xG", "value": round(filtered["xg"].mean(),2), "icon": "🎯", "color":"#004C97"}
]

cols = st.columns(len(kpi_data))
for col, kpi in zip(cols, kpi_data):
    col.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {kpi['color']} 0%, #000000 100%);
            padding: 20px;
            border-radius: 15px;
            text-align:center;
            box-shadow: 3px 3px 15px rgba(0,0,0,0.6);
            transition: transform 0.2s;
        ">
            <div style="font-size:35px;">{kpi['icon']}</div>
            <h4 style="color:#FFD700; margin:5px 0;">{kpi['title']}</h4>
            <h2 style="color:#FFD700; margin:0; font-size:28px;">{kpi['value']}</h2>
        </div>
    """, unsafe_allow_html=True)

# ================== PLAYER OVERVIEW ==================
st.markdown("## 👤 Player Overview")
st.markdown(f"**عدد اللاعبين الفريدين في البيانات:** <span style='color:#FFD700'>{filtered['player'].nunique()}</span>", unsafe_allow_html=True)

player_counts = filtered.groupby("player")["match_id"].nunique().reset_index()
player_counts.rename(columns={"match_id":"matches_played"}, inplace=True)
player_counts = player_counts.sort_values(by="matches_played", ascending=False)

st.markdown("### توزيع عدد المباريات لكل اللاعبين")
fig_player = px.bar(
    player_counts,
    x="player",
    y="matches_played",
    color="matches_played",
    color_continuous_scale="Viridis",
    labels={"matches_played":"عدد المباريات","player":"اللاعب"}
)
fig_player.update_layout(
    xaxis_tickangle=-45,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#FFD700")
)
st.plotly_chart(fig_player, use_container_width=True)

# ================== TABS ==================
tab1, tab2, tab3, tab4 = st.tabs(
    ["🏟️ Overview", "📅 Seasons", "👤 Players", "🧠 Insights"]
)

with tab1:
    st.subheader("Goals Across Rounds")
    goals_round = filtered.groupby("round")["goals_for"].sum().reset_index()
    fig1 = px.line(goals_round, x="round", y="goals_for", markers=True)
    fig1.update_layout(font=dict(color="#FFD700"))
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Home vs Away Performance")
    ha = filtered.groupby("home_away")[["goals_for","goals_against"]].mean().reset_index()
    fig2 = px.bar(ha, x="home_away", y=["goals_for","goals_against"], barmode="group")
    fig2.update_layout(font=dict(color="#FFD700"))
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Season Comparison")
    season_stats = filtered.groupby("season")[["goals_for","goals_against","xg"]].mean().reset_index()
    fig3 = px.bar(season_stats, x="season", y="goals_for")
    fig3.update_layout(font=dict(color="#FFD700"))
    st.plotly_chart(fig3, use_container_width=True)
    fig4 = px.line(season_stats, x="season", y=["xg","goals_for"], markers=True)
    fig4.update_layout(font=dict(color="#FFD700"))
    st.plotly_chart(fig4, use_container_width=True)

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
    fig5.update_layout(font=dict(color="#FFD700"))
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("### بيانات اللاعبين - قابلة للبحث والتحميل")
    st.dataframe(filtered, height=500)  # scrollbar عمودي للبيانات الكبيرة

    # زر تحميل البيانات المفلترة
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ تحميل البيانات المفلترة كـ CSV",
        data=csv,
        file_name='barcelona_filtered_data.csv',
        mime='text/csv'
    )

with tab4:
    st.subheader("Correlation Insights")
    corr = filtered[["goals_for","shots","shots_on_target","possession_pct","xg"]].corr()
    fig6 = px.imshow(corr, text_auto=True, aspect="auto")
    fig6.update_layout(font=dict(color="#FFD700"))
    st.plotly_chart(fig6, use_container_width=True)
    st.markdown("""
    ### Key Insights
    - Higher possession correlates with more goals.
    - Shots on target are critical for outcomes.
    - Some players outperform their expected goals (xG).
    """)

st.divider()
st.subheader("Raw Data Preview")
st.dataframe(filtered, height=500)

import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from pathlib import Path
from sklearn.linear_model import LinearRegression
import numpy as np

# ================== PATHS ==================
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR.parent / "assets"
DATA_DIR = BASE_DIR.parent / "data"

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="FC Barcelona Performance Intelligence",
    layout="wide"
)

# ================== BACKGROUND & STYLING ==================
def set_background(image_path):
    image_path = Path(image_path)
    # ترميز الصورة للخلفية
    encoded = ""
    if image_path.exists():
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
    
    st.markdown(f"""
    <style>
    /* الخلفية الرئيسية */
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* تعديل الـ Sidebar لألوان علم برشلونة */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #A50044 0%, #004C97 100%) !important;
        border-right: 2px solid #FFD700;
    }}
    
    /* نصوص الـ Sidebar باللون الذهبي */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {{
        color: #FFD700 !important;
    }}

    .block-container {{
        background-color: rgba(0, 0, 0, 0.85);
        padding: 2rem;
        border-radius: 18px;
    }}
    
    h1,h2,h3,h4,p,span,a {{ color:#FFD700; }}
    </style>
    """, unsafe_allow_html=True)

set_background(ASSETS_DIR / "barca_bg.png")

# ================== LOAD DATA ==================
@st.cache_data
def load_data():
    # تأكد من وجود الملف في المسار الصحيح
    df = pd.read_csv(DATA_DIR / "FC_Barcelona_Big_Dataset_TimeSeries.csv")
    
    df.rename(columns={
        "season_x": "season",
        "player": "player",
        "xG_x": "xg",
        "xG_y": "player_xg",
        "shots_x": "shots",
        "shots_y": "player_shots"
    }, inplace=True)
    
    df['season'] = df['season'].astype(str).str.strip()
    df['player'] = df['player'].astype(str).str.strip()
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"خطأ في تحميل البيانات: {e}")
    st.stop()

# ================== HEADER ==================
col_logo, col_title = st.columns([1,6])
with col_logo:
    st.image(ASSETS_DIR / "barca_logo.png", width=90)

with col_title:
    st.markdown("""
    <div style="background-color: rgba(0,0,0,0.7); padding: 15px; border-radius:12px; text-align:center;">
        <h1 style="margin:0;">FC Barcelona Performance Intelligence Dashboard</h1>
        <p style="margin:0;">Multi-Season Match • Team • Player Analytics</p>
    </div>
    """, unsafe_allow_html=True)

# ================== SIDEBAR FILTERS ==================
st.sidebar.markdown("<h3 style='text-align:center;'>🔎 Filters</h3>", unsafe_allow_html=True)

season_options = sorted(df["season"].unique())
default_season = ["2024/2025"] if "2024/2025" in season_options else [season_options[-1]]

season_filter = st.sidebar.multiselect("Season", options=season_options, default=default_season)

player_options = sorted(df[df["season"].isin(season_filter)]["player"].unique())
player_filter = st.sidebar.multiselect("Player", options=player_options, default=player_options)

filtered = df[(df["season"].isin(season_filter)) & (df["player"].isin(player_filter))]

st.sidebar.markdown(f"""
<hr style="border:1px solid #FFD700;">
<div style="text-align:center;">
    <h4>Eng. Goda Emad</h4>
    <a href='https://github.com/Goda-Emad' target='_blank' style='color:#FFD700;'>GitHub</a> | 
    <a href='https://www.linkedin.com/in/goda-emad/' target='_blank' style='color:#FFD700;'>LinkedIn</a>
</div>
""", unsafe_allow_html=True)

# ================== KPI CARDS (6 CARDS) ==================
st.markdown("## 📊 Key Performance Indicators")

kpi_data = [
    {"title": "Matches", "value": filtered["match_id"].nunique(), "icon": "🏟️", "color":"#A50044"},
    {"title": "Goals Scored", "value": int(filtered["goals_for"].sum()), "icon": "⚽", "color":"#004C97"},
    {"title": "Assists", "value": int(filtered["assists"].sum()), "icon": "👟", "color":"#A50044"}, # الـ KPI الجديد
    {"title": "Goals Conceded", "value": int(filtered["goals_against"].sum()), "icon": "🛡️", "color":"#004C97"},
    {"title": "Avg Possession", "value": f"{round(filtered['possession_pct'].mean(),1)}%", "icon": "📊", "color":"#A50044"},
    {"title": "Avg Team xG", "value": round(filtered["xg"].mean(),2), "icon": "🎯", "color":"#004C97"}
]

cols = st.columns(len(kpi_data))
for col, kpi in zip(cols, kpi_data):
    col.markdown(f"""
        <div style="background: linear-gradient(135deg, {kpi['color']} 0%, #000000 100%);
                    padding: 20px; border-radius: 15px; text-align:center; border: 1px solid #FFD700;">
            <div style="font-size:30px;">{kpi['icon']}</div>
            <p style="margin:5px 0; font-size:14px;">{kpi['title']}</p>
            <h2 style="margin:0; font-size:24px;">{kpi['value']}</h2>
        </div>
    """, unsafe_allow_html=True)

# ================== TABS ==================
tab1, tab2, tab3, tab4 = st.tabs(["🏟️ Overview", "📅 Seasons", "👤 Players", "🧠 AI Insights"])

with tab1:
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Goals Across Rounds")
        goals_round = filtered.groupby("round")["goals_for"].sum().reset_index()
        fig1 = px.line(goals_round, x="round", y="goals_for", markers=True, color_discrete_sequence=['#FFD700'])
        st.plotly_chart(fig1, use_container_width=True)
    with col_r:
        st.subheader("Home vs Away Goals")
        ha = filtered.groupby("home_away")[["goals_for","goals_against"]].mean().reset_index()
        fig2 = px.bar(ha, x="home_away", y=["goals_for","goals_against"], barmode="group", color_discrete_map={"goals_for":"#A50044", "goals_against":"#004C97"})
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Season Performance Comparison")
    season_stats = filtered.groupby("season")[["goals_for","xg"]].mean().reset_index()
    fig3 = px.bar(season_stats, x="season", y=["goals_for","xg"], barmode="group")
    st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.subheader("Player Contribution Analysis")
    player_stats = filtered.groupby("player")[["goals","assists","minutes_played"]].sum().reset_index()
    fig5 = px.scatter(player_stats, x="minutes_played", y="goals", size="assists", hover_name="player", color="goals")
    st.plotly_chart(fig5, use_container_width=True)
    st.dataframe(player_stats.sort_values(by="goals", ascending=False), use_container_width=True)

with tab4:
    st.subheader("🧠 Intelligence & Predictions")
    
    # نموذج بسيط لتوقع الأهداف بناءً على xG والاستحواذ
    model_df = filtered[['xg', 'possession_pct', 'goals_for']].dropna()
    if len(model_df) > 5:
        X = model_df[['xg', 'possession_pct']]
        y = model_df['goals_for']
        model = LinearRegression().fit(X, y)
        
        st.markdown("### Goal Prediction Model")
        st.write("استخدم المؤشرات التالية لتوقع عدد أهداف الفريق في مباراة افتراضية:")
        
        c1, c2 = st.columns(2)
        input_xg = c1.slider("Expected Goals (xG)", 0.0, 5.0, 1.5)
        input_pos = c2.slider("Possession %", 30, 80, 60)
        
        prediction = model.predict([[input_xg, input_pos]])[0]
        st.metric("Predicted Goals", f"{round(max(0, prediction), 2)} ⚽")
        
        st.info("هذا التوقع مبني على البيانات التاريخية المفلترة حالياً باستخدام Linear Regression.")
    else:
        st.warning("بيانات غير كافية لإنشاء نموذج التوقع. يرجى اختيار مواسم أكثر.")

st.divider()
st.subheader("Raw Data Preview")
st.dataframe(filtered, height=400)

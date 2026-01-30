import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. إعدادات الصفحة والتصميم CSS ---
st.set_page_config(page_title="Barça Intelligence Dashboard", layout="wide", page_icon="⚽")

# تصميم CSS بخلفية متدرجة احترافية وألوان البلاوغرانا
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #051937 0%, #004d7a 50%, #a50044 100%);
        color: white;
    }
    [data-testid="stMetricValue"] { color: #edbb00 !important; font-weight: bold; }
    .stMetric { background-color: rgba(255, 255, 255, 0.05); border: 1px solid #edbb00; border-radius: 10px; padding: 15px; }
    h1, h2, h3 { color: #edbb00 !important; text-shadow: 1px 1px 2px #000; }
    .stDataFrame { border: 1px solid #edbb00; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. وظيفة تحميل البيانات الذكية ---
@st.cache_data
def load_data():
    # البحث عن الملف في المجلدات المختلفة لضمان التشغيل
    paths = ['data/FC_Barcelona_Big_Dataset_TimeSeries.csv', '../data/FC_Barcelona_Big_Dataset_TimeSeries.csv', 'FC_Barcelona_Big_Dataset_TimeSeries.csv']
    df = None
    for p in paths:
        if os.path.exists(p):
            df = pd.read_csv(p)
            break
    
    if df is not None:
        df.columns = df.columns.str.strip() # تنظيف أسماء الأعمدة
    return df

try:
    df_full = load_data()

    # --- 3. القائمة الجانبية (الفلاتر) ---
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/47/FC_Barcelona_logo.svg/200px-FC_Barcelona_logo.svg.png", width=120)
    st.sidebar.title("إعدادات اللوحة")
    
    season = st.sidebar.selectbox("اختر الموسم", sorted(df_full['season_x'].unique(), reverse=True))
    venue = st.sidebar.radio("مكان المباراة", ["الكل", "Home", "Away"])
    
    # تصفية البيانات
    filtered_df = df_full[df_full['season_x'] == season]
    if venue != "الكل":
        filtered_df = filtered_df[filtered_df['home_away'] == venue]

    # بيانات المباريات الفريدة (لأن الملف يكرر المباراة لكل لاعب)
    match_df = filtered_df.drop_duplicates(subset=['match_id']).sort_values('round')

    # --- 4. الواجهة الرئيسية ---
    st.title(f"📊 تحليلات أداء برشلونة - موسم {season}")
    
    # صف المؤشرات (KPIs)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("إجمالي المباريات", len(match_df))
    with k2:
        st.metric("الأهداف المسجلة", match_df['goals_for'].sum())
    with k3:
        st.metric("متوسط الاستحواذ", f"{round(match_df['possession_pct'].mean(), 1)}%")
    with k4:
        wins = len(match_df[match_df['goals_for'] > match_df['goals_against']])
        win_rate = round((wins/len(match_df)*100), 1) if len(match_df)>0 else 0
        st.metric("نسبة الفوز", f"{win_rate}%")

    st.markdown("---")

    # --- 5. الرسوم البيانية ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("⚽ الأهداف المسجلة مقابل المستقبلة (حسب الجولة)")
        fig_goals = px.bar(match_df, x='round', y=['goals_for', 'goals_against'],
                           barmode='group', color_discrete_map={"goals_for": "#edbb00", "goals_against": "#a50044"},
                           template="plotly_dark")
        st.plotly_chart(fig_goals, use_container_width=True)

    with col_right:
        st.subheader("🎯 الاستحواذ مقابل الأهداف المتوقعة (xG)")
        fig_xg = px.scatter(match_df, x='xG_x', y='goals_for', size='shots_x', color='possession_pct',
                            hover_data=['opponent'], color_continuous_scale='Reds', template="plotly_dark")
        st.plotly_chart(fig_xg, use_container_width=True)

    st.markdown("---")

    # --- 6. تحليل اللاعبين ---
    st.subheader("🌟 أفضل هدافي الفريق والمصنعين")
    player_stats = filtered_df.groupby('player').agg({
        'goals': 'max',
        'assists': 'max'
    }).reset_index()

    p_col1, p_col2 = st.columns(2)
    with p_col1:
        top_scorers = player_stats.sort_values('goals', ascending=False).head(8)
        fig_p = px.bar(top_scorers, x='goals', y='player', orientation='h', title="أكثر اللاعبين تسجيلاً",
                       color='goals', color_continuous_scale='YlOrRd', template="plotly_dark")
        st.plotly_chart(fig_p, use_container_width=True)

    with p_col2:
        top_assists = player_stats.sort_values('assists', ascending=False).head(8)
        fig_a = px.bar(top_assists, x='assists', y='player', orientation='h', title="أكثر اللاعبين صناعة",
                       color='assists', color_continuous_scale='Blues', template="plotly_dark")
        st.plotly_chart(fig_a, use_container_width=True)

    # جدول البيانات
    with st.expander("🔍 استعراض تفاصيل المباريات المصفاة"):
        st.dataframe(match_df[['round', 'opponent', 'home_away', 'goals_for', 'goals_against', 'possession_pct', 'xG_x']], 
                     use_container_width=True)

except Exception as e:
    st.error(f"خطأ في تحميل البيانات: {e}")
    st.info("تأكد من رفع ملف 'FC_Barcelona_Big_Dataset_TimeSeries.csv' داخل مجلد 'data'.")

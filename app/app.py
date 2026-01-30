import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. إعدادات الصفحة والهوية البصرية ---
st.set_page_config(page_title="FCB Analytics Hub", layout="wide", page_icon="🔵")

# تصميم CSS متقدم لخلفية احترافية وتنسيق الـ KPIs
st.markdown("""
    <style>
    /* تغيير خلفية التطبيق بالكامل لتشبه ألوان برشلونة */
    .stApp {
        background: linear-gradient(135deg, #001d3d 0%, #003566 30%, #a50044 100%);
        color: white;
    }
    
    /* تنسيق كروت الـ KPI */
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.07);
        border: 2px solid #edbb00; /* إطار ذهبي */
        border-radius: 20px;
        padding: 20px 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: transform 0.3s;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
    }
    
    /* تلوين أرقام الـ KPI باللون الذهبي */
    [data-testid="stMetricValue"] {
        color: #edbb00 !important;
        font-family: 'Arial Black';
        font-size: 35px !important;
    }
    
    /* تلوين عناوين الـ KPI بالأبيض */
    [data-testid="stMetricLabel"] {
        color: #ffffff !important;
        font-weight: bold;
        font-size: 18px !important;
    }

    /* تحسين شكل القائمة الجانبية */
    .css-1d391kg {
        background-color: #001d3d !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. دالة تحميل البيانات ---
@st.cache_data
def load_data():
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, '..', 'data', 'FC_Barcelona_Big_Dataset_TimeSeries.csv')
    df = pd.read_csv(file_path)
    return df

try:
    df = load_data()

    # --- 3. القائمة الجانبية (Sidebar) مع اللوجو ---
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/47/FC_Barcelona_logo.svg/1200px-FC_Barcelona_logo.svg.png", width=150)
    st.sidebar.markdown("<h2 style='text-align: center; color: #edbb00;'>BARÇA HUB</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    # فلاتر البحث
    selected_season = st.sidebar.selectbox("📅 اختر الموسم", sorted(df['season_x'].unique(), reverse=True))
    selected_venue = st.sidebar.multiselect("🏟️ الملعب", options=df['home_away'].unique(), default=df['home_away'].unique())

    # تصفية الداتا
    mask = (df['season_x'] == selected_season) & (df['home_away'].isin(selected_venue))
    filtered_df = df[mask]
    
    # استخراج داتا المباريات الفريدة للـ KPIs
    match_data = filtered_df.drop_duplicates(subset=['match_id'])

    # --- 4. العرض الرئيسي ---
    st.markdown("<h1 style='text-align: center; color: #edbb00; font-size: 50px;'>FC BARCELONA DASHBOARD</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>تحليل أداء الفريق - موسم {selected_season}</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # صف الـ KPIs الاحترافي
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        st.metric(label="إجمالي المباريات", value=len(match_data))
    with kpi2:
        total_goals = match_data['goals_for'].sum()
        st.metric(label="الأهداف المسجلة", value=total_goals)
    with kpi3:
        avg_poss = round(match_data['possession_pct'].mean(), 1)
        st.metric(label="متوسط الاستحواذ", value=f"{avg_poss}%")
    with kpi4:
        # احتساب نسبة الفوز
        wins = len(match_data[match_data['goals_for'] > match_data['goals_against']])
        win_rate = round((wins/len(match_data)*100), 1) if len(match_data) > 0 else 0
        st.metric(label="نسبة الفوز", value=f"{win_rate}%")

    st.markdown("<br><hr>", unsafe_allow_html=True)

    # --- 5. الرسوم البيانية ---
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 📊 توزيع الاستحواذ حسب الخصم")
        fig_poss = px.bar(match_data, x='opponent', y='possession_pct', 
                          color='possession_pct', color_continuous_scale='Reds',
                          template="plotly_dark")
        st.plotly_chart(fig_poss, use_container_width=True)

    with c2:
        st.markdown("### ⚽ الأهداف المسجلة مقابل xG")
        fig_xg = px.scatter(match_data, x='xG_x', y='goals_for', size='shots_x', 
                            color='goals_for', hover_data=['opponent'],
                            template="plotly_dark")
        st.plotly_chart(fig_xg, use_container_width=True)

    # --- 6. جدول البيانات ---
    st.markdown("### 📋 سجل المباريات التفصيلي")
    st.dataframe(match_data[['round', 'opponent', 'home_away', 'goals_for', 'goals_against', 'possession_pct']], 
                 use_container_width=True)

except Exception as e:
    st.error(f"حدث خطأ: {e}")

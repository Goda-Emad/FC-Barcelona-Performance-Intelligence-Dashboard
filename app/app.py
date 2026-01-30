import streamlit as st
import pandas as pd
import plotly.express as px
import os

# إعدادات الصفحة
st.set_page_config(page_title="Barça Intelligence Dashboard", layout="wide", page_icon="🔵")

# تصميم CSS للهوية البصرية (ألوان برشلونة)
st.markdown("""
    <style>
    .main { background-color: #004d98; }
    div[data-testid="stMetricValue"] { color: #edbb00 !important; font-weight: bold; }
    .stMetric { background-color: rgba(165, 0, 68, 0.2); border-left: 5px solid #edbb00; padding: 10px; border-radius: 5px; }
    h1, h2, h3 { color: #edbb00 !important; font-family: 'Arial Black'; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    # حل مشكلة المسار: نتحرك خطوة للخلف من مجلد app ثم ندخل مجلد data
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, '..', 'data', 'FC_Barcelona_Big_Dataset_TimeSeries.csv')
    
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

try:
    df = load_data()

    # --- القائمة الجانبية ---
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/47/FC_Barcelona_logo.svg/200px-FC_Barcelona_logo.svg.png", width=150)
    st.sidebar.markdown("### إعدادات التحليل")
    
    selected_season = st.sidebar.multiselect("الموسم", options=df['Season'].unique(), default=df['Season'].unique()[:2])
    selected_venue = st.sidebar.radio("مكان المباراة", ["الكل", "Home", "Away"])

    # تصفية الداتا
    mask = df['Season'].isin(selected_season)
    if selected_venue != "الكل":
        mask &= (df['Venue'] == selected_venue)
    
    filtered_df = df[mask].sort_values('Date')

    # --- الواجهة الرئيسية ---
    st.title("🔵🔴 FC Barcelona Analytics Dashboard")
    st.markdown(f"تحليل أداء الفريق لمواسم: {', '.join(selected_season)}")

    # مؤشرات الأداء
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        wins = len(filtered_df[filtered_df['Result'] == 'W'])
        st.metric("عدد الانتصارات", wins)
    with kpi2:
        avg_poss = round(filtered_df['Poss'].mean(), 1)
        st.metric("متوسط الاستحواذ", f"{avg_poss}%")
    with kpi3:
        total_goals = filtered_df['GF'].sum()
        st.metric("الأهداف المسجلة", total_goals)
    with kpi4:
        win_rate = round((wins / len(filtered_df)) * 100, 1) if len(filtered_df) > 0 else 0
        st.metric("نسبة الفوز", f"{win_rate}%")

    st.markdown("---")

    # الرسوم البيانية
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📈 تطور الأهداف خلال الموسم")
        fig_line = px.line(filtered_df, x='Date', y=['GF', 'GA'], 
                           color_discrete_map={"GF": "#edbb00", "GA": "#a50044"},
                           template="plotly_dark")
        st.plotly_chart(fig_line, use_container_width=True)

    with col_right:
        st.subheader("🛡️ النتائج حسب الخصوم")
        fig_bar = px.bar(filtered_df, x='Opponent', y='GF', color='Result',
                         color_discrete_map={"W": "#004d98", "D": "#7f7f7f", "L": "#a50044"},
                         template="plotly_dark")
        st.plotly_chart(fig_bar, use_container_width=True)

    # عرض جدول البيانات بصورة أنيقة
    st.subheader("📋 سجل المباريات المختار")
    st.dataframe(filtered_df[['Date', 'Opponent', 'Result', 'GF', 'GA', 'Poss', 'Attendance']], use_container_width=True)

except Exception as e:
    st.error(f"خطأ في تحميل الملف: {e}")
    st.info("تأكد من أن الكود موجود داخل مجلد 'app' والبيانات داخل مجلد 'data'.")

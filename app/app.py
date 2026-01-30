import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- إعدادات الصفحة والهوية البصرية ---
st.set_page_config(page_title="Barça Intelligence Dashboard", layout="wide", page_icon="🔵")

# تصميم CSS مخصص لخلفية احترافية وألوان النادي
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #004d98 0%, #a50044 100%);
        color: white;
    }
    [data-testid="stMetricValue"] { color: #edbb00 !important; font-size: 32px; }
    .stMetric {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(237, 187, 0, 0.4);
        border-radius: 12px;
        padding: 15px;
    }
    .plot-container { border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    # حل مشكلة المسار للوصول لمجلد data من داخل مجلد app
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, '..', 'data', 'FC_Barcelona_Big_Dataset_TimeSeries.csv')
    
    # تحميل البيانات وتحويل التواريخ
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

try:
    df = load_data()

    # --- القائمة الجانبية (Sidebar) ---
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/47/FC_Barcelona_logo.svg/200px-FC_Barcelona_logo.svg.png", width=120)
    st.sidebar.markdown("## فلاتر التحليل")
    
    seasons = st.sidebar.multiselect("📅 الموسم", options=df['Season'].unique(), default=df['Season'].unique()[:3])
    venue = st.sidebar.radio("🏟️ الملعب", ["الكل", "Home", "Away"])
    
    # تصفية البيانات بناءً على الاختيارات
    filtered_df = df[df['Season'].isin(seasons)]
    if venue != "الكل":
        filtered_df = filtered_df[filtered_df['Venue'] == venue]

    # --- الواجهة الرئيسية ---
    st.title("🔵🔴 FC Barcelona Intelligence Hub")
    st.markdown("---")

    # صف المؤشرات (KPIs)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("إجمالي المباريات", len(filtered_df))
    with kpi2:
        win_rate = round((len(filtered_df[filtered_df['Result'] == 'W']) / len(filtered_df)) * 100, 1) if len(filtered_df)>0 else 0
        st.metric("نسبة الفوز", f"{win_rate}%")
    with kpi3:
        st.metric("أهداف مسجلة (GF)", filtered_df['GF'].sum()) #
    with kpi4:
        avg_poss = round(filtered_df['Poss'].mean(), 1) #
        st.metric("متوسط الاستحواذ", f"{avg_poss}%")

    st.markdown("---")

    # الرسوم البيانية
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 تحليل الأهداف المسجلة والمستقبلة")
        fig_goals = px.area(filtered_df.sort_values('Date'), x='Date', y=['GF', 'GA'], 
                            color_discrete_map={"GF": "#edbb00", "GA": "#ffffff"},
                            template="plotly_dark")
        st.plotly_chart(fig_goals, use_container_width=True)

    with col2:
        st.subheader("🎯 الاستحواذ مقابل النتيجة")
        fig_scatter = px.scatter(filtered_df, x='Poss', y='GF', color='Result',
                                 hover_data=['Opponent', 'Date'],
                                 color_discrete_map={"W": "#00c853", "D": "#ffd600", "L": "#d50000"},
                                 template="plotly_dark")
        st.plotly_chart(fig_scatter, use_container_width=True)

    # جدول البيانات
    with st.expander("📋 عرض تفاصيل المباريات"):
        st.dataframe(filtered_df[['Date', 'Opponent', 'Result', 'GF', 'GA', 'Poss', 'Attendance']], 
                     use_container_width=True)

except Exception as e:
    st.error(f"حدث خطأ في المسار: {e}")
    st.info("تأكد من تحديث المستودع ليكون ملف البيانات داخل مجلد data والكود داخل app.")

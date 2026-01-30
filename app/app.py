import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- إعدادات الصفحة والهوية البصرية ---
st.set_page_config(page_title="Barça Intelligence Hub", layout="wide", page_icon="⚽")

# تصميم CSS احترافي (ألوان برشلونة مع خلفية متدرجة)
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #004d98 0%, #a50044 100%);
        color: white;
    }
    .stMetric {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid #edbb00;
        border-radius: 15px;
        padding: 20px;
    }
    div[data-testid="stMetricValue"] { color: #edbb00 !important; }
    .plot-container { border: 2px solid rgba(237, 187, 0, 0.3); border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    # حل مشكلة المسار (الخروج من app والدخول إلى data)
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, '..', 'data', 'FC_Barcelona_Big_Dataset_TimeSeries.csv')
    
    if not os.path.exists(file_path):
        # محاولة بديلة إذا كان التشغيل محلياً من المجلد الرئيسي
        file_path = 'data/FC_Barcelona_Big_Dataset_TimeSeries.csv'

    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

try:
    df = load_data()

    # --- القائمة الجانبية (Sidebar) مع الفلاتر ---
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/47/FC_Barcelona_logo.svg/200px-FC_Barcelona_logo.svg.png", width=120)
    st.sidebar.title("لوحة التحكم الذكية")
    
    st.sidebar.markdown("---")
    season_filter = st.sidebar.multiselect("📅 اختر المواسم:", options=df['Season'].unique(), default=df['Season'].unique()[:3])
    venue_filter = st.sidebar.multiselect("🏟️ مكان المباراة:", options=df['Venue'].unique(), default=df['Venue'].unique())
    result_filter = st.sidebar.multiselect("🎯 النتيجة:", options=df['Result'].unique(), default=df['Result'].unique())

    # تطبيق الفلاتر
    filtered_df = df[
        (df['Season'].isin(season_filter)) & 
        (df['Venue'].isin(venue_filter)) & 
        (df['Result'].isin(result_filter))
    ]

    # --- الواجهة الرئيسية ---
    st.title("📊 FC Barcelona Performance Analytics")
    st.subheader(f"تحليل البيانات لـ {len(filtered_df)} مباراة")

    # صف المؤشرات الرئيسية (KPIs)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("إجمالي الأهداف (له)", filtered_df['GF'].sum())
    with m2:
        st.metric("إجمالي الأهداف (عليه)", filtered_df['GA'].sum())
    with m3:
        avg_poss = round(filtered_df['Poss'].mean(), 1)
        st.metric("متوسط الاستحواذ", f"{avg_poss}%")
    with m4:
        win_count = len(filtered_df[filtered_df['Result'] == 'W'])
        win_pct = round((win_count / len(filtered_df) * 100), 1) if len(filtered_df) > 0 else 0
        st.metric("نسبة الفوز", f"{win_pct}%")

    st.markdown("---")

    # الرسوم البيانية التفاعلية
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 الأهداف المسجلة عبر الزمن")
        fig_line = px.area(filtered_df.sort_values('Date'), x='Date', y='GF', 
                           line_shape='spline', color_discrete_sequence=['#edbb00'],
                           template="plotly_dark")
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        st.markdown("### 📊 توزيع الاستحواذ حسب الخصم")
        # عرض أفضل 15 خصم من حيث الاستحواذ
        top_poss = filtered_df.groupby('Opponent')['Poss'].mean().sort_values(ascending=False).head(15).reset_index()
        fig_bar = px.bar(top_poss, x='Poss', y='Opponent', orientation='h',
                         color='Poss', color_continuous_scale='Reds',
                         template="plotly_dark")
        st.plotly_chart(fig_bar, use_container_width=True)

    # جدول البيانات التفاعلي
    st.markdown("### 📋 تفاصيل المباريات المصفاة")
    st.dataframe(filtered_df[['Date', 'Season', 'Opponent', 'Venue', 'Result', 'GF', 'GA', 'Poss']], 
                 use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"❌ تعذر تحميل البيانات: {e}")
    st.warning("تأكد من تحديث مستودع GitHub الخاص بك وأن ملف البيانات موجود في مجلد 'data'.")

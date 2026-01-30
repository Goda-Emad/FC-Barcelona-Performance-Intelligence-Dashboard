import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# إعدادات الصفحة
st.set_page_config(page_title="FC Barcelona Intelligence Dashboard", layout="wide")

# تصميم CSS مخصص لهوية برشلونة
st.markdown("""
    <style>
    .main {
        background-color: #004d98; /* أزرق برشلونة */
        color: white;
    }
    .stMetric {
        background-color: #a50044; /* أحمر برشلونة */
        padding: 15px;
        border-radius: 10px;
        color: white !important;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #edbb00; /* ذهبي */
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv('FC_Barcelona_Big_Dataset_TimeSeries.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    return df

try:
    df = load_data()

    # --- القائمة الجانبية (Side Bar) للفلاتر ---
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/47/FC_Barcelona_logo.svg/1200px-FC_Barcelona_logo.svg.png", width=100)
    st.sidebar.title("الفلاتر الذكية")
    
    seasons = st.sidebar.multiselect("اختر الموسم:", options=df['Season'].unique(), default=df['Season'].unique()[:3])
    venues = st.sidebar.multiselect("مكان المباراة:", options=df['Venue'].unique(), default=df['Venue'].unique())
    opponents = st.sidebar.selectbox("اختر خصم معين (اختياري):", options=["الكل"] + list(df['Opponent'].unique()))

    # تصفية البيانات
    filtered_df = df[df['Season'].isin(seasons) & df['Venue'].isin(venues)]
    if opponents != "الكل":
        filtered_df = filtered_df[filtered_df['Opponent'] == opponents]

    # --- الواجهة الرئيسية ---
    st.title("📊 FC Barcelona Performance Intelligence")
    st.markdown("---")

    # الصف الأول: مؤشرات الأداء (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("إجمالي المباريات", len(filtered_df))
    with col2:
        avg_goals = round(filtered_df['GF'].mean(), 2)
        st.metric("معدل الأهداف/مباراة", avg_goals)
    with col3:
        win_rate = round((len(filtered_df[filtered_df['Result'] == 'W']) / len(filtered_df)) * 100, 1)
        st.metric("نسبة الفوز", f"{win_rate}%")
    with col4:
        avg_poss = round(filtered_df['Poss'].mean(), 1)
        st.metric("متوسط الاستحواذ", f"{avg_poss}%")

    st.markdown("---")

    # الصف الثاني: الرسوم البيانية
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📈 اتجاه الأهداف المسجلة والمستقبلة")
        fig_goals = px.line(filtered_df.sort_values('Date'), x='Date', y=['GF', 'GA'], 
                             labels={'value': 'الأهداف', 'Date': 'التاريخ'},
                             color_discrete_map={"GF": "#edbb00", "GA": "#a50044"},
                             template="plotly_dark")
        st.plotly_chart(fig_goals, use_container_width=True)

    with c2:
        st.subheader("🎯 الاستحواذ مقابل النتيجة")
        fig_poss = px.scatter(filtered_df, x='Poss', y='GF', color='Result',
                               size='Poss', hover_data=['Opponent', 'Date'],
                               color_discrete_map={"W": "green", "D": "gray", "L": "red"},
                               template="plotly_dark")
    st.plotly_chart(fig_poss, use_container_width=True)

    # الصف الثالث: تحليل الخصوم
    st.subheader("🏟️ تحليل الأداء أمام أقوى الخصوم")
    top_opponents = filtered_df.groupby('Opponent')['GF'].sum().sort_values(ascending=False).head(10).reset_index()
    fig_bar = px.bar(top_opponents, x='Opponent', y='GF', color='GF', 
                      color_continuous_scale='Reds', template="plotly_dark")
    st.plotly_chart(fig_bar, use_container_width=True)

    # عرض البيانات الخام
    with st.expander("🔍 استعراض البيانات المصفاة"):
        st.dataframe(filtered_df.style.highlight_max(axis=0, subset=['GF', 'Poss'], color='#edbb00'))

except Exception as e:
    st.error(f"حدث خطأ أثناء تحميل البيانات: {e}")
    st.info("تأكد من وجود ملف 'FC_Barcelona_Big_Dataset_TimeSeries.csv' في نفس مجلد الكود.")

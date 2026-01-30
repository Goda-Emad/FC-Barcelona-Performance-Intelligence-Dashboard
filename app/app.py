import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- إعدادات الصفحة ---
st.set_page_config(page_title="FCB Analytics", layout="wide")

# تصميم CSS للهوية البصرية
st.markdown("""
    <style>
    .main { background-color: #004d98; color: white; }
    .stMetric { background-color: rgba(165, 0, 68, 0.2); border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    # 1. تحديد المسار بدقة
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, '..', 'data', 'FC_Barcelona_Big_Dataset_TimeSeries.csv')
    
    # 2. قراءة البيانات مع معالجة الأسماء
    df = pd.read_csv(file_path)
    
    # تنظيف أسماء الأعمدة من أي مسافات زائدة
    df.columns = df.columns.str.strip()
    
    # التأكد من وجود عمود التاريخ وتحويله
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date']) # حذف الصفوف التي لا تحتوي على تاريخ صحيح
    else:
        st.error("لم يتم العثور على عمود باسم 'Date'. الأعمدة المتاحة هي: " + str(df.columns.tolist()))
        
    return df

try:
    df = load_data()

    # --- القائمة الجانبية ---
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/47/FC_Barcelona_logo.svg/200px-FC_Barcelona_logo.svg.png", width=100)
    
    # فلتر المواسم
    seasons = st.sidebar.multiselect("اختر الموسم", options=df['Season'].unique(), default=df['Season'].unique()[:2])
    
    filtered_df = df[df['Season'].isin(seasons)].sort_values('Date')

    # --- العرض الرئيسي ---
    st.title("🔵🔴 FC Barcelona Performance Hub")
    
    # عرض الـ KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المباريات", len(filtered_df))
    col2.metric("متوسط الاستحواذ", f"{round(filtered_df['Poss'].mean(), 1)}%")
    col3.metric("الأهداف المسجلة", filtered_df['GF'].sum())

    # رسم بياني احترافي
    fig = px.line(filtered_df, x='Date', y='GF', title='تطور التهديف عبر الزمن',
                  color_discrete_sequence=['#edbb00'], template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # عرض البيانات
    st.dataframe(filtered_df, use_container_width=True)

except Exception as e:
    st.error(f"حدث خطأ: {e}")

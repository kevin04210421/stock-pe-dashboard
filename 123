
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

@st.cache_data
def load_data():
    df = pd.read_csv("pe_summary_with_name.csv")
    return df

df = load_data()

st.title("📈 台股本益比河流圖分析系統")

sectors = st.multiselect("選擇公司名稱", options=df['公司名稱'].unique(), default=None)
only_undervalued = st.checkbox("只顯示跌破低估")

filtered_df = df.copy()
if sectors:
    filtered_df = filtered_df[filtered_df['公司名稱'].isin(sectors)]
if only_undervalued:
    filtered_df = filtered_df[filtered_df['是否跌破低估'] == True]

st.subheader("📊 篩選結果")
st.dataframe(filtered_df, use_container_width=True)

selected_stock = st.selectbox("🔍 選擇查看河流圖", options=filtered_df['stock_id'].unique())
chart_path = f"pe_charts/{selected_stock}_pe.png"
if os.path.exists(chart_path):
    st.image(chart_path, caption=f"{selected_stock} 河流圖")
else:
    st.warning("找不到圖片")

st.markdown("---")
st.caption("由 ChatGPT 協助產出 Streamlit App")

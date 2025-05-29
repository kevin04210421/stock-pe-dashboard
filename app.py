
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from FinMind.data import DataLoader

# 初始化 API
api = DataLoader()
api.login_by_token(api_token="your_token_here")  # ← 改成你的 token

# Streamlit 介面
st.set_page_config(page_title="台股河流圖分析", layout="wide")
st.title("📈 台股即時本益比河流圖分析（含波動率）")

# 使用者輸入
stock_id = st.text_input("輸入股票代碼（例如 2330）", value="2330")
years = st.slider("選擇歷史年限", 3, 10, 5)
show_vol = st.checkbox("顯示股價波動率指標", value=True)

if stock_id:
    # 取得歷史股價
    start_date = f"{pd.Timestamp.today().year - years}-01-01"
    end_date = pd.Timestamp.today().strftime("%Y-%m-%d")
    price = api.taiwan_stock_daily(
        stock_id=stock_id,
        start_date=start_date,
        end_date=end_date
    )
    price["date"] = pd.to_datetime(price["date"])
    price = price.sort_values("date")

    # 取得 EPS 財報
    eps_data = api.taiwan_stock_financial_statement(
        stock_id=stock_id,
        start_date=start_date,
        end_date=end_date
    )
    eps_data = eps_data[eps_data["type"] == "EPS"]
    eps_data = eps_data[["date", "value"]].rename(columns={"value": "eps"})
    eps_data["date"] = pd.to_datetime(eps_data["date"])
    eps_data = eps_data.set_index("date").resample("D").ffill().reset_index()

    # 合併計算 PE
    df = pd.merge(price, eps_data, on="date", how="left")
    df["pe"] = df["close"] / df["eps"]
    df = df.dropna(subset=["pe", "eps"])
    median_pe = df["pe"].median()

    # 計算 PE 區間
    pe_levels = {
        "低估": median_pe * 0.8,
        "合理": median_pe,
        "偏高": median_pe * 1.2,
        "高估": median_pe * 1.4,
    }

    # 波動率（60日）
    if show_vol:
        df["return"] = df["close"].pct_change()
        df["volatility_60"] = df["return"].rolling(60).std() * np.sqrt(252)

    # 畫圖
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["date"], df["close"], label="股價", color="black")
    for label, pe_val in pe_levels.items():
        ax.plot(df["date"], pe_val * df["eps"], linestyle="--", label=label)
    ax.set_title(f"{stock_id} 河流圖（PE 中位數：{median_pe:.1f}）")
    ax.legend()

    if show_vol:
        ax2 = ax.twinx()
        ax2.plot(df["date"], df["volatility_60"], color="purple", alpha=0.3, label="波動率(60日)")
        ax2.set_ylabel("波動率")
        ax2.legend(loc="upper right")

    st.pyplot(fig)

    # 顯示表格
    st.subheader("📊 最新資料")
    latest = df.dropna().iloc[-1]
    st.write({
        "收盤價": latest["close"],
        "EPS": latest["eps"],
        "PE": round(latest["pe"], 2),
        "中位PE": round(median_pe, 2),
        "波動率(60日)": f"{latest['volatility_60'] * 100:.2f}%" if show_vol else "未計算"
    })

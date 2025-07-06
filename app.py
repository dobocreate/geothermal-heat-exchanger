"""
地中熱交換システム計算ツール
Streamlitアプリケーション
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ページ設定
st.set_page_config(
    page_title="地中熱交換システム計算ツール",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# タイトル
st.title("🌡️ 地中熱交換システム計算ツール")
st.markdown("地中熱交換システムの性能計算と最適化を行います")

# サイドバー - 入力パラメータ
st.sidebar.header("📊 計算条件")

# 基本パラメータ
st.sidebar.subheader("基本条件")
initial_temp = st.sidebar.slider("初期温度 (℃)", 20.0, 40.0, 30.0, 0.1)
ground_temp = st.sidebar.slider("地下水温度 (℃)", 10.0, 20.0, 15.0, 0.1)
flow_rate = st.sidebar.slider("総流量 (L/min)", 20.0, 100.0, 50.0, 1.0)
pipe_length = st.sidebar.slider("管浸水距離 (m)", 3.0, 15.0, 5.0, 0.5)

# 配管条件
st.sidebar.subheader("配管条件")
pipe_material = st.sidebar.selectbox(
    "配管材質",
    ["鋼管", "アルミ管", "銅管"]
)

# メイン画面
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📈 計算結果")
    
    # 仮の計算結果（後で実装）
    final_temp = initial_temp - (initial_temp - ground_temp) * 0.28
    efficiency = ((initial_temp - final_temp) / (initial_temp - ground_temp)) * 100
    
    # 結果表示
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric("最終温度", f"{final_temp:.1f}℃", f"{final_temp - initial_temp:.1f}℃")
    
    with metric_col2:
        st.metric("熱交換効率", f"{efficiency:.1f}%")
    
    with metric_col3:
        st.metric("温度降下", f"{initial_temp - final_temp:.1f}℃")

with col2:
    st.header("⚙️ 最適化提案")
    
    if final_temp > 23.0:
        st.warning("⚠️ 目標温度（22-23℃）を超えています")
        st.markdown("**改善提案：**")
        st.markdown("- 管長を約20mに延長")
        st.markdown("- 地下水循環システムの導入")
        st.markdown("- 32A配管の使用")
    else:
        st.success("✅ 目標温度範囲内です")

# 詳細計算結果
st.header("📋 詳細計算結果")

# 仮の管径別比較データ
pipe_data = {
    "管径": ["15A", "32A", "40A", "50A", "65A", "80A"],
    "最終温度(℃)": [27.2, 25.8, 27.3, 27.0, 28.0, 27.8],
    "効率(%)": [18.8, 27.9, 18.1, 20.0, 13.5, 14.4],
    "流速(m/s)": [1.023, 0.236, 0.365, 0.217, 0.275, 0.203]
}

df = pd.DataFrame(pipe_data)
st.dataframe(df, use_container_width=True)

# グラフ表示
st.header("📊 視覚化")

# 管径別効率比較
fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=("管径別効率", "管径別最終温度"),
    specs=[[{"secondary_y": False}, {"secondary_y": False}]]
)

# 効率グラフ
fig.add_trace(
    go.Bar(x=df["管径"], y=df["効率(%)"], name="効率", marker_color="blue"),
    row=1, col=1
)

# 温度グラフ
fig.add_trace(
    go.Scatter(x=df["管径"], y=df["最終温度(℃)"], mode="lines+markers", 
               name="最終温度", line=dict(color="red")),
    row=1, col=2
)

fig.update_layout(height=400, showlegend=True)
st.plotly_chart(fig, use_container_width=True)

# フッター
st.markdown("---")
st.markdown("**開発者**: dobocreate | **バージョン**: 1.0.1 | **更新**: 2024-07-06")
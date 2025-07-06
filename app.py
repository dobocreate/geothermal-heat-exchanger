"""
地中熱交換システム計算ツール
Streamlitアプリケーション
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math

# ページ設定
st.set_page_config(
    page_title="地中熱交換システム計算ツール",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# サイドバー - ページ選択
page = st.sidebar.selectbox(
    "ページ選択",
    ["🔧 計算ツール", "📚 理論解説"]
)

if page == "🔧 計算ツール":
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
    pipe_diameter = st.sidebar.selectbox(
        "配管口径",
        ["15A", "20A", "25A", "32A", "40A", "50A", "65A", "80A"],
        index=3  # デフォルトは32A
    )

    # 地下水温度変化の設定
    st.sidebar.subheader("地下水温度設定")
    consider_groundwater_temp_rise = st.sidebar.checkbox(
        "地下水温度上昇を考慮する",
        value=False,
        help="長期運転による地下水温度の上昇を考慮する場合はチェック"
    )
    if consider_groundwater_temp_rise:
        groundwater_temp_rise = st.sidebar.slider(
            "地下水温度上昇値 (℃)", 
            0.0, 5.0, 2.0, 0.1,
            help="長期運転による地下水温度の上昇分"
        )

    # メイン画面
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📈 計算結果")
        
        # 配管仕様データ（内径mm）
        pipe_specs = {
        "15A": 16.1,
        "20A": 21.6,
        "25A": 27.6,
        "32A": 35.7,
        "40A": 41.6,
        "50A": 52.9,
        "65A": 67.9,
        "80A": 80.7
        }
        
        # 材質による熱伝導率 (W/m・K)
        thermal_conductivity = {
        "鋼管": 50.0,
        "アルミ管": 237.0,
        "銅管": 398.0
        }
        
        # 実効地下水温度の計算
        effective_ground_temp = ground_temp
        if consider_groundwater_temp_rise:
            effective_ground_temp += groundwater_temp_rise
        
        # 配管内径と断面積の計算
        inner_diameter = pipe_specs[pipe_diameter] / 1000  # m
        pipe_area = math.pi * (inner_diameter / 2) ** 2  # m²
        
        # 流速の計算 (m/s)
        flow_rate_m3s = flow_rate / 60000  # L/min → m³/s
        velocity = flow_rate_m3s / pipe_area
        
        # レイノルズ数の計算（水の動粘度: 約1.0e-6 m²/s at 20℃）
        kinematic_viscosity = 1.0e-6
        reynolds = velocity * inner_diameter / kinematic_viscosity
        
        # プラントル数（水の場合、約7.0）
        prandtl = 7.0
        
        # ヌッセルト数の計算（層流/乱流判定）
        if reynolds < 2300:  # 層流
            nusselt = 3.66
        else:  # 乱流（Dittus-Boelter式）
            nusselt = 0.023 * (reynolds ** 0.8) * (prandtl ** 0.3)
        
        # 熱伝達係数の計算 (W/m²・K)
        water_thermal_conductivity = 0.6  # W/m・K（水の熱伝導率）
        heat_transfer_coefficient = nusselt * water_thermal_conductivity / inner_diameter
        
        # 配管の熱抵抗を考慮した総括熱伝達係数
        pipe_thickness = 0.003  # 配管厚さ（仮定値: 3mm）
        pipe_thermal_cond = thermal_conductivity[pipe_material]
        
        # 総括熱伝達係数 U (W/m²・K)
        U = 1 / (1/heat_transfer_coefficient + pipe_thickness/pipe_thermal_cond)
        
        # 熱交換面積
        heat_exchange_area = math.pi * inner_diameter * pipe_length
        
        # 水の比熱と質量流量
        specific_heat = 4186  # J/kg・K
        density = 1000  # kg/m³
        mass_flow_rate = flow_rate_m3s * density  # kg/s
        
        # NTU（伝熱単位数）の計算
        NTU = U * heat_exchange_area / (mass_flow_rate * specific_heat)
        
        # 効率の計算（対向流型熱交換器として近似）
        effectiveness = 1 - math.exp(-NTU)
        
        # 最終温度の計算
        final_temp = initial_temp - effectiveness * (initial_temp - effective_ground_temp)
        
        # 熱交換効率（％）
        if initial_temp != effective_ground_temp:
            efficiency = effectiveness * 100
        else:
            efficiency = 0
        
        # 結果表示
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        
        with metric_col1:
            st.metric("最終温度", f"{final_temp:.1f}℃", f"{final_temp - initial_temp:.1f}℃")
        
        with metric_col2:
            st.metric("熱交換効率", f"{efficiency:.1f}%")
        
        with metric_col3:
            st.metric("温度降下", f"{initial_temp - final_temp:.1f}℃")
        
        # 追加の計算結果表示
        st.subheader("詳細パラメータ")
        detail_col1, detail_col2, detail_col3, detail_col4 = st.columns(4)
        
        with detail_col1:
            st.metric("流速", f"{velocity:.3f} m/s")
        
        with detail_col2:
            st.metric("レイノルズ数", f"{reynolds:.0f}")
        
        with detail_col3:
            st.metric("熱伝達係数", f"{heat_transfer_coefficient:.0f} W/m²·K")
        
        with detail_col4:
            st.metric("NTU", f"{NTU:.3f}")

    with col2:
        st.header("⚙️ 最適化提案")
        
        if final_temp > 23.0:
            st.warning("⚠️ 目標温度（22-23℃）を超えています")
            st.markdown("**改善提案：**")
            if pipe_length < 20:
                st.markdown(f"- 管浸水距離を約{20}mに延長（現在: {pipe_length}m）")
            else:
                st.markdown("- より大口径の配管を検討")
            st.markdown("- 地下水循環システムの導入")
            st.markdown("- 32A配管の使用")
        else:
            st.success("✅ 目標温度範囲内です")

    # 詳細計算結果
    st.header("📋 詳細計算結果")

    # 管径別比較データの計算
    pipe_comparison = []
    for pipe_size in ["15A", "20A", "25A", "32A", "40A", "50A", "65A", "80A"]:
        # 各管径での計算
        inner_d = pipe_specs[pipe_size] / 1000
        area = math.pi * (inner_d / 2) ** 2
        vel = flow_rate_m3s / area
        re = vel * inner_d / kinematic_viscosity
        
        if re < 2300:
            nu = 3.66
        else:
            nu = 0.023 * (re ** 0.8) * (prandtl ** 0.3)
        
        h = nu * water_thermal_conductivity / inner_d
        U_temp = 1 / (1/h + pipe_thickness/pipe_thermal_cond)
        A_temp = math.pi * inner_d * pipe_length
        NTU_temp = U_temp * A_temp / (mass_flow_rate * specific_heat)
        eff_temp = 1 - math.exp(-NTU_temp)
        final_t = initial_temp - eff_temp * (initial_temp - effective_ground_temp)
        
        pipe_comparison.append({
            "管径": pipe_size,
            "最終温度(℃)": round(final_t, 1),
            "効率(%)": round(eff_temp * 100, 1),
            "流速(m/s)": round(vel, 3),
            "レイノルズ数": int(re)
        })

    df = pd.DataFrame(pipe_comparison)
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

    # 計算条件の表示
    st.header("📝 計算条件")
    condition_col1, condition_col2, condition_col3 = st.columns(3)

    with condition_col1:
        st.markdown("**基本条件**")
        st.markdown(f"- 初期温度: {initial_temp}℃")
        st.markdown(f"- 地下水温度: {ground_temp}℃")
        if consider_groundwater_temp_rise:
            st.markdown(f"- 地下水温度上昇: +{groundwater_temp_rise}℃")
            st.markdown(f"- 実効地下水温度: {effective_ground_temp}℃")

    with condition_col2:
        st.markdown("**流量条件**")
        st.markdown(f"- 総流量: {flow_rate} L/min")
        st.markdown(f"- 管浸水距離: {pipe_length} m")
        st.markdown(f"- 配管口径: {pipe_diameter}")

    with condition_col3:
        st.markdown("**配管仕様**")
        st.markdown(f"- 配管材質: {pipe_material}")
        st.markdown(f"- 内径: {inner_diameter*1000:.1f} mm")
        st.markdown(f"- 熱伝導率: {pipe_thermal_cond} W/m·K")

    # フッター
    st.markdown("---")
    st.markdown("**開発者**: dobocreate | **バージョン**: 1.1.0 | **更新**: 2025-01-06")

elif page == "📚 理論解説":
    st.title("📚 地中熱交換システムの理論解説")
    st.markdown("地中熱交換システムの計算に使用している理論と数式について解説します")
    
    # 理論解説の内容
    st.header("1. 熱交換の基本原理")
    st.markdown("""
    地中熱交換システムは、地下水と配管内の流体との間で熱交換を行うシステムです。
    本ツールでは、以下の理論に基づいて計算を行っています。
    """)
    
    st.header("2. レイノルズ数（Re）")
    st.latex(r"Re = \frac{vD}{\nu}")
    st.markdown("""
    - v: 流速 [m/s]
    - D: 配管内径 [m]
    - ν: 動粘度 [m²/s]
    
    Re < 2300: 層流、Re ≥ 2300: 乱流
    """)
    
    st.header("3. ヌッセルト数（Nu）")
    st.markdown("**層流の場合（Re < 2300）:**")
    st.latex(r"Nu = 3.66")
    
    st.markdown("**乱流の場合（Re ≥ 2300）- Dittus-Boelter式:**")
    st.latex(r"Nu = 0.023 \cdot Re^{0.8} \cdot Pr^{0.3}")
    st.markdown("- Pr: プラントル数（水の場合、約7.0）")
    
    st.header("4. 熱伝達係数（h）")
    st.latex(r"h = \frac{Nu \cdot k}{D}")
    st.markdown("""
    - k: 流体の熱伝導率 [W/m·K]
    - D: 配管内径 [m]
    """)
    
    st.header("5. 総括熱伝達係数（U）")
    st.latex(r"\frac{1}{U} = \frac{1}{h} + \frac{t}{k_{pipe}}")
    st.markdown("""
    - t: 配管厚さ [m]
    - k_pipe: 配管材質の熱伝導率 [W/m·K]
    """)
    
    st.header("6. NTU（伝熱単位数）法")
    st.latex(r"NTU = \frac{UA}{\dot{m}c_p}")
    st.markdown("""
    - A: 熱交換面積 [m²] = πDL
    - ṁ: 質量流量 [kg/s]
    - c_p: 比熱 [J/kg·K]
    """)
    
    st.header("7. 熱交換効率（ε）")
    st.latex(r"\varepsilon = 1 - e^{-NTU}")
    st.markdown("対向流型熱交換器として近似した場合の効率")
    
    st.header("8. 最終温度の計算")
    st.latex(r"T_{final} = T_{initial} - \varepsilon(T_{initial} - T_{ground})")
    st.markdown("""
    - T_initial: 初期温度 [℃]
    - T_ground: 地下水温度 [℃]
    - T_final: 最終温度 [℃]
    """)
    
    st.header("9. 配管材質の熱伝導率")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        | 材質 | 熱伝導率 [W/m·K] |
        |------|------------------|
        | 鋼管 | 50.0 |
        | アルミ管 | 237.0 |
        | 銅管 | 398.0 |
        """)
    
    with col2:
        st.markdown("""
        | 配管口径 | 内径 [mm] |
        |----------|----------|
        | 15A | 16.1 |
        | 20A | 21.6 |
        | 25A | 27.6 |
        | 32A | 35.7 |
        | 40A | 41.6 |
        | 50A | 52.9 |
        | 65A | 67.9 |
        | 80A | 80.7 |
        """)
    
    st.info("""
    💡 **注意事項**
    - 本計算は理想的な条件下での理論値です
    - 実際の性能は、地下水の流動状態、配管の汚れ、設置条件などにより変動します
    - 長期運転時は地下水温度の上昇を考慮する必要があります
    """)
    
    # フッター
    st.markdown("---")
    st.markdown("**開発者**: dobocreate | **バージョン**: 1.1.0 | **更新**: 2025-01-06")
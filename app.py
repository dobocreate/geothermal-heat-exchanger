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

    # メイン画面にタブを設置
    tab1, tab2 = st.tabs(["🔧 単一配管計算", "📊 複数配管比較"])
    
    with tab1:
        # 単一配管計算ページ
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header("📈 計算結果")
        
        # 配管仕様データ（JIS規格に基づく内径mm）
        pipe_specs = {
            "15A": 16.1,
            "20A": 22.2,
            "25A": 28.0,
            "32A": 33.5,  # summary.mdに合わせて修正
            "40A": 41.2,
            "50A": 52.6,
            "65A": 67.8,
            "80A": 80.1
        }
        
        # 管径別の推奨本数（50L/minの総流量を分配）
        pipe_counts = {
            "15A": 1,   # 50 L/min × 1本
            "20A": 1,   # 50 L/min × 1本
            "25A": 1,   # 50 L/min × 1本
            "32A": 4,   # 12.5 L/min × 4本
            "40A": 2,   # 25 L/min × 2本
            "50A": 1,   # 50 L/min × 1本
            "65A": 1,   # 50 L/min × 1本
            "80A": 1    # 50 L/min × 1本
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
        
        # 平均温度の計算（物性値計算用）
        avg_temp = (initial_temp + effective_ground_temp) / 2
        
        # 配管内径と断面積の計算
        inner_diameter = pipe_specs[pipe_diameter] / 1000  # m
        pipe_area = math.pi * (inner_diameter / 2) ** 2  # m²
        
        # 1本あたりの流量を計算
        num_pipes = pipe_counts[pipe_diameter]
        flow_per_pipe = flow_rate / num_pipes  # L/min/本
        
        # 流速の計算 (m/s)
        flow_rate_m3s_per_pipe = flow_per_pipe / 60000  # L/min → m³/s
        velocity = flow_rate_m3s_per_pipe / pipe_area
        
        # 温度依存の物性値計算（平均温度基準）
        # 動粘度の計算 [m²/s]
        if avg_temp <= 20:
            kinematic_viscosity = 1.004e-6
            water_thermal_conductivity = 0.598
            prandtl = 7.01
            density = 998.2
            specific_heat = 4182
        elif avg_temp <= 25:
            # 線形補間
            t_ratio = (avg_temp - 20) / 5
            kinematic_viscosity = 1.004e-6 - (1.004e-6 - 0.893e-6) * t_ratio
            water_thermal_conductivity = 0.598 + (0.607 - 0.598) * t_ratio
            prandtl = 7.01 - (7.01 - 6.13) * t_ratio
            density = 998.2 - (998.2 - 997.0) * t_ratio
            specific_heat = 4182 - (4182 - 4179) * t_ratio
        else:
            kinematic_viscosity = 0.801e-6
            water_thermal_conductivity = 0.615
            prandtl = 5.42
            density = 995.6
            specific_heat = 4178
        
        reynolds = velocity * inner_diameter / kinematic_viscosity
        
        # ヌッセルト数の計算（層流/乱流判定）
        if reynolds < 2300:  # 層流
            nusselt = 3.66
        else:  # 乱流（Dittus-Boelter式、冷却時）
            nusselt = 0.023 * (reynolds ** 0.8) * (prandtl ** 0.3)
        
        # 熱伝達係数の計算 (W/m²・K)
        heat_transfer_coefficient = nusselt * water_thermal_conductivity / inner_diameter
        
        # 配管の熱抵抗を考慮した総括熱伝達係数
        # 外径の計算（概算）
        if pipe_diameter in ["15A", "20A", "25A"]:
            pipe_thickness = 0.0028  # 2.8mm
        elif pipe_diameter in ["32A", "40A"]:
            pipe_thickness = 0.0032  # 3.2mm
        else:
            pipe_thickness = 0.0036  # 3.6mm
        
        outer_diameter = inner_diameter + 2 * pipe_thickness
        pipe_thermal_cond = thermal_conductivity[pipe_material]
        
        # 管外側熱伝達係数（静止水中の自然対流）
        h_outer = 300  # W/m²·K
        
        # 総括熱伝達係数 U (W/m²・K)
        # 内径基準での計算
        U = 1 / (1/heat_transfer_coefficient + 
                inner_diameter/(2*pipe_thermal_cond) * math.log(outer_diameter/inner_diameter) + 
                inner_diameter/(outer_diameter*h_outer))
        
        # 熱交換面積（U字管として往復を考慮）
        total_length = pipe_length * 2  # 往復分
        heat_exchange_area = math.pi * inner_diameter * total_length
        
        # 質量流量（1本あたり）
        mass_flow_rate_per_pipe = flow_rate_m3s_per_pipe * density  # kg/s
        
        # NTU（伝熱単位数）の計算（1本あたり）
        NTU_per_pipe = U * heat_exchange_area / (mass_flow_rate_per_pipe * specific_heat)
        
        # 全体のNTU（並列配管の場合、1本あたりのNTUと同じ）
        NTU = NTU_per_pipe
        
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
        
        # 配管本数の表示
        st.metric("配管本数", f"{num_pipes} 本", f"1本あたり {flow_per_pipe:.1f} L/min")
        
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
        
        # 物性値の表示
        st.subheader(f"物性値（平均温度 {avg_temp:.1f}℃）")
        prop_col1, prop_col2, prop_col3, prop_col4 = st.columns(4)
        
        with prop_col1:
            st.metric("動粘度", f"{kinematic_viscosity*1e6:.3f}×10⁻⁶ m²/s")
        
        with prop_col2:
            st.metric("熱伝導率", f"{water_thermal_conductivity:.3f} W/m·K")
        
        with prop_col3:
            st.metric("プラントル数", f"{prandtl:.2f}")
        
        with prop_col4:
            st.metric("総括熱伝達係数", f"{U:.1f} W/m²·K")

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
            if pipe_diameter != "32A":
                st.markdown("- 32A配管の使用（最適効率）")
            else:
                st.markdown("- 複数の32A配管を並列配置")
        else:
            st.success("✅ 目標温度範囲内です")
        
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
            st.markdown(f"- 配管本数: {num_pipes} 本")
    
    with tab2:
        # 複数配管比較ページ
        st.header("📋 管径別比較結果")
        
        # 共通データの再定義
        pipe_specs = {
            "15A": 16.1,
            "20A": 22.2,
            "25A": 28.0,
            "32A": 33.5,
            "40A": 41.2,
            "50A": 52.6,
            "65A": 67.8,
            "80A": 80.1
        }
        
        pipe_counts = {
            "15A": 1,
            "20A": 1,
            "25A": 1,
            "32A": 4,
            "40A": 2,
            "50A": 1,
            "65A": 1,
            "80A": 1
        }
        
        thermal_conductivity = {
            "鋼管": 50.0,
            "アルミ管": 237.0,
            "銅管": 398.0
        }
        
        # 実効地下水温度の計算
        effective_ground_temp = ground_temp
        if consider_groundwater_temp_rise:
            effective_ground_temp += groundwater_temp_rise
        
        # 平均温度の計算
        avg_temp = (initial_temp + effective_ground_temp) / 2
        
        # 温度依存の物性値計算
        if avg_temp <= 20:
            kinematic_viscosity = 1.004e-6
            water_thermal_conductivity = 0.598
            prandtl = 7.01
            density = 998.2
            specific_heat = 4182
        elif avg_temp <= 25:
            t_ratio = (avg_temp - 20) / 5
            kinematic_viscosity = 1.004e-6 - (1.004e-6 - 0.893e-6) * t_ratio
            water_thermal_conductivity = 0.598 + (0.607 - 0.598) * t_ratio
            prandtl = 7.01 - (7.01 - 6.13) * t_ratio
            density = 998.2 - (998.2 - 997.0) * t_ratio
            specific_heat = 4182 - (4182 - 4179) * t_ratio
        else:
            kinematic_viscosity = 0.801e-6
            water_thermal_conductivity = 0.615
            prandtl = 5.42
            density = 995.6
            specific_heat = 4178
        
        pipe_thermal_cond = thermal_conductivity[pipe_material]
        h_outer = 300
        total_length = pipe_length * 2
        
        # 管径別比較データの計算
        pipe_comparison = []
        for pipe_size in ["15A", "20A", "25A", "32A", "40A", "50A", "65A", "80A"]:
            # 各管径での計算
            inner_d = pipe_specs[pipe_size] / 1000
            area = math.pi * (inner_d / 2) ** 2
            n_pipes = pipe_counts[pipe_size]
            flow_per_p = flow_rate / n_pipes
            flow_rate_m3s_per_p = flow_per_p / 60000
            vel = flow_rate_m3s_per_p / area
            re = vel * inner_d / kinematic_viscosity
            
            if re < 2300:
                nu = 3.66
            else:
                nu = 0.023 * (re ** 0.8) * (prandtl ** 0.3)
            
            h = nu * water_thermal_conductivity / inner_d
            
            # 外径の計算
            if pipe_size in ["15A", "20A", "25A"]:
                thickness = 0.0028
            elif pipe_size in ["32A", "40A"]:
                thickness = 0.0032
            else:
                thickness = 0.0036
            
            outer_d = inner_d + 2 * thickness
            
            # 総括熱伝達係数（内径基準）
            U_temp = 1 / (1/h + 
                         inner_d/(2*pipe_thermal_cond) * math.log(outer_d/inner_d) + 
                         inner_d/(outer_d*h_outer))
            
            A_temp = math.pi * inner_d * total_length
            mass_flow_per_p = flow_rate_m3s_per_p * density
            NTU_temp = U_temp * A_temp / (mass_flow_per_p * specific_heat)
            eff_temp = 1 - math.exp(-NTU_temp)
            final_t = initial_temp - eff_temp * (initial_temp - effective_ground_temp)
            
            pipe_comparison.append({
                "管径": pipe_size,
                "本数": n_pipes,
                "最終温度(℃)": round(final_t, 1),
                "効率(%)": round(eff_temp * 100, 1),
                "流速(m/s)": round(vel, 3),
                "レイノルズ数": int(re),
                "h_i(W/m²K)": int(h),
                "U(W/m²K)": round(U_temp, 1),
                "NTU": round(NTU_temp, 3)
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
        
        # 最適配管の提案
        st.header("🎆 最適配管の分析")
        
        # 最も効率が高い配管を特定
        best_pipe = df.loc[df["効率(%)"].idxmax()]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.success(f"🥇 最適配管: {best_pipe['管径']}")
            st.metric("最終温度", f"{best_pipe['最終温度(℃)']}℃")
        
        with col2:
            st.metric("効率", f"{best_pipe['効率(%)']}%")
            st.metric("本数", f"{best_pipe['本数']}本")
        
        with col3:
            st.metric("流速", f"{best_pipe['流速(m/s)']} m/s")
            st.metric("NTU", f"{best_pipe['NTU']}")

        # フッター
        st.markdown("---")
        st.markdown("**開発者**: dobocreate | **バージョン**: 1.2.0 | **更新**: 2025-01-06")

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
    
    st.header("9. 水の物性値（温度依存）")
    st.markdown("""
    | 温度[℃] | ρ[kg/m³] | ν[×10⁻⁶m²/s] | k[W/(m·K)] | Cp[J/kgK] | Pr[-] |
    |---------|----------|---------------|------------|-----------|-------|
    | 15 | 999.1 | 1.139 | 0.589 | 4186 | 8.09 |
    | 20 | 998.2 | 1.004 | 0.598 | 4182 | 7.01 |
    | **22.5** | **997.6** | **0.949** | **0.603** | **4181** | **6.57** |
    | 25 | 997.0 | 0.893 | 0.607 | 4179 | 6.13 |
    | 30 | 995.6 | 0.801 | 0.615 | 4178 | 5.42 |
    
    - ρ: 密度、ν: 動粘度、k: 熱伝導率、Cp: 比熱、Pr: プラントル数
    - **太字**: 平均温度22.5℃での参考値
    """)
    
    st.header("10. 配管仕様")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **材質の熱伝導率**
        | 材質 | 熱伝導率 [W/m·K] |
        |------|------------------|
        | 鋼管 | 50.0 |
        | アルミ管 | 237.0 |
        | 銅管 | 398.0 |
        """)
    
    with col2:
        st.markdown("""
        **JIS規格配管寸法**
        | 配管口径 | 内径 [mm] | 標準肉厚 [mm] |
        |----------|-----------|---------------|
        | 15A | 16.1 | 2.8 |
        | 20A | 22.2 | 2.8 |
        | 25A | 28.0 | 2.8 |
        | 32A | 33.5 | 3.2 |
        | 40A | 41.2 | 3.2 |
        | 50A | 52.6 | 3.6 |
        | 65A | 67.8 | 3.6 |
        | 80A | 80.1 | 3.6 |
        """)
    
    st.header("11. 管外側熱伝達係数")
    st.markdown("""
    **自然対流熱伝達係数の目安**
    - 静止水中：h_o = 300 W/(m²·K)
    - 弱い対流：h_o = 500-1000 W/(m²·K)
    - 強制対流：h_o = 1000-5000 W/(m²·K)
    
    本計算では、地下水中の自然対流として h_o = 300 W/(m²·K) を採用
    """)
    
    st.header("12. 計算の前提条件")
    st.markdown("""
    1. **U字管構造**：往路と復路の総延長で計算（片道5m × 2 = 10m）
    2. **地下水温度**：一定と仮定（大量の地下水により温度上昇は無視）
    3. **定常状態**：非定常な温度変化は考慮しない
    4. **一次元熱伝達**：径方向のみの熱伝達を考慮
    5. **管内流れ**：十分発達した流れと仮定
    """)
    
    st.info("""
    💡 **注意事項**
    - 本計算は理想的な条件下での理論値です
    - 実際の性能は、地下水の流動状態、配管の汚れ、設置条件などにより変動します
    - 長期運転時は地下水温度の上昇を考慮する必要があります
    - 配管の経年劣化による熱伝達性能の低下も考慮が必要です
    """)
    
    # フッター
    st.markdown("---")
    st.markdown("**開発者**: dobocreate | **バージョン**: 1.2.0 | **更新**: 2025-01-06")
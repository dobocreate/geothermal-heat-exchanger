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
    initial_sidebar_state="collapsed"
)

# サイドバー - ページ選択

# ページの初期化
if "page" not in st.session_state:
    st.session_state.page = "計算ツール"

# ボタンスタイルのカスタムCSS
st.markdown("""
<style>
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ボタンをコンテナに配置
button_col1 = st.sidebar.container()
button_col2 = st.sidebar.container()
button_col3 = st.sidebar.container()

# 各ボタンを配置（クリック時に即座にページを変更）
with button_col1:
    if st.button("🔧 計算ツール", use_container_width=True, 
                 type="primary" if st.session_state.page == "計算ツール" else "secondary",
                 key="btn_calc"):
        st.session_state.page = "計算ツール"
        st.rerun()

with button_col2:
    if st.button("📚 理論解説", use_container_width=True,
                 type="primary" if st.session_state.page == "理論解説" else "secondary",
                 key="btn_theory"):
        st.session_state.page = "理論解説"
        st.rerun()

with button_col3:
    if st.button("📊 物性値", use_container_width=True,
                 type="primary" if st.session_state.page == "物性値" else "secondary",
                 key="btn_props"):
        st.session_state.page = "物性値"
        st.rerun()

page = st.session_state.page

if page == "計算ツール":
    # タイトル
    st.markdown("<h1 style='text-align: center;'>🌡️ 地中熱交換簡易シミュレーター</h1>", unsafe_allow_html=True)
    st.markdown("地中に設置した管を通して通水した水の温度変化をシミュレーションするツールです。")
    
    # 計算条件の入力セクション
    st.header("📊 計算条件")
    
    # 左側に概念図、右側に計算条件を配置
    fig_col, input_col = st.columns([1, 2])
    
    with fig_col:
        st.image("geothermal.jpg", 
                 caption="地中熱交換システムの構造", 
                 use_container_width=True)
        st.markdown("""<small>
        ・管浸水距離 L: U字管の深さ<br>
        ・掘削径 φ: ボーリング孔の直径<br>
        ・1セット: 往路・復路の2本構成
        </small>""", unsafe_allow_html=True)
    
    with input_col:
        # 2行2列レイアウトで計算条件を配置
        # 1行目
        row1_col1, row1_col2 = st.columns([1, 1], gap="medium")
        
        with row1_col1:
            st.subheader("基本条件")
            
            # 目標出口温度
            target_col1, target_col2 = st.columns([3, 1])
            
            # セッション状態の初期化
            if "target_value" not in st.session_state:
                st.session_state.target_value = 23.0
            
            with target_col1:
                target_temp_slider = st.slider("目標出口温度 (℃)", 20.0, 30.0, st.session_state.target_value, 0.1, 
                                              help="最終温度との比較に使用する。計算には使用しない",
                                              key="target_slider")
            with target_col2:
                st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
                target_temp_input = st.number_input("", min_value=20.0, max_value=30.0, value=st.session_state.target_value, step=0.1, 
                                                   key="target_input", label_visibility="collapsed")
            
            # 同期処理：どちらかが変更されたら共通の値を更新
            if target_temp_slider != st.session_state.target_value:
                st.session_state.target_value = target_temp_slider
                st.rerun()
            elif target_temp_input != st.session_state.target_value:
                st.session_state.target_value = target_temp_input
                st.rerun()
            
            target_temp = st.session_state.target_value
            
            # 入口温度
            initial_col1, initial_col2 = st.columns([3, 1])
            
            if "initial_value" not in st.session_state:
                st.session_state.initial_value = 30.0
            
            with initial_col1:
                initial_temp_slider = st.slider("入口温度 (℃)", 20.0, 40.0, st.session_state.initial_value, 0.1, key="initial_slider")
            with initial_col2:
                st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
                initial_temp_input = st.number_input("", min_value=20.0, max_value=40.0, value=st.session_state.initial_value, step=0.1, 
                                                    key="initial_input", label_visibility="collapsed")
            
            if initial_temp_slider != st.session_state.initial_value:
                st.session_state.initial_value = initial_temp_slider
                st.rerun()
            elif initial_temp_input != st.session_state.initial_value:
                st.session_state.initial_value = initial_temp_input
                st.rerun()
            
            initial_temp = st.session_state.initial_value
            
            # 総流量
            flow_col1, flow_col2 = st.columns([3, 1])
            
            if "flow_value" not in st.session_state:
                st.session_state.flow_value = 50.0
            
            with flow_col1:
                flow_rate_slider = st.slider("総流量 (L/min)", 20.0, 100.0, st.session_state.flow_value, 1.0, key="flow_slider")
            with flow_col2:
                st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
                flow_rate_input = st.number_input("", min_value=20.0, max_value=100.0, value=st.session_state.flow_value, step=1.0, 
                                                 key="flow_input", label_visibility="collapsed")
            
            if flow_rate_slider != st.session_state.flow_value:
                st.session_state.flow_value = flow_rate_slider
                st.rerun()
            elif flow_rate_input != st.session_state.flow_value:
                st.session_state.flow_value = flow_rate_input
                st.rerun()
            
            flow_rate = st.session_state.flow_value
    
        with row1_col2:
            st.subheader("地盤条件")
            # 地下水温度
            ground_col1, ground_col2 = st.columns([3, 1])
            
            if "ground_value" not in st.session_state:
                st.session_state.ground_value = 15.0
            
            with ground_col1:
                ground_temp_slider = st.slider("地下水温度 (℃)", 10.0, 20.0, st.session_state.ground_value, 0.1, key="ground_slider")
            with ground_col2:
                st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
                ground_temp_input = st.number_input("", min_value=10.0, max_value=20.0, value=st.session_state.ground_value, step=0.1, 
                                                   key="ground_input", label_visibility="collapsed")
            
            if ground_temp_slider != st.session_state.ground_value:
                st.session_state.ground_value = ground_temp_slider
                st.rerun()
            elif ground_temp_input != st.session_state.ground_value:
                st.session_state.ground_value = ground_temp_input
                st.rerun()
            
            ground_temp = st.session_state.ground_value
            
            # 管浸水距離
            length_col1, length_col2 = st.columns([3, 1])
            
            if "length_value" not in st.session_state:
                st.session_state.length_value = 5.0
            
            with length_col1:
                pipe_length_slider = st.slider("管浸水距離 (m)", 3.0, 15.0, st.session_state.length_value, 0.5, key="length_slider")
            with length_col2:
                st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
                pipe_length_input = st.number_input("", min_value=3.0, max_value=15.0, value=st.session_state.length_value, step=0.5, 
                                                   key="length_input", label_visibility="collapsed")
            
            if pipe_length_slider != st.session_state.length_value:
                st.session_state.length_value = pipe_length_slider
                st.rerun()
            elif pipe_length_input != st.session_state.length_value:
                st.session_state.length_value = pipe_length_input
                st.rerun()
            
            pipe_length = st.session_state.length_value
            
            # 掘削径の選択
            boring_diameter = st.selectbox(
                "掘削径",
                ["φ116", "φ250"],
                index=1,  # デフォルトはφ250
                help="配管用の掘削径で、配管後に地下水などで充満される範囲を示す"
            )
            boring_diameter_mm = 116 if boring_diameter == "φ116" else 250
    
        # 2行目
        row2_col1, row2_col2 = st.columns([1, 1], gap="medium")
        
        with row2_col1:
            st.subheader("配管条件")
            pipe_material = st.selectbox(
                "配管材質",
                ["鋼管", "アルミ管", "銅管"]
            )
            pipe_diameter = st.selectbox(
                "管径",
                ["15A", "20A", "25A", "32A", "40A", "50A", "65A", "80A"],
                index=3  # デフォルトは32A
            )
            
            # 管径別の推奨本数（参考値）
            pipe_counts_default = {
                "15A": 1,   # 50 L/min × 1本
                "20A": 1,   # 50 L/min × 1本
                "25A": 1,   # 50 L/min × 1本
                "32A": 1,   # 12.5 L/min × 1本
                "40A": 1,   # 25 L/min × 1本
                "50A": 1,   # 50 L/min × 1本
                "65A": 1,   # 50 L/min × 1本
                "80A": 1    # 50 L/min × 1本
            }
            
            # 配管セット本数の設定
            num_pipes_user = st.selectbox(
                "配管セット本数",
                options=[1, 2, 3, 4, 5],
                index=pipe_counts_default.get(pipe_diameter, 1) - 1,
                help="U字管構造のため往路復路の2本で1セットとする"
            )
        
        with row2_col2:
            st.subheader("詳細設定")
            consider_groundwater_temp_rise = st.checkbox(
                "地下水温度上昇を考慮する",
                value=False,
                help="熱交換による地下水温度の上昇を自動計算します"
            )
            
            # 地下水循環の設定
            if consider_groundwater_temp_rise:
                consider_circulation = st.checkbox(
                    "地下水の循環を考慮する",
                    value=False,
                    help="地下水が循環せず、指定時間運転した場合の温度上昇を計算"
                )
                
                if consider_circulation:
                    # 運転時間
                    op_col1, op_col2 = st.columns([3, 1])
                    
                    if "operation_value" not in st.session_state:
                        st.session_state.operation_value = 10
                    
                    with op_col1:
                        operation_minutes_slider = st.slider("運転時間 (分)", 1, 60, st.session_state.operation_value, 1, key="operation_slider")
                    with op_col2:
                        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
                        operation_minutes_input = st.number_input("", min_value=1, max_value=60, value=st.session_state.operation_value, step=1, 
                                                                 key="operation_input", label_visibility="collapsed")
                    
                    if operation_minutes_slider != st.session_state.operation_value:
                        st.session_state.operation_value = operation_minutes_slider
                        st.rerun()
                    elif operation_minutes_input != st.session_state.operation_value:
                        st.session_state.operation_value = operation_minutes_input
                        st.rerun()
                    
                    operation_minutes = st.session_state.operation_value
                    operation_hours = operation_minutes / 60  # 時間に変換
                else:
                    # 1回の通水時間を計算（デフォルト）
                    operation_hours = 1  # 暫定値、後で計算される
                    
                # 温度上昇上限値
                limit_col1, limit_col2 = st.columns([3, 1])
                
                if "limit_value" not in st.session_state:
                    st.session_state.limit_value = 5
                
                with limit_col1:
                    temp_rise_limit_slider = st.slider("温度上昇上限値 (℃)", 5, 20, st.session_state.limit_value, 1, 
                                                      help="地下水温度上昇の最大制限値", key="limit_slider")
                with limit_col2:
                    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
                    temp_rise_limit_input = st.number_input("", min_value=5, max_value=20, value=st.session_state.limit_value, step=1, 
                                                           key="limit_input", label_visibility="collapsed")
                
                if temp_rise_limit_slider != st.session_state.limit_value:
                    st.session_state.limit_value = temp_rise_limit_slider
                    st.rerun()
                elif temp_rise_limit_input != st.session_state.limit_value:
                    st.session_state.limit_value = temp_rise_limit_input
                    st.rerun()
                
                temp_rise_limit = st.session_state.limit_value
            else:
                operation_hours = 1  # デフォルト値（後で再計算される）
                temp_rise_limit = 5  # デフォルト値
                consider_circulation = False
    
    st.markdown("---")  # 計算条件と結果を区切る

    # 計算結果のタイトル
    st.subheader("📈 計算結果")

    # メイン画面にタブを設置
    # タブのフォントサイズを調整
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1rem;
        font-weight: 400;
    }
    </style>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔧 単一配管計算", "📊 複数配管比較計算"])
    
    with tab1:
        # 単一配管計算ページ
        
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
        
        # 初期計算用の地下水温度
        effective_ground_temp = ground_temp
        
        # 平均温度の計算（物性値計算用）
        avg_temp = (initial_temp + effective_ground_temp) / 2
        
        # 配管内径と断面積の計算
        inner_diameter = pipe_specs[pipe_diameter] / 1000  # m
        pipe_area = math.pi * (inner_diameter / 2) ** 2  # m²
        
        # 1本あたりの流量を計算
        num_pipes = num_pipes_user  # ユーザー設定値を使用
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
        # 外径データ（JIS規格）
        pipe_outer_diameters = {
            "15A": 21.7 / 1000,  # m
            "20A": 27.2 / 1000,
            "25A": 34.0 / 1000,
            "32A": 42.7 / 1000,
            "40A": 48.6 / 1000,
            "50A": 60.5 / 1000,
            "65A": 76.3 / 1000,
            "80A": 89.1 / 1000
        }
        
        outer_diameter = pipe_outer_diameters[pipe_diameter]
        pipe_thermal_cond = thermal_conductivity[pipe_material]
        
        # 管外側熱伝達係数（静止水中の自然対流）
        h_outer = 300  # W/m²·K
        
        # 総括熱伝達係数 U (W/m²・K)
        # 内径基準での計算
        U = 1 / (1/heat_transfer_coefficient + 
                inner_diameter/(2*pipe_thermal_cond) * math.log(outer_diameter/inner_diameter) + 
                inner_diameter/(outer_diameter*h_outer))
        
        # 配管面積と掘削径の検証
        total_pipe_area = num_pipes * math.pi * (outer_diameter / 2) ** 2 * 1000000  # mm²
        boring_area = math.pi * (boring_diameter_mm / 2) ** 2  # mm²
        
        if total_pipe_area > boring_area * 0.8:  # 80%を超えたら警告
            st.error(f"⚠️ 配管総面積が掘削径の80%を超えています！")
            st.warning(f"配管総面積: {total_pipe_area:.0f}mm²")
            st.warning(f"掘削断面積: {boring_area:.0f}mm²")
            st.warning(f"占有率: {total_pipe_area/boring_area*100:.1f}%")
        
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
        
        # 最終温度の計算（初回）
        final_temp = initial_temp - effectiveness * (initial_temp - effective_ground_temp)
        
        # 地下水温度上昇の計算
        if consider_groundwater_temp_rise:
            # 熱交換量の計算 [W]
            heat_exchange_rate = mass_flow_rate_per_pipe * num_pipes * specific_heat * (initial_temp - final_temp)
            
            # 地下水の体積計算（ボーリング孔内のみ）
            # 掘削孔の体積
            boring_volume = math.pi * (boring_diameter_mm / 2000) ** 2 * pipe_length  # m³
            # 配管の総体積（U字管なので往復分で2倍）
            pipe_total_volume = math.pi * (outer_diameter / 2) ** 2 * pipe_length * num_pipes * 2  # m³
            # 地下水体積
            groundwater_volume = boring_volume - pipe_total_volume  # m³
            groundwater_mass = groundwater_volume * density  # kg
            
            # 1回の通水時間を計算（循環を考慮しない場合）
            if not consider_circulation:
                # U字管の全長を流速で除して通水時間を求める
                total_pipe_length = pipe_length * 2  # U字管往復
                transit_time_seconds = total_pipe_length / velocity  # 秒
                operation_hours = transit_time_seconds / 3600  # 時間に変換
            
            # 地下水の温度上昇を計算
            operation_time = operation_hours * 3600  # 秒
            if groundwater_mass > 0:
                groundwater_temp_rise = (heat_exchange_rate * operation_time) / (groundwater_mass * specific_heat)
            else:
                st.error("⚠️ 地下水体積が負またはゼロです。配管が多すぎるか、掘削径が小さすぎます。")
                groundwater_temp_rise = 0.0
            
            # 温度上昇を制限
            groundwater_temp_rise_unlimited = groundwater_temp_rise
            groundwater_temp_rise = min(groundwater_temp_rise, temp_rise_limit)
            
            # 実効地下水温度を更新
            effective_ground_temp = ground_temp + groundwater_temp_rise
            
            # 平均温度を再計算（物性値の更新が必要な場合）
            avg_temp_new = (initial_temp + effective_ground_temp) / 2
            
            # 温度が大きく変わった場合は物性値を再計算する必要があるが、
            # ここでは簡略化のため、最終温度のみ再計算
            # 最終温度を再計算
            final_temp = initial_temp - effectiveness * (initial_temp - effective_ground_temp)
        else:
            groundwater_temp_rise = 0.0
        
        # 熱交換効率（％）
        if initial_temp != effective_ground_temp:
            efficiency = effectiveness * 100
        else:
            efficiency = 0
        
        # 結果表示
        # 目標温度との比較（計算結果の上に表示）
        if final_temp > target_temp:
            st.warning(f"⚠️ 目標温度（{target_temp}℃）を超えています")
        else:
            st.success("✅ 目標温度範囲内です")
        
        st.markdown("")  # スペースを追加
        
        # 重要な3つの指標を枠線で強調表示
        main_col1, main_col2, main_col3 = st.columns(3)
        
        with main_col1:
            st.markdown(f"""
            <div style="border: 3px solid #ff4b4b; border-radius: 10px; padding: 13px; background-color: #fff5f5; text-align: center;">
                <h3 style="margin: 0; color: #ff4b4b; font-size: 18px;">🌡️ 出口温度</h3>
                <h1 style="margin: 7px 0; color: #333; font-size: 36px;">{final_temp:.1f}℃</h1>
                <p style="margin: 0; color: #666; font-size: 14px;">温度降下: {initial_temp - final_temp:.1f}℃</p>
            </div>
            """, unsafe_allow_html=True)
        
        with main_col2:
            if consider_groundwater_temp_rise:
                st.markdown(f"""
                <div style="border: 3px solid #1976d2; border-radius: 10px; padding: 13px; background-color: #f0f7ff; text-align: center;">
                    <h3 style="margin: 0; color: #1976d2; font-size: 18px;">💧 地下水温</h3>
                    <h1 style="margin: 7px 0; color: #333; font-size: 36px;">{effective_ground_temp:.1f}℃</h1>
                    <p style="margin: 0; color: #666; font-size: 14px;">温度上昇: +{groundwater_temp_rise:.1f}℃</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="border: 3px solid #1976d2; border-radius: 10px; padding: 13px; background-color: #f0f7ff; text-align: center;">
                    <h3 style="margin: 0; color: #1976d2; font-size: 18px;">💧 地下水温</h3>
                    <h1 style="margin: 7px 0; color: #333; font-size: 36px;">{effective_ground_temp:.1f}℃</h1>
                    <p style="margin: 0; color: #666; font-size: 14px;">初期温度のまま</p>
                </div>
                """, unsafe_allow_html=True)
        
        with main_col3:
            # 通水時間の計算
            total_pipe_length = pipe_length * 2  # U字管往復
            transit_time_seconds = total_pipe_length / velocity
            transit_time_minutes = transit_time_seconds / 60
            
            if consider_circulation:
                time_display = f"{operation_minutes}"
                time_unit = "分"
                time_description = "循環運転時間"
            else:
                time_display = f"{transit_time_minutes:.1f}"
                time_unit = "分"
                time_description = "1回通水時間"
            
            st.markdown(f"""
            <div style="border: 3px solid #4caf50; border-radius: 10px; padding: 13px; background-color: #f1f8e9; text-align: center;">
                <h3 style="margin: 0; color: #4caf50; font-size: 18px;">⏱️ 通水時間</h3>
                <h1 style="margin: 7px 0; color: #333; font-size: 36px;">{time_display}{time_unit}</h1>
                <p style="margin: 0; color: #666; font-size: 14px;">{time_description}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("")  # スペース追加
        
        # その他の指標（1行4列）
        sub_col1, sub_col2, sub_col3, sub_col4 = st.columns(4)
        
        with sub_col1:
            st.metric("熱交換効率", f"{efficiency:.1f}%", help="水から地下水への熱の移動割合。100%に近いほど効率的")
        
        with sub_col2:
            if consider_groundwater_temp_rise:
                st.metric("熱交換量", f"{heat_exchange_rate/1000:.1f} kW", help="地下に捨てられる熱量。エアコン1台は約2-3kW")
            else:
                heat_exchange_rate = mass_flow_rate_per_pipe * num_pipes * specific_heat * (initial_temp - final_temp)
                st.metric("熱交換量", f"{heat_exchange_rate/1000:.1f} kW", help="地下に捨てられる熱量。エアコン1台は約2-3kW")
        
        with sub_col3:
            if consider_groundwater_temp_rise:
                st.metric("地下水体積", f"{groundwater_volume:.3f} m³", help="ボーリング孔内の地下水量。配管を除いた有効体積")
            else:
                st.metric("地下水体積", "-", help="温度上昇計算時のみ表示")
        
        with sub_col4:
            st.metric("配管本数", f"{num_pipes} セット")
        
        # 結果表示終了
        
        # 最適化提案（コメントアウト - 将来的に復活しやすいように）
        # st.markdown("---")
        # st.subheader("⚙️ 最適化提案")
        # 
        # if final_temp > target_temp:
        #     st.warning(f"⚠️ 目標温度（{target_temp}℃）を超えています")
        #     st.markdown("**改善提案：**")
        #     if pipe_length < 20:
        #         st.markdown(f"- 管浸水距離を約{20}mに延長（現在: {pipe_length}m）")
        #     else:
        #         st.markdown("- より大口径の配管を検討")
        #     st.markdown("- 地下水循環システムの導入")
        #     if pipe_diameter != "32A":
        #         st.markdown("- 32A配管の使用（最適効率）")
        #     else:
        #         st.markdown("- 複数の32A配管を並列配置")
        # else:
        #     st.success("✅ 目標温度範囲内です")
        
        # 計算条件の表示（コメントアウト - 将来的に復活しやすいように）
        # st.markdown("---")
        # st.subheader("📝 計算条件")
        # condition_col1, condition_col2, condition_col3 = st.columns(3)
        # 
        # with condition_col1:
        #     st.markdown("**基本条件**")
        #     st.markdown(f"- 初期温度: {initial_temp}℃")
        #     st.markdown(f"- 地下水温度: {ground_temp}℃")
        #     st.markdown(f"- 目標温度: {target_temp}℃")
        #     if consider_groundwater_temp_rise:
        #         st.markdown(f"- 地下水温度上昇: +{groundwater_temp_rise:.2f}℃（自動計算）")
        #         st.markdown(f"- 最終地下水温度: {effective_ground_temp:.1f}℃")
        #         if consider_circulation:
        #             st.markdown(f"- 運転時間: {operation_minutes}分")
        #         else:
        #             st.markdown(f"- 通水時間: {operation_hours*3600:.1f}秒（{operation_hours*60:.1f}分）")
        #         st.markdown(f"- 温度上昇上限: {temp_rise_limit}℃")
        #     st.markdown(f"- 掘削径: {boring_diameter}")
        # 
        # with condition_col2:
        #     st.markdown("**流量条件**")
        #     st.markdown(f"- 総流量: {flow_rate} L/min")
        #     st.markdown(f"- 管浸水距離: {pipe_length} m")
        #     st.markdown(f"- 管径: {pipe_diameter}")
        # 
        # with condition_col3:
        #     st.markdown("**配管仕様**")
        #     st.markdown(f"- 配管材質: {pipe_material}")
        #     st.markdown(f"- 内径: {inner_diameter*1000:.1f} mm")
        #     st.markdown(f"- 外径: {outer_diameter*1000:.1f} mm")
        #     st.markdown(f"- 熱伝導率: {pipe_thermal_cond} W/m·K")
        #     st.markdown(f"- 配管セット本数: {num_pipes} セット")
        
        # 地下水温度上昇の詳細（チェックされている場合）
        if consider_groundwater_temp_rise:
            st.markdown("---")
            st.subheader("🌊 地下水温度上昇の詳細")
            gw_col1, gw_col2, gw_col3, gw_col4 = st.columns(4)
            with gw_col1:
                st.metric("掘削孔体積", f"{boring_volume:.3f} m³")
            with gw_col2:
                st.metric("配管総体積", f"{pipe_total_volume:.3f} m³")
            with gw_col3:
                st.metric("地下水質量", f"{groundwater_mass:.0f} kg")
            with gw_col4:
                if consider_circulation:
                    time_label = f"{operation_minutes}分運転"
                else:
                    time_label = f"1回通水（{operation_hours*60:.1f}分）"
                    
                if groundwater_temp_rise_unlimited > temp_rise_limit:
                    st.metric(f"{time_label}での温度上昇", f"{groundwater_temp_rise:.2f}℃", f"制限前: {groundwater_temp_rise_unlimited:.2f}℃")
                else:
                    st.metric(f"{time_label}での温度上昇", f"{groundwater_temp_rise:.2f}℃")
        
        # 追加の計算結果表示
        st.markdown("---")
        st.subheader("詳細パラメータ")
        detail_col1, detail_col2, detail_col3, detail_col4 = st.columns(4)
        
        with detail_col1:
            st.metric("流速", f"{velocity:.3f} m/s", help="配管内の水の流れる速度。0.5-2.0m/sが適正範囲")
        
        with detail_col2:
            st.metric("レイノルズ数", f"{reynolds:.0f}", help="流れの状態を示す数値。2300以下は層流（おとなしい流れ）、以上は乱流（かき混ぜ効果あり）")
        
        with detail_col3:
            st.metric("熱伝達係数", f"{heat_transfer_coefficient:.0f} W/m²·K", help="配管内面での熱の移動しやすさ。数値が大きいほど熱交換が活発")
        
        with detail_col4:
            st.metric("NTU", f"{NTU:.3f}", help="熱交換の能力を示す無次元数。0.3以上で効率的な熱交換が期待できる")
        
        # 物性値の表示
        st.markdown("---")
        st.subheader(f"物性値（平均温度 {avg_temp:.1f}℃）")
        prop_col1, prop_col2, prop_col3, prop_col4 = st.columns(4)
        
        with prop_col1:
            st.metric("動粘度", f"{kinematic_viscosity*1e6:.3f}×10⁻⁶ m²/s", help="水の粘っこさ。温度が高いほど小さくなり流れやすくなる")
        
        with prop_col2:
            st.metric("熱伝導率", f"{water_thermal_conductivity:.3f} W/m·K", help="水の熱の伝わりやすさ。温度によって微妙に変化する")
        
        with prop_col3:
            st.metric("プラントル数", f"{prandtl:.2f}", help="水の熱的性質を表す数値。水は約6-7で、熱移動計算に使用")
        
        with prop_col4:
            st.metric("総括熱伝達係数", f"{U:.1f} W/m²·K")

    
    with tab2:
        # 複数配管比較ページ
        
        # 各管径のセット本数を設定
        st.subheader("配管セット本数の設定")
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
        
        with col1:
            n_15A = st.number_input("15A", min_value=1, max_value=10, value=1, key="n_15A")
        with col2:
            n_20A = st.number_input("20A", min_value=1, max_value=10, value=1, key="n_20A")
        with col3:
            n_25A = st.number_input("25A", min_value=1, max_value=10, value=1, key="n_25A")
        with col4:
            n_32A = st.number_input("32A", min_value=1, max_value=10, value=1, key="n_32A")
        with col5:
            n_40A = st.number_input("40A", min_value=1, max_value=10, value=1, key="n_40A")
        with col6:
            n_50A = st.number_input("50A", min_value=1, max_value=10, value=1, key="n_50A")
        with col7:
            n_65A = st.number_input("65A", min_value=1, max_value=10, value=1, key="n_65A")
        with col8:
            n_80A = st.number_input("80A", min_value=1, max_value=10, value=1, key="n_80A")
        
        # ユーザー入力の本数でpipe_countsを更新
        pipe_counts_user = {
            "15A": n_15A,
            "20A": n_20A,
            "25A": n_25A,
            "32A": n_32A,
            "40A": n_40A,
            "50A": n_50A,
            "65A": n_65A,
            "80A": n_80A
        }
        
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
        
        # 初期計算用の地下水温度
        effective_ground_temp = ground_temp
        groundwater_temp_rise = 0.0  # 初期値
        
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
        warnings_list = []  # 警告メッセージ用リスト
        
        for pipe_size in ["15A", "20A", "25A", "32A", "40A", "50A", "65A", "80A"]:
            # 各管径での計算
            inner_d = pipe_specs[pipe_size] / 1000
            area = math.pi * (inner_d / 2) ** 2
            n_pipes = pipe_counts_user[pipe_size]
            flow_per_p = flow_rate / n_pipes
            flow_rate_m3s_per_p = flow_per_p / 60000
            vel = flow_rate_m3s_per_p / area
            re = vel * inner_d / kinematic_viscosity
            
            if re < 2300:
                nu = 3.66
            else:
                nu = 0.023 * (re ** 0.8) * (prandtl ** 0.3)
            
            h = nu * water_thermal_conductivity / inner_d
            
            # 外径データ（JIS規格）
            pipe_outer_diameters_comp = {
                "15A": 21.7 / 1000,  # m
                "20A": 27.2 / 1000,
                "25A": 34.0 / 1000,
                "32A": 42.7 / 1000,
                "40A": 48.6 / 1000,
                "50A": 60.5 / 1000,
                "65A": 76.3 / 1000,
                "80A": 89.1 / 1000
            }
            
            outer_d = pipe_outer_diameters_comp[pipe_size]
            
            # 配管面積と掘削径の検証
            total_pipe_area_temp = n_pipes * math.pi * (outer_d / 2) ** 2 * 1000000  # mm²
            if total_pipe_area_temp > boring_area * 0.8:
                warnings_list.append(f"{pipe_size}: 配管総面積が掘削径の80%を超過 ({total_pipe_area_temp/boring_area*100:.1f}%)")
            
            # 総括熱伝達係数（内径基準）
            U_temp = 1 / (1/h + 
                         inner_d/(2*pipe_thermal_cond) * math.log(outer_d/inner_d) + 
                         inner_d/(outer_d*h_outer))
            
            A_temp = math.pi * inner_d * total_length
            mass_flow_per_p = flow_rate_m3s_per_p * density
            NTU_temp = U_temp * A_temp / (mass_flow_per_p * specific_heat)
            eff_temp = 1 - math.exp(-NTU_temp)
            final_t = initial_temp - eff_temp * (initial_temp - effective_ground_temp)
            
            # 地下水温度上昇の計算（各配管サイズごと）
            if consider_groundwater_temp_rise:
                # 熱交換量の計算 [W]
                heat_rate_temp = mass_flow_per_p * n_pipes * specific_heat * (initial_temp - final_t)
                
                # 地下水の体積計算（ボーリング孔内のみ）
                boring_volume_temp = math.pi * (boring_diameter_mm / 2000) ** 2 * pipe_length  # m³
                # 配管の総体積（U字管なので往復分で2倍）
                pipe_total_volume_temp = math.pi * (outer_d / 2) ** 2 * pipe_length * n_pipes * 2  # m³
                # 地下水体積
                groundwater_volume_temp = boring_volume_temp - pipe_total_volume_temp  # m³
                groundwater_mass_temp = groundwater_volume_temp * density  # kg
                
                # 運転時間での温度上昇
                # 循環を考慮しない場合は1回の通水時間を計算
                if not consider_circulation:
                    total_pipe_length_temp = pipe_length * 2  # U字管往復
                    transit_time_seconds_temp = total_pipe_length_temp / vel  # 秒
                    operation_hours_temp = transit_time_seconds_temp / 3600  # 時間に変換
                else:
                    operation_hours_temp = operation_hours
                    
                operation_time = operation_hours_temp * 3600  # 秒
                if groundwater_mass_temp > 0:
                    gw_temp_rise = (heat_rate_temp * operation_time) / (groundwater_mass_temp * specific_heat)
                    gw_temp_rise = min(gw_temp_rise, temp_rise_limit)
                else:
                    gw_temp_rise = 0.0
                
                # 実効地下水温度で再計算
                effective_ground_temp_local = ground_temp + gw_temp_rise
                final_t = initial_temp - eff_temp * (initial_temp - effective_ground_temp_local)
            else:
                gw_temp_rise = 0.0
            
            pipe_comparison.append({
                "管径": pipe_size,
                "本数": n_pipes,
                "出口温度(℃)": round(final_t, 1),
                "効率(%)": round(eff_temp * 100, 1),
                "流速(m/s)": round(vel, 3),
                "レイノルズ数": int(re),
                "h_i(W/m²K)": int(h),
                "U(W/m²K)": round(U_temp, 1),
                "NTU": round(NTU_temp, 3)
            })

        df = pd.DataFrame(pipe_comparison)
        
        # 管径別比較結果
        st.subheader("📋 管径別比較結果")
        st.dataframe(df, use_container_width=True)
        
        # 警告表示
        if warnings_list:
            st.error("⚠️ 配管面積に関する警告")
            for warning in warnings_list:
                st.warning(warning)

        # グラフ表示
        st.header("📊 視覚化")

        # 管径別効率比較
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("管径別効率", "管径別出口温度"),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )

        # 効率グラフ
        fig.add_trace(
            go.Bar(x=df["管径"], y=df["効率(%)"], name="効率", marker_color="blue"),
            row=1, col=1
        )

        # 温度グラフ
        fig.add_trace(
            go.Scatter(x=df["管径"], y=df["出口温度(℃)"], mode="lines+markers", 
                       name="出口温度", line=dict(color="red")),
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
            st.metric("出口温度", f"{best_pipe['出口温度(℃)']}℃")
        
        with col2:
            st.metric("効率", f"{best_pipe['効率(%)']}%")
            st.metric("本数", f"{best_pipe['本数']}本")
        
        with col3:
            st.metric("流速", f"{best_pipe['流速(m/s)']} m/s")
            st.metric("NTU", f"{best_pipe['NTU']}")

        # フッター
        st.markdown("---")
        st.markdown("**開発者**: dobocreate | **バージョン**: 1.2.0 | **更新**: 2025-01-06")

elif page == "理論解説":
    st.title("📚 地中熱交換簡易シミュレーターの理論解説")
    st.markdown("地中熱交換システムの原理と、このツールで使用している計算理論について解説します")
    
    # システム概念の説明
    st.header("🌍 地中熱交換システムとは")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ### 基本原理
        地中熱交換システムは、**地下の安定した温度環境**を利用した省エネルギー技術です：
        
        **🌡️ 地下温度の特徴**
        - 地下10m以深では年間を通じてほぼ一定温度（15-18℃）
        - 夏の暑い時期でも地下は涼しい
        - 冬の寒い時期でも地下は温かい
        
        **❄️ 冷房運転での活用（本ツールの対象）**
        - エアコンの排熱（30-35℃）を地下水（15-18℃）で冷却
        - 冷却塔が不要となり、省スペース・省エネ
        - 騒音の軽減効果
        """)
    
    with col2:
        st.info("""
        **💡 実用例**
        
        **オフィスビル**
        - 屋上冷却塔の代替
        - 景観への配慮
        
        **工場**
        - プロセス冷却水の処理
        - 水使用量の削減
        
        **データセンター**
        - 高発熱機器の冷却
        - 安定した冷却性能
        """)
    
    st.markdown("---")
    
    # U字管構造の説明
    st.header("🔧 U字管構造の利点")
    
    u_col1, u_col2 = st.columns([1, 1])
    with u_col1:
        st.markdown("""
        ### なぜU字管なのか？
        
        **施工面での利点**
        - 1回のボーリングで往復配管を設置
        - 掘削コストの削減
        - 狭い敷地でも設置可能
        
        **維持管理面での利点**
        - 地上に出入口が集約
        - メンテナンスが容易
        - 漏水リスクの低減
        """)
    
    with u_col2:
        st.markdown("""
        ### 熱交換効率の向上
        
        **往路での予備冷却**
        - 入口→底部：徐々に温度降下
        
        **復路での本格冷却**
        - 底部→出口：さらなる温度降下
        
        **結果**
        - 1本の直管より高い冷却効果
        - 滞留時間の確保
        """)
    
    st.markdown("---")
    
    # 設計時の考慮事項
    st.header("📐 設計時の重要ポイント")
    
    design_col1, design_col2, design_col3 = st.columns(3)
    
    with design_col1:
        st.markdown("""
        **🔍 管径選定**
        
        **32A（内径33.5mm）推奨の理由**
        - 適切な流速（1-2m/s）
        - 効率的な熱交換
        - 施工の容易さ
        - コストバランス
        """)
    
    with design_col2:
        st.markdown("""
        **📏 深度・流量設計**
        
        **深度の決定要因**
        - 地下水位
        - 土質条件
        - 必要な熱交換量
        
        **流量の最適化**
        - 熱交換効率とのバランス
        - ポンプ動力の考慮
        """)
    
    with design_col3:
        st.markdown("""
        **🌊 地下水への影響**
        
        **温度上昇の制限**
        - 環境保護の観点
        - 長期安定運転
        
        **影響範囲の予測**
        - 地下水流動の考慮
        - 熱拡散の評価
        """)
    
    st.markdown("---")
    
    # 計算理論の説明（簡略化）
    st.header("🧮 計算理論の基礎")
    st.markdown("""
    このツールでは、以下の理論に基づいて熱交換計算を行っています。
    土木エンジニアの皆様には数式の詳細よりも、**何を表しているか**を理解していただければ十分です。
    """)
    
    # 主要パラメータの説明
    theory_col1, theory_col2 = st.columns(2)
    
    with theory_col1:
        st.subheader("📊 流れの状態（レイノルズ数）")
        st.markdown("""
        **何を表すか**: 配管内の水の流れ方
        
        - **2300未満**: おとなしい流れ（層流）
        - **2300以上**: かき混ぜ効果のある流れ（乱流）
        
        **設計への影響**
        - 乱流の方が熱交換効率が良い
        - 流速を上げると乱流になりやすい
        - ただし、ポンプ動力も増加
        """)
        
        st.subheader("🌡️ 熱の移りやすさ（熱伝達係数）")
        st.markdown("""
        **何を表すか**: 配管壁面での熱の移動効率
        
        **影響要因**
        - 流れの状態（乱流ほど良い）
        - 配管材質（銅>アルミ>鋼）
        - 管径（細いほど効率的だが流量制限）
        
        **設計指針**
        - 値が大きいほど効率的
        - 1000-5000 W/m²·K が一般的
        """)
    
    with theory_col2:
        st.subheader("⚡ 熱交換能力（NTU）")
        st.markdown("""
        **何を表すか**: システム全体の熱交換能力
        
        **NTU値の目安**
        - **0.1以下**: 効率悪い
        - **0.3-0.5**: 実用的
        - **1.0以上**: 高効率（コスト増）
        
        **向上方法**
        - 配管を長くする
        - 管径を細くする（流量制限あり）
        - 複数本並列設置
        """)
        
        st.subheader("💧 最終的な冷却効果")
        st.markdown("""
        **計算の流れ**
        1. 流れの状態を判定
        2. 熱の移りやすさを計算
        3. システム能力（NTU）を算出
        4. 実際の温度降下を予測
        
        **結果の見方**
        - 温度降下が大きいほど効果的
        - ただし、地下水温度上昇も考慮
        """)
    
    st.markdown("---")
    
    # 実務的な設計指針
    st.header("📋 実務的な設計指針")
    
    guidance_col1, guidance_col2 = st.columns(2)
    
    with guidance_col1:
        st.markdown("""
        ### 🎯 設計目標値
        
        **温度条件**
        - 入口温度: 30-35℃（エアコン排熱）
        - 目標出口温度: 20-25℃
        - 地下水温度: 15-18℃（地域により変動）
        
        **流体条件**
        - 流速: 0.5-2.0 m/s（適正範囲）
        - 流量: 10-100 L/min（設備規模による）
        
        **効率指標**
        - 熱交換効率: 30-70%
        - NTU: 0.3-1.0
        """)
    
    with guidance_col2:
        st.markdown("""
        ### ⚠️ 制約条件
        
        **環境制約**
        - 地下水温度上昇: 5℃以下
        - 地下水利用許可の範囲内
        
        **施工制約**
        - 掘削径: 100-200mm（一般的）
        - 掘削深度: 地下水位+10m以上
        - 配管占有率: 掘削面積の80%以下
        
        **経済性**
        - 初期コスト vs 運転コスト
        - 冷却塔との比較検討
        """)
    
    st.markdown("---")
    
    st.header("🔧 よくある設計質問と回答")
    
    with st.expander("Q1: なぜ32Aが推奨されるのですか？"):
        st.markdown("""
        **A1**: 以下のバランスが最も良いためです
        - 適度な流速（1-2m/s）で効率的な熱交換
        - 実用的な流量（10-50L/min）に対応
        - 施工コストと性能のバランス
        - 一般的な配管規格で入手しやすい
        """)
    
    with st.expander("Q2: 管長はどのように決めればよいですか？"):
        st.markdown("""
        **A2**: 以下の要因を総合的に判断します
        - **必要な冷却量**: 大きいほど長い管長が必要
        - **地質条件**: 掘削可能深度の制限
        - **地下水位**: 地下水位以下での設置が必要
        - **経済性**: 深いほど掘削コストが増加
        
        **目安**: 10-20mが一般的、効果不足なら複数本並列
        """)
    
    with st.expander("Q3: 地下水温度上昇が制限を超えた場合は？"):
        st.markdown("""
        **A3**: 以下の対策を検討してください
        1. **配管本数を増やす**: 1本あたりの負荷を分散
        2. **流量を増やす**: 滞留時間を短縮
        3. **運転時間を短縮**: 連続運転を避ける
        4. **複数孔に分散**: 熱的影響を分散
        5. **地下水流動の活用**: 自然循環による熱拡散
        """)
    
    with st.expander("Q4: このツールの計算精度はどの程度ですか？"):
        st.markdown("""
        **A4**: 簡易計算ツールとしての精度
        - **誤差範囲**: ±20-30%程度
        - **適用範囲**: 一般的な地中熱交換システム
        - **前提条件**: 定常状態、均一地質、静止地下水
        
        **詳細設計時の注意**
        - 地質調査結果の反映
        - 地下水流動の考慮
        - 長期性能の評価
        - 安全率の設定（1.5-2.0倍程度）
        """)
    
    st.markdown("---")
    
    # 技術的詳細（従来の数式部分を簡略化して残す）
    with st.expander("🔬 技術的詳細（熱工学の専門知識がある方向け）"):
        st.markdown("### 主要な計算式")
        
        st.markdown("**レイノルズ数**")
        st.latex(r"Re = \frac{vD}{\nu}")
        
        st.markdown("**ヌッセルト数（乱流時）**")
        st.latex(r"Nu = 0.023 \cdot Re^{0.8} \cdot Pr^{0.3}")
        
        st.markdown("**NTU法による効率計算**")
        st.latex(r"NTU = \frac{UA}{\dot{m}c_p}")
        st.latex(r"\varepsilon = 1 - e^{-NTU}")
        
        st.markdown("**最終温度**")
        st.latex(r"T_{final} = T_{initial} - \varepsilon(T_{initial} - T_{ground})")
    
    st.header("10. 計算の前提条件")
    st.markdown("""
    ### 基本的な前提条件
    1. **U字管構造**：往路と復路の総延長で計算（管浸水距離 × 2）
    2. **定常状態**：各時点での熱交換は定常状態として計算
    3. **一次元熱伝達**：径方向のみの熱伝達を考慮
    4. **管内流れ**：十分発達した流れと仮定
    5. **ボーリング孔**：円柱形状、配管との間隙は地下水で満たされる
    
    ### 地下水温度の扱い
    
    #### A. 地下水温度上昇を考慮しない場合（デフォルト）
    - 地下水温度は一定（大量の地下水により温度変化は無視）
    - 地下水は常に初期温度を維持
    - 短時間運転や地下水流動が活発な場合に適用
    
    #### B. 地下水温度上昇を考慮する場合
    
    **B-1. 循環を考慮しない（デフォルト）**
    - 1回の通水時間を自動計算：通水時間 = U字管全長 ÷ 流速
    - この時間での熱交換による地下水温度上昇を計算
    - 実際の配管通過時間に基づく評価
    
    **B-2. 循環を考慮する**
    - ユーザーが指定した運転時間（1〜60分）での累積的な温度上昇
    - 地下水がボーリング孔内に滞留する場合を想定
    - 長時間運転や地下水流動が少ない場合に適用
    
    ### 計算の流れ
    1. 初期地下水温度で熱交換計算
    2. 地下水温度上昇を計算（考慮する場合）
    3. 上昇後の地下水温度で最終温度を再計算
    4. 温度上昇は設定した上限値（5〜20℃）で制限
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

elif page == "物性値":
    st.title("📊 物性値")
    st.markdown("地中熱交換システムの計算に使用する物性値です")
    
    st.header("1. 水の物性値（温度依存）")
    st.markdown("""
    | 温度[℃] | ρ[kg/m³] | ν[×10⁻⁶m²/s] | k[W/(m·K)] | Cp[J/kg·K] | Pr[-] |
    |---------|----------|---------------|------------|-----------|-------|
    | 15 | 999.1 | 1.139 | 0.589 | 4186 | 8.09 |
    | 20 | 998.2 | 1.004 | 0.598 | 4182 | 7.01 |
    | **22.5** | **997.6** | **0.949** | **0.603** | **4181** | **6.57** |
    | 25 | 997.0 | 0.893 | 0.607 | 4179 | 6.13 |
    | 30 | 995.6 | 0.801 | 0.615 | 4178 | 5.42 |
    | 35 | 994.0 | 0.725 | 0.623 | 4178 | 4.86 |
    | 40 | 992.2 | 0.658 | 0.630 | 4179 | 4.36 |
    
    - ρ: 密度
    - ν: 動粘度  
    - k: 熱伝導率
    - Cp: 比熱
    - Pr: プラントル数
    - **太字**: 平均温度22.5℃での参考値
    """)
    
    st.header("2. 配管仕様")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("材質の熱伝導率")
        st.markdown("""
        | 材質 | 熱伝導率 [W/m·K] |
        |------|------------------|
        | 鋼管 | 50.0 |
        | アルミ管 | 237.0 |
        | 銅管 | 398.0 |
        | ステンレス管 | 16.0 |
        | 塩ビ管 | 0.17 |
        """)
    
    with col2:
        st.subheader("JIS規格配管寸法")
        st.markdown("""
        | 呼び径 | 内径 [mm] | 外径 [mm] | 肉厚 [mm] |
        |--------|-----------|-----------|-----------|
        | 15A | 16.1 | 21.7 | 2.8 |
        | 20A | 22.2 | 27.2 | 2.5 |
        | 25A | 28.0 | 34.0 | 3.0 |
        | 32A | 33.5 | 42.7 | 4.6 |
        | 40A | 41.2 | 48.6 | 3.7 |
        | 50A | 52.6 | 60.5 | 3.95 |
        | 65A | 67.8 | 76.3 | 4.25 |
        | 80A | 80.1 | 89.1 | 4.5 |
        """)
    
    st.info("""
    💡 **注意事項**
    - 配管寸法はJIS G 3452（配管用炭素鋼鋼管）に基づく
    - 実際の寸法は規格や製造メーカーにより若干異なる場合があります
    - 本ツールでは標準的な値を採用しています
    """)
    
    st.header("3. 管外側熱伝達係数")
    st.markdown("""
    **自然対流熱伝達係数の目安**
    
    | 条件 | h_o [W/(m²·K)] | 備考 |
    |------|----------------|------|
    | 静止水中（自然対流） | 200-600 | 本ツールは300を採用 |
    | 弱い対流 | 500-1000 | 地下水流速 < 0.1 m/s |
    | 強制対流 | 1000-5000 | 地下水流速 > 0.1 m/s |
    | 空気中（自然対流） | 5-25 | 参考値 |
    
    **影響要因**
    - 地下水流速
    - 配管表面温度と地下水温度の差
    - 配管の配置（水平/垂直）
    - 配管表面の状態
    """)
    
    st.header("4. その他の物性値")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("土壌の熱物性（未使用）")
        st.markdown("""
        | 土壌種類 | 熱伝導率 [W/m·K] | 熱拡散率 [m²/s] |
        |----------|------------------|-----------------|
        | 砂（乾燥） | 0.3-0.8 | 2-5×10⁻⁷ |
        | 砂（飽和） | 2.0-4.0 | 5-10×10⁻⁷ |
        | 粘土（乾燥） | 0.4-1.0 | 2-5×10⁻⁷ |
        | 粘土（飽和） | 1.2-2.5 | 5-8×10⁻⁷ |
        | 岩盤 | 2.0-7.0 | 10-30×10⁻⁷ |
        """)
    
    with col4:
        st.subheader("地下水の物性")
        st.markdown("""
        **標準的な値（15℃）**
        - 密度：999.1 kg/m³
        - 動粘度：1.139×10⁻⁶ m²/s
        - 熱伝導率：0.589 W/(m·K)
        - 比熱：4186 J/(kg·K)
        
        **地下水流速の目安（未使用）**
        - 透水係数 k = 10⁻⁴ m/s：良好な帯水層
        - 透水係数 k = 10⁻⁶ m/s：一般的な砂層
        - 透水係数 k = 10⁻⁸ m/s：シルト・粘土層
        """)
    
    # フッター
    st.markdown("---")
    st.markdown("**開発者**: dobocreate | **バージョン**: 1.2.0 | **更新**: 2025-01-06")
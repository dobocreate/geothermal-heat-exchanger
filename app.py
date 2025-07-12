"""
地中熱交換簡易シミュレーター
Streamlitアプリケーション
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math

# ページ設定
st.set_page_config(
    page_title="地中熱交換簡易シミュレーター",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# サイドバー - ページ選択

# ページの初期化
if "page" not in st.session_state:
    st.session_state.page = "単一配管計算"

# ボタンスタイルのカスタムCSS
st.markdown("""
<style>
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ページ遷移時の処理
if "previous_page" not in st.session_state:
    st.session_state.previous_page = st.session_state.page
    st.session_state.page_changed = False

if st.session_state.previous_page != st.session_state.page:
    st.session_state.previous_page = st.session_state.page
    st.session_state.page_changed = True
else:
    st.session_state.page_changed = False

# ボタンをコンテナに配置
button_col1 = st.sidebar.container()
button_col2 = st.sidebar.container()
button_col3 = st.sidebar.container()
button_col4 = st.sidebar.container()

# 各ボタンを配置（クリック時に即座にページを変更）
with button_col1:
    if st.button("🔧 単一配管計算", use_container_width=True, 
                 type="primary" if st.session_state.page == "単一配管計算" else "secondary",
                 key="btn_single"):
        st.session_state.page = "単一配管計算"
        st.rerun()

with button_col2:
    if st.button("📊 複数配管比較", use_container_width=True,
                 type="primary" if st.session_state.page == "複数配管比較" else "secondary",
                 key="btn_multiple"):
        st.session_state.page = "複数配管比較"
        st.rerun()

with button_col3:
    if st.button("📚 理論解説", use_container_width=True,
                 type="primary" if st.session_state.page == "理論解説" else "secondary",
                 key="btn_theory"):
        st.session_state.page = "理論解説"
        st.rerun()

with button_col4:
    if st.button("📊 物性値", use_container_width=True,
                 type="primary" if st.session_state.page == "物性値" else "secondary",
                 key="btn_props"):
        st.session_state.page = "物性値"
        st.rerun()

page = st.session_state.page

if page == "単一配管計算":
    # ページ遷移時のスクロールリセット用
    if st.session_state.page_changed:
        st.empty()
    
    # タイトル
    st.markdown("<h1 style='text-align: center;'>🌡️ 地中熱交換簡易シミュレーター</h1>", unsafe_allow_html=True)
    st.markdown("""
    地上の温水を、地盤の安定した温度環境を利用して冷却する、環境配慮型システムの設計を支援する簡易シミュレーターです。
    """)
    
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
                ground_temp_slider = st.slider("地下水温度 (℃)", 0.0, 20.0, st.session_state.ground_value, 0.1, key="ground_slider")
            with ground_col2:
                st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
                ground_temp_input = st.number_input("", min_value=0.0, max_value=20.0, value=st.session_state.ground_value, step=0.1, 
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
                pipe_length_slider = st.slider("管浸水距離 (m)", 1.0, 30.0, st.session_state.length_value, 0.5, key="length_slider")
            with length_col2:
                st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
                pipe_length_input = st.number_input("", min_value=1.0, max_value=30.0, value=st.session_state.length_value, step=0.5, 
                                                   key="length_input", label_visibility="collapsed")
            
            if pipe_length_slider != st.session_state.length_value:
                st.session_state.length_value = pipe_length_slider
                st.rerun()
            elif pipe_length_input != st.session_state.length_value:
                st.session_state.length_value = pipe_length_input
                st.rerun()
            
            pipe_length = st.session_state.length_value
            
            # 掘削径の選択
            if "boring_diameter" not in st.session_state:
                st.session_state.boring_diameter = "φ250"
            
            boring_diameter = st.selectbox(
                "掘削径",
                ["φ116", "φ250"],
                help="配管用の掘削径で、配管後に地下水などで充満される範囲を示す",
                key="boring_diameter"
            )
            boring_diameter_mm = 116 if boring_diameter == "φ116" else 250
    
        # 2行目
        row2_col1, row2_col2 = st.columns([1, 1], gap="medium")
        
        with row2_col1:
            st.subheader("配管条件")
            
            # 配管材質の選択
            if "pipe_material" not in st.session_state:
                st.session_state.pipe_material = "鋼管"
            
            pipe_material = st.selectbox(
                "配管材質",
                ["鋼管", "アルミ管", "銅管"],
                key="pipe_material"
            )
            
            # 管径の選択
            if "pipe_diameter" not in st.session_state:
                st.session_state.pipe_diameter = "32A"
            
            pipe_diameter = st.selectbox(
                "管径",
                ["15A", "20A", "25A", "32A", "40A", "50A", "65A", "80A"],
                key="pipe_diameter"
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
            # 管径が変更された場合のデフォルト値設定
            if "num_pipes_user" not in st.session_state:
                st.session_state.num_pipes_user = pipe_counts_default.get(pipe_diameter, 1)
            
            # 管径が変更された場合の処理
            if "previous_pipe_diameter" not in st.session_state:
                st.session_state.previous_pipe_diameter = pipe_diameter
            
            if st.session_state.previous_pipe_diameter != pipe_diameter:
                # 管径が変更された場合、デフォルト値にリセット
                st.session_state.num_pipes_user = pipe_counts_default.get(pipe_diameter, 1)
                st.session_state.previous_pipe_diameter = pipe_diameter
            
            num_pipes_user = st.selectbox(
                "配管セット本数",
                options=[1, 2, 3, 4, 5],
                help="U字管構造のため往路復路の2本で1セットとする",
                key="num_pipes_user"
            )
        
        with row2_col2:
            st.subheader("詳細設定")
            # チェックボックスのセッション状態管理
            if "consider_groundwater_temp_rise" not in st.session_state:
                st.session_state.consider_groundwater_temp_rise = False
            
            consider_groundwater_temp_rise = st.checkbox(
                "地下水温度上昇を考慮する",
                value=st.session_state.consider_groundwater_temp_rise,
                help="熱交換による地下水温度の上昇を自動計算します",
                key="consider_groundwater_temp_rise"
            )
            
            # 地下水循環の設定
            if consider_groundwater_temp_rise:
                # 地下水循環のチェックボックス
                if "consider_circulation" not in st.session_state:
                    st.session_state.consider_circulation = False
                
                consider_circulation = st.checkbox(
                    "地下水の循環を考慮する",
                    value=st.session_state.consider_circulation,
                    help="地下水が循環せず、指定時間運転した場合の温度上昇を計算",
                    key="consider_circulation"
                )
                
                if consider_circulation:
                    # 循環方式の選択
                    if "circulation_type" not in st.session_state:
                        st.session_state.circulation_type = "同じ水を循環"
                    
                    circulation_type = st.radio(
                        "運転方式",
                        ["同じ水を循環", "新しい水を連続供給"],
                        help="同じ水を循環：冷却された水を再び配管に戻して使用\n新しい水を連続供給：常に新しい温水を供給し続ける",
                        key="circulation_type",
                        horizontal=True
                    )
                    
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
                circulation_type = None
    
    st.markdown("---")  # 計算条件と結果を区切る

    # 計算結果のタイトル
    st.header("📈 計算結果")
    
    # 入力セクションで定義された変数を取得
    # セッション状態から値を取得
    target_temp = st.session_state.get("target_value", 25.0)
    initial_temp = st.session_state.get("initial_value", 30.0)
    flow_rate = st.session_state.get("flow_value", 50.0)
    ground_temp = st.session_state.get("ground_value", 15.0)
    pipe_length = st.session_state.get("length_value", 5.0)
    boring_diameter = st.session_state.get("boring_diameter", "φ250")
    boring_diameter_mm = 116 if boring_diameter == "φ116" else 250
    pipe_material = st.session_state.get("pipe_material", "鋼管")
    pipe_diameter = st.session_state.get("pipe_diameter", "32A")
    num_pipes_user = st.session_state.get("num_pipes_user", 1)
    consider_groundwater_temp_rise = st.session_state.get("consider_groundwater_temp_rise", False)
    
    # 地下水温度上昇関連の変数
    operation_minutes = None  # デフォルト値を設定
    if consider_groundwater_temp_rise:
        consider_circulation = st.session_state.get("consider_circulation", False)
        if consider_circulation:
            circulation_type = st.session_state.get("circulation_type", "同じ水を循環")
            operation_minutes = st.session_state.get("operation_value", 10)
            if circulation_type == "同じ水を循環":
                operation_hours = operation_minutes / 60  # 分を時間に変換
            else:
                operation_hours = 1  # 新しい水を連続供給の場合
        else:
            operation_hours = 1  # デフォルト値（後で再計算される）
            circulation_type = None
        temp_rise_limit = st.session_state.get("limit_value", 5.0)
    else:
        operation_hours = 1  # デフォルト値
        temp_rise_limit = 5  # デフォルト値
        consider_circulation = False
        circulation_type = None
    
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
    
    # 配管外径データ（SGP規格）
    pipe_outer_diameter_sgp = {
        "15A": 21.7,   # mm
        "20A": 27.2,   # mm
        "25A": 34.0,   # mm
        "32A": 42.7,   # mm
        "40A": 48.6,   # mm
        "50A": 60.5,   # mm
        "65A": 76.3,   # mm
        "80A": 89.1    # mm
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
    
    # ヌセルト数の計算（層流/乱流判定）
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
    
    # 変数の初期化（後で使用する可能性があるもの）
    time_history = []
    inlet_temp_history = []
    outlet_temp_history = []
    ground_temp_history = []
    boring_volume = 0
    pipe_total_volume = 0
    groundwater_volume = 0
    groundwater_mass = 0
    heat_exchange_rate = 0
    groundwater_temp_rise_unlimited = 0
    
    # 地下水温度上昇の計算
    if consider_groundwater_temp_rise:
        # 初期熱交換量の計算 [W]
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
            
        # 循環方式に応じた計算
        if consider_circulation and circulation_type == "同じ水を循環":
            # 同じ水を循環させる場合の計算（反復計算）
            time_step = 60  # 1分ごとの計算
            num_steps = int(operation_hours * 3600 / time_step)
            
            current_inlet_temp = initial_temp
            current_ground_temp = ground_temp
            
            # 時系列データを保存するリスト
            time_history = []
            inlet_temp_history = []
            outlet_temp_history = []
            ground_temp_history = []
            
            for i in range(num_steps):
                # 現在の温度での熱交換計算
                current_effectiveness = 1 - math.exp(-NTU)
                current_outlet_temp = current_inlet_temp - current_effectiveness * (current_inlet_temp - current_ground_temp)
                
                # 熱交換量
                current_heat_rate = mass_flow_rate_per_pipe * num_pipes * specific_heat * (current_inlet_temp - current_outlet_temp)
                
                # 地下水温度上昇
                if groundwater_mass > 0:
                    delta_ground_temp = (current_heat_rate * time_step) / (groundwater_mass * specific_heat)
                    current_ground_temp += delta_ground_temp
                    # 物理的制約：地下水温度は入口温度を超えない
                    current_ground_temp = min(current_ground_temp, ground_temp + temp_rise_limit, current_inlet_temp)
                
                # データを記録
                time_history.append(i * time_step / 60)  # 分単位
                inlet_temp_history.append(current_inlet_temp)
                outlet_temp_history.append(current_outlet_temp)
                ground_temp_history.append(current_ground_temp)
                
                # 次のステップの入口温度は現在の出口温度
                current_inlet_temp = current_outlet_temp
            
            # 最終結果
            final_temp = current_outlet_temp
            effective_ground_temp = current_ground_temp
            groundwater_temp_rise = current_ground_temp - ground_temp
            groundwater_temp_rise_unlimited = groundwater_temp_rise
            
        else:
            # 新しい水を連続供給する場合、または循環を考慮しない場合
            if consider_circulation and circulation_type == "新しい水を連続供給":
                # 時系列データを生成（新しい水を連続供給）
                time_step = 60  # 1分ごとの計算
                num_steps = int(operation_hours * 3600 / time_step)
                
                current_ground_temp = ground_temp
                
                # 時系列データを保存するリスト
                time_history = []
                inlet_temp_history = []
                outlet_temp_history = []
                ground_temp_history = []
                
                for i in range(num_steps):
                    # 現在の地下水温度での出口温度計算
                    current_effectiveness = 1 - math.exp(-NTU)
                    current_outlet_temp = initial_temp - current_effectiveness * (initial_temp - current_ground_temp)
                    
                    # 熱交換量
                    current_heat_rate = mass_flow_rate_per_pipe * num_pipes * specific_heat * (initial_temp - current_outlet_temp)
                    
                    # 地下水温度上昇
                    if groundwater_mass > 0:
                        delta_ground_temp = (current_heat_rate * time_step) / (groundwater_mass * specific_heat)
                        current_ground_temp += delta_ground_temp
                        # 物理的制約：地下水温度は入口温度を超えない
                        current_ground_temp = min(current_ground_temp, ground_temp + temp_rise_limit, initial_temp)
                    
                    # データを記録
                    time_history.append(i * time_step / 60)  # 分単位
                    inlet_temp_history.append(initial_temp)  # 入口温度は一定
                    outlet_temp_history.append(current_outlet_temp)
                    ground_temp_history.append(current_ground_temp)
                
                # 最終結果
                final_temp = outlet_temp_history[-1] if outlet_temp_history else initial_temp
                effective_ground_temp = current_ground_temp
                groundwater_temp_rise = current_ground_temp - ground_temp
                groundwater_temp_rise_unlimited = groundwater_temp_rise
                
            else:
                # 循環を考慮しない場合（1回通水）
                operation_time = operation_hours * 3600  # 秒
                if groundwater_mass > 0:
                    groundwater_temp_rise = (heat_exchange_rate * operation_time) / (groundwater_mass * specific_heat)
                else:
                    st.error("⚠️ 地下水体積が負またはゼロです。配管が多すぎるか、掘削径が小さすぎます。")
                    groundwater_temp_rise = 0.0
                
                # 温度上昇を制限（物理的制約も考慮）
                groundwater_temp_rise_unlimited = groundwater_temp_rise
                # 地下水温度は入口温度を超えない
                max_possible_rise = initial_temp - ground_temp
                groundwater_temp_rise = min(groundwater_temp_rise, temp_rise_limit, max_possible_rise)
                
                # 実効地下水温度を更新
                effective_ground_temp = ground_temp + groundwater_temp_rise
                
                # 最終温度を再計算
                final_temp = initial_temp - effectiveness * (initial_temp - effective_ground_temp)
    else:
        groundwater_temp_rise = 0.0
        # 地下水温度上昇を考慮しない場合、初回計算の値をそのまま使用
        # （final_tempは既に586行目で計算済み）
    
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
    main_col1, main_col2, main_col3 = st.columns([1, 1, 1], gap="medium")
    
    with main_col1:
        st.markdown(f"""
        <div style="border: 3px solid #ff4b4b; border-radius: 10px; padding: 13px; background-color: #fff5f5; text-align: center; margin-bottom: 15px;">
            <h3 style="margin: 0; color: #ff4b4b; font-size: 18px;">🌡️ 出口温度</h3>
            <h1 style="margin: 0px 0; color: #333; font-size: 36px;">{final_temp:.1f}℃</h1>
            <p style="margin: 0; color: #666; font-size: 14px;">温度降下: {initial_temp - final_temp:.1f}℃</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")  # モバイル表示時のスペース追加
    
    with main_col2:
        if consider_groundwater_temp_rise:
            st.markdown(f"""
            <div style="border: 3px solid #1976d2; border-radius: 10px; padding: 13px; background-color: #f0f7ff; text-align: center; margin-bottom: 15px;">
                <h3 style="margin: 0; color: #1976d2; font-size: 18px;">💧 地下水温</h3>
                <h1 style="margin: 0px 0; color: #333; font-size: 36px;">{effective_ground_temp:.1f}℃</h1>
                <p style="margin: 0; color: #666; font-size: 14px;">温度上昇: +{groundwater_temp_rise:.1f}℃</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("")  # モバイル表示時のスペース追加
        else:
            st.markdown(f"""
            <div style="border: 3px solid #1976d2; border-radius: 10px; padding: 13px; background-color: #f0f7ff; text-align: center; margin-bottom: 15px;">
                <h3 style="margin: 0; color: #1976d2; font-size: 18px;">💧 地下水温</h3>
                <h1 style="margin: 0px 0; color: #333; font-size: 36px;">{effective_ground_temp:.1f}℃</h1>
                <p style="margin: 0; color: #666; font-size: 14px;">初期温度のまま</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("")  # モバイル表示時のスペース追加
    
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
        <div style="border: 3px solid #4caf50; border-radius: 10px; padding: 13px; background-color: #f1f8e9; text-align: center; margin-bottom: 15px;">
            <h3 style="margin: 0; color: #4caf50; font-size: 18px;">⏱️ 通水時間</h3>
            <h1 style="margin: 0px 0; color: #333; font-size: 36px;">{time_display}{time_unit}</h1>
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
    
    # 温度変化グラフ（循環を考慮する場合）
    if consider_groundwater_temp_rise and consider_circulation:
        st.markdown("---")
        st.subheader("📊 温度変化の時系列")
        
        # グラフを作成
        fig = go.Figure()
        
        # 入口温度（循環水温度）
        fig.add_trace(go.Scatter(
            x=time_history,
            y=inlet_temp_history,
        mode='lines',
        name='入口温度（循環水）',
        line=dict(color='red', width=2)
        ))
        
        # 出口温度
        fig.add_trace(go.Scatter(
        x=time_history,
        y=outlet_temp_history,
        mode='lines',
        name='出口温度',
        line=dict(color='blue', width=2)
        ))
        
        # 地下水温度
        fig.add_trace(go.Scatter(
        x=time_history,
        y=ground_temp_history,
        mode='lines',
        name='地下水温度',
        line=dict(color='green', width=2, dash='dash')
        ))
        
        # 目標温度線
        fig.add_hline(y=target_temp, line_dash="dot", line_color="gray", 
                 annotation_text=f"目標温度 {target_temp}℃", 
                 annotation_position="right")
        
        # 初期地下水温度線
        fig.add_hline(y=ground_temp, line_dash="dot", line_color="lightgreen", 
                 annotation_text=f"初期地下水温度 {ground_temp}℃", 
                 annotation_position="left")
        
        # グラフタイトルを運転方式に応じて変更
        graph_title = "循環による温度変化" if circulation_type == "同じ水を循環" else "連続供給による温度変化"
        
        fig.update_layout(
        title=graph_title,
        xaxis_title="経過時間（分）",
        yaxis_title="温度（℃）",
        height=400,
        showlegend=True,
        hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 収束状況の説明
        if circulation_type == "同じ水を循環":
            convergence_temp = (inlet_temp_history[-1] + ground_temp_history[-1]) / 2
            st.info(f"💡 {operation_minutes}分後の状態：循環水温度 {inlet_temp_history[-1]:.1f}℃、地下水温度 {ground_temp_history[-1]:.1f}℃に向かって収束中")
        else:
            st.info(f"💡 {operation_minutes}分後の状態：出口温度 {outlet_temp_history[-1]:.1f}℃、地下水温度 {ground_temp_history[-1]:.1f}℃")
    
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
    
    # 追加の計算結果表示（地下水温度上昇に関係なく表示）
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

elif page == "複数配管比較":
    # ページ遷移時のスクロールリセット用
    if st.session_state.page_changed:
        st.empty()
    
    # タイトル
    st.markdown("<h1 style='text-align: center;'>📊 複数配管比較計算</h1>", unsafe_allow_html=True)
    st.markdown("""
    異なる管径での性能を比較し、最適な配管仕様を見つけるためのツールです。
    """)
    
    # 複数配管比較ページ
    
    # 入力セクションで定義された変数を取得（複数配管比較タブ用）
    # セッション状態から値を取得
    target_temp = st.session_state.get("target_value", 25.0)
    initial_temp = st.session_state.get("initial_value", 30.0)
    flow_rate = st.session_state.get("flow_value", 50.0)
    ground_temp = st.session_state.get("ground_value", 15.0)
    pipe_length = st.session_state.get("length_value", 5.0)
    boring_diameter = st.session_state.get("boring_diameter", "φ250")
    boring_diameter_mm = 116 if boring_diameter == "φ116" else 250
    pipe_material = st.session_state.get("pipe_material", "鋼管")
    consider_groundwater_temp_rise = st.session_state.get("consider_groundwater_temp_rise", False)
    
    # 地下水温度上昇関連の変数
    if consider_groundwater_temp_rise:
        consider_circulation = st.session_state.get("consider_circulation", False)
        if consider_circulation:
            circulation_type = st.session_state.get("circulation_type", "同じ水を循環")
            if circulation_type == "同じ水を循環":
                operation_hours = st.session_state.get("hours_value", 8.0) / 60  # 分を時間に変換
            else:
                operation_hours = 1  # 新しい水を連続供給の場合
        else:
            operation_hours = 1  # デフォルト値（後で再計算される）
            circulation_type = None
        temp_rise_limit = st.session_state.get("limit_value", 5.0)
    else:
        operation_hours = 1  # デフォルト値
        temp_rise_limit = 5  # デフォルト値
        consider_circulation = False
        circulation_type = None

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
        boring_area = math.pi * (boring_diameter_mm / 2) ** 2  # mm²
        
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
                
                # 循環方式に応じた計算
                if consider_circulation and circulation_type == "同じ水を循環":
                    # 同じ水を循環させる場合の計算（反復計算）
                    time_step = 60  # 1分ごとの計算
                    num_steps = int(operation_hours * 3600 / time_step)
                    
                    current_inlet_temp = initial_temp
                    current_ground_temp = ground_temp
                    
                    for i in range(num_steps):
                        # 現在の温度での熱交換計算
                        current_effectiveness = 1 - math.exp(-NTU_temp)
                        current_outlet_temp = current_inlet_temp - current_effectiveness * (current_inlet_temp - current_ground_temp)
                        
                        # 熱交換量
                        current_heat_rate = mass_flow_per_p * n_pipes * specific_heat * (current_inlet_temp - current_outlet_temp)
                        
                        # 地下水温度上昇
                        if groundwater_mass_temp > 0:
                            delta_ground_temp = (current_heat_rate * time_step) / (groundwater_mass_temp * specific_heat)
                            current_ground_temp += delta_ground_temp
                            # 物理的制約：地下水温度は入口温度を超えない
                            current_ground_temp = min(current_ground_temp, ground_temp + temp_rise_limit, current_inlet_temp)
                        
                        # 次のステップの入口温度は現在の出口温度
                        current_inlet_temp = current_outlet_temp
                    
                    # 最終結果
                    final_t = current_outlet_temp
                    effective_ground_temp_local = current_ground_temp
                    gw_temp_rise = current_ground_temp - ground_temp
                    
                else:
                    # 新しい水を連続供給する場合、または循環を考慮しない場合
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
                        # 物理的制約：地下水温度は入口温度を超えない
                        max_possible_rise = initial_temp - ground_temp
                        gw_temp_rise = min(gw_temp_rise, temp_rise_limit, max_possible_rise)
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
    # ページ遷移時のスクロールリセット用
    if st.session_state.page_changed:
        st.empty()
    
    st.title("📚 地中熱交換の理論解説")
    st.markdown("本シミュレーターで適用している熱交換理論の詳細な解説")
    
    # 計算フローチャート
    st.header("🔄 本ツールの計算フローと適用理論")
    st.markdown("""
    以下に、実際の計算過程と各ステップで使用される理論式を詳細に示します。
    """)
    
    # ステップ1
    with st.expander("📌 ステップ1: 入力データの処理と物性値の決定"):
        st.markdown("""
        ### 1-1. 平均温度の計算
        """)
        st.latex(r"T_{avg} = \frac{T_{initial} + T_{ground}}{2}")
        st.markdown("""
        **記号の説明：**
        - **Tavg**: 平均温度 [℃]
        - **Tinitial**: 入口温度 [℃]
        - **Tground**: 地下水温度 [℃]
        """)
        
        st.markdown("""
        ### 1-2. 物性値の決定（線形補間）
        温度範囲に応じて以下の物性値を設定：
        - **動粘度** ν [m²/s]
        - **熱伝導率** k [W/m·K]
        - **プラントル数** Pr [-]
        - **密度** ρ [kg/m³]
        - **比熱** cp [J/kg·K]
        
        ### 1-3. 流量計算
        """)
        st.latex(r"\dot{m} = \rho \cdot Q_{volume}")
        st.markdown("""
        **記号の説明：**
        - **ṁ**: 質量流量 [kg/s]
        - **ρ**: 密度 [kg/m³]
        - **Qvolume**: 体積流量 [m³/s] = (流量[L/min] / 60000)
        """)
    
    # ステップ2
    with st.expander("📌 ステップ2: 管内流動状態の判定"):
        st.markdown("""
        ### 2-1. 流速の計算
        """)
        st.latex(r"v = \frac{Q_{volume}}{A} = \frac{Q_{volume}}{\pi (D/2)^2}")
        st.markdown("""
        **記号の説明：**
        - **v**: 流速 [m/s]
        - **Qvolume**: 1本あたりの体積流量 [m³/s]
        - **A**: 配管断面積 [m²]
        - **D**: 配管内径 [m]
        - **π**: 円周率 ≈ 3.14159
        """)
        
        st.markdown("""
        ### 2-2. レイノルズ数の計算
        """)
        st.latex(r"Re = \frac{vD}{\nu}")
        st.markdown("""
        **記号の説明：**
        - **Re**: レイノルズ数 [-]（無次元）
        - **v**: 流速 [m/s]
        - **D**: 配管内径 [m]
        - **ν**: 動粘度 [m²/s]
        """)
        
        st.markdown("""
        - **Re < 2300**: 層流 → Nu = 3.66
        - **Re ≥ 2300**: 乱流 → Dittus-Boelter式を使用
        """)
    
    # ステップ3
    with st.expander("📌 ステップ3: 熱伝達係数の計算"):
        st.markdown("""
        ### 3-1. ヌセルト数の決定
        
        **層流の場合（Re < 2300）：**
        """)
        st.latex(r"Nu = 3.66")
        st.markdown("""
        **記号の説明：**
        - **Nu**: ヌセルト数 [-]（無次元）
        """)
        
        st.markdown("""
        **乱流の場合（Re ≥ 2300）：**
        """)
        st.latex(r"Nu = 0.023 \cdot Re^{0.8} \cdot Pr^{0.3}")
        st.markdown("""
        **記号の説明：**
        - **Nu**: ヌセルト数 [-]
        - **Re**: レイノルズ数 [-]
        - **Pr**: プラントル数 [-]
        - **0.023, 0.8, 0.3**: 実験的に決定された定数
        """)
        
        st.markdown("""
        ### 3-2. 管内側熱伝達係数
        """)
        st.latex(r"h_i = \frac{Nu \cdot k_{water}}{D}")
        st.markdown("""
        **記号の説明：**
        - **hi**: 管内側熱伝達係数 [W/m²·K]
        - **Nu**: ヌセルト数 [-]
        - **kwater**: 水の熱伝導率 [W/m·K]
        - **D**: 配管内径 [m]
        """)
        
        st.markdown("""
        ### 3-3. 管外側熱伝達係数
        - ho = 300 [W/m²·K]（自然対流を仮定）
        """)
    
    # ステップ4
    with st.expander("📌 ステップ4: 総括熱伝達係数の計算"):
        st.markdown("""
        ### 4-1. 内径基準の総括熱伝達係数
        """)
        st.latex(r"U_i = \frac{1}{\frac{1}{h_i} + \frac{r_i \ln(r_o/r_i)}{k_{pipe}} + \frac{r_i}{r_o h_o}}")
        st.markdown("""
        **記号の説明：**
        - **Ui**: 内径基準の総括熱伝達係数 [W/m²·K]
        - **hi**: 管内側熱伝達係数 [W/m²·K]
        - **ri**: 配管内半径 [m]
        - **ro**: 配管外半径 [m]
        - **kpipe**: 配管材の熱伝導率 [W/m·K]
        - **ho**: 管外側熱伝達係数 [W/m²·K]
        """)
        
        st.markdown("""
        各項の物理的意味：
        - **第1項**: 管内側の対流熱抵抗
        - **第2項**: 管壁の伝導熱抵抗
        - **第3項**: 管外側の対流熱抵抗
        
        ### 4-2. 伝熱面積の計算
        """)
        st.latex(r"A = \pi D L_{total}")
        st.markdown("""
        **記号の説明：**
        - **A**: 伝熱面積 [m²]
        - **π**: 円周率 ≈ 3.14159
        - **D**: 配管内径 [m]
        - **Ltotal**: U字管の総延長 = 2 × 管浸水距離 [m]
        """)
    
    # ステップ5
    with st.expander("📌 ステップ5: NTU-ε法による熱交換計算"):
        st.markdown("""
        ### 5-1. 伝熱単位数（NTU）の計算
        """)
        st.latex(r"NTU = \frac{UA}{\dot{m}c_p}")
        st.markdown("""
        **記号の説明：**
        - **NTU**: 伝熱単位数 [-]（無次元）
        - **U**: 総括熱伝達係数 [W/m²·K]
        - **A**: 伝熱面積 [m²]
        - **ṁ**: 質量流量 [kg/s]
        - **cp**: 比熱 [J/kg·K]
        """)
        
        st.markdown("""
        ### 5-2. 熱交換効率の計算
        """)
        st.latex(r"\varepsilon = 1 - e^{-NTU}")
        st.markdown("""
        **記号の説明：**
        - **ε**: 熱交換効率 [-]（0～1の値）
        - **e**: 自然対数の底 ≈ 2.718
        - **NTU**: 伝熱単位数 [-]
        """)
        
        st.markdown("""
        - 対向流熱交換器で熱容量比Cr = 0の場合の理論解
        - 地下水側の熱容量が非常に大きいと仮定
        
        ### 5-3. 出口温度の計算
        """)
        st.latex(r"T_{out} = T_{in} - \varepsilon(T_{in} - T_{ground})")
        st.markdown("""
        **記号の説明：**
        - **Tout**: 出口温度 [℃]
        - **Tin**: 入口温度 [℃]
        - **Tground**: 地下水温度 [℃]
        - **ε**: 熱交換効率 [-]
        """)
    
    # ステップ6
    with st.expander("📌 ステップ6: 熱交換量の計算"):
        st.markdown("""
        ### 6-1. 総熱交換量
        """)
        st.latex(r"Q = \dot{m} \cdot c_p \cdot (T_{in} - T_{out})")
        st.markdown("""
        **記号の説明：**
        - **Q**: 総熱交換量 [W]
        - **ṁ**: 総質量流量 [kg/s]
        - **cp**: 比熱 [J/kg·K]
        - **Tin**: 入口温度 [℃]
        - **Tout**: 出口温度 [℃]
        """)
        
        st.markdown("""
        - 温度差から実際の熱移動量を計算
        
        ### 6-2. 熱流束の確認
        """)
        st.latex(r"q = \frac{Q}{A}")
        st.markdown("""
        **記号の説明：**
        - **q**: 熱流束 [W/m²]
        - **Q**: 総熱交換量 [W]
        - **A**: 伝熱面積 [m²]
        """)
        
        st.markdown("""
        - 単位面積あたりの熱流量
        - 設計の妥当性確認に使用
        """)
    
    # ステップ7
    with st.expander("📌 ステップ7: 地下水温度上昇の計算（オプション）"):
        st.markdown("""
        ### 7-1. 地下水体積の計算
        """)
        st.latex(r"V_{gw} = V_{boring} - V_{pipes}")
        st.markdown("""
        **記号の説明：**
        - **Vgw**: 地下水体積 [m³]
        - **Vboring**: ボーリング孔体積 [m³] = π(Dboring²/4)L
        - **Vpipes**: 配管総体積 [m³]（U字管なので2倍）
        - **Dboring**: ボーリング孔径 [m]
        - **L**: 管浸水距離 [m]
        """)
        
        st.markdown("""
        ### 7-2. 地下水質量
        """)
        st.latex(r"m_{gw} = \rho_{water} \cdot V_{gw}")
        st.markdown("""
        **記号の説明：**
        - **mgw**: 地下水質量 [kg]
        - **ρwater**: 水の密度 [kg/m³]
        - **Vgw**: 地下水体積 [m³]
        """)
        
        st.markdown("""
        ### 7-3. 温度上昇の計算
        
        **A. 循環なしの場合（1回通水）：**
        """)
        st.latex(r"t_{transit} = \frac{L_{total}}{v}")
        st.latex(r"\Delta T_{gw} = \frac{Q \cdot t_{transit}}{m_{gw} \cdot c_p}")
        st.markdown("""
        **記号の説明：**
        - **ttransit**: 通水時間 [s]
        - **Ltotal**: U字管の総延長 [m]
        - **v**: 流速 [m/s]
        - **ΔTgw**: 地下水温度上昇 [K]
        - **Q**: 熱交換量 [W]
        - **mgw**: 地下水質量 [kg]
        - **cp**: 比熱 [J/kg·K]
        """)
        
        st.markdown("""
        **B. 循環ありの場合（連続運転）：**
        
        時間ステップごとに以下を反復：
        1. 現在の地下水温度でNTU計算
        2. 効率εと出口温度を計算
        3. 熱交換量Qを計算
        4. 地下水温度上昇ΔTを計算
        5. **物理的制約を適用**：地下水温度 ≤ 現在の入口温度
        6. 次ステップの入口温度 = 現在の出口温度
        
        **温度収束の特性：**
        - 「同じ水を循環」モードでは、循環水温度と地下水温度が最終的に熱平衡状態に収束
        - 収束温度は初期条件と熱容量比によって決定
        - 「新しい水を連続供給」モードでは、地下水温度は入口温度に漸近
        
        ### 7-4. 温度上昇の制限（物理的制約）
        
        **熱力学第二法則による制約：**
        地下水温度は入口温度を超えることはできません。
        """)
        st.latex(r"T_{ground,max} = T_{in}")
        st.latex(r"\Delta T_{gw,max} = T_{in} - T_{ground,initial}")
        
        st.markdown("""
        **実際の制限値：**
        """)
        st.latex(r"\Delta T_{gw,limited} = \min(\Delta T_{gw}, \Delta T_{limit}, \Delta T_{gw,max})")
        st.markdown("""
        **記号の説明：**
        - **Tground,max**: 地下水の物理的上限温度 [℃]
        - **Tin**: 入口温度 [℃]
        - **ΔTgw,max**: 物理的に可能な最大温度上昇 [K]
        - **ΔTgw,limited**: 制限後の地下水温度上昇 [K]
        - **ΔTgw**: 計算された地下水温度上昇 [K]
        - **ΔTlimit**: ユーザー設定の上限値 [K]（5-20℃）
        - **min()**: 最小値を選択する関数
        
        ⚠️ **重要**：30℃の水で35℃まで地下水温度が上昇するような非物理的な結果は起こりません。
        """)
    
    # ステップ8
    with st.expander("📌 ステップ8: 最終計算と結果の評価"):
        st.markdown("""
        ### 8-1. 最終出口温度の決定
        
        地下水温度上昇を考慮した場合：
        """)
        st.latex(r"T_{ground,final} = T_{ground,initial} + \Delta T_{gw}")
        st.latex(r"T_{out,final} = T_{in} - \varepsilon(T_{in} - T_{ground,final})")
        st.markdown("""
        **記号の説明：**
        - **Tground,final**: 最終地下水温度 [℃]
        - **Tground,initial**: 初期地下水温度 [℃]
        - **ΔTgw**: 地下水温度上昇 [K]
        - **Tout,final**: 最終出口温度 [℃]
        - **Tin**: 入口温度 [℃]
        - **ε**: 熱交換効率 [-]
        """)
        
        st.markdown("""
        ### 8-2. 性能指標の評価
        
        **温度降下率：**
        """)
        st.latex(r"\eta_{temp} = \frac{T_{in} - T_{out}}{T_{in} - T_{ground}} \times 100\%")
        st.markdown("""
        **記号の説明：**
        - **ηtemp**: 温度降下率 [%]
        - **Tin**: 入口温度 [℃]
        - **Tout**: 出口温度 [℃]
        - **Tground**: 地下水温度 [℃]
        """)
        
        st.markdown("""
        **熱交換効率の確認：**
        - NTU > 0.3: 実用的な性能
        - ε > 0.5: 良好な熱交換
        
        ### 8-3. 目標温度との比較
        
        目標温度を下回った場合の対策提案：
        - 配管セット本数の増加
        - 管浸水距離の延長
        - 流量の調整
        """)
    
    st.info("""
    💡 **計算の特徴**
    - すべての計算は理論式に基づいており、経験的な補正係数は最小限
    - 温度依存の物性値を考慮することで、より正確な予測が可能
    - 地下水温度上昇の考慮により、長時間運転時の性能低下を予測
    - **熱力学第二法則による物理的制約を実装**（地下水温度 ≤ 入口温度）
    """)
    
    st.info("""
    💡 **注意事項**
    - 本計算は理想的な条件下での理論値です
    - 実際の性能は、地下水の流動状態、配管の汚れ、設置条件などにより変動します
    - 設計時は適切な安全率を考慮してください
    """)
    
    st.markdown("---")
    
    # 熱力学の基礎法則
    st.header("⚖️ 熱力学の基礎法則")
    
    st.subheader("熱力学第一法則（エネルギー保存則）")
    st.markdown("""
    エネルギーは生成も消滅もせず、ただ形態を変えるのみ。
    """)
    st.latex(r"\Delta U = Q - W")
    st.markdown("""
    **記号の説明：**
    - **ΔU**: 内部エネルギーの変化 [J]
    - **Q**: 系に加えられた熱量 [J]
    - **W**: 系が外部にした仕事 [J]
    
    本システムでは、入口から持ち込まれた熱エネルギーが地下水に移動します。
    """)
    
    st.subheader("熱力学第二法則（エントロピー増大則）")
    st.markdown("""
    熱は高温から低温へのみ自然に流れる。
    """)
    st.latex(r"dS \geq \frac{dQ}{T}")
    st.markdown("""
    **記号の説明：**
    - **dS**: エントロピーの変化 [J/K]
    - **dQ**: 熱量の変化 [J]
    - **T**: 絶対温度 [K]
    
    **本システムへの適用：**
    - 地下水温度は入口温度を超えることはできません
    - 30℃の水から15℃の地下水へ熱が流れるのは自然
    - 30℃の水から35℃の地下水へ熱が流れることは不可能
    """)
    
    st.warning("""
    ⚠️ **物理的制約の重要性**
    
    以前のバージョンでは、地下水温度が入口温度を超える非物理的な結果が発生する可能性がありました。
    現在は、熱力学第二法則に基づく物理的制約を実装し、正しい結果を保証しています。
    """)
    
    st.markdown("---")
    
    # 熱移動の基礎理論
    st.header("🔬 熱移動の基礎理論")
    
    st.subheader("1. 熱移動の3つの形態")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**熱伝導（Conduction）**")
        st.latex(r"q = -k \nabla T")
        st.markdown("""
        物質内部の分子振動による熱移動
        - 固体内部の熱移動が主
        - 配管壁での熱抵抗
        
        **記号の説明：**
        - **q**: 熱流束 [W/m²]
        - **k**: 熱伝導率 [W/m·K]
        - **∇T**: 温度勾配 [K/m]
        """)
    
    with col2:
        st.markdown("**対流（Convection）**")
        st.latex(r"q = h(T_s - T_\infty)")
        st.markdown("""
        流体の移動を伴う熱移動
        - 管内流れでの主要な熱移動
        - 強制対流と自然対流
        
        **記号の説明：**
        - **q**: 熱流束 [W/m²]
        - **h**: 熱伝達係数 [W/m²·K]
        - **Ts**: 壁面温度 [K]
        - **T∞**: 流体バルク温度 [K]
        """)
    
    with col3:
        st.markdown("**放射（Radiation）**")
        st.latex(r"q = \epsilon \sigma (T_1^4 - T_2^4)")
        st.markdown("""
        電磁波による熱移動
        - 本計算では無視
        - 低温域では影響小
        
        **記号の説明：**
        - **q**: 熱流束 [W/m²]
        - **ε**: 放射率 [-]
        - **σ**: Stefan-Boltzmann定数
          (5.67×10⁻⁸ W/m²·K⁴)
        - **T₁, T₂**: 絶対温度 [K]
        """)
    
    st.subheader("2. エネルギー保存則（熱力学第一法則）")
    st.markdown("""
    系に出入りする熱量と仕事の総和は、系の内部エネルギー変化に等しい
    """)
    st.latex(r"dE_{system}/dt = \dot{Q}_{in} - \dot{Q}_{out} + \dot{W}")
    st.markdown("""
    **記号の説明：**
    
    **Esystem**: 系の内部エネルギー [J]<br>
    **Q̇in**: 系に入る熱流量 [W]<br>
    **Q̇out**: 系から出る熱流量 [W]<br>
    **Ẇ**: 系に加えられる仕事率 [W]<br>
    **t**: 時間 [s]
    """)
    
    st.markdown("""
    **定常流動系のエネルギー方程式：**
    """)
    st.latex(r"\dot{m}(h_{out} - h_{in}) = \dot{Q} - \dot{W}")
    st.markdown("""
    **記号の説明：**
    
    **ṁ**: 質量流量 [kg/s]<br>
    **hin, hout**: 入口・出口エンタルピー [J/kg]<br>
    **Q̇**: 熱流量 [W]<br>
    **Ẇ**: 仕事率 [W]
    """)
    
    st.markdown("""
    配管内流れでは仕事項がゼロ、エンタルピー変化を温度変化で表すと：
    """)
    st.latex(r"\dot{Q} = \dot{m} c_p (T_{out} - T_{in})")
    st.markdown("""
    **記号の説明：**
    - **Q̇**: 熱流量 [W]
    - **ṁ**: 質量流量 [kg/s]
    - **cp**: 定圧比熱 [J/kg·K]
    - **Tin, Tout**: 入口・出口温度 [K または ℃]
    """)
    
    st.markdown("---")
    
    # 管内流れの流体力学
    st.header("💧 管内流れの流体力学理論")
    
    st.subheader("1. 連続の式と運動量保存")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**連続の式（質量保存）**")
        st.latex(r"\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \vec{v}) = 0")
        st.markdown("""
        **記号の説明：**
        - **ρ**: 密度 [kg/m³]
        - **t**: 時間 [s]
        - **v⃗**: 速度ベクトル [m/s]
        - **∇·**: 発散演算子 [1/m]
        - **∂/∂t**: 時間に関する偏微分
        
        非圧縮性定常流では：
        """)
        st.latex(r"v_1 A_1 = v_2 A_2")
        st.markdown("""
        **記号の説明：**
        - **v₁, v₂**: 断面1, 2での流速 [m/s]
        - **A₁, A₂**: 断面1, 2での断面積 [m²]
        """)
    
    with col2:
        st.markdown("**ナビエ・ストークス方程式**")
        st.latex(r"\rho \left(\frac{\partial \vec{v}}{\partial t} + (\vec{v} \cdot \nabla)\vec{v}\right) = -\nabla p + \mu \nabla^2 \vec{v} + \rho \vec{g}")
        st.markdown("""
        慣性力（非定常項＋対流項）、圧力、粘性力、体積力の釣り合い
        
        **記号の説明：**
        - **ρ**: 密度 [kg/m³]
        - **∂v⃗/∂t**: 局所的時間変化（非定常項） [m/s²]
        - **(v⃗·∇)v⃗**: 対流項（移流項） [m/s²]
        - **v⃗**: 速度ベクトル [m/s]
        - **p**: 圧力 [Pa = N/m²]
        - **∇p**: 圧力勾配 [Pa/m]
        - **μ**: 動粘性係数 [Pa·s = kg/m·s]
        - **∇²**: ラプラシアン演算子 [1/m²]
        - **g⃗**: 重力加速度ベクトル [m/s²]
        
        ※実質微分 D/Dt = ∂/∂t + (v⃗·∇) を展開表示
        """)
    
    st.subheader("2. 無次元数による流れの特性化")
    
    st.markdown("**レイノルズ数の導出**")
    st.markdown("""
    ナビエ・ストークス方程式を無次元化すると、慣性力と粘性力の比として現れる：
    """)
    st.latex(r"Re = \frac{\text{慣性力}}{\text{粘性力}} = \frac{\rho v L}{\mu} = \frac{v L}{\nu}")
    st.markdown("""
    **記号の説明：**
    - **Re**: レイノルズ数 [-]（無次元）
    - **ρ**: 密度 [kg/m³]
    - **v**: 代表流速 [m/s]
    - **L**: 代表長さ（管径D） [m]
    - **μ**: 動粘性係数 [Pa·s]
    - **ν**: 動粘度（= μ/ρ） [m²/s]
    """)
    
    st.markdown("""
    **臨界レイノルズ数（Re = 2300）の意味：**
    - 層流から乱流への遷移点
    - 実験的に決定された普遍的な値
    - 管径や流体によらず一定
    """)
    
    st.markdown("---")
    
    # 管内流れの熱伝達
    st.header("🌊 管内流れの熱伝達理論")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. レイノルズ数と流動状態")
        st.markdown("""
        管内流れの状態は**レイノルズ数**により判定されます。
        """)
        st.latex(r"Re = \frac{\rho v D}{\mu} = \frac{vD}{\nu}")
        st.markdown("""
        **記号の説明：**
        - **ρ**: 流体密度 [kg/m³]
        - **v**: 平均流速 [m/s]
        - **D**: 管内径 [m]
        - **μ**: 動粘性係数 [Pa·s]
        - **ν**: 動粘度 [m²/s]
        
        **物理的意味：**
        - 慣性力と粘性力の比を表す無次元数
        - Re < 2300: 層流（規則的な流れ）
        - Re > 2300: 乱流（不規則な流れ）
        
        **理論的背景：**
        オズボーン・レイノルズの実験（1883年）により、
        流れの遷移が無次元数で整理できることが発見されました。
        """)
    
    with col2:
        st.subheader("2. ヌセルト数と熱伝達")
        st.markdown("""
        熱伝達の強さは**ヌセルト数**で表されます。
        """)
        st.latex(r"Nu = \frac{hD}{k}")
        st.markdown("""
        **記号の説明：**
        - **Nu**: ヌセルト数 [-]（無次元）
        - **h**: 熱伝達係数 [W/m²·K]
        - **D**: 管内径 [m]
        - **k**: 流体の熱伝導率 [W/m·K]
        
        **物理的意味：**
        - 対流熱伝達と熱伝導の比
        - 大きいほど対流による熱移動が活発
        
        **層流の理論解（グレーツ解）：**
        - 十分発達した層流: Nu = 3.66
        
        **乱流の実験相関式（Dittus-Boelter式）：**
        """)
        st.latex(r"Nu = 0.023 \cdot Re^{0.8} \cdot Pr^{n}")
        st.markdown("""
        **記号の説明：**
        - **Nu**: ヌセルト数 [-]（無次元）
        - **Re**: レイノルズ数 [-]（無次元）
        - **Pr**: プラントル数 [-]（無次元）
        - **n**: 指数 [-]（冷却時: n = 0.3, 加熱時: n = 0.4）
        - **0.023, 0.8**: 実験的に求められた定数
        """)
    
    st.markdown("---")
    
    # 熱交換器の設計理論
    st.header("🔄 熱交換器の設計理論")
    
    st.subheader("対数平均温度差（LMTD）法")
    st.markdown("""
    熱交換器の基本設計式は以下で表されます：
    """)
    st.latex(r"Q = UA \cdot LMTD")
    st.markdown("""
    **記号の説明：**
    - **Q**: 熱交換量 [W]
    - **U**: 総括熱伝達係数 [W/m²·K]
    - **A**: 伝熱面積 [m²]
    - **LMTD**: 対数平均温度差 [K]
    
    しかし、対向流や並流の場合のLMTD計算は複雑なため、
    本ツールではより汎用的な**NTU-ε法**を採用しています。
    """)
    
    st.subheader("NTU-ε法（有効度-伝熱単位数法）")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        **伝熱単位数（NTU）の定義：**
        """)
        st.latex(r"NTU = \frac{UA}{C_{min}}")
        st.markdown("""
        - **U**: 総括熱伝達係数 [W/m²·K]
        - **A**: 伝熱面積 [m²]
        - **Cmin**: 最小熱容量流量 [W/K]
        
        **物理的意味：**
        - 熱交換器のサイズと能力の指標
        - 無次元化された熱交換能力
        """)
    
    with col2:
        st.markdown("""
        **有効度（ε）の定義：**
        """)
        st.latex(r"\varepsilon = \frac{Q_{actual}}{Q_{max}}")
        st.markdown("""
        **記号の説明：**
        - **ε**: 有効度（熱交換効率） [-]（0～1）
        - **Qactual**: 実際の熱交換量 [W]
        - **Qmax**: 理論上の最大熱交換量 [W]
        
        **対向流型の理論解：**
        """)
        st.latex(r"\varepsilon = 1 - e^{-NTU}")
        st.markdown("""
        **記号の説明：**
        - **ε**: 有効度 [-]
        - **e**: 自然対数の底（≈2.718）
        - **NTU**: 伝熱単位数 [-]
        
        （熱容量比Cr = 0の場合）
        """)
    
    st.markdown("---")
    
    # 総括熱伝達係数
    st.header("🔧 総括熱伝達係数の理論")
    st.markdown("""
    配管壁を通しての熱移動は、複数の熱抵抗の組み合わせとして扱います。
    """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("熱抵抗の直列モデル")
        st.latex(r"\frac{1}{UA} = \frac{1}{h_i A_i} + \frac{\ln(r_o/r_i)}{2\pi L k} + \frac{1}{h_o A_o}")
        st.markdown("""
        **記号の説明：**
        - **hi, ho**: 内側・外側熱伝達係数 [W/m²·K]
        - **Ai, Ao**: 内側・外側伝熱面積 [m²]
        - **ri, ro**: 内半径・外半径 [m]
        - **L**: 管長 [m]
        - **k**: 管材の熱伝導率 [W/m·K]
        
        **各項の意味：**
        - 第1項: 管内側の対流熱抵抗
        - 第2項: 管壁の伝導熱抵抗
        - 第3項: 管外側の対流熱抵抗
        """)
    
    with col2:
        st.subheader("内径基準の総括熱伝達係数")
        st.latex(r"U_i = \frac{1}{\frac{1}{h_i} + \frac{r_i \ln(r_o/r_i)}{k_{pipe}} + \frac{r_i}{r_o h_o}}")
        st.markdown("""
        **記号の説明：**
        - **Ui**: 内径基準の総括熱伝達係数 [W/m²·K]
        - **hi**: 管内側熱伝達係数 [W/m²·K]
        - **ri, ro**: 内半径・外半径 [m]
        - **kpipe**: 配管材の熱伝導率 [W/m·K]
        - **ho**: 管外側熱伝達係数 [W/m²·K]
        
        **設計上の考慮：**
        - 通常、管内側の熱抵抗が支配的
        - 管材の熱伝導率の影響は比較的小さい
        - 汚れ係数は本ツールでは考慮していない
        """)
    
    st.markdown("---")
    
    # 温度依存物性値
    st.header("🌡️ 温度依存物性値の扱い")
    st.markdown("""
    水の物性値は温度により変化します。本ツールでは、平均温度での物性値を使用しています。
    """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("プラントル数")
        st.latex(r"Pr = \frac{c_p \mu}{k} = \frac{\nu}{\alpha}")
        st.markdown("""
        **記号の説明：**
        - **Pr**: プラントル数 [-]（無次元）
        - **cp**: 定圧比熱 [J/kg·K]
        - **μ**: 動粘性係数 [Pa·s]
        - **k**: 熱伝導率 [W/m·K]
        - **ν**: 動粘度 [m²/s]
        - **α**: 熱拡散率（= k/ρcp） [m²/s]
        
        **物理的意味：**
        - 運動量拡散と熱拡散の比
        - 水の場合: Pr ≈ 7（20℃）
        - 速度境界層と温度境界層の関係を示す
        """)
    
    with col2:
        st.subheader("物性値の温度依存性")
        st.markdown("""
        **主な変化：**
        - 動粘度: 温度上昇で減少
        - 熱伝導率: わずかに増加
        - プラントル数: 温度上昇で減少
        
        **計算への影響：**
        - レイノルズ数の変化
        - ヌセルト数の変化
        - 最終的な熱伝達係数への影響
        """)
    
    st.markdown("---")
    
    # 地下水温度上昇の理論
    st.header("♨️ 地下水温度上昇の理論")
    st.markdown("""
    熱交換により地下水の温度が上昇する場合の計算方法について説明します。
    """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("エネルギー保存則の適用")
        st.markdown("""
        ボーリング孔内の地下水に対するエネルギー収支：
        """)
        st.latex(r"m_{gw} c_p \frac{dT_{gw}}{dt} = Q")
        st.markdown("""
        **記号の説明：**
        - **mgw**: 地下水質量 [kg]
        - **cp**: 比熱 [J/kg·K]
        - **Tgw**: 地下水温度 [K]
        - **t**: 時間 [s]
        - **Q**: 熱交換量 [W]
        
        **積分すると：**
        """)
        st.latex(r"\Delta T_{gw} = \frac{Q \cdot t}{m_{gw} c_p}")
        st.markdown("""
        - **ΔTgw**: 地下水温度上昇 [K]
        - **Q**: 熱交換量 [W]
        - **t**: 運転時間 [s]
        - **mgw**: 地下水質量 [kg]
        - **cp**: 比熱 [J/kg·K]
        """)
    
    with col2:
        st.subheader("循環運転時の反復計算")
        st.markdown("""
        同じ水を循環させる場合：
        
        1. **初期状態**: 入口温度 = 設定値
        2. **熱交換**: 出口温度を計算
        3. **地下水温度上昇**: ΔT計算
        4. **次サイクル**: 出口温度が新たな入口温度
        
        この過程を時間ステップごとに繰り返し、
        系が平衡状態に達するまで計算します。
        """)
    
    # 計算式のまとめ
    with st.expander("📊 本ツールで使用している計算式のまとめ"):
        st.markdown("### 主要な計算式と記号の説明")
        
        st.markdown("**1. レイノルズ数（流れの状態を表す無次元数）**")
        st.latex(r"Re = \frac{vD}{\nu}")
        st.markdown("""
        - **Re**: レイノルズ数 [-] （無次元）
        - **v**: 流速 [m/s]
        - **D**: 配管内径 [m]
        - **ν**: 動粘度 [m²/s]
        """)
        
        st.markdown("**2. ヌセルト数（熱伝達の無次元数、乱流時）**")
        st.latex(r"Nu = 0.023 \cdot Re^{0.8} \cdot Pr^{0.3}")
        st.markdown("""
        - **Nu**: ヌセルト数 [-] （無次元）
        - **Re**: レイノルズ数 [-]
        - **Pr**: プラントル数 [-] （水の熱的性質）
        - **0.023, 0.8, 0.3**: 実験的に求められた定数（Dittus-Boelter式）
        """)
        
        st.markdown("**3. 熱伝達係数の計算**")
        st.latex(r"h = \frac{Nu \cdot k}{D}")
        st.markdown("""
        - **h**: 熱伝達係数 [W/m²·K]
        - **Nu**: ヌセルト数 [-]
        - **k**: 水の熱伝導率 [W/m·K]
        - **D**: 配管内径 [m]
        """)
        
        st.markdown("**4. NTU法による効率計算**")
        st.latex(r"NTU = \frac{UA}{\dot{m}c_p}")
        st.markdown("""
        - **NTU**: 移動単位数 [-] （熱交換能力の指標）
        - **U**: 総括熱伝達係数 [W/m²·K]
        - **A**: 伝熱面積 [m²] （配管内表面積）
        - **ṁ**: 質量流量 [kg/s]
        - **cp**: 比熱 [J/kg·K]
        """)
        
        st.markdown("**5. 熱交換効率**")
        st.latex(r"\varepsilon = 1 - e^{-NTU}")
        st.markdown("""
        - **ε**: 熱交換効率 [-] （0～1の値）
        - **e**: 自然対数の底（≈2.718）
        - **NTU**: 移動単位数 [-]
        """)
        
        st.markdown("**6. 最終温度の計算**")
        st.latex(r"T_{final} = T_{initial} - \varepsilon(T_{initial} - T_{ground})")
        st.markdown("""
        - **Tfinal**: 出口温度 [℃]
        - **Tinitial**: 入口温度 [℃]
        - **Tground**: 地下水温度 [℃]
        - **ε**: 熱交換効率 [-]
        """)
        
        st.markdown("**7. 熱交換量**")
        st.latex(r"Q = \dot{m} \cdot c_p \cdot (T_{initial} - T_{final})")
        st.markdown("""
        - **Q**: 熱交換量 [W]
        - **ṁ**: 質量流量 [kg/s]
        - **cp**: 比熱 [J/kg·K]
        - **Tinitial**: 入口温度 [℃]
        - **Tfinal**: 出口温度 [℃]
        """)
        
        st.info("""
        **理論的背景**
        - 熱交換器設計の標準的な理論体系（Incropera, DeWitt等）
        - 管内流れの熱伝達相関式（Dittus-Boelter, 1930）
        - NTU-ε法（Kays and London, 1964）
        - 無次元数による整理（相似則の適用）
        """)
    
    st.markdown("---")
    
    # 理論の限界と適用範囲
    st.header("⚠️ 理論の限界と適用範囲")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("本理論の前提条件")
        st.markdown("""
        **流体力学的前提：**
        - 定常流れ
        - 十分発達した流れ
        - 非圧縮性流体
        - 一様な断面
        
        **熱的前提：**
        - 定常伝熱
        - 一定物性値（平均温度で評価）
        - 軸方向熱伝導は無視
        - 放射伝熱は無視
        """)
    
    with col2:
        st.subheader("適用範囲")
        st.markdown("""
        **レイノルズ数：**
        - 層流: Re < 2300
        - 乱流: 2300 < Re < 10⁵
        
        **プラントル数：**
        - 0.6 < Pr < 160（Dittus-Boelter式）
        
        **幾何学的制限：**
        - L/D > 60（十分発達した流れ）
        - 円管（非円形断面は別途補正要）
        """)
    
    st.header("🔍 本ツールにおける計算の前提条件")
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
    
    st.markdown("---")
    
    # フッター
    st.markdown("---")
    st.markdown("**開発者**: dobocreate | **バージョン**: 1.2.0 | **更新**: 2025-01-06")


elif page == "物性値":
    # ページ遷移時のスクロールリセット用
    if st.session_state.page_changed:
        st.empty()
    
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
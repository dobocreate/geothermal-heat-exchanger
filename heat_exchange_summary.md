# 地中熱交換システム検討結果まとめ

## 1. 検討概要

### 1.1 目的
地中熱交換システムにおいて、φ250のボーリング孔を深度10m程度実施し、鋼管を通じて初期温度30℃、総流量50L/minの循環水を送水する際の最終温度を算定する。

### 1.2 検討条件
- **初期温度**：30.0℃
- **地下水温度**：15.0℃（一定）
- **管浸水距離**：5.0m（片道）、10.0m（U字管全長）
- **総流量**：50.0 L/min
- **ボーリング孔径**：φ250mm
- **地盤条件**：砂地盤（透水係数高、地下水で満たされている）

## 2. 理論計算方法

### 2.1 基本式

#### 熱交換の基本式
```
Q = ṁ × Cp × (T_in - T_out) = U × A × ΔTLM
```

#### 効率とNTUの関係
```
ε = 1 - exp(-NTU)
T_out = T_ground + (T_in - T_ground) × (1 - ε)
```

### 2.2 Reynolds数とNusselt数

#### Reynolds数
```
Re = V × D / ν
```
- V：管内平均流速 [m/s]
- D：管内径 [m]
- ν：動粘性係数 [m²/s]

#### Nusselt数（Dittus-Boelter式、冷却）
```
Nu = 0.023 × Re^0.8 × Pr^0.3
```
- Pr：プラントル数
- 指数0.3は冷却の場合（管壁温度 < 流体温度）

### 2.3 熱伝達係数

#### 管内側熱伝達係数
```
h_i = Nu × k / D
```

#### 総括伝熱係数
```
1/U = 1/h_i + (d_i/(2×k_pipe)) × ln(d_o/d_i) + d_i/(d_o×h_o)
```
- h_o：管外側熱伝達係数 = 300 W/(m²·K)（静止水中の自然対流）

### 2.4 NTU（伝熱単位数）
```
NTU = U × A / (ṁ × Cp)
```
- A：伝熱面積 = π × D × L

## 3. 物性値（22.5℃）

| 物性値 | 記号 | 値 | 単位 |
|--------|------|-----|------|
| 密度 | ρ | 997.6 | kg/m³ |
| 動粘性係数 | ν | 0.949×10⁻⁶ | m²/s |
| 熱伝導率 | k | 0.603 | W/(m·K) |
| 比熱 | Cp | 4181 | J/(kg·K) |
| プラントル数 | Pr | 6.57 | - |

### 温度による物性値の変化

| 温度[℃] | ρ[kg/m³] | ν[×10⁻⁶m²/s] | k[W/(m·K)] | Cp[J/kgK] | Pr[-] |
|---------|----------|---------------|------------|-----------|-------|
| 15 | 999.1 | 1.139 | 0.589 | 4186 | 8.09 |
| 20 | 998.2 | 1.004 | 0.598 | 4182 | 7.01 |
| **22.5** | **997.6** | **0.949** | **0.603** | **4181** | **6.57** |
| 25 | 997.0 | 0.893 | 0.607 | 4179 | 6.13 |
| 30 | 995.6 | 0.801 | 0.615 | 4178 | 5.42 |

## 4. 計算結果

### 4.1 管径別・材質別最終温度（22.5℃）

| 管径 | 鋼管[℃] | アルミ管[℃] | 銅管[℃] | 最適材質 |
|------|----------|-------------|----------|----------|
| 15A | 27.18 | 27.14 | 27.14 | 銅管 |
| **32A** | **25.82** | **25.75** | **25.74** | **銅管（最適）** |
| 40A | 27.28 | 27.22 | 27.21 | 銅管 |
| 50A | 26.99 | 26.93 | 26.93 | 銅管 |
| 65A | 27.97 | 27.91 | 27.91 | 銅管 |
| 80A | 27.83 | 27.77 | 27.76 | 銅管 |

### 4.2 32A鋼管の詳細計算結果

| 項目 | 記号 | 値 | 単位 |
|------|------|-----|------|
| 管内径 | D | 33.5 | mm |
| 流速 | V | 0.236 | m/s |
| Reynolds数 | Re | 8,344 | - |
| Nusselt数 | Nu | 55.5 | - |
| 管内側熱伝達係数 | h_i | 999 | W/(m²·K) |
| 総括伝熱係数 | U | 269.8 | W/(m²·K) |
| NTU | NTU | 0.327 | - |
| 最終温度 | T_out | 25.82 | ℃ |
| 温度降下 | ΔT | 4.18 | ℃ |
| 熱交換量(全体) | Q_total | 29.1 | kW |
| 効率 | η | 27.9 | % |

### 4.3 全管径の主要計算結果（22.5℃、鋼管）

| 管径 | 流速[m/s] | Re数 | h_i[W/m²K] | U[W/m²K] | NTU | T_out[℃] | 効率[%] |
|------|-----------|------|------------|----------|-----|----------|---------|
| 15A | 1.023 | 17,361 | 3,734 | 358 | 0.208 | 27.18 | 18.8 |
| **32A** | **0.236** | **8,344** | **999** | **270** | **0.327** | **25.82** | **27.9** |
| 40A | 0.365 | 14,673 | 1,379 | 291 | 0.200 | 27.28 | 18.1 |
| 50A | 0.217 | 11,293 | 861 | 250 | 0.224 | 26.99 | 20.0 |
| 65A | 0.275 | 18,004 | 997 | 259 | 0.145 | 27.97 | 13.5 |
| 80A | 0.203 | 15,464 | 758 | 239 | 0.156 | 27.83 | 14.4 |

## 5. 管径による効率の違いの分析

### 5.1 なぜ32Aが最適なのか

#### 15Aと32Aの比較

| 項目 | 15A | 32A | 比率(32A/15A) |
|------|-----|-----|---------------|
| 管内径 [mm] | 16.1 | 33.5 | 2.08 |
| 流速 [m/s] | 1.023 | 0.236 | 0.23 |
| 滞留時間 [秒] | 9.8 | 42.4 | **4.33** |
| h_i [W/m²K] | 3,734 | 999 | 0.27 |
| U [W/m²K] | 357.9 | 269.8 | 0.75 |
| 伝熱面積 [m²] | 0.506 | 1.052 | **2.08** |
| NTU | 0.208 | 0.327 | **1.57** |
| 温度降下 [℃] | 2.82 | 4.18 | 1.48 |

**32Aが優れている理由**：
1. 伝熱面積が2.08倍に増加
2. 滞留時間が4.33倍に増加
3. NTUが1.57倍となり、熱交換効率が向上

#### 32Aと40Aの比較

| 項目 | 32A | 40A | 比率(40A/32A) |
|------|-----|-----|---------------|
| 1本流量 [L/min] | 12.5 | 25.0 | **2.00** |
| 流速 [m/s] | 0.236 | 0.365 | 1.55 |
| 滞留時間 [秒] | 42.3 | 27.4 | **0.65** |
| NTU（1本） | 0.327 | 0.200 | **0.61** |
| 効率 [%] | 27.9 | 18.1 | 0.65 |

**40Aが劣る理由**：
1. 1本あたりの流量が2倍（熱容量流量が増加）
2. 伝熱面積は1.14倍しか増えない
3. NTUが大幅に低下（0.327→0.200）

### 5.2 流速と熱交換効率の関係

**流速が遅い方が効率的な理由**：
1. **滞留時間の増加効果 ＞ 熱伝達係数の低下効果**
2. 低NTU領域（0.2～0.5）では滞留時間の影響が大きい
3. 32Aは適切な流量と十分な滞留時間のバランスが最適

## 6. 設計上の推奨事項

### 6.1 現状での結論
- **最適条件**：32A銅管
- **達成温度**：25.74℃
- **効率**：28.0%
- **目標温度（22-23℃）との差**：約3℃

### 6.2 目標温度達成のための方策

#### 方法1：管長の延長
- 現状：10m（片道5m×2）
- 必要：約20m（片道10m×2）
- 効果：最終温度22-23℃を達成可能

#### 方法2：管外側の対流促進
- 現状：h_o = 300 W/(m²·K)（静止水）
- 改善：h_o = 1000 W/(m²·K)（強制対流）
- 方法：地下水の循環システム導入

#### 方法3：管径・本数の最適化
- より多数の32A管を使用
- 並列配置による総伝熱面積の増加

### 6.3 実務上の留意点

1. **施工性**：32Aは15Aより施工が容易
2. **圧力損失**：流速が遅いため圧力損失は小さい
3. **経済性**：材質による温度差は0.1℃程度なので鋼管で十分
4. **メンテナンス**：適切な流速により管内の汚れ付着を防止

## 7. 計算の妥当性

### 7.1 採用した物性値
- 平均温度22.5℃での物性値を使用
- 理論値との誤差：1%以内
- 温度依存性による誤差：±10%程度

### 7.2 熱伝達係数の設定
- **h_i**：理論計算（Dittus-Boelter式、冷却n=0.3）
- **h_o**：300 W/(m²·K)（静止水中の自然対流として妥当）

### 7.3 計算手法
- U字管全体を一つの熱交換器として計算
- ε-NTU法による効率計算
- 地下水温度一定の仮定は妥当（大量の地下水）

## 8. まとめ

1. **32A銅管が最適**（最終温度25.74℃）
2. 目標温度22-23℃達成には追加対策が必要
3. 流速と滞留時間のバランスが重要
4. 材質の影響は小さく、管径の選択が最重要
# 地中熱交換システム計算ツール

地中熱交換システムの性能計算と最適化を行うStreamlitアプリケーションです。

## 概要

このツールは、地中熱交換システムにおける循環水の温度変化を計算し、最適な配管径や材質を提案します。

### 主な機能

- 熱交換効率の計算（ε-NTU法）
- Reynolds数、Nusselt数の自動計算
- 配管径・材質別の性能比較
- インタラクティブな結果表示
- 最適化提案の自動生成

## 必要条件

- Python 3.8以上
- pip (Pythonパッケージマネージャー)

## インストール

1. リポジトリをクローン
```bash
git clone https://github.com/[your-username]/geothermal-heat-exchanger.git
cd geothermal-heat-exchanger
```

2. 仮想環境の作成（推奨）
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

## 使用方法

1. アプリケーションの起動
```bash
streamlit run app.py
```

2. ブラウザが自動的に開き、アプリケーションが表示されます
3. サイドバーで計算条件を入力
4. リアルタイムで計算結果が表示されます

## 計算理論

本ツールは以下の理論に基づいて計算を行います：

- 熱交換の基本式: Q = ṁ × Cp × ΔT
- Dittus-Boelter式によるNusselt数計算
- ε-NTU法による熱交換効率計算

詳細は[heat_exchange_summary.md](heat_exchange_summary.md)を参照してください。

## プロジェクト構造

```
geothermal-heat-exchanger/
├── app.py                    # Streamlitメインアプリケーション
├── calculations/             # 計算モジュール
│   ├── __init__.py
│   ├── heat_exchanger.py     # 熱交換計算
│   ├── fluid_properties.py   # 流体物性値
│   └── pipe_database.py      # 配管データベース
├── utils/                    # ユーティリティ
│   └── visualization.py      # グラフ作成
├── tests/                    # テストコード
├── requirements.txt          # 依存パッケージ
└── README.md                 # このファイル
```

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを作成して変更内容を議論してください。

## 作者

[Your Name]
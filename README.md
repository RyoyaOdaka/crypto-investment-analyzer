# 🚀 Crypto Investment Analyzer

仮想通貨投資分析アプリ - リアルタイム価格追跡、AI投資分析、バックテスト、取引シミュレーター

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

## ✨ 主要機能

### 📈 リアルタイム価格追跡
- トップ10仮想通貨の価格表示
- 24時間変動率のリアルタイム更新
- CoinGecko API統合

### 📊 インタラクティブチャート
- 複数期間選択（24時間、7日、30日、90日、1年）
- Rechartsによる美しい可視化
- 5分ごとの自動更新

### 💼 ポートフォリオ管理
- 実際の保有資産の追加・削除
- リアルタイム損益計算
- 購入価格と現在価格の比較

### 🤖 AI投資分析
テクニカル指標に基づく投資推奨システム

**基本指標:**
- RSI (相対力指数)
- ボラティリティ
- トレンド分析
- 価格変動率（7日・30日）

**高度なテクニカル指標:**
- **MACD (移動平均収束拡散)**
  - ゴールデンクロス/デッドクロス検出
  - MACDライン、シグナルライン、ヒストグラム

- **ボリンジャーバンド**
  - 上限・中央・下限バンド計算
  - 価格位置判定（上限上/下限下/上半分/下半分）

**推奨スコアリング:**
- 0-100点のスコアリングシステム
- 強い買い/買い/様子見/売り の4段階推奨
- リスクレベル評価（低/中/高）

### 🔄 バックテスト機能
過去データで取引戦略をシミュレーション

**対応戦略:**
- RSI売られすぎ/買われすぎ戦略
- MACDゴールデンクロス/デッドクロス戦略
- ボリンジャーバンド上限/下限突破戦略

**パフォーマンス指標:**
- 総リターン・リターン率
- 勝率（勝ち/負けトレード）
- 最大ドローダウン
- シャープレシオ
- 平均利益/取引

**可視化:**
- 資産曲線チャート
- 取引履歴テーブル
- パフォーマンスダッシュボード

### 💰 取引シミュレーター
仮想資金でリスクなく取引の練習

**機能:**
- 複数の仮想ポートフォリオ作成
- 初期資金の自由設定（デフォルト$10,000）
- リアルタイム価格での仮想売買
- 8種類の仮想通貨対応（BTC, ETH, BNB, XRP, ADA, SOL, DOT, DOGE）

**自動計算:**
- 平均取得単価の自動計算
- リアルタイム損益計算
- 残高・保有数量チェック
- 10秒ごとの価格更新

## 🛠 技術スタック

### バックエンド
- **FastAPI** - 高速非同期Webフレームワーク
- **PostgreSQL 16** - リレーショナルデータベース
- **Redis 7** - キャッシングレイヤー
- **SQLAlchemy** - 非同期ORM
- **Pydantic** - データバリデーション
- **httpx** - 非同期HTTPクライアント

### フロントエンド
- **React 18** - UIライブラリ
- **TypeScript** - 型安全性
- **Vite** - ビルドツール
- **React Query** - データフェッチング・キャッシング
- **Recharts** - チャート可視化
- **Tailwind CSS** - CSSフレームワーク
- **Axios** - HTTPクライアント

### インフラ
- **Docker & Docker Compose** - コンテナ化
- **CoinGecko API** - 仮想通貨データソース

## 🚀 クイックスタート

### 前提条件
- Docker & Docker Compose
- Git

### インストール

1. リポジトリをクローン
```bash
git clone https://github.com/RyoyaOdaka/crypto-investment-analyzer.git
cd crypto-investment-analyzer
```

2. Docker Composeで起動
```bash
docker-compose up -d
```

3. ブラウザでアクセス
- フロントエンド: http://localhost:5173
- バックエンドAPI: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs

### 環境変数
バックエンドの環境変数は `backend/.env` で設定可能:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/crypto_db
REDIS_URL=redis://redis:6379/0
DEBUG=True
```

## 📁 プロジェクト構成

```
crypto-investment-analyzer/
├── backend/
│   ├── app/
│   │   ├── api/              # APIエンドポイント
│   │   │   ├── crypto.py         # 価格・チャートAPI
│   │   │   ├── portfolio.py      # ポートフォリオAPI
│   │   │   ├── analysis.py       # 投資分析API
│   │   │   ├── backtest.py       # バックテストAPI
│   │   │   └── virtual_portfolio.py  # 取引シミュレーターAPI
│   │   ├── core/             # コア設定
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/           # データベースモデル
│   │   │   ├── portfolio.py
│   │   │   └── virtual_portfolio.py
│   │   ├── schemas/          # Pydanticスキーマ
│   │   │   ├── analysis.py
│   │   │   ├── backtest.py
│   │   │   └── virtual_portfolio.py
│   │   ├── services/         # ビジネスロジック
│   │   │   ├── crypto_service.py      # CoinGecko API統合
│   │   │   ├── redis_service.py       # Redisキャッシング
│   │   │   ├── analysis_service.py    # テクニカル分析
│   │   │   ├── backtest_service.py    # バックテストエンジン
│   │   │   └── virtual_portfolio_service.py
│   │   └── main.py           # アプリケーションエントリポイント
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/       # Reactコンポーネント
│   │   │   ├── TopCryptos.tsx          # 価格リスト
│   │   │   ├── CryptoChart.tsx         # チャート
│   │   │   ├── Portfolio.tsx           # ポートフォリオ管理
│   │   │   ├── InvestmentAnalysis.tsx  # AI投資分析
│   │   │   ├── Backtest.tsx            # バックテスト
│   │   │   └── TradingSimulator.tsx    # 取引シミュレーター
│   │   ├── services/
│   │   │   └── api.ts        # API クライアント
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── Dockerfile
│   └── package.json
│
└── docker-compose.yml
```

## 📊 API エンドポイント

### 仮想通貨価格
- `GET /api/v1/crypto/price/{symbol}` - 個別通貨の価格取得
- `GET /api/v1/crypto/top?limit=10` - トップ通貨リスト
- `GET /api/v1/crypto/chart/{symbol}?days=7` - チャートデータ

### 投資分析
- `GET /api/v1/analysis/recommendations?limit=10` - 推奨リスト
- `GET /api/v1/analysis/recommend/{symbol}` - 個別通貨の分析

### バックテスト
- `POST /api/v1/backtest/run` - バックテスト実行
- `GET /api/v1/backtest/strategies` - 利用可能な戦略リスト

### ポートフォリオ
- `GET /api/v1/portfolio/` - ポートフォリオ一覧
- `POST /api/v1/portfolio/` - ポートフォリオ追加
- `DELETE /api/v1/portfolio/{id}` - ポートフォリオ削除

### 取引シミュレーター
- `POST /api/v1/virtual-portfolio/` - 仮想ポートフォリオ作成
- `GET /api/v1/virtual-portfolio/{id}/summary` - サマリー取得
- `POST /api/v1/virtual-portfolio/trade` - 仮想取引実行
- `GET /api/v1/virtual-portfolio/{id}/transactions` - 取引履歴

詳細なAPIドキュメント: http://localhost:8000/docs

## 🔧 開発

### バックエンド開発
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### フロントエンド開発
```bash
cd frontend
npm install
npm run dev
```

### データベースマイグレーション
テーブルは自動作成されます（`init_db()`）

## 🧪 テクニカル分析アルゴリズム

### RSI (Relative Strength Index)
```python
def calculate_rsi(prices: List[float], period: int = 14) -> float:
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas[-period:]]
    losses = [-d if d < 0 else 0 for d in deltas[-period:]]

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
```

### MACD
```python
def calculate_macd(prices: List[float]) -> MACDIndicator:
    ema_12 = calculate_ema(prices, 12)
    ema_26 = calculate_ema(prices, 26)
    macd_line = ema_12[-1] - ema_26[-1]
    signal_line = calculate_ema(macd_line_values, 9)[-1]
    histogram = macd_line - signal_line

    # ゴールデンクロス/デッドクロス検出
    if prev_histogram < 0 and histogram > 0:
        signal = "buy"
    elif prev_histogram > 0 and histogram < 0:
        signal = "sell"

    return MACDIndicator(macd_line, signal_line, histogram, signal)
```

### ボリンジャーバンド
```python
def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: int = 2):
    middle_band = sma(prices[-period:])
    std = standard_deviation(prices[-period:])
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)

    # 価格位置判定
    if current_price > upper_band:
        position = "above_upper"
    elif current_price > middle_band:
        position = "upper_half"
    elif current_price > lower_band:
        position = "lower_half"
    else:
        position = "below_lower"

    return BollingerBands(upper_band, middle_band, lower_band, position)
```

## 📈 バックテスト例

### RSI Reversal戦略（90日間）
```json
{
  "symbol": "BTC",
  "strategy": {
    "name": "RSI Reversal",
    "buy_signal": "rsi_oversold",
    "sell_signal": "rsi_overbought",
    "initial_capital": 10000.0,
    "trade_size_percent": 100.0
  },
  "period_days": 90
}
```

**結果:**
- 総リターン: +$1,960 (+19.6%)
- 勝率: 66.67%
- 取引回数: 3回
- 最大ドローダウン: -3.8%
- シャープレシオ: 0.85

## 🎯 使い方

1. **価格チェック**: リアルタイムでトップ10通貨の価格を確認
2. **投資分析**: AI推奨スコアで投資候補を発見
3. **バックテスト**: 戦略を過去データで検証
4. **取引練習**: シミュレーターで実際の取引を練習
5. **ポートフォリオ追跡**: 実際の保有資産の損益を管理

## ⚠️ 免責事項

このアプリケーションは教育・学習目的で作成されています。

- 提供される投資推奨は参考情報であり、投資助言ではありません
- 実際の投資判断は自己責任で行ってください
- 過去のパフォーマンスは将来の結果を保証するものではありません
- 仮想通貨投資にはリスクが伴います

## 📝 ライセンス

MIT License

## 👨‍💻 作者

Created with [Claude Code](https://claude.com/claude-code)

---

⭐ 気に入ったらスターをお願いします！

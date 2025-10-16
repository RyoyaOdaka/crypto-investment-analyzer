# 仮想通貨投資分析アプリ

仮想通貨に関する投資分析を補助するWebアプリケーション

## 技術スタック

### フロントエンド
- React + TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- Recharts

### バックエンド
- FastAPI (Python 3.12+)
- PostgreSQL
- Redis
- SQLAlchemy
- Alembic

### インフラ
- Docker & Docker Compose

## 開発環境のセットアップ

```bash
# リポジトリのクローン
git clone <repository-url>
cd GeoLocater

# Docker Composeで起動
docker-compose up -d

# フロントエンド: http://localhost:5173
# バックエンドAPI: http://localhost:8000
# API ドキュメント: http://localhost:8000/docs
```

## プロジェクト構造

```
.
├── backend/           # FastAPI バックエンド
│   └── app/
│       ├── api/       # APIエンドポイント
│       ├── core/      # 設定・共通機能
│       ├── models/    # データベースモデル
│       ├── schemas/   # Pydanticスキーマ
│       └── services/  # ビジネスロジック
├── frontend/          # React フロントエンド
└── docker-compose.yml
```

## 主な機能（予定）

- 仮想通貨価格のリアルタイム表示
- 価格チャートの可視化
- テクニカル指標の計算
- ポートフォリオ管理
- 損益計算
- 価格アラート機能

## ライセンス

MIT

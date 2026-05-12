# コインパーキング営業支援ツール

図面アップロード → AI解析 → 相場調査 → 収支試算 → 提案資料作成

## ローカル起動

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-xxxxx
uvicorn main:app --reload
# → http://localhost:8000
```

## Renderへのデプロイ手順

1. [GitHub](https://github.com) で新しいリポジトリを作成
2. このフォルダの内容をpush
   ```bash
   git init
   git add .
   git commit -m "initial commit"
   git remote add origin https://github.com/YOUR_NAME/parking-tool.git
   git push -u origin main
   ```
3. [Render.com](https://render.com) でアカウント作成（無料）
4. Dashboard → **New** → **Web Service**
5. GitHubリポジトリを連携して選択
6. 設定：
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. **Environment Variables** に追加：
   - Key: `ANTHROPIC_API_KEY`
   - Value: `sk-ant-あなたのAPIキー`
8. **Create Web Service** をクリック → 数分でURLが発行される

## ファイル構成

```
parking-app/
├── main.py              # FastAPI バックエンド（APIエンドポイント）
├── requirements.txt     # 依存パッケージ
├── render.yaml          # Render設定
├── templates/
│   └── index.html       # フロントエンド（全ステップ）
└── static/              # 静的ファイル置き場
```

## APIエンドポイント

| パス | メソッド | 説明 |
|------|---------|------|
| `/` | GET | メイン画面 |
| `/api/analyze-floorplan` | POST | 図面解析（画像またはデモ） |
| `/api/market-research` | POST | 周辺相場調査 |
| `/api/finance` | POST | 収支試算 |
| `/api/proposal` | POST | 提案資料生成 |

# 契約管理 API（Backend）

日々の契約（携帯電話・電気・ガス・保険など）を管理する FastAPI バックエンドです。

| 項目 | 内容 |
|------|------|
| フレームワーク | FastAPI |
| API ベースパス | `/api/v1/contract` |
| 仕様書 | リポジトリルートの `API_CONTRACT.md` |

---

## 前提条件

- Python 3.12 以上（推奨）
- PostgreSQL（`public.accounts` テーブルが存在すること）
- 契約管理用スキーマ（`DB/1_db.sql` を実行済みであること）

---

## セットアップ

### 1. 仮想環境の作成と依存パッケージのインストール

`backend` フォルダで実行します。

```powershell
cd backend
python -m venv env
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. データベースの準備

PostgreSQL に接続し、契約管理スキーマを作成します（未作成の場合）。

```powershell
psql -U tamtuser -d tamtdb -f ..\DB\1_db.sql
```

### 3. 環境変数（`.env`）

`backend/.env` に接続情報などを設定します。初回は以下を参考に作成してください。

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tamtdb
DB_USER=tamtuser
DB_PASSWORD=TAMTTAMT

# JWT（認証 API と同一の値を設定）
SECRET_KEY=change-me-to-same-as-auth-api
ALGORITHM=HS256
COOKIE_NAME=access_token
CORS_ORIGINS=

# デバッグ環境（true の場合 JWT を使わず DEBUG_AID をユーザー ID とする）
DEBUG=true
DEBUG_AID=1

# ファイルストレージ
STORAGE_PATH=storage
MAX_UPLOAD_SIZE=10485760
```

| 環境変数 | 説明 |
|----------|------|
| `DB_HOST` | DB ホスト |
| `DB_PORT` | DB ポート |
| `DB_NAME` | データベース名 |
| `DB_USER` | DB ユーザー名 |
| `DB_PASSWORD` | DB パスワード |
| `SECRET_KEY` | JWT 署名用秘密鍵（認証 API と同一） |
| `ALGORITHM` | JWT アルゴリズム（既定: `HS256`） |
| `COOKIE_NAME` | JWT Cookie 名（既定: `access_token`） |
| `CORS_ORIGINS` | 許可オリジン（カンマ区切り。未設定時は CORS ミドルウェア無効） |
| `DEBUG` | `true` のときデバッグモード |
| `DEBUG_AID` | デバッグモード時に使用するユーザー ID（`public.accounts.id`） |
| `STORAGE_PATH` | 契約書ファイルの保存先（既定: `storage`） |
| `MAX_UPLOAD_SIZE` | アップロード上限バイト数（既定: 10MB） |

---

## 起動方法

仮想環境を有効化したうえで、`backend` フォルダから起動します。

```powershell
cd backend
.\env\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

起動確認:

```powershell
curl http://localhost:8000/health
```

レスポンス例:

```json
{ "status": "ok" }
```

インポート確認:

```powershell
python -c "from app.main import app; print('OK', len(app.routes))"
```

---

## 認証

### 本番・結合環境（`DEBUG=false`）

認証 API（`m_login`）が発行した JWT を **HttpOnly Cookie** で受け取り、ユーザー ID（`aid`）を特定します。

- Cookie 名: `COOKIE_NAME`（既定 `access_token`）
- JWT の `username` クレームで `public.accounts` を検索し、`id` を `aid` として使用
- `SECRET_KEY`・`ALGORITHM`・`COOKIE_NAME` は認証 API と **同一** にすること

フロントエンドから呼ぶ場合は `withCredentials: true`（axios）が必要です。

### デバッグ環境（`DEBUG=true`）

JWT 検証をスキップし、`.env` の `DEBUG_AID` をそのままユーザー ID として使います。ローカル開発向けです。**本番では必ず `DEBUG=false` にしてください。**

---

## API ドキュメント

サーバー起動後、ブラウザで OpenAPI ドキュメントを参照できます。

| URL | 内容 |
|-----|------|
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |

---

## 主なエンドポイント

ベースパス: `/api/v1/contract`

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/categories` | カテゴリ一覧 |
| POST | `/categories` | カテゴリ作成 |
| PUT | `/categories/{category_id}` | カテゴリ更新 |
| DELETE | `/categories/{category_id}` | カテゴリ削除（論理削除） |
| GET | `/contracts` | 契約一覧 |
| POST | `/contracts` | 契約作成 |
| GET | `/contracts/{contract_id}` | 契約詳細 |
| PUT | `/contracts/{contract_id}` | 契約更新 |
| DELETE | `/contracts/{contract_id}` | 契約削除（論理削除） |
| GET | `/contracts/{contract_id}/credentials` | 認証情報一覧 |
| POST | `/contracts/{contract_id}/credentials` | 認証情報追加 |
| PUT | `/contracts/{contract_id}/credentials/{credential_id}` | 認証情報更新 |
| DELETE | `/contracts/{contract_id}/credentials/{credential_id}` | 認証情報削除 |
| GET | `/contracts/{contract_id}/credentials/{credential_id}/reveal` | パスワード等の復号表示 |
| GET | `/contracts/{contract_id}/contacts` | 連絡先一覧 |
| POST | `/contracts/{contract_id}/contacts` | 連絡先追加 |
| PUT | `/contracts/{contract_id}/contacts/{contact_id}` | 連絡先更新 |
| DELETE | `/contracts/{contract_id}/contacts/{contact_id}` | 連絡先削除 |
| GET | `/contracts/{contract_id}/attachments` | 契約書ファイル一覧 |
| POST | `/contracts/{contract_id}/attachments` | ファイルアップロード |
| PUT | `/contracts/{contract_id}/attachments/{attachment_id}` | ファイル情報更新 |
| DELETE | `/contracts/{contract_id}/attachments/{attachment_id}` | ファイル削除 |
| GET | `/contracts/{contract_id}/attachments/{attachment_id}/download` | ファイルダウンロード |
| GET | `/dashboard` | ダッシュボード集計 |

詳細は `API_CONTRACT.md` を参照してください。

---

## 使用例（デバッグモード）

`DEBUG=true`・`DEBUG_AID=1` の状態で、カテゴリ一覧を取得する例です。

```powershell
curl http://localhost:8000/api/v1/contract/categories
```

カテゴリ作成:

```powershell
curl -X POST http://localhost:8000/api/v1/contract/categories `
  -H "Content-Type: application/json" `
  -d '{"name": "携帯電話", "icon": "phone", "sort_order": 10}'
```

---

## ファイルストレージ

契約書 PDF や画像（JPEG / PNG / WebP）を `STORAGE_PATH` 配下に保存します。

保存パス形式:

```
storage/{aid}/{contract_id}/{uuid}_{ファイル名}
```

- DB の `contract.attachments` にはメタデータのみ保持
- 削除時は DB を論理削除し、ストレージ上の実ファイルも削除

---

## プロジェクト構成

```
backend/
  .env                 # 環境変数
  requirements.txt     # 依存パッケージ
  readme.md            # 本ファイル
  storage/             # 契約書ファイル（自動作成）
  app/
    main.py            # FastAPI エントリポイント
    config.py          # 設定読み込み
    database.py        # DB 接続
    deps.py            # 認証（aid 取得）
    models.py          # SQLAlchemy モデル
    exceptions.py      # エラーハンドラ
    api/v1/contract/   # API ルーター
    schemas/           # Pydantic スキーマ
    services/          # ビジネスロジック
    security/          # JWT 検証
```

---

## トラブルシューティング

### `ModuleNotFoundError: No module named 'pydantic_settings'`

仮想環境が有効化されていない、または依存パッケージ未インストールです。

```powershell
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
```

### DB 接続エラー

`.env` の DB 接続情報と PostgreSQL の起動状態を確認してください。`DB/1_db.sql` が実行済みかも確認します。

### 401 Unauthorized（`DEBUG=false` 時）

- 認証 API でログイン済みか
- Cookie がリクエストに含まれているか
- `SECRET_KEY` が認証 API と一致しているか

を確認してください。

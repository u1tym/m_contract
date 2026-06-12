# 契約管理フロントエンド

Vue 3 + TypeScript + Vite で構築した契約管理 UI です。

## 前提

- バックエンド API（`backend/`）が起動していること
- ログインは別画面（`f_login`）で行う想定。本アプリにログイン UI はありません

## セットアップ

```powershell
cd frontend
npm install
```

## 環境変数

`.env` を編集します。

| 変数 | 説明 |
|------|------|
| `VITE_CONTRACT_ORIGIN` | 本番ビルド時の契約 API 起点（例: `https://host/api/v1/contract`） |
| `VITE_LOGIN_ORIGIN` | 本番ビルド時の認証 API 起点（例: `https://host/api/auth`） |
| `VITE_DEBUG` | `true` のときセッション延長（`POST /refresh`）をスキップ |

開発時（`npm run dev`）は Vite プロキシを使用し、契約 API は `http://127.0.0.1:8000` に転送されます。

## 起動

```powershell
npm run dev
```

ブラウザで表示された URL（通常 `http://localhost:5173/mobile/contract/`）を開きます。

## ビルド

```powershell
npm run build
```

## 機能

- 契約一覧（契約中 / 終了 / 指定日フィルタ / カテゴリ・キーワード / 削除済み含む）
- 契約詳細・新規作成・編集・論理削除・復元
- 契約終了（`status=cancelled` + 終了日）— 削除とは別操作
- 認証情報・連絡先・契約書ファイルの管理
- カテゴリ管理

## セッション延長

本番（`VITE_DEBUG=false`）では、契約 API 呼び出し前に `POST {VITE_LOGIN_ORIGIN}/refresh` を実行します。

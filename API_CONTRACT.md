# 契約管理 API 設計仕様書

## 概要

契約管理フロントエンド向けの REST API 仕様。バックエンドは Python + FastAPI で実装する。

| 項目 | 内容 |
|------|------|
| ベースパス | `/api/v1/contract` |
| 認証 | バックエンドでログインユーザー（`aid` = `public.accounts.id`）を判別済み。リクエスト・レスポンスにユーザー情報は含めない |
| データ形式 | JSON（`Content-Type: application/json`）。ファイルアップロードは `multipart/form-data` |
| 日付形式 | ISO 8601 日付 `YYYY-MM-DD` |
| 日時形式 | ISO 8601 `YYYY-MM-DDTHH:MM:SS+09:00` |

---

## 共通仕様

### 認証・認可

- すべてのエンドポイントは認証必須とする。
- バックエンドはセッションまたはトークンから `aid`（`public.accounts.id`）を取得し、DB アクセス時に自動的に `aid` フィルタを適用する。
- 認証時は `public.accounts.is_deleted = false` のアカウントのみ有効とする。
- 他ユーザーのデータへのアクセスは `404 Not Found` を返す（存在を漏らさない）。

### 共通レスポンスヘッダー

```
Content-Type: application/json; charset=utf-8
```

ファイルダウンロード時:

```
Content-Type: {content_type}
Content-Disposition: attachment; filename="{file_name}"
```

### エラーレスポンス形式

```json
{
  "detail": "エラーメッセージ",
  "code": "ERROR_CODE"
}
```

バリデーションエラー（422）の場合は FastAPI 標準形式:

```json
{
  "detail": [
    {
      "loc": ["body", "provider_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### HTTP ステータスコード

| コード | 用途 |
|--------|------|
| `200` | 取得成功・更新成功 |
| `201` | 作成成功 |
| `204` | 削除成功（ボディなし） |
| `400` | リクエスト不正 |
| `404` | リソース未存在 |
| `409` | 競合（重複等） |
| `413` | ファイルサイズ超過 |
| `422` | バリデーションエラー |
| `500` | サーバー内部エラー |

### ページネーション（一覧系）

クエリパラメータ:

| パラメータ | 型 | デフォルト | 説明 |
|-----------|-----|-----------|------|
| `page` | int | `1` | ページ番号（1 始まり） |
| `per_page` | int | `20` | 1 ページあたり件数（最大 100） |

レスポンス共通ラッパー:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "per_page": 20,
  "total_pages": 0
}
```

### 列挙型（Enum）

#### ContractStatus

| 値 | 表示名 |
|----|--------|
| `active` | 契約中 |
| `suspended` | 一時停止 |
| `cancelled` | 解約済み |
| `pending` | 手続き中 |

#### PaymentCycle

| 値 | 表示名 |
|----|--------|
| `monthly` | 月額 |
| `yearly` | 年額 |
| `quarterly` | 四半期 |
| `biannual` | 半年 |
| `one_time` | 一括 |
| `other` | その他 |

#### CredentialType

| 値 | 表示名 |
|----|--------|
| `login_id` | ログイン ID |
| `password` | パスワード |
| `pin` | 暗証番号 |
| `customer_number` | お客様番号 |
| `email` | メールアドレス |
| `phone` | 電話番号 |
| `api_key` | API キー |
| `other` | その他 |

#### ContactType

| 値 | 表示名 |
|----|--------|
| `phone` | 電話 |
| `email` | メール |
| `url` | URL |
| `address` | 住所 |
| `other` | その他 |

---

## データモデル（API スキーマ）

### Category

```json
{
  "id": 1,
  "name": "携帯電話",
  "icon": "phone",
  "sort_order": 10
}
```

### Payment（契約に内包）

契約の一部として返却する。独立したリソース ID は持たない。

```json
{
  "amount": "5980.00",
  "currency": "JPY",
  "payment_cycle": "monthly",
  "payment_day": 27,
  "payment_method": "クレジットカード",
  "is_tax_included": true,
  "payment_notes": null
}
```

> `amount` は文字列で返却（精度保持のため）。リクエストも文字列または数値を受け付ける。

### Credential

```json
{
  "id": 1,
  "credential_type": "login_id",
  "label": "マイページ",
  "value": "user@example.com",
  "url": "https://example.com/login",
  "notes": null,
  "sort_order": 0
}
```

パスワード一覧取得時のマスク例:

```json
{
  "id": 2,
  "credential_type": "password",
  "label": "マイページ",
  "value": "********",
  "is_masked": true,
  "url": "https://example.com/login",
  "notes": null,
  "sort_order": 1
}
```

### Contact

```json
{
  "id": 1,
  "contact_type": "phone",
  "label": "カスタマーセンター",
  "value": "0120-000-000",
  "notes": "平日 9:00-18:00",
  "sort_order": 0
}
```

### Attachment

```json
{
  "id": 1,
  "file_name": "契約書_2024.pdf",
  "content_type": "application/pdf",
  "file_size": 1048576,
  "description": "契約書 2024 年版",
  "sort_order": 0,
  "created_at": "2026-01-15T09:00:00+09:00"
}
```

### ContractSummary（一覧用）

```json
{
  "id": 1,
  "category": {
    "id": 1,
    "name": "携帯電話",
    "icon": "phone"
  },
  "provider_name": "NTTドコモ",
  "contract_name": "ファミリープラン",
  "status": "active",
  "start_date": "2024-04-01",
  "end_date": null,
  "amount": "5980.00",
  "payment_cycle": "monthly",
  "monthly_amount": "5980.00",
  "credential_count": 2,
  "attachment_count": 1,
  "updated_at": "2026-06-01T10:30:00+09:00"
}
```

### ContractDetail（詳細用）

```json
{
  "id": 1,
  "category_id": 1,
  "category": {
    "id": 1,
    "name": "携帯電話",
    "icon": "phone"
  },
  "provider_name": "NTTドコモ",
  "contract_name": "ファミリープラン",
  "contract_number": "1234567890",
  "status": "active",
  "start_date": "2024-04-01",
  "end_date": null,
  "renewal_date": "2027-03-31",
  "auto_renewal": true,
  "notes": "家族3回線",
  "payment": {
    "amount": "5980.00",
    "currency": "JPY",
    "payment_cycle": "monthly",
    "payment_day": 27,
    "payment_method": "クレジットカード",
    "is_tax_included": true,
    "payment_notes": null
  },
  "credentials": [],
  "contacts": [],
  "attachments": [],
  "is_deleted": false,
  "created_at": "2026-01-15T09:00:00+09:00",
  "updated_at": "2026-06-01T10:30:00+09:00"
}
```

### DashboardSummary（ダッシュボード用）

```json
{
  "total_contracts": 12,
  "active_contracts": 10,
  "monthly_total_amount": "45230.00",
  "by_category": [
    {
      "category_id": 1,
      "category_name": "携帯電話",
      "contract_count": 2,
      "monthly_amount": "12000.00"
    }
  ],
  "upcoming_renewals": [
    {
      "contract_id": 5,
      "provider_name": "東京ガス",
      "renewal_date": "2026-07-01"
    }
  ]
}
```

---

## エンドポイント一覧

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/categories` | カテゴリ一覧 |
| POST | `/categories` | カテゴリ作成 |
| PUT | `/categories/{category_id}` | カテゴリ更新 |
| DELETE | `/categories/{category_id}` | カテゴリ削除 |
| GET | `/contracts` | 契約一覧 |
| POST | `/contracts` | 契約作成 |
| GET | `/contracts/{contract_id}` | 契約詳細 |
| PUT | `/contracts/{contract_id}` | 契約更新 |
| DELETE | `/contracts/{contract_id}` | 契約削除 |
| POST | `/contracts/{contract_id}/restore` | 契約の復元（論理削除の取り消し） |
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
| POST | `/contracts/{contract_id}/attachments` | 契約書ファイルアップロード |
| PUT | `/contracts/{contract_id}/attachments/{attachment_id}` | 契約書ファイル情報更新 |
| DELETE | `/contracts/{contract_id}/attachments/{attachment_id}` | 契約書ファイル削除 |
| GET | `/contracts/{contract_id}/attachments/{attachment_id}/download` | 契約書ファイルダウンロード |
| GET | `/dashboard` | ダッシュボード集計 |

---

## エンドポイント詳細

### カテゴリ

#### `GET /categories`

ログインユーザーが登録したカテゴリ一覧を取得する。

**レスポンス `200`**

```json
{
  "items": [
    {
      "id": 1,
      "name": "携帯電話",
      "icon": "phone",
      "sort_order": 10
    }
  ]
}
```

---

#### `POST /categories`

カテゴリを新規作成する。

**リクエストボディ**

```json
{
  "name": "ジム",
  "icon": "fitness",
  "sort_order": 100
}
```

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `name` | string | ○ | カテゴリ名（100 文字以内） |
| `icon` | string | — | アイコン識別子 |
| `sort_order` | int | — | 表示順 |

**レスポンス `201`**: 作成した `Category`

**エラー**

| コード | code | 説明 |
|--------|------|------|
| `409` | `CATEGORY_NAME_DUPLICATE` | 同名カテゴリが既に存在 |

---

#### `PUT /categories/{category_id}`

カテゴリを更新する。

**リクエストボディ**

```json
{
  "name": "ジム・フィットネス",
  "icon": "fitness",
  "sort_order": 100
}
```

**レスポンス `200`**: 更新後の `Category`

---

#### `DELETE /categories/{category_id}`

カテゴリを削除する。紐づく契約が存在する場合は削除不可。

**レスポンス `204`**

**エラー**

| コード | code | 説明 |
|--------|------|------|
| `409` | `CATEGORY_IN_USE` | 契約が紐づいている |

---

### 契約

#### `GET /contracts`

契約一覧を取得する。

**クエリパラメータ**

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `page` | int | ページ番号 |
| `per_page` | int | 件数 |
| `status` | string | 状態フィルタ（`active` 等） |
| `category_id` | int | カテゴリ ID フィルタ |
| `q` | string | キーワード検索（会社名・契約名・契約番号） |
| `sort` | string | ソート。`updated_at_desc`（デフォルト）, `provider_name_asc`, `start_date_desc` |
| `group` | string | 契約グループ。`active`（契約中）, `ended`（終了）, `all`（すべて）。省略時はグループフィルタなし |
| `as_of_date` | date | 指定日時点で契約中のものに絞り込み（`YYYY-MM-DD`）。指定時は `group` より優先 |
| `include_deleted` | bool | `true` のとき論理削除済みも含める（既定 `false`） |

**レスポンス `200`**

```json
{
  "items": [
    {
      "id": 1,
      "category": { "id": 1, "name": "携帯電話", "icon": "phone" },
      "provider_name": "NTTドコモ",
      "contract_name": "ファミリープラン",
      "status": "active",
      "start_date": "2024-04-01",
      "end_date": null,
      "amount": "5980.00",
      "payment_cycle": "monthly",
      "monthly_amount": "5980.00",
      "credential_count": 2,
      "attachment_count": 1,
      "is_deleted": false,
      "updated_at": "2026-06-01T10:30:00+09:00"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20,
  "total_pages": 1
}
```

**フィルタの組み合わせ**

| パラメータ | 挙動 |
|-----------|------|
| `group=active` | 終了していない契約。終了の定義は下記 |
| `group=ended` | 終了した契約。終了の定義は下記 |
| `group=all` | グループによる絞り込みなし |
| `as_of_date` | 指定日時点で契約期間内かつ `status != cancelled` |
| `include_deleted=true` | `is_deleted = true` の契約も一覧に含める |

**終了の定義**（`group=ended` の判定、基準日は `as_of_date` または当日）

- `status = cancelled` **または**
- `end_date` が基準日より前

**契約中の定義**（`group=active`）

- 上記「終了」に該当しない（かつ `include_deleted` 未指定時は未削除）

---

#### `POST /contracts`

契約を新規作成する。支払い情報・認証情報・連絡先を同時に登録可能。

**リクエストボディ**

```json
{
  "category_id": 1,
  "provider_name": "NTTドコモ",
  "contract_name": "ファミリープラン",
  "contract_number": "1234567890",
  "status": "active",
  "start_date": "2024-04-01",
  "end_date": null,
  "renewal_date": "2027-03-31",
  "auto_renewal": true,
  "notes": "家族3回線",
  "payment": {
    "amount": "5980",
    "payment_cycle": "monthly",
    "payment_day": 27,
    "payment_method": "クレジットカード",
    "is_tax_included": true
  },
  "credentials": [
    {
      "credential_type": "login_id",
      "label": "マイページ",
      "value": "user@example.com",
      "url": "https://example.com/login"
    },
    {
      "credential_type": "password",
      "label": "マイページ",
      "value": "my-secret-password"
    }
  ],
  "contacts": [
    {
      "contact_type": "phone",
      "label": "カスタマーセンター",
      "value": "151",
      "notes": "24時間対応"
    }
  ]
}
```

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `category_id` | int | ○ | カテゴリ ID（自分のカテゴリのみ） |
| `provider_name` | string | ○ | 会社名（200 文字以内） |
| `contract_name` | string | — | プラン名 |
| `contract_number` | string | — | 契約番号 |
| `status` | string | — | デフォルト `active` |
| `start_date` | date | — | 開始日 |
| `end_date` | date | — | 終了日 |
| `renewal_date` | date | — | 更新日 |
| `auto_renewal` | bool | — | デフォルト `true` |
| `notes` | string | — | メモ |
| `payment` | object | — | 支払い情報（1 件） |
| `credentials` | array | — | 初期認証情報 |
| `contacts` | array | — | 初期連絡先 |

**`payment` オブジェクト**

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `amount` | string/number | — | 金額（0 以上） |
| `currency` | string | — | デフォルト `JPY` |
| `payment_cycle` | string | — | 支払い周期 |
| `payment_day` | int | — | 1〜31 |
| `payment_method` | string | — | 支払い方法 |
| `is_tax_included` | bool | — | デフォルト `true` |
| `payment_notes` | string | — | 備考 |

**レスポンス `201`**: `ContractDetail`

---

#### `GET /contracts/{contract_id}`

契約詳細を取得する。支払い・認証情報・連絡先・契約書ファイルをすべて含む。

**クエリパラメータ**

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `include_deleted` | bool | `true` のとき論理削除済み契約も取得（既定 `false`） |

**レスポンス `200`**: `ContractDetail`

- `credentials` の `password` 型はマスクして返す。
- `is_deleted` で論理削除状態を示す。

---

#### `PUT /contracts/{contract_id}`

契約本体と支払い情報を更新する。認証情報・連絡先・契約書ファイルは個別エンドポイントで操作。

**リクエストボディ**

```json
{
  "category_id": 1,
  "provider_name": "NTTドコモ",
  "contract_name": "ファミリープラン改",
  "contract_number": "1234567890",
  "status": "active",
  "start_date": "2024-04-01",
  "end_date": null,
  "renewal_date": "2027-03-31",
  "auto_renewal": true,
  "notes": "更新メモ",
  "payment": {
    "amount": "6500",
    "payment_cycle": "monthly",
    "payment_day": 27,
    "payment_method": "クレジットカード",
    "is_tax_included": true,
    "payment_notes": null
  }
}
```

**レスポンス `200`**: `ContractDetail`（子リソース含む）

---

#### `DELETE /contracts/{contract_id}`

契約を論理削除する。紐づく認証情報・連絡先・契約書ファイルも連鎖論理削除される。ストレージ上の実ファイルも削除する。

**レスポンス `204`**

> 契約終了（`status=cancelled` や `end_date` の設定）とは別操作。終了は `PUT` で行う。

---

#### `POST /contracts/{contract_id}/restore`

論理削除した契約を復元する。紐づく認証情報・連絡先・契約書ファイルのメタデータも連鎖復元する。

**レスポンス `200`**: `ContractDetail`

**エラー**

| コード | code | 説明 |
|--------|------|------|
| `404` | `NOT_FOUND` | 削除済み契約が見つからない |

> 削除時にストレージから物理削除された契約書ファイルは復元されない。復元後のダウンロードは `404` となる場合がある。

---

### 認証情報

#### `GET /contracts/{contract_id}/credentials`

**レスポンス `200`**

```json
{
  "items": [
    {
      "id": 1,
      "credential_type": "login_id",
      "label": "マイページ",
      "value": "user@example.com",
      "is_masked": false,
      "url": "https://example.com/login",
      "notes": null,
      "sort_order": 0
    },
    {
      "id": 2,
      "credential_type": "password",
      "label": "マイページ",
      "value": "********",
      "is_masked": true,
      "url": null,
      "notes": null,
      "sort_order": 1
    }
  ]
}
```

---

#### `POST /contracts/{contract_id}/credentials`

**リクエストボディ**

```json
{
  "credential_type": "password",
  "label": "マイページ",
  "value": "my-secret-password",
  "url": "https://example.com/login",
  "notes": null,
  "sort_order": 0
}
```

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `credential_type` | string | ○ | 種別 |
| `label` | string | — | ラベル |
| `value` | string | ○ | 値（アプリ層で暗号化して DB に保存） |
| `url` | string | — | URL |
| `notes` | string | — | 備考 |
| `sort_order` | int | — | 表示順 |

**レスポンス `201`**: `Credential`（`password` はマスク状態で返す）

---

#### `PUT /contracts/{contract_id}/credentials/{credential_id}`

**リクエストボディ**: `POST` と同じ（部分更新対応）

> `value` を省略した場合は既存値を維持する。

**レスポンス `200`**: `Credential`

---

#### `DELETE /contracts/{contract_id}/credentials/{credential_id}`

**レスポンス `204`**

---

#### `GET /contracts/{contract_id}/credentials/{credential_id}/reveal`

マスクされた認証情報の実値を復号して返す。フロントエンドで「表示」ボタン押下時に使用。

**レスポンス `200`**

```json
{
  "id": 2,
  "credential_type": "password",
  "label": "マイページ",
  "value": "my-secret-password"
}
```

---

### 連絡先

#### `GET /contracts/{contract_id}/contacts`

**レスポンス `200`**

```json
{
  "items": [
    {
      "id": 1,
      "contact_type": "phone",
      "label": "カスタマーセンター",
      "value": "0120-000-000",
      "notes": "平日 9:00-18:00",
      "sort_order": 0
    }
  ]
}
```

---

#### `POST /contracts/{contract_id}/contacts`

**リクエストボディ**

```json
{
  "contact_type": "phone",
  "label": "カスタマーセンター",
  "value": "0120-000-000",
  "notes": "平日 9:00-18:00",
  "sort_order": 0
}
```

**レスポンス `201`**: `Contact`

---

#### `PUT /contracts/{contract_id}/contacts/{contact_id}`

**レスポンス `200`**: `Contact`

---

#### `DELETE /contracts/{contract_id}/contacts/{contact_id}`

**レスポンス `204`**

---

### 契約書ファイル

#### `GET /contracts/{contract_id}/attachments`

契約に紐づくファイル一覧を取得する。

**レスポンス `200`**

```json
{
  "items": [
    {
      "id": 1,
      "file_name": "契約書_2024.pdf",
      "content_type": "application/pdf",
      "file_size": 1048576,
      "description": "契約書 2024 年版",
      "sort_order": 0,
      "created_at": "2026-01-15T09:00:00+09:00"
    }
  ]
}
```

---

#### `POST /contracts/{contract_id}/attachments`

契約書ファイルをアップロードする。

**リクエスト**: `multipart/form-data`

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `file` | file | ○ | アップロードファイル |
| `description` | string | — | ファイルの説明 |
| `sort_order` | int | — | 表示順 |

**制限**

| 項目 | 値 |
|------|-----|
| 最大ファイルサイズ | 10 MB（実装時に調整可） |
| 許可 MIME タイプ | `application/pdf`, `image/jpeg`, `image/png`, `image/webp` |

**レスポンス `201`**: `Attachment`

**エラー**

| コード | code | 説明 |
|--------|------|------|
| `413` | `FILE_TOO_LARGE` | ファイルサイズ超過 |
| `400` | `FILE_TYPE_NOT_ALLOWED` | 許可されていないファイル形式 |

---

#### `PUT /contracts/{contract_id}/attachments/{attachment_id}`

ファイルのメタデータ（説明・表示順）を更新する。ファイル本体の差し替えは DELETE → POST で行う。

**リクエストボディ**

```json
{
  "description": "契約書 2025 年版",
  "sort_order": 1
}
```

**レスポンス `200`**: `Attachment`

---

#### `DELETE /contracts/{contract_id}/attachments/{attachment_id}`

ファイルを削除する。DB レコードとストレージ上の実ファイルの両方を削除する。

**レスポンス `204`**

---

#### `GET /contracts/{contract_id}/attachments/{attachment_id}/download`

ファイルをダウンロードする。

**レスポンス `200`**: ファイルバイナリ（`Content-Disposition: attachment`）

---

### ダッシュボード

#### `GET /dashboard`

契約の集計情報を返す。フロントエンドのトップ画面向け。

**レスポンス `200`**: `DashboardSummary`

- `monthly_total_amount` は各契約の `amount` を `payment_cycle` に基づき月額換算した合計。

---

## FastAPI ルーター構成（実装参考）

```
app/
  api/
    v1/
      contract/
        router.py          # ルーター統合
        categories.py      # カテゴリ CRUD
        contracts.py       # 契約 CRUD
        credentials.py     # 認証情報 CRUD
        contacts.py        # 連絡先 CRUD
        attachments.py     # 契約書ファイル CRUD
        dashboard.py       # ダッシュボード
  schemas/
    contract/
      category.py
      contract.py
      credential.py
      contact.py
      attachment.py
      dashboard.py
  services/
    contract_service.py
    encryption_service.py
    storage_service.py
```

ルーター登録例:

```python
from fastapi import APIRouter
from app.api.v1.contract import categories, contracts, dashboard

router = APIRouter(prefix="/api/v1/contract", tags=["contract"])
router.include_router(categories.router)
router.include_router(contracts.router)
router.include_router(dashboard.router)
```

---

## 実装メモ

### 暗号化

- `credentials.value` はアプリケーション層で暗号化してから DB の `TEXT` カラムに保存する。
- `credential_type` が `password` または `api_key` の場合、一覧・詳細ではマスクする。
- 復号は `/reveal` エンドポイントのみで行う。

### 月額換算

- 契約一覧の `monthly_amount` は契約の `amount` と `payment_cycle` から算出する。
- 換算ルールは DB ビュー `contract.v_monthly_cost_summary` と同一とする。

### トランザクション

- `POST /contracts` で子リソースを同時作成する場合は 1 トランザクションで処理する。
- 契約削除時は DB 削除とストレージファイル削除を同一トランザクション（または補償処理）で整合性を保つ。

### OpenAPI

- FastAPI の自動生成 OpenAPI（`/docs`）がそのまま API ドキュメントとなる。
- 本仕様書のスキーマは Pydantic モデルとして定義する。

---

## 補足: フロントエンド画面と API の対応

| 画面 | 使用 API |
|------|---------|
| トップ（ダッシュボード） | `GET /dashboard` |
| 契約一覧 | `GET /contracts`, `GET /categories` |
| 契約詳細 | `GET /contracts/{id}` |
| 契約登録・編集 | `POST /contracts`, `PUT /contracts/{id}` |
| 認証情報編集 | `POST/PUT/DELETE .../credentials`, `GET .../reveal` |
| 連絡先編集 | `POST/PUT/DELETE .../contacts` |
| 契約書ファイル | `POST/GET/DELETE .../attachments`, `GET .../download` |
| カテゴリ管理 | `GET/POST/PUT/DELETE /categories` |

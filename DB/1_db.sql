-- =============================================================================
-- 契約管理 DB スキーマ
-- 仕様: DB_CONTRACT_SPEC.md
-- DBMS: PostgreSQL
-- 前提: public.accounts テーブルが既に存在すること
-- 備考: すべてのテーブルで論理削除（is_deleted）を採用。物理 DELETE は行わない。
-- =============================================================================

-- -----------------------------------------------------------------------------
-- スキーマ
-- -----------------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS contract;

-- -----------------------------------------------------------------------------
-- updated_at 自動更新用トリガー関数
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION contract.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- 1. contract.categories（契約カテゴリ）
-- -----------------------------------------------------------------------------
CREATE TABLE contract.categories (
    id          SERIAL          NOT NULL,
    aid         INTEGER         NOT NULL,
    name        VARCHAR(100)    NOT NULL,
    icon        VARCHAR(50),
    sort_order  INTEGER         NOT NULL DEFAULT 0,
    is_deleted  BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT categories_pkey
        PRIMARY KEY (id),

    CONSTRAINT categories_aid_fkey
        FOREIGN KEY (aid)
        REFERENCES public.accounts (id)
        ON DELETE RESTRICT
);

CREATE UNIQUE INDEX categories_aid_name_unique
    ON contract.categories (aid, name)
    WHERE is_deleted = FALSE;

CREATE INDEX idx_categories_aid
    ON contract.categories (aid)
    WHERE is_deleted = FALSE;

CREATE INDEX idx_categories_aid_sort_order
    ON contract.categories (aid, sort_order)
    WHERE is_deleted = FALSE;

CREATE TRIGGER trg_categories_updated_at
    BEFORE UPDATE ON contract.categories
    FOR EACH ROW
    EXECUTE PROCEDURE contract.set_updated_at();

COMMENT ON TABLE contract.categories IS '契約カテゴリ（ユーザーが自由に登録）';
COMMENT ON COLUMN contract.categories.aid IS 'ユーザー ID（public.accounts.id）';
COMMENT ON COLUMN contract.categories.is_deleted IS '論理削除フラグ';

-- -----------------------------------------------------------------------------
-- 2. contract.contracts（契約）
-- -----------------------------------------------------------------------------
CREATE TABLE contract.contracts (
    id              SERIAL          NOT NULL,
    aid             INTEGER         NOT NULL,
    category_id     INTEGER         NOT NULL,
    provider_name   VARCHAR(200)    NOT NULL,
    contract_name   VARCHAR(200),
    contract_number VARCHAR(100),
    status          VARCHAR(20)     NOT NULL DEFAULT 'active',
    start_date      DATE,
    end_date        DATE,
    renewal_date    DATE,
    auto_renewal    BOOLEAN         NOT NULL DEFAULT TRUE,
    amount          NUMERIC(12, 2),
    currency        CHAR(3)         NOT NULL DEFAULT 'JPY',
    payment_cycle   VARCHAR(20),
    payment_day     SMALLINT,
    payment_method  VARCHAR(50),
    is_tax_included BOOLEAN         NOT NULL DEFAULT TRUE,
    payment_notes   TEXT,
    notes           TEXT,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT contracts_pkey
        PRIMARY KEY (id),

    CONSTRAINT contracts_aid_fkey
        FOREIGN KEY (aid)
        REFERENCES public.accounts (id)
        ON DELETE RESTRICT,

    CONSTRAINT contracts_category_id_fkey
        FOREIGN KEY (category_id)
        REFERENCES contract.categories (id)
        ON DELETE RESTRICT,

    CONSTRAINT contracts_status_check
        CHECK (status IN ('active', 'suspended', 'cancelled', 'pending')),

    CONSTRAINT contracts_payment_cycle_check
        CHECK (
            payment_cycle IS NULL
            OR payment_cycle IN (
                'monthly', 'yearly', 'quarterly', 'biannual', 'one_time', 'other'
            )
        ),

    CONSTRAINT contracts_date_check
        CHECK (
            end_date IS NULL
            OR start_date IS NULL
            OR end_date >= start_date
        ),

    CONSTRAINT contracts_payment_day_check
        CHECK (
            payment_day IS NULL
            OR (payment_day BETWEEN 1 AND 31)
        ),

    CONSTRAINT contracts_amount_check
        CHECK (amount IS NULL OR amount >= 0)
);

CREATE INDEX idx_contracts_aid
    ON contract.contracts (aid)
    WHERE is_deleted = FALSE;

CREATE INDEX idx_contracts_aid_status
    ON contract.contracts (aid, status)
    WHERE is_deleted = FALSE;

CREATE INDEX idx_contracts_aid_category_id
    ON contract.contracts (aid, category_id)
    WHERE is_deleted = FALSE;

CREATE INDEX idx_contracts_provider_name
    ON contract.contracts (aid, provider_name)
    WHERE is_deleted = FALSE;

CREATE TRIGGER trg_contracts_updated_at
    BEFORE UPDATE ON contract.contracts
    FOR EACH ROW
    EXECUTE PROCEDURE contract.set_updated_at();

COMMENT ON TABLE contract.contracts IS '契約本体・支払い情報（1 契約 1 支払い）';
COMMENT ON COLUMN contract.contracts.aid IS 'ユーザー ID（public.accounts.id）';
COMMENT ON COLUMN contract.contracts.is_deleted IS '論理削除フラグ';

-- -----------------------------------------------------------------------------
-- 3. contract.credentials（認証情報）
-- -----------------------------------------------------------------------------
CREATE TABLE contract.credentials (
    id              SERIAL          NOT NULL,
    contract_id     INTEGER         NOT NULL,
    credential_type VARCHAR(30)     NOT NULL,
    label           VARCHAR(100),
    value           TEXT            NOT NULL,
    url             VARCHAR(500),
    notes           TEXT,
    sort_order      INTEGER         NOT NULL DEFAULT 0,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT credentials_pkey
        PRIMARY KEY (id),

    CONSTRAINT credentials_contract_id_fkey
        FOREIGN KEY (contract_id)
        REFERENCES contract.contracts (id)
        ON DELETE RESTRICT,

    CONSTRAINT credentials_credential_type_check
        CHECK (credential_type IN (
            'login_id', 'password', 'pin', 'customer_number',
            'email', 'phone', 'api_key', 'other'
        ))
);

CREATE INDEX idx_credentials_contract_id
    ON contract.credentials (contract_id)
    WHERE is_deleted = FALSE;

CREATE TRIGGER trg_credentials_updated_at
    BEFORE UPDATE ON contract.credentials
    FOR EACH ROW
    EXECUTE PROCEDURE contract.set_updated_at();

COMMENT ON TABLE contract.credentials IS '認証情報（ログイン ID・パスワード等）';
COMMENT ON COLUMN contract.credentials.is_deleted IS '論理削除フラグ';

-- -----------------------------------------------------------------------------
-- 4. contract.contacts（連絡先）
-- -----------------------------------------------------------------------------
CREATE TABLE contract.contacts (
    id           SERIAL          NOT NULL,
    contract_id  INTEGER         NOT NULL,
    contact_type VARCHAR(20)     NOT NULL,
    label        VARCHAR(100),
    value        VARCHAR(500)    NOT NULL,
    notes        TEXT,
    sort_order   INTEGER         NOT NULL DEFAULT 0,
    is_deleted   BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT contacts_pkey
        PRIMARY KEY (id),

    CONSTRAINT contacts_contract_id_fkey
        FOREIGN KEY (contract_id)
        REFERENCES contract.contracts (id)
        ON DELETE RESTRICT,

    CONSTRAINT contacts_contact_type_check
        CHECK (contact_type IN ('phone', 'email', 'url', 'address', 'other'))
);

CREATE INDEX idx_contacts_contract_id
    ON contract.contacts (contract_id)
    WHERE is_deleted = FALSE;

CREATE TRIGGER trg_contacts_updated_at
    BEFORE UPDATE ON contract.contacts
    FOR EACH ROW
    EXECUTE PROCEDURE contract.set_updated_at();

COMMENT ON TABLE contract.contacts IS '連絡先（問い合わせ先・サポート URL 等）';
COMMENT ON COLUMN contract.contacts.is_deleted IS '論理削除フラグ';

-- -----------------------------------------------------------------------------
-- 5. contract.attachments（契約書ファイル）
-- -----------------------------------------------------------------------------
CREATE TABLE contract.attachments (
    id           SERIAL          NOT NULL,
    contract_id  INTEGER         NOT NULL,
    file_name    VARCHAR(255)    NOT NULL,
    storage_path VARCHAR(500)    NOT NULL,
    content_type VARCHAR(100),
    file_size    BIGINT          NOT NULL,
    description  VARCHAR(200),
    sort_order   INTEGER         NOT NULL DEFAULT 0,
    is_deleted   BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT attachments_pkey
        PRIMARY KEY (id),

    CONSTRAINT attachments_contract_id_fkey
        FOREIGN KEY (contract_id)
        REFERENCES contract.contracts (id)
        ON DELETE RESTRICT,

    CONSTRAINT attachments_file_size_check
        CHECK (file_size > 0)
);

CREATE INDEX idx_attachments_contract_id
    ON contract.attachments (contract_id)
    WHERE is_deleted = FALSE;

CREATE TRIGGER trg_attachments_updated_at
    BEFORE UPDATE ON contract.attachments
    FOR EACH ROW
    EXECUTE PROCEDURE contract.set_updated_at();

COMMENT ON TABLE contract.attachments IS '契約書ファイル（メタデータ）';
COMMENT ON COLUMN contract.attachments.is_deleted IS '論理削除フラグ';

-- -----------------------------------------------------------------------------
-- ビュー: 月額換算支払い合計（アクティブ契約のみ）
-- -----------------------------------------------------------------------------
CREATE VIEW contract.v_monthly_cost_summary AS
SELECT
    c.aid,
    c.id AS contract_id,
    c.provider_name,
    c.contract_name,
    CASE c.payment_cycle
        WHEN 'monthly'   THEN c.amount
        WHEN 'yearly'    THEN c.amount / 12
        WHEN 'quarterly' THEN c.amount / 3
        WHEN 'biannual'  THEN c.amount / 6
        ELSE 0
    END AS monthly_amount
FROM contract.contracts c
WHERE c.status = 'active'
  AND c.is_deleted = FALSE
  AND c.amount IS NOT NULL
  AND c.payment_cycle IS NOT NULL;

COMMENT ON VIEW contract.v_monthly_cost_summary IS 'ユーザーごとの月額換算支払い合計（アクティブ契約のみ）';


USE master;
GO

-- Tao database neu chua ton tai
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'FinSmartDB')
BEGIN
    CREATE DATABASE FinSmartDB
    COLLATE Vietnamese_CI_AS;
END
GO

USE FinSmartDB;
GO


IF OBJECT_ID('dbo.finance_aisuggestion',  'U') IS NOT NULL DROP TABLE dbo.finance_aisuggestion;
IF OBJECT_ID('dbo.finance_chatmessage',   'U') IS NOT NULL DROP TABLE dbo.finance_chatmessage;
IF OBJECT_ID('dbo.finance_budget',        'U') IS NOT NULL DROP TABLE dbo.finance_budget;
IF OBJECT_ID('dbo.finance_goal',          'U') IS NOT NULL DROP TABLE dbo.finance_goal;
IF OBJECT_ID('dbo.finance_transaction',   'U') IS NOT NULL DROP TABLE dbo.finance_transaction;
IF OBJECT_ID('dbo.finance_category',      'U') IS NOT NULL DROP TABLE dbo.finance_category;
IF OBJECT_ID('dbo.finance_userprofile',   'U') IS NOT NULL DROP TABLE dbo.finance_userprofile;
IF OBJECT_ID('dbo.auth_user',             'U') IS NOT NULL DROP TABLE dbo.auth_user;
GO

-- ============================================================
-- BANG: auth_user  (nguoi dung - Django built-in)
-- ============================================================
CREATE TABLE dbo.auth_user (
    id            BIGINT          NOT NULL IDENTITY(1,1),
    password      NVARCHAR(128)   NOT NULL,
    last_login    DATETIME2(6)    NULL,
    is_superuser  BIT             NOT NULL DEFAULT 0,
    username      NVARCHAR(150)   NOT NULL,
    first_name    NVARCHAR(150)   NOT NULL DEFAULT N'',
    last_name     NVARCHAR(150)   NOT NULL DEFAULT N'',
    email         NVARCHAR(254)   NOT NULL DEFAULT N'',
    is_staff      BIT             NOT NULL DEFAULT 0,
    is_active     BIT             NOT NULL DEFAULT 1,
    date_joined   DATETIME2(6)    NOT NULL DEFAULT GETDATE(),

    CONSTRAINT PK_auth_user PRIMARY KEY (id),
    CONSTRAINT UQ_auth_user_username UNIQUE (username)
);
GO

-- ============================================================
-- BANG: finance_userprofile  (avatar/currency mo rong cho auth_user)
-- ============================================================
CREATE TABLE dbo.finance_userprofile (
    id          BIGINT          NOT NULL IDENTITY(1,1),
    user_id     BIGINT          NOT NULL,
    avatar_url  NVARCHAR(500)   NULL,
    currency    NVARCHAR(10)    NOT NULL DEFAULT N'VND',
    created_at  DATETIME2(6)    NOT NULL DEFAULT GETDATE(),

    CONSTRAINT PK_finance_userprofile PRIMARY KEY (id),
    CONSTRAINT UQ_finance_userprofile_user UNIQUE (user_id),
    CONSTRAINT FK_userprofile_user
        FOREIGN KEY (user_id) REFERENCES dbo.auth_user(id)
        ON DELETE CASCADE
);
GO

-- ============================================================
-- BANG: finance_category  (danh muc thu / chi)
-- ============================================================
CREATE TABLE dbo.finance_category (
    id          BIGINT          NOT NULL IDENTITY(1,1),
    name        NVARCHAR(100)   NOT NULL,
    [type]      NVARCHAR(10)    NOT NULL,   -- 'income' | 'expense'
    icon        NVARCHAR(50)    NULL,
    color       NVARCHAR(20)    NULL,
    is_default  BIT             NOT NULL DEFAULT 0,
    user_id     BIGINT          NULL,
    created_at  DATETIME2(6)    NOT NULL DEFAULT GETDATE(),

    CONSTRAINT PK_finance_category PRIMARY KEY (id),
    CONSTRAINT CHK_category_type CHECK ([type] IN ('income','expense')),
    CONSTRAINT FK_category_user
        FOREIGN KEY (user_id) REFERENCES dbo.auth_user(id)
        ON DELETE CASCADE
);
GO

-- ============================================================
-- BANG: finance_transaction  (giao dich thu / chi)
-- ============================================================
CREATE TABLE dbo.finance_transaction (
    id          BIGINT          NOT NULL IDENTITY(1,1),
    user_id     BIGINT          NOT NULL,
    [type]      NVARCHAR(10)    NOT NULL,   -- 'income' | 'expense'
    amount      DECIMAL(15,0)   NOT NULL,
    description NVARCHAR(255)   NOT NULL,
    note        NVARCHAR(MAX)   NULL,
    [date]      DATE            NOT NULL,
    category_id BIGINT          NULL,
    created_at  DATETIME2(6)    NOT NULL DEFAULT GETDATE(),

    CONSTRAINT PK_finance_transaction PRIMARY KEY (id),
    CONSTRAINT CHK_transaction_type  CHECK ([type] IN ('income','expense')),
    CONSTRAINT CHK_transaction_amount CHECK (amount >= 0),
    CONSTRAINT FK_transaction_user
        FOREIGN KEY (user_id) REFERENCES dbo.auth_user(id)
        ON DELETE CASCADE,
    CONSTRAINT FK_transaction_category
        FOREIGN KEY (category_id) REFERENCES dbo.finance_category(id)
        ON DELETE SET NULL
);
GO

-- ============================================================
-- BANG: finance_budget  (ngan sach theo thang)
-- ============================================================
CREATE TABLE dbo.finance_budget (
    id          BIGINT          NOT NULL IDENTITY(1,1),
    user_id     BIGINT          NOT NULL,
    [month]     INT             NOT NULL,   -- 1..12
    [year]      INT             NOT NULL,
    amount      DECIMAL(15,0)   NOT NULL,
    category_id BIGINT          NULL,
    created_at  DATETIME2(6)    NOT NULL DEFAULT GETDATE(),

    CONSTRAINT PK_finance_budget PRIMARY KEY (id),
    CONSTRAINT CHK_budget_month CHECK ([month] BETWEEN 1 AND 12),
    CONSTRAINT CHK_budget_year  CHECK ([year]  BETWEEN 2000 AND 2100),
    CONSTRAINT CHK_budget_amount CHECK (amount > 0),
    CONSTRAINT FK_budget_user
        FOREIGN KEY (user_id) REFERENCES dbo.auth_user(id)
        ON DELETE CASCADE,
    CONSTRAINT FK_budget_category
        FOREIGN KEY (category_id) REFERENCES dbo.finance_category(id)
        ON DELETE SET NULL
);
GO

-- ============================================================
-- BANG: finance_goal  (muc tieu tiet kiem)
-- ============================================================
CREATE TABLE dbo.finance_goal (
    id               BIGINT          NOT NULL IDENTITY(1,1),
    user_id          BIGINT          NOT NULL,
    linked_budget_id BIGINT          NULL,
    name             NVARCHAR(200)   NOT NULL,
    target_amount    DECIMAL(15,0)   NOT NULL,
    current_amount   DECIMAL(15,0)   NOT NULL DEFAULT 0,
    deadline         DATE            NULL,
    icon             NVARCHAR(50)    NULL DEFAULT N'🎯',
    created_at       DATETIME2(6)    NOT NULL DEFAULT GETDATE(),

    CONSTRAINT PK_finance_goal PRIMARY KEY (id),
    CONSTRAINT CHK_goal_target  CHECK (target_amount  > 0),
    CONSTRAINT CHK_goal_current CHECK (current_amount >= 0),
    CONSTRAINT FK_goal_user
        FOREIGN KEY (user_id) REFERENCES dbo.auth_user(id)
        ON DELETE CASCADE,
    CONSTRAINT FK_goal_budget
        FOREIGN KEY (linked_budget_id) REFERENCES dbo.finance_budget(id)
        ON DELETE SET NULL
);
GO

-- ============================================================
-- BANG: finance_chatmessage  (lich su chat voi AI)
-- ============================================================
CREATE TABLE dbo.finance_chatmessage (
    id          BIGINT          NOT NULL IDENTITY(1,1),
    user_id     BIGINT          NOT NULL,
    session_key NVARCHAR(40)    NOT NULL DEFAULT N'default',
    role        NVARCHAR(20)    NOT NULL,   -- 'user' | 'assistant'
    content     NVARCHAR(MAX)   NOT NULL,
    created_at  DATETIME2(6)    NOT NULL DEFAULT GETDATE(),

    CONSTRAINT PK_finance_chatmessage PRIMARY KEY (id),
    CONSTRAINT CHK_chat_role CHECK (role IN ('user','assistant')),
    CONSTRAINT FK_chatmessage_user
        FOREIGN KEY (user_id) REFERENCES dbo.auth_user(id)
        ON DELETE CASCADE
);
GO

-- ============================================================
-- BANG: finance_aisuggestion  (goi y tu AI)
-- ============================================================
CREATE TABLE dbo.finance_aisuggestion (
    id         BIGINT          NOT NULL IDENTITY(1,1),
    user_id    BIGINT          NOT NULL,
    [type]     NVARCHAR(30)    NOT NULL,   -- 'spending_alert' | 'saving_tip' | 'goal_progress' | 'budget_advice'
    title      NVARCHAR(200)   NOT NULL,
    message    NVARCHAR(MAX)   NOT NULL,
    priority   NVARCHAR(10)    NOT NULL,   -- 'low' | 'medium' | 'high'
    created_at DATETIME2(6)    NOT NULL DEFAULT GETDATE(),

    CONSTRAINT PK_finance_aisuggestion PRIMARY KEY (id),
    CONSTRAINT CHK_ai_type     CHECK ([type]    IN ('spending_alert','saving_tip','goal_progress','budget_advice','category_insight','anomaly_detect','income_boost','smart_saving','recurring_expense','budget_optimization','savings_milestone','spending_pattern','category_trend')),
    CONSTRAINT CHK_ai_priority CHECK (priority  IN ('low','medium','high')),
    CONSTRAINT FK_aisuggestion_user
        FOREIGN KEY (user_id) REFERENCES dbo.auth_user(id)
        ON DELETE CASCADE
);
GO


CREATE INDEX IX_transaction_user_date ON dbo.finance_transaction (user_id, [date] DESC);
CREATE INDEX IX_transaction_type      ON dbo.finance_transaction ([type]);
CREATE INDEX IX_budget_user_month     ON dbo.finance_budget      (user_id, [year], [month]);
CREATE INDEX IX_goal_user             ON dbo.finance_goal        (user_id);
CREATE INDEX IX_chat_user_time        ON dbo.finance_chatmessage (user_id, created_at);
CREATE INDEX IX_chat_session          ON dbo.finance_chatmessage (session_key);
CREATE INDEX IX_category_type         ON dbo.finance_category    ([type], is_default);
CREATE INDEX IX_userprofile_currency  ON dbo.finance_userprofile (currency);
GO

-- ============================================================
-- DU LIEU MAU: 16 danh muc mac dinh
-- ============================================================
INSERT INTO dbo.finance_category (name, [type], icon, color, is_default, user_id) VALUES
-- Thu nhap
(N'Lương',          'income',  N'💰', N'#16a34a', 1, NULL),
(N'Thưởng',         'income',  N'🎁', N'#15803d', 1, NULL),
(N'Kinh doanh',     'income',  N'🏪', N'#166534', 1, NULL),
(N'Đầu tư',         'income',  N'📈', N'#14532d', 1, NULL),
(N'Thu nhập khác',  'income',  N'💵', N'#22c55e', 1, NULL),
(N'Tiết kiệm',      'income',  N'🏦', N'#86efac', 1, NULL),
-- Chi tieu
(N'Ăn uống',        'expense', N'🍜', N'#f97316', 1, NULL),
(N'Di chuyển',      'expense', N'🚗', N'#3b82f6', 1, NULL),
(N'Nhà ở',          'expense', N'🏠', N'#8b5cf6', 1, NULL),
(N'Giải trí',       'expense', N'🎮', N'#ec4899', 1, NULL),
(N'Y tế',           'expense', N'🏥', N'#ef4444', 1, NULL),
(N'Học tập',        'expense', N'📚', N'#06b6d4', 1, NULL),
(N'Quần áo',        'expense', N'👕', N'#f59e0b', 1, NULL),
(N'Điện thoại',     'expense', N'📱', N'#6366f1', 1, NULL),
(N'Mua sắm',        'expense', N'🛒', N'#d946ef', 1, NULL),
(N'Chi tiêu khác',  'expense', N'💸', N'#6b7280', 1, NULL);
GO


INSERT INTO dbo.auth_user (password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
VALUES
(
    N'pbkdf2_sha256$870000$demo$...changeme',
    0,
    N'test@finsmart.vn',
    N'Sinh vien',
    N'Test',
    N'test@finsmart.vn',
    0, 1,
    GETDATE()
),
(
    N'pbkdf2_sha256$870000$admin$...changeme',
    1,
    N'admin@finsmart.vn',
    N'Quan tri',
    N'Admin',
    N'admin@finsmart.vn',
    1, 1,
    GETDATE()
);
GO

INSERT INTO dbo.finance_userprofile (user_id, avatar_url, currency)
SELECT id, N'https://i.pravatar.cc/160?img=12', N'VND'
FROM dbo.auth_user
WHERE username = N'test@finsmart.vn';

INSERT INTO dbo.finance_userprofile (user_id, avatar_url, currency)
SELECT id, N'https://i.pravatar.cc/160?img=5', N'VND'
FROM dbo.auth_user
WHERE username = N'admin@finsmart.vn';
GO

-- ============================================================
-- VIEW: Thong ke tong quan tai chinh theo nguoi dung
-- ============================================================
CREATE OR ALTER VIEW dbo.vw_user_summary AS
SELECT
    u.id                                        AS user_id,
    u.username,
    u.email,
    u.first_name + N' ' + u.last_name           AS full_name,
    p.avatar_url,
    p.currency,
    u.is_staff,
    u.is_superuser,
    u.is_active,
    ISNULL(SUM(CASE WHEN t.[type] = 'income'  THEN t.amount ELSE 0 END), 0) AS total_income,
    ISNULL(SUM(CASE WHEN t.[type] = 'expense' THEN t.amount ELSE 0 END), 0) AS total_expense,
    ISNULL(SUM(CASE WHEN t.[type] = 'income'  THEN t.amount ELSE -t.amount END), 0) AS balance,
    COUNT(t.id)                                 AS total_transactions,
    (SELECT COUNT(*) FROM dbo.finance_budget b WHERE b.user_id = u.id) AS total_budgets,
    (SELECT COUNT(*) FROM dbo.finance_goal  g WHERE g.user_id = u.id) AS total_goals
FROM dbo.auth_user u
LEFT JOIN dbo.finance_userprofile p ON p.user_id = u.id
LEFT JOIN dbo.finance_transaction t ON t.user_id = u.id
GROUP BY u.id, u.username, u.email, u.first_name, u.last_name, p.avatar_url, p.currency, u.is_staff, u.is_superuser, u.is_active;
GO

-- ============================================================
-- VIEW: Chi tieu theo danh muc (thang hien tai)
-- ============================================================
CREATE OR ALTER VIEW dbo.vw_expense_by_category AS
SELECT
    t.user_id,
    c.name      AS category_name,
    c.color     AS category_color,
    c.[type]    AS category_type,
    SUM(t.amount)                AS total_amount,
    COUNT(t.id)                  AS transaction_count,
    MONTH(t.[date])              AS [month],
    YEAR(t.[date])               AS [year]
FROM dbo.finance_transaction t
JOIN dbo.finance_category c ON c.id = t.category_id
GROUP BY
    t.user_id, c.name, c.color, c.[type],
    MONTH(t.[date]), YEAR(t.[date]);
GO

-- ============================================================
-- STORED PROCEDURE: Lay bao cao tai chinh theo thang
-- ============================================================
CREATE OR ALTER PROCEDURE dbo.sp_monthly_report
    @user_id INT,
    @month   INT,
    @year    INT
AS
BEGIN
    SET NOCOUNT ON;

    -- Tong thu / chi trong thang
    SELECT
        SUM(CASE WHEN [type] = 'income'  THEN amount ELSE 0 END) AS total_income,
        SUM(CASE WHEN [type] = 'expense' THEN amount ELSE 0 END) AS total_expense,
        SUM(CASE WHEN [type] = 'income'  THEN amount ELSE -amount END) AS net_balance,
        COUNT(*) AS transaction_count
    FROM dbo.finance_transaction
    WHERE user_id = @user_id
      AND MONTH([date]) = @month
      AND YEAR([date])  = @year;

    -- Chi tieu theo danh muc
    SELECT
        c.name              AS category_name,
        c.color,
        SUM(t.amount)       AS spent,
        COUNT(t.id)         AS tx_count
    FROM dbo.finance_transaction t
    JOIN dbo.finance_category c ON c.id = t.category_id
    WHERE t.user_id = @user_id
      AND t.[type]  = 'expense'
      AND MONTH(t.[date]) = @month
      AND YEAR(t.[date])  = @year
    GROUP BY c.name, c.color
    ORDER BY spent DESC;
END;
GO


CREATE OR ALTER PROCEDURE dbo.sp_admin_create_user
    @username NVARCHAR(150),
    @email NVARCHAR(254),
    @password_hash NVARCHAR(128),
    @first_name NVARCHAR(150) = N'',
    @last_name NVARCHAR(150) = N'',
    @is_staff BIT = 0,
    @is_superuser BIT = 0,
    @avatar_url NVARCHAR(500) = NULL,
    @currency NVARCHAR(10) = N'VND'
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (SELECT 1 FROM dbo.auth_user WHERE username = @username)
    BEGIN
        RAISERROR(N'Username da ton tai.', 16, 1);
        RETURN;
    END

    IF EXISTS (SELECT 1 FROM dbo.auth_user WHERE email = @email)
    BEGIN
        RAISERROR(N'Email da ton tai.', 16, 1);
        RETURN;
    END

    INSERT INTO dbo.auth_user (
        password, last_login, is_superuser, username, first_name, last_name,
        email, is_staff, is_active, date_joined
    )
    VALUES (
        @password_hash, NULL, @is_superuser, @username, @first_name, @last_name,
        @email, CASE WHEN @is_superuser = 1 THEN 1 ELSE @is_staff END, 1, GETDATE()
    );

    DECLARE @new_user_id BIGINT = SCOPE_IDENTITY();

    INSERT INTO dbo.finance_userprofile (user_id, avatar_url, currency)
    VALUES (@new_user_id, @avatar_url, @currency);

    SELECT @new_user_id AS created_user_id;
END;
GO

PRINT N'FinSmartDB tao thanh cong!';
PRINT N'Cac bang: auth_user, finance_userprofile, finance_category, finance_transaction, finance_budget, finance_goal, finance_chatmessage, finance_aisuggestion';
PRINT N'Cac view: vw_user_summary, vw_expense_by_category';
PRINT N'Stored procedure: sp_monthly_report, sp_admin_create_user';
GO


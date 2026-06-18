-- NekoCafé 数据库初始化脚本
-- 自动在 PostgreSQL 容器首次启动时执行

-- ===== 预约服务表 =====
CREATE TABLE IF NOT EXISTS reservations (
    id              VARCHAR(64) PRIMARY KEY,
    store_id        VARCHAR(32) NOT NULL,
    customer_id     VARCHAR(32) NOT NULL,
    date            DATE NOT NULL,
    time_slot       VARCHAR(16) NOT NULL,
    guest_count     INTEGER NOT NULL CHECK (guest_count BETWEEN 1 AND 20),
    table_type      VARCHAR(16) DEFAULT 'standard',
    status          VARCHAR(16) DEFAULT 'PENDING'
                    CHECK (status IN ('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED', 'NO_SHOW')),
    remark          VARCHAR(200) DEFAULT '',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    expires_at      TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '15 minutes'),

    CONSTRAINT uq_store_slot UNIQUE (store_id, date, time_slot, status)
);

CREATE INDEX IF NOT EXISTS idx_reservations_customer ON reservations(customer_id);
CREATE INDEX IF NOT EXISTS idx_reservations_store_date ON reservations(store_id, date);
CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status);

-- ===== 时段容量表 =====
CREATE TABLE IF NOT EXISTS time_slots (
    store_id        VARCHAR(32) NOT NULL,
    date            DATE NOT NULL,
    time_slot       VARCHAR(16) NOT NULL,
    total_capacity  INTEGER NOT NULL DEFAULT 10,
    booked_count    INTEGER NOT NULL DEFAULT 0,
    version         INTEGER NOT NULL DEFAULT 0,  -- 乐观锁

    PRIMARY KEY (store_id, date, time_slot)
);

-- ===== 门店表 =====
CREATE TABLE IF NOT EXISTS stores (
    id              VARCHAR(32) PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    address         VARCHAR(200),
    phone           VARCHAR(20),
    open_time       TIME NOT NULL DEFAULT '10:00',
    close_time      TIME NOT NULL DEFAULT '22:00',
    max_guest       INTEGER NOT NULL DEFAULT 50,
    status          VARCHAR(16) DEFAULT 'ACTIVE',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 插入默认门店数据
INSERT INTO stores (id, name, address, phone, max_guest) VALUES
    ('store_001', 'NekoCafé 五道口旗舰店', '北京市海淀区成府路28号', '010-8888-0001', 60),
    ('store_002', 'NekoCafé 国贸店', '北京市朝阳区建国门外大街1号', '010-8888-0002', 40),
    ('store_003', 'NekoCafé 望京店', '北京市朝阳区望京街10号', '010-8888-0003', 45)
ON CONFLICT (id) DO NOTHING;

-- ===== 会员服务表 (member 数据库) =====
CREATE DATABASE nekocafe_member;
\c nekocafe_member;

CREATE TABLE IF NOT EXISTS members (
    id              VARCHAR(64) PRIMARY KEY,
    phone           VARCHAR(20) UNIQUE NOT NULL,
    nickname        VARCHAR(50) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    level           VARCHAR(16) DEFAULT 'BRONZE'
                    CHECK (level IN ('BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND')),
    points          INTEGER DEFAULT 0,
    total_spent     DECIMAL(10,2) DEFAULT 0.00,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_members_phone ON members(phone);
CREATE INDEX IF NOT EXISTS idx_members_level ON members(level);

-- ===== 积分记录表 =====
CREATE TABLE IF NOT EXISTS points_records (
    id              SERIAL PRIMARY KEY,
    member_id       VARCHAR(64) NOT NULL REFERENCES members(id),
    amount          INTEGER NOT NULL,
    reason          VARCHAR(100) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_points_member ON points_records(member_id);

-- Create analytics database
CREATE DATABASE IF NOT EXISTS analytics;

-- Events table - raw events from the game
CREATE TABLE IF NOT EXISTS analytics.events
(
    event_id UUID DEFAULT generateUUIDv4(),
    event_type String,
    tg_id Int64,
    event_data String,
    event_time DateTime DEFAULT now(),
    session_id String,
    game_version String DEFAULT ''
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_type, tg_id, event_time)
TTL event_time + INTERVAL 365 DAY;

-- Sessions table
CREATE TABLE IF NOT EXISTS analytics.sessions
(
    session_id String,
    tg_id Int64,
    start_time DateTime,
    end_time DateTime DEFAULT now(),
    duration_seconds UInt32 DEFAULT 0,
    events_count UInt32 DEFAULT 0,
    game_version String DEFAULT '',
    _version UInt64 DEFAULT 1
)
ENGINE = ReplacingMergeTree(_version)
PARTITION BY toYYYYMM(start_time)
ORDER BY (session_id, tg_id);

-- Users first touch - track when users first appeared
CREATE TABLE IF NOT EXISTS analytics.users_first_touch
(
    tg_id Int64,
    first_seen DateTime,
    first_session_id String,
    referral_source String DEFAULT '',
    game_version String DEFAULT '',
    _version UInt64 DEFAULT 1
)
ENGINE = ReplacingMergeTree(_version)
ORDER BY tg_id;

-- Payments table
CREATE TABLE IF NOT EXISTS analytics.payments
(
    payment_id String,
    tg_id Int64,
    amount_stars UInt32,
    payment_type String,
    payment_status String DEFAULT 'pending',
    payment_time DateTime DEFAULT now(),
    game_version String DEFAULT '',
    _version UInt64 DEFAULT 1
)
ENGINE = ReplacingMergeTree(_version)
PARTITION BY toYYYYMM(payment_time)
ORDER BY (payment_id, tg_id);

-- Daily aggregates
CREATE TABLE IF NOT EXISTS analytics.daily_aggregates
(
    date Date,
    dau UInt32 DEFAULT 0,
    new_users UInt32 DEFAULT 0,
    sessions_count UInt32 DEFAULT 0,
    total_revenue_stars UInt32 DEFAULT 0,
    avg_session_duration Float32 DEFAULT 0,
    _version UInt64 DEFAULT 1
)
ENGINE = ReplacingMergeTree(_version)
ORDER BY date;

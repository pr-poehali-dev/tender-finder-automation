CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE,
    email VARCHAR(255) UNIQUE,
    username VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_premium BOOLEAN DEFAULT FALSE,
    free_requests_used INTEGER DEFAULT 0,
    free_requests_limit INTEGER DEFAULT 5
);

CREATE TABLE IF NOT EXISTS usage_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    prompt TEXT NOT NULL,
    generated_code TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_free BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_usage_history_user_id ON usage_history(user_id);

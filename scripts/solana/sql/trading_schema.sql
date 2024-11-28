-- Virtual Wallets Table
CREATE TABLE IF NOT EXISTS virtual_wallets (
    user_id INTEGER REFERENCES users(user_id),
    balance NUMERIC(20,9) DEFAULT 1000.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id)
);

-- Positions Table
CREATE TABLE IF NOT EXISTS positions (
    position_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    token_address VARCHAR(44) REFERENCES solana_tokens(token_address),
    entry_price_sol NUMERIC(20,9),
    current_price_sol NUMERIC(20,9),
    size_sol NUMERIC(20,9),
    position_type VARCHAR(10),
    leverage NUMERIC(5,2) DEFAULT 1.0,
    status VARCHAR(20) DEFAULT 'open',
    pnl_sol NUMERIC(20,9),
    entry_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    close_timestamp TIMESTAMP,
    CONSTRAINT valid_position_type CHECK (position_type IN ('long', 'short'))
);

-- Update Timestamp Function
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for Virtual Wallets
DROP TRIGGER IF EXISTS update_wallet_timestamp ON virtual_wallets;
CREATE TRIGGER update_wallet_timestamp
    BEFORE UPDATE ON virtual_wallets
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_open_positions 
    ON positions(user_id) 
    WHERE status = 'open';

CREATE INDEX IF NOT EXISTS idx_token_positions 
    ON positions(token_address, status);

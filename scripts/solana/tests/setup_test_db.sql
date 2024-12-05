-- Drop existing tables if they exist
DROP TABLE IF EXISTS token_prices CASCADE;
DROP TABLE IF EXISTS solana_tokens CASCADE;

-- Create tokens table
CREATE TABLE IF NOT EXISTS solana_tokens (
    token_address TEXT PRIMARY KEY,
    is_active BOOLEAN DEFAULT true,
    last_update TIMESTAMP WITH TIME ZONE
);

-- Create prices table
CREATE TABLE IF NOT EXISTS token_prices (
    token_address TEXT REFERENCES solana_tokens(token_address),
    price_sol NUMERIC,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_token_prices_token_address ON token_prices(token_address);
CREATE INDEX IF NOT EXISTS idx_token_prices_timestamp ON token_prices(timestamp);

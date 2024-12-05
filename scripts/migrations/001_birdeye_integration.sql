-- Migration: Add Birdeye Integration Support
-- Description: Updates schema to support Birdeye API price data and tracking

BEGIN;

-- 1. Add Birdeye-specific fields to existing solana_tokens table
ALTER TABLE solana_tokens
    ADD COLUMN IF NOT EXISTS birdeye_id VARCHAR(44),
    ADD COLUMN IF NOT EXISTS birdeye_metadata JSONB DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS last_birdeye_update TIMESTAMP,
    ADD COLUMN IF NOT EXISTS verification_status VARCHAR(20) DEFAULT 'unverified';

-- 2. Add Birdeye-specific fields to existing token_prices table
ALTER TABLE token_prices
    ADD COLUMN IF NOT EXISTS source VARCHAR(20) DEFAULT 'rpc',
    ADD COLUMN IF NOT EXISTS source_timestamp TIMESTAMP,
    ADD COLUMN IF NOT EXISTS source_latency INTEGER,
    ADD COLUMN IF NOT EXISTS confidence_score NUMERIC(5,2),
    ADD COLUMN IF NOT EXISTS price_metadata JSONB DEFAULT '{}';

-- 3. Add Birdeye-specific fields to existing token_metrics table
ALTER TABLE token_metrics
    ADD COLUMN IF NOT EXISTS birdeye_volume_24h NUMERIC(20,9),
    ADD COLUMN IF NOT EXISTS birdeye_liquidity NUMERIC(20,9),
    ADD COLUMN IF NOT EXISTS data_source VARCHAR(20) DEFAULT 'rpc';

-- 4. Create price source tracking table
CREATE TABLE IF NOT EXISTS price_source_stats (
    id SERIAL PRIMARY KEY,
    source VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    request_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    average_latency INTEGER,
    rate_limit_hits INTEGER DEFAULT 0,
    CONSTRAINT unique_source_timestamp UNIQUE (source, timestamp)
);

-- 5. Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_token_prices_source 
    ON token_prices(source, timestamp DESC);
    
CREATE INDEX IF NOT EXISTS idx_token_birdeye_update 
    ON solana_tokens(last_birdeye_update) 
    WHERE verification_status = 'verified';

CREATE INDEX IF NOT EXISTS idx_price_source_stats_timestamp
    ON price_source_stats(timestamp DESC);

-- 6. Create function to update source stats
CREATE OR REPLACE FUNCTION update_price_source_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Round timestamp to minute for aggregation
    WITH rounded_time AS (
        SELECT date_trunc('minute', NEW.source_timestamp) as minute_timestamp
    )
    INSERT INTO price_source_stats (
        source, 
        timestamp, 
        request_count,
        success_count,
        average_latency
    )
    SELECT
        NEW.source,
        minute_timestamp,
        1,
        1,
        NEW.source_latency
    FROM rounded_time
    ON CONFLICT (source, timestamp) DO UPDATE
    SET 
        request_count = price_source_stats.request_count + 1,
        success_count = price_source_stats.success_count + 1,
        average_latency = (
            price_source_stats.average_latency * price_source_stats.request_count + 
            NEW.source_latency
        ) / (price_source_stats.request_count + 1);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 7. Create trigger for stats tracking
DROP TRIGGER IF EXISTS trg_update_price_stats ON token_prices;
CREATE TRIGGER trg_update_price_stats
    AFTER INSERT ON token_prices
    FOR EACH ROW
    EXECUTE FUNCTION update_price_source_stats();

-- 8. Create view for monitoring
CREATE OR REPLACE VIEW v_price_source_performance AS
WITH hourly_stats AS (
    SELECT 
        source,
        date_trunc('hour', timestamp) as hour,
        sum(request_count) as total_requests,
        sum(success_count) as successful_requests,
        sum(error_count) as failed_requests,
        avg(average_latency) as avg_latency,
        sum(rate_limit_hits) as rate_limits
    FROM price_source_stats
    WHERE timestamp > NOW() - INTERVAL '24 hours'
    GROUP BY source, date_trunc('hour', timestamp)
)
SELECT 
    source,
    hour,
    total_requests,
    successful_requests,
    failed_requests,
    avg_latency,
    rate_limits,
    CASE 
        WHEN total_requests > 0 THEN 
            (successful_requests::float / total_requests * 100)
        ELSE 0 
    END as success_rate
FROM hourly_stats
ORDER BY hour DESC, source;

COMMIT;

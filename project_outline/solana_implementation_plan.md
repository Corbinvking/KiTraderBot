# Enhanced Solana Implementation Plan for KiTraderBot

## System Context
- Running on Ubuntu with PostgreSQL 16.4
- Python 3.12 virtual environment
- Systemd managed service (kitraderbot.service)
- Existing user management system with role-based access
- Database-driven architecture with asyncpg

## 1. Infrastructure Preparation
### 1.1 Database Extensions
```sql
-- Add required extensions for JSONB and crypto functions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enhance existing tables
ALTER TABLE user_settings 
ADD COLUMN IF NOT EXISTS solana_preferences JSONB DEFAULT '{
    "max_position_size": 100,
    "default_slippage": 1.0,
    "risk_level": "medium"
}'::jsonb;
```

### 1.2 New Schema Implementation
```sql
-- Token tracking with enhanced metadata
CREATE TABLE solana_tokens (
    token_address VARCHAR(44) PRIMARY KEY,
    symbol VARCHAR(20),
    name VARCHAR(100),
    decimals INTEGER,
    first_seen_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',
    risk_score NUMERIC(5,2),
    verification_status VARCHAR(20) DEFAULT 'unverified',
    CONSTRAINT valid_address CHECK (token_address ~ '^[1-9A-HJ-NP-Za-km-z]{32,44}$')
);

-- Enhanced price tracking
CREATE TABLE token_prices (
    id SERIAL PRIMARY KEY,
    token_address VARCHAR(44) REFERENCES solana_tokens(token_address),
    price_sol NUMERIC(20,9),
    price_usd NUMERIC(20,9),
    volume_24h_sol NUMERIC(20,9),
    liquidity_sol NUMERIC(20,9),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50),
    confidence_score NUMERIC(3,2)
);

-- Market metrics for analysis
CREATE TABLE token_metrics (
    token_address VARCHAR(44) REFERENCES solana_tokens(token_address),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    holders_count INTEGER,
    transactions_24h INTEGER,
    volume_24h_sol NUMERIC(20,9),
    price_change_24h NUMERIC(10,2),
    market_cap_sol NUMERIC(20,9),
    liquidity_change_24h NUMERIC(10,2),
    PRIMARY KEY (token_address, timestamp)
);

-- Enhanced simulated trades
CREATE TABLE simulated_trades (
    trade_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    token_address VARCHAR(44) REFERENCES solana_tokens(token_address),
    entry_price_sol NUMERIC(20,9),
    position_size_sol NUMERIC(20,9),
    leverage NUMERIC(5,2) DEFAULT 1.0,
    trade_type VARCHAR(10) CHECK (trade_type IN ('long', 'short')),
    status VARCHAR(20) DEFAULT 'open',
    entry_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exit_timestamp TIMESTAMP,
    exit_price_sol NUMERIC(20,9),
    pnl_sol NUMERIC(20,9),
    fees_sol NUMERIC(20,9),
    slippage_percent NUMERIC(5,2),
    execution_details JSONB
);

-- Indexes for performance
CREATE INDEX idx_token_prices_timestamp ON token_prices(timestamp DESC);
CREATE INDEX idx_token_address_status ON solana_tokens(token_address) WHERE is_active = true;
CREATE INDEX idx_open_trades ON simulated_trades(user_id) WHERE status = 'open';
```

## 2. Core Components Implementation

### 2.1 Solana RPC Manager
```python
class SolanaRPCManager:
    def __init__(self):
        self.endpoints = {
            'primary': 'https://api.mainnet-beta.solana.com',
            'backup': [
                'https://solana-api.projectserum.com',
                'https://rpc.ankr.com/solana'
            ]
        }
        self.current_endpoint = None
        self.web3 = None
        self.retry_count = 3
        self.timeout = 10
        self.last_request_time = {}  # Rate limiting
        
    async def initialize(self):
        """Setup connection pool and health checks"""
        pass

    async def get_token_data(self, token_address: str):
        """Fetch token metadata and current state"""
        pass

    async def monitor_mempool(self):
        """Watch for new token creations and trades"""
        pass
```

### 2.2 Token Tracking System
```python
class TokenTracker:
    def __init__(self, rpc_manager: SolanaRPCManager, db_pool):
        self.rpc = rpc_manager
        self.db = db_pool
        self.tracked_tokens = {}
        self.price_feeds = {}
        self.update_interval = 60  # seconds
        
    async def track_new_token(self, token_address: str):
        """Add new token to tracking system"""
        pass

    async def update_prices(self):
        """Update price data for all tracked tokens"""
        pass

    async def calculate_metrics(self, token_address: str):
        """Calculate and store token metrics"""
        pass
```

### 2.3 Trading Engine
```python
class SimulatedTrading:
    def __init__(self, db_pool, token_tracker: TokenTracker):
        self.db = db_pool
        self.tracker = token_tracker
        self.position_limits = {
            'basic': 100,
            'premium': 1000,
            'admin': float('inf')
        }
        
    async def execute_trade(self, user_id: int, token_address: str, 
                          amount_sol: float, trade_type: str):
        """Execute a simulated trade"""
        pass

    async def calculate_pnl(self, trade_id: int):
        """Calculate current PnL for a trade"""
        pass
```

## 3. Integration with Existing Bot

### 3.1 New Command Handlers
```python
@restricted(UserRole.BASIC)
async def cmd_token_info(update: Update, context: CallbackContext):
    """Handler for /info command"""
    pass

@restricted(UserRole.BASIC)
async def cmd_trade(update: Update, context: CallbackContext):
    """Handler for /trade command"""
    pass

@restricted(UserRole.PREMIUM)
async def cmd_analyze(update: Update, context: CallbackContext):
    """Handler for /analyze command"""
    pass
```

### 3.2 User Interface Enhancements
```python
class TradingKeyboard:
    """Custom keyboard layouts for trading"""
    @staticmethod
    def trade_options(token_address: str):
        """Create trading option buttons"""
        pass

    @staticmethod
    def position_management():
        """Create position management buttons"""
        pass
```

## 4. Implementation Timeline

### Week 1: Database & Infrastructure
- Day 1-2: Database schema implementation
- Day 3-4: RPC manager setup and testing
- Day 5: Integration with existing user system

### Week 2: Token Tracking
- Day 1-2: Token discovery system
- Day 3-4: Price tracking implementation
- Day 5: Metrics calculation system

### Week 3: Trading Engine
- Day 1-2: Simulated trading core
- Day 3-4: Position management
- Day 5: Risk management implementation

### Week 4: Bot Integration
- Day 1-2: Command handlers
- Day 3-4: User interface implementation
- Day 5: Testing and optimization

## 5. Testing Strategy

### 5.1 Unit Tests
```python
class TestSolanaIntegration(unittest.TestCase):
    async def test_rpc_connection(self):
        pass
    
    async def test_token_tracking(self):
        pass
    
    async def test_trade_execution(self):
        pass
```

### 5.2 Integration Tests
- RPC failover scenarios
- Database consistency checks
- Command handler validation

### 5.3 Load Testing
- Multiple concurrent users
- High-frequency price updates
- Large position calculations

## 6. Monitoring & Maintenance

### 6.1 Health Checks
```python
async def health_check():
    """Verify system components"""
    checks = {
        'rpc': check_rpc_connection(),
        'database': check_db_connection(),
        'token_tracking': check_token_updates(),
        'trading_engine': check_trade_execution()
    }
    return checks
```

### 6.2 Alerting
- RPC connection issues
- Database performance problems
- Trading engine anomalies
- Token tracking delays

## Next Steps
1. Verify current database state and permissions
2. Install required Solana packages
3. Implement database schema changes
4. Begin RPC manager implementation

Would you like to proceed with any specific aspect of this plan? 

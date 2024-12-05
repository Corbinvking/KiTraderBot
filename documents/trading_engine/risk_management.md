# Risk Management Parameters Guide

## Position Limits

### Size Limits
- Minimum position size: 0.1 SOL
- Maximum position size: 100.0 SOL
- Maximum positions per user: 5

### Exposure Limits
- Per-token exposure limit: 25% of total balance
- Total exposure limit: 75% of total balance
- Maximum positions per direction: 3 (long/short)

### Account Tiers
```python
position_limits = {
    'basic': 100.0,     # 100 SOL
    'premium': 1000.0,  # 1000 SOL
    'admin': inf        # No limit
}
```

## Risk Checks

### 1. Balance Validation
- Validates user has sufficient balance
- Checks locked collateral limits
- Prevents negative balances

### 2. Position Concentration
- Maximum 3 positions per direction (long/short)
- Prevents over-concentration in single token
- Enforces diversification requirements

### 3. Price Volatility
- Monitors 10-period price volatility
- Blocks trades when volatility > 10%
- Protects against market turbulence

### 4. Transaction Safety
- Uses database transactions
- Implements position locking
- Prevents race conditions

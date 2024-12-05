# Trading Engine Integration Guide

## Integration with TokenTracker

### Basic Setup
```python
from KiTraderBot.scripts.solana.token_tracker import TokenTracker
from KiTraderBot.scripts.solana.trading_engine import TradingEngine
from KiTraderBot.scripts.solana.birdeye_client import BirdeyeClient

# Initialize components
birdeye_client = BirdeyeClient()
token_tracker = TokenTracker(db_pool, birdeye_client)
trading_engine = TradingEngine(db_pool, token_tracker, birdeye_client)

# Initialize database tables
await trading_engine.initialize()
```

### Opening a Position
```python
# First ensure token is tracked
await token_tracker.track_token(token_address)

# Open position
position = await trading_engine.open_position(
    user_id=1,
    token_address=token_address,
    size_sol=Decimal('1.0'),
    position_type='long'
)
```

### Position Management
```python
# Get user's positions
positions = await trading_engine.get_user_positions(
    user_id=1,
    status='open'
)

# Get position history
history = await trading_engine.get_position_history(
    position_id=position['position_id'],
    include_price_updates=True
)

# Close position
result = await trading_engine.close_position(position['position_id'])
```

### Risk Validation
```python
# Validate before opening position
valid, message = await trading_engine.validate_position_risk(
    user_id=1,
    token_address=token_address,
    size_sol=Decimal('1.0'),
    position_type='long'
)

if valid:
    position = await trading_engine.open_position(...)
else:
    print(f"Risk check failed: {message}")
```

### Error Handling
```python
try:
    position = await trading_engine.open_position(...)
except ValueError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Trading error: {e}")
```

## Best Practices

1. Always validate positions before opening
2. Use proper error handling
3. Clean up resources when done
4. Monitor position limits
5. Track trading history

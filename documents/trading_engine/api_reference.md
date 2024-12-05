# Trading Engine API Reference

## Position Management

### open_position
```python
async def open_position(
    user_id: int,
    token_address: str,
    size_sol: Decimal,
    position_type: str  # 'long' or 'short'
) -> Optional[Dict]
```
Opens a new trading position.

**Parameters:**
- `user_id`: User identifier
- `token_address`: Solana token address
- `size_sol`: Position size in SOL
- `position_type`: Either 'long' or 'short'

**Returns:**
```python
{
    'position_id': int,
    'size': Decimal,
    'type': str,
    'entry_price': Decimal
}
```

### close_position
```python
async def close_position(position_id: int) -> Optional[Dict]
```
Closes an existing position.

**Parameters:**
- `position_id`: Position identifier

**Returns:**
```python
{
    'position_id': int,
    'exit_price': Decimal,
    'pnl': Decimal
}
```

### get_user_positions
```python
async def get_user_positions(
    user_id: int,
    status: str = 'open',  # 'open', 'closed', 'all'
    limit: int = 50,
    offset: int = 0
) -> List[Dict]
```
Retrieves user's positions with pagination.

**Parameters:**
- `user_id`: User identifier
- `status`: Filter by position status
- `limit`: Maximum number of records
- `offset`: Pagination offset

### get_position_history
```python
async def get_position_history(
    position_id: int,
    include_price_updates: bool = False
) -> Dict
```
Gets detailed history for a position.

**Parameters:**
- `position_id`: Position identifier
- `include_price_updates`: Include price history

### validate_position_risk
```python
async def validate_position_risk(
    user_id: int,
    token_address: str,
    size_sol: Decimal,
    position_type: str
) -> Tuple[bool, str]
```
Validates position against risk management rules.

**Parameters:**
- `user_id`: User identifier
- `token_address`: Token address
- `size_sol`: Position size
- `position_type`: Position type

**Returns:**
Tuple of (is_valid: bool, message: str)

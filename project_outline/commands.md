# KiTraderBot Commands Implementation Plan

## Core Commands

### Basic Commands
- [x] /start - Welcome message and introduction
- [x] /help - Show available commands and usage
- [ ] /settings - View and modify user settings

### Wallet Commands
- [x] /wallet - Show wallet balance and summary
- [x] /positions - List open positions
- [x] /positions closed - List closed positions

### Trading Commands
- [x] /open <token_address> <size_sol> <type> - Open new position
- [x] /close <position_id> - Close existing position
- [ ] /price <token_address> - Get current token price
- [ ] /info <token_address> - Get token information

### Admin Commands
- [x] /adduser <username> <role> - Add new user (admin only)
- [x] /removeuser <username> - Remove user (admin only)
- [x] /users - List all users (admin only)

## Advanced Features (Phase 2)

### Price Alerts
- [ ] /alert add <token> <price> - Add price alert
- [ ] /alert list - List active alerts
- [ ] /alert remove <alert_id> - Remove alert

### Trading Analytics
- [ ] /stats - Show trading statistics
- [ ] /history - View trading history
- [ ] /performance - Account performance metrics

### Risk Management
- [ ] /risk set <parameter> <value> - Set risk parameters
- [ ] /risk view - View current risk settings
- [ ] /limits - View trading limits

## Implementation Status
- Basic Commands: 100% Complete
- Wallet Commands: 100% Complete
- Trading Commands: 50% Complete
- Admin Commands: 100% Complete
- Advanced Features: 0% Complete

## Command Parameters

### Open Position
- token_address: Solana token address
- size_sol: Position size in SOL
- type: 'long' or 'short'

### Close Position
- position_id: ID of position to close

### Price Alerts
- token: Token symbol or address
- price: Target price level
- alert_id: ID of alert to remove

### Risk Management
- parameter: Risk parameter name
- value: New parameter value

## Command Access Levels
- Basic: All users
- Premium: Premium users only
- Admin: Admin users only

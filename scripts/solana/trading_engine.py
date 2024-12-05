"""
Trading Engine for Solana Token Trading
=====================================

This module implements the core trading functionality:
- Position management
- Virtual wallet handling
- PnL calculations
- Risk management
"""

import logging
from typing import Optional, Dict, List, Tuple
from datetime import datetime
from decimal import Decimal
import asyncpg
import asyncio

from .token_tracker import TokenTracker
from .birdeye_client import BirdeyeClient

logger = logging.getLogger(__name__)

class TradingEngine:
    """Manages simulated trading operations"""
    
    # Trading limits
    MIN_TRADE_SIZE = Decimal('0.1')  # SOL
    MAX_TRADE_SIZE = Decimal('100.0')  # SOL
    MAX_POSITIONS_PER_USER = 5
    
    def __init__(self, db_pool: asyncpg.Pool, token_tracker: TokenTracker, birdeye_client: BirdeyeClient):
        self.db = db_pool
        self.token_tracker = token_tracker
        self.birdeye = birdeye_client
        self.position_limits = {
            'basic': Decimal('100.0'),    # 100 SOL
            'premium': Decimal('1000.0'), # 1000 SOL
            'admin': Decimal('inf')       # No limit
        }
        self.logger = logging.getLogger(__name__)
        self._lock = asyncio.Lock()

    async def initialize(self):
        """Initialize database tables"""
        async with self.db.acquire() as conn:
            # Create virtual wallets table first
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS virtual_wallets (
                    user_id INTEGER PRIMARY KEY,
                    balance_sol NUMERIC NOT NULL DEFAULT 1000.0 
                        CHECK (balance_sol >= 0 AND balance_sol <= 1000000.0),
                    locked_sol NUMERIC NOT NULL DEFAULT 0.0 
                        CHECK (locked_sol >= 0 AND locked_sol <= 1000000.0),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT total_balance_check CHECK (balance_sol + locked_sol >= 0)
                )
            """)
            
            # Create positions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS trading_positions (
                    position_id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES virtual_wallets(user_id),
                    token_address TEXT NOT NULL REFERENCES solana_tokens(token_address),
                    position_type TEXT CHECK (position_type IN ('long', 'short')),
                    size_sol NUMERIC CHECK (size_sol > 0),
                    entry_price NUMERIC NOT NULL,
                    entry_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    close_price NUMERIC,
                    close_time TIMESTAMP WITH TIME ZONE,
                    pnl NUMERIC,
                    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'closed')),
                    CONSTRAINT valid_size_range 
                        CHECK (size_sol >= 0.1 AND size_sol <= 100.0)
                )
            """)
            
            # Create index for user positions
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_positions 
                ON trading_positions(user_id, status)
            """)
            
            # Create trade history table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS trade_history (
                    trade_id SERIAL PRIMARY KEY,
                    position_id INTEGER REFERENCES trading_positions(position_id),
                    user_id INTEGER NOT NULL REFERENCES virtual_wallets(user_id),
                    token_address TEXT NOT NULL,
                    action TEXT NOT NULL CHECK (action IN ('BUY', 'SELL')),
                    price NUMERIC NOT NULL,
                    size_sol NUMERIC NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create token metadata table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS token_metadata (
                    token_address TEXT PRIMARY KEY REFERENCES solana_tokens(token_address),
                    symbol TEXT NOT NULL,
                    name TEXT NOT NULL,
                    decimals INTEGER NOT NULL DEFAULT 9,
                    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for token lookup
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_token_metadata_symbol 
                ON token_metadata(symbol)
            """)

    async def close(self):
        """Cleanup resources"""
        if hasattr(self, 'birdeye'):
            await self.birdeye.close()

    async def get_token_price(self, token_address: str) -> Optional[Decimal]:
        """Get current token price from Birdeye"""
        try:
            token_info = await self.birdeye.get_token_info(token_address)
            if token_info:
                price = Decimal(str(token_info['mc'] / token_info['liquidity']))
                # Store price in database for history
                async with self.db.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO token_prices (token_address, price_sol, timestamp)
                        VALUES ($1, $2, NOW())
                    """, token_address, price)
                return price
            return None
        except Exception as e:
            self.logger.error(f"Error getting token price: {e}")
            return None

    async def get_wallet(self, user_id: int) -> Optional[Dict]:
        """Get user's virtual wallet"""
        try:
            async with self.db.acquire() as conn:
                wallet = await conn.fetchrow("""
                    SELECT user_id, balance_sol, locked_sol, created_at, last_updated
                    FROM virtual_wallets
                    WHERE user_id = $1
                """, user_id)
                
                if not wallet:
                    # Create new wallet if doesn't exist
                    wallet = await conn.fetchrow("""
                        INSERT INTO virtual_wallets (user_id, balance_sol, locked_sol)
                        VALUES ($1, 1000.0, 0.0)
                        RETURNING user_id, balance_sol, locked_sol, created_at, last_updated
                    """, user_id)
                
                return dict(wallet)
        except Exception as e:
            self.logger.error(f"Error getting wallet for user {user_id}: {e}")
            return None

    async def open_position(
        self,
        user_id: int,
        token_address: str,
        size_sol: Decimal,
        position_type: str
    ) -> Optional[Dict]:
        """Open a new trading position"""
        try:
            # Input validation
            if not isinstance(size_sol, Decimal):
                size_sol = Decimal(str(size_sol))
            
            if size_sol < self.MIN_TRADE_SIZE:
                raise ValueError("Position size too small")
            if size_sol > self.MAX_TRADE_SIZE:
                raise ValueError("Position size too large")
            if position_type not in ('long', 'short'):
                raise ValueError("Invalid position type")
            
            async with self._lock:  # Prevent race conditions
                # Check user's existing positions
                async with self.db.acquire() as conn:
                    position_count = await conn.fetchval("""
                        SELECT COUNT(*) FROM trading_positions
                        WHERE user_id = $1 AND status = 'open'
                    """, user_id)
                    
                    if position_count >= self.MAX_POSITIONS_PER_USER:
                        raise ValueError("Maximum positions reached")
                    
                    # Get current price
                    current_price = await self.get_token_price(token_address)
                    if not current_price:
                        raise ValueError("Could not get current token price")
                    
                    # Start transaction
                    async with conn.transaction():
                        # Update wallet
                        wallet_update = await conn.fetchrow("""
                            UPDATE virtual_wallets
                            SET balance_sol = balance_sol - $1,
                                locked_sol = locked_sol + $1,
                                last_updated = NOW()
                            WHERE user_id = $2
                            AND balance_sol >= $1
                            RETURNING balance_sol, locked_sol
                        """, size_sol, user_id)
                        
                        if not wallet_update:
                            raise ValueError("Insufficient balance")
                        
                        # Create position
                        position = await conn.fetchrow("""
                            INSERT INTO trading_positions (
                                user_id, token_address, position_type,
                                size_sol, entry_price, status
                            ) VALUES ($1, $2, $3, $4, $5, 'open')
                            RETURNING position_id
                        """, user_id, token_address, position_type,
                            size_sol, current_price)
                        
                        # Record in trade history
                        await conn.execute("""
                            INSERT INTO trade_history (
                                position_id, user_id, token_address,
                                action, price, size_sol
                            ) VALUES ($1, $2, $3, $4, $5, $6)
                        """, position['position_id'], user_id, token_address,
                            'BUY', current_price, size_sol)
                        
                        return {
                            'position_id': position['position_id'],
                            'size': size_sol,
                            'type': position_type,
                            'entry_price': current_price
                        }
                        
        except Exception as e:
            self.logger.error(f"Error opening position: {e}")
            raise

    async def close_position(self, position_id: int) -> Optional[Dict]:
        """Close an existing position"""
        try:
            async with self.db.acquire() as conn:
                # Get position details
                position = await conn.fetchrow("""
                    SELECT * FROM trading_positions
                    WHERE position_id = $1 AND status = 'open'
                """, position_id)

                if not position:
                    raise ValueError("Position not found or already closed")

                # Get current price
                current_price = await self.get_token_price(position['token_address'])
                if not current_price:
                    raise ValueError("Could not get current token price")

                # Calculate PnL
                if position['position_type'] == 'long':
                    pnl = (current_price - position['entry_price']) * position['size_sol']
                else:
                    pnl = (position['entry_price'] - current_price) * position['size_sol']

                async with conn.transaction():
                    # Update position
                    await conn.execute("""
                        UPDATE trading_positions
                        SET status = 'closed',
                            close_price = $1,
                            pnl = $2,
                            close_time = NOW()
                        WHERE position_id = $3
                    """, current_price, pnl, position_id)

                    # Record closing trade in history
                    await conn.execute("""
                        INSERT INTO trade_history (
                            position_id, user_id, token_address,
                            action, price, size_sol
                        ) VALUES ($1, $2, $3, $4, $5, $6)
                    """, position_id, position['user_id'], position['token_address'],
                        'SELL', current_price, position['size_sol'])

                    # Update wallet balance (return initial size + pnl)
                    await conn.execute("""
                        UPDATE virtual_wallets
                        SET balance_sol = balance_sol + $1,
                            locked_sol = locked_sol - $2,
                            last_updated = NOW()
                        WHERE user_id = $3
                    """, position['size_sol'] + pnl, position['size_sol'], position['user_id'])

                    return {
                        'position_id': position_id,
                        'exit_price': current_price,
                        'pnl': pnl
                    }

        except Exception as e:
            self.logger.error(f"Error closing position {position_id}: {e}")
            raise

    async def get_positions(self, user_id: int, status: str = 'open') -> List[Dict]:
        """Get user's positions"""
        try:
            async with self.db.acquire() as conn:
                positions = await conn.fetch("""
                    SELECT p.*, t.symbol, t.name
                    FROM positions p
                    LEFT JOIN token_metadata t ON p.token_address = t.token_address
                    WHERE p.user_id = $1 AND p.status = $2
                    ORDER BY p.created_at DESC
                """, user_id, status)

                result = []
                for pos in positions:
                    current_price = await self.get_token_price(pos['token_address'])
                    if current_price:
                        if pos['position_type'] == 'long':
                            pnl = (current_price - pos['entry_price_sol']) * pos['size_sol']
                        else:
                            pnl = (pos['entry_price_sol'] - current_price) * pos['size_sol']
                        
                        result.append({
                            'position_id': pos['position_id'],
                            'symbol': pos['symbol'],
                            'size_sol': pos['size_sol'],
                            'entry_price_sol': pos['entry_price_sol'],
                            'current_price_sol': current_price,
                            'pnl_sol': pnl,
                            'position_type': pos['position_type'],
                            'created_at': pos['created_at']
                        })
                
                return result
                
        except Exception as e:
            self.logger.error(f"Error getting positions: {e}")
            return []

    async def get_user_positions(
        self,
        user_id: int,
        status: str = 'open',
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """Get user's trading positions with pagination"""
        try:
            # Input validation
            if status not in ('open', 'closed', 'all'):
                raise ValueError("Invalid status. Must be 'open', 'closed', or 'all'")
            if limit < 1 or limit > 100:
                raise ValueError("Limit must be between 1 and 100")
            if offset < 0:
                raise ValueError("Offset cannot be negative")
            
            async with self.db.acquire() as conn:
                # Build query based on status
                query = """
                    SELECT 
                        p.position_id,
                        p.token_address,
                        p.position_type,
                        p.size_sol,
                        p.entry_price,
                        p.entry_time,
                        p.close_price,
                        p.close_time,
                        p.pnl,
                        p.status,
                        COALESCE(t.symbol, p.token_address) as token_symbol,  -- Use address as fallback
                        COALESCE(t.name, 'Unknown Token') as token_name
                    FROM trading_positions p
                    LEFT JOIN token_metadata t ON p.token_address = t.token_address
                    WHERE p.user_id = $1
                """
                
                params = [user_id]
                if status != 'all':
                    query += " AND p.status = $2"
                    params.append(status)
                    
                # Add ordering and pagination
                query += """
                    ORDER BY p.entry_time DESC
                    LIMIT ${}
                    OFFSET ${}
                """.format(len(params) + 1, len(params) + 2)
                params.extend([limit, offset])
                
                # Execute query
                rows = await conn.fetch(query, *params)
                
                # Format results
                positions = []
                for row in rows:
                    position = dict(row)
                    
                    # Get current price for open positions
                    if position['status'] == 'open':
                        current_price = await self.get_token_price(position['token_address'])
                        if current_price:
                            # Calculate unrealized PnL
                            if position['position_type'] == 'long':
                                position['unrealized_pnl'] = (current_price - position['entry_price']) * position['size_sol']
                            else:
                                position['unrealized_pnl'] = (position['entry_price'] - current_price) * position['size_sol']
                            position['current_price'] = current_price
                    
                    positions.append(position)
                    
                return positions
                
        except Exception as e:
            self.logger.error(f"Error getting positions for user {user_id}: {e}")
            raise

    async def get_position_history(
        self,
        position_id: int,
        include_price_updates: bool = False
    ) -> Dict:
        """Get detailed history for a position"""
        try:
            async with self.db.acquire() as conn:
                # Get position details
                position = await conn.fetchrow("""
                    SELECT 
                        p.*,
                        COALESCE(t.symbol, p.token_address) as token_symbol,
                        COALESCE(t.name, 'Unknown Token') as token_name
                    FROM trading_positions p
                    LEFT JOIN token_metadata t ON p.token_address = t.token_address
                    WHERE p.position_id = $1
                """, position_id)
                
                if not position:
                    raise ValueError("Position not found")
                
                # Convert to dict and calculate metrics
                history = dict(position)
                
                # Get trade history
                trades = await conn.fetch("""
                    SELECT action, price, size_sol, timestamp
                    FROM trade_history
                    WHERE position_id = $1
                    ORDER BY timestamp ASC
                """, position_id)
                history['trades'] = [dict(t) for t in trades]
                
                # Include price updates if requested
                if include_price_updates:
                    price_updates = await conn.fetch("""
                        SELECT price_sol, timestamp
                        FROM token_prices
                        WHERE token_address = $1
                        AND timestamp BETWEEN $2 AND COALESCE($3, NOW())
                        ORDER BY timestamp ASC
                    """, position['token_address'], 
                        position['entry_time'],
                        position['close_time'])
                    history['price_updates'] = [dict(p) for p in price_updates]
                
                # Calculate metrics
                if history['status'] == 'closed':
                    history['duration'] = (history['close_time'] - history['entry_time']).total_seconds()
                    history['roi'] = (history['pnl'] / (history['size_sol'] * history['entry_price'])) * 100
                else:
                    # Get current price for open positions
                    current_price = await self.get_token_price(position['token_address'])
                    if current_price:
                        if position['position_type'] == 'long':
                            unrealized_pnl = (current_price - position['entry_price']) * position['size_sol']
                        else:
                            unrealized_pnl = (position['entry_price'] - current_price) * position['size_sol']
                        history['current_price'] = current_price
                        history['unrealized_pnl'] = unrealized_pnl
                        history['unrealized_roi'] = (unrealized_pnl / (history['size_sol'] * history['entry_price'])) * 100
                
                return history
                
        except Exception as e:
            self.logger.error(f"Error getting position history for {position_id}: {e}")
            raise

    async def validate_position_risk(
        self,
        user_id: int,
        token_address: str,
        size_sol: Decimal,
        position_type: str
    ) -> Tuple[bool, str]:
        """Validate position against risk management rules"""
        try:
            async with self.db.acquire() as conn:
                # 1. Check user's total exposure
                total_exposure = await conn.fetchval("""
                    SELECT COALESCE(SUM(size_sol), 0)
                    FROM trading_positions
                    WHERE user_id = $1 AND status = 'open'
                """, user_id)
                
                # Get user's wallet
                wallet = await self.get_wallet(user_id)
                if not wallet:
                    return False, "Wallet not found"
                    
                total_balance = wallet['balance_sol'] + wallet['locked_sol']
                
                # Calculate exposure ratio
                current_exposure_ratio = total_exposure / total_balance if total_balance > 0 else 0
                new_exposure_ratio = (total_exposure + size_sol) / total_balance if total_balance > 0 else float('inf')
                
                # 2. Risk checks
                # Maximum exposure per token (25% of total balance)
                token_exposure = await conn.fetchval("""
                    SELECT COALESCE(SUM(size_sol), 0)
                    FROM trading_positions
                    WHERE user_id = $1 AND token_address = $2 AND status = 'open'
                """, user_id, token_address)
                
                if (token_exposure + size_sol) > (total_balance * Decimal('0.25')):
                    return False, "Position would exceed per-token exposure limit (25% of balance)"
                
                # Maximum total exposure (75% of total balance)
                if new_exposure_ratio > Decimal('0.75'):
                    return False, "Position would exceed total exposure limit (75% of balance)"
                
                # 3. Position concentration
                open_positions = await conn.fetch("""
                    SELECT position_type, COUNT(*) as count
                    FROM trading_positions
                    WHERE user_id = $1 AND status = 'open'
                    GROUP BY position_type
                """, user_id)
                
                position_counts = {p['position_type']: p['count'] for p in open_positions}
                
                # Maximum positions per direction (3 long, 3 short)
                if position_counts.get(position_type, 0) >= 3:
                    return False, f"Maximum {position_type} positions reached (3)"
                
                # 4. Price volatility check
                price_history = await conn.fetch("""
                    SELECT price_sol
                    FROM token_prices
                    WHERE token_address = $1
                    ORDER BY timestamp DESC
                    LIMIT 10
                """, token_address)
                
                if len(price_history) >= 2:
                    prices = [p['price_sol'] for p in price_history]
                    max_price = max(prices)
                    min_price = min(prices)
                    volatility = (max_price - min_price) / min_price if min_price > 0 else 0
                    
                    if volatility > Decimal('0.1'):  # 10% volatility threshold
                        return False, "Token price too volatile (>10% range)"
                
                return True, "Position passes risk checks"
                
        except Exception as e:
            self.logger.error(f"Error validating position risk: {e}")
            return False, f"Risk validation error: {str(e)}"


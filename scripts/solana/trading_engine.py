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
from typing import Optional, Dict, List
from datetime import datetime
import asyncpg
from decimal import Decimal

from .token_tracker import TokenTracker
from ..user_management import UserManager

logger = logging.getLogger(__name__)

class Position:
    """Represents a trading position"""
    def __init__(self, 
                 position_id: int,
                 user_id: int, 
                 token_address: str, 
                 entry_price: Decimal,
                 size: Decimal,
                 position_type: str,
                 leverage: Decimal = Decimal('1.0')):
        self.position_id = position_id
        self.user_id = user_id
        self.token_address = token_address
        self.entry_price = entry_price
        self.size = size
        self.position_type = position_type
        self.leverage = leverage
        self.status = 'open'
        self.entry_timestamp = datetime.utcnow()
        self.close_timestamp = None
        self.current_price = entry_price
        self.pnl = Decimal('0.0')

    @property
    def value(self) -> Decimal:
        """Calculate position value in SOL"""
        return self.size * self.current_price

    def update_pnl(self, current_price: Decimal) -> Decimal:
        """Update position PnL"""
        self.current_price = current_price
        if self.position_type == 'long':
            self.pnl = (current_price - self.entry_price) * self.size * self.leverage
        else:  # short
            self.pnl = (self.entry_price - current_price) * self.size * self.leverage
        return self.pnl

class TradingEngine:
    """Manages simulated trading operations"""
    
    def __init__(self, db_pool: asyncpg.Pool, token_tracker: TokenTracker, user_manager: UserManager):
        self.db = db_pool
        self.token_tracker = token_tracker
        self.user_manager = user_manager
        self.logger = logging.getLogger(__name__)
        self.position_limits = {
            'basic': Decimal('100.0'),    # 100 SOL
            'premium': Decimal('1000.0'), # 1000 SOL
            'admin': Decimal('inf')       # No limit
        }

    async def get_wallet(self, user_id: int) -> Optional[Dict]:
        """Get user's virtual wallet"""
        try:
            async with self.db.acquire() as conn:
                wallet = await conn.fetchrow("""
                    SELECT user_id, balance, created_at, last_updated
                    FROM virtual_wallets
                    WHERE user_id = $1
                """, user_id)
                
                if not wallet:
                    # Create new wallet if doesn't exist
                    wallet = await conn.fetchrow("""
                        INSERT INTO virtual_wallets (user_id, balance)
                        VALUES ($1, 1000.0)
                        RETURNING user_id, balance, created_at, last_updated
                    """, user_id)
                
                return dict(wallet)
        except Exception as e:
            self.logger.error(f"Error getting wallet for user {user_id}: {e}")
            return None

    async def open_position(self, 
                          user_id: int, 
                          token_address: str, 
                          size_sol: Decimal,
                          position_type: str,
                          leverage: Decimal = Decimal('1.0')) -> Optional[Dict]:
        """Open a new trading position"""
        try:
            # Verify user has enough balance
            wallet = await self.get_wallet(user_id)
            if not wallet or wallet['balance'] < size_sol:
                raise ValueError("Insufficient balance")

            # Get current token price
            token_price = await self.token_tracker.get_latest_price(token_address)
            if not token_price:
                raise ValueError("Could not get token price")

            async with self.db.acquire() as conn:
                # Start transaction
                async with conn.transaction():
                    # Create position
                    position = await conn.fetchrow("""
                        INSERT INTO positions (
                            user_id, token_address, entry_price_sol,
                            current_price_sol, size_sol, position_type,
                            leverage, status
                        ) VALUES ($1, $2, $3, $3, $4, $5, $6, 'open')
                        RETURNING position_id
                    """, user_id, token_address, token_price, 
                        size_sol, position_type, leverage)

                    # Update wallet balance
                    await conn.execute("""
                        UPDATE virtual_wallets
                        SET balance = balance - $1,
                            last_updated = CURRENT_TIMESTAMP
                        WHERE user_id = $2
                    """, size_sol, user_id)

                    return {
                        'position_id': position['position_id'],
                        'entry_price': token_price,
                        'size': size_sol,
                        'type': position_type
                    }

        except Exception as e:
            self.logger.error(f"Error opening position: {e}")
            return None

    async def close_position(self, position_id: int) -> Optional[Dict]:
        """Close an existing position"""
        try:
            async with self.db.acquire() as conn:
                # Get position details
                position = await conn.fetchrow("""
                    SELECT * FROM positions
                    WHERE position_id = $1 AND status = 'open'
                """, position_id)

                if not position:
                    raise ValueError("Position not found or already closed")

                # Get current price
                current_price = await self.token_tracker.get_latest_price(position['token_address'])
                if not current_price:
                    raise ValueError("Could not get token price")

                # Calculate PnL
                pnl = self._calculate_pnl(
                    position['position_type'],
                    position['entry_price_sol'],
                    current_price,
                    position['size_sol'],
                    position['leverage']
                )

                async with conn.transaction():
                    # Update position
                    await conn.execute("""
                        UPDATE positions
                        SET status = 'closed',
                            close_timestamp = CURRENT_TIMESTAMP,
                            current_price_sol = $1,
                            pnl_sol = $2
                        WHERE position_id = $3
                    """, current_price, pnl, position_id)

                    # Update wallet balance (return initial size + pnl)
                    await conn.execute("""
                        UPDATE virtual_wallets
                        SET balance = balance + $1,
                            last_updated = CURRENT_TIMESTAMP
                        WHERE user_id = $2
                    """, position['size_sol'] + pnl, position['user_id'])

                    return {
                        'position_id': position_id,
                        'exit_price': current_price,
                        'pnl': pnl
                    }

        except Exception as e:
            self.logger.error(f"Error closing position {position_id}: {e}")
            return None

    async def get_positions(self, user_id: int, status: str = 'open') -> List[Dict]:
        """Get user's positions"""
        try:
            async with self.db.acquire() as conn:
                positions = await conn.fetch("""
                    SELECT p.*, t.symbol, t.name
                    FROM positions p
                    LEFT JOIN solana_tokens t ON p.token_address = t.token_address
                    WHERE p.user_id = $1 AND p.status = $2
                    ORDER BY p.entry_timestamp DESC
                """, user_id, status)
                
                return [dict(pos) for pos in positions]
        except Exception as e:
            self.logger.error(f"Error getting positions for user {user_id}: {e}")
            return []

    def _calculate_pnl(self, 
                      position_type: str,
                      entry_price: Decimal,
                      current_price: Decimal,
                      size: Decimal,
                      leverage: Decimal) -> Decimal:
        """Calculate position PnL"""
        if position_type == 'long':
            return (current_price - entry_price) * size * leverage
        else:  # short
            return (entry_price - current_price) * size * leverage

    async def update_position_prices(self):
        """Update current prices for all open positions"""
        try:
            async with self.db.acquire() as conn:
                # Get all open positions
                positions = await conn.fetch("""
                    SELECT position_id, token_address
                    FROM positions
                    WHERE status = 'open'
                """)
                
                for position in positions:
                    # Get current price
                    current_price = await self.token_tracker.get_latest_price(position['token_address'])
                    if current_price:
                        # Update position price
                        await conn.execute("""
                            UPDATE positions
                            SET current_price_sol = $1,
                                last_updated = CURRENT_TIMESTAMP
                            WHERE position_id = $2
                        """, current_price, position['position_id'])
                        
        except Exception as e:
            self.logger.error(f"Error updating position prices: {e}")

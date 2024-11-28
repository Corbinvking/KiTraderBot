"""
Solana Token Tracker
==================

Tracks token prices and updates database
"""

import logging
from typing import Optional, Dict
from decimal import Decimal
import asyncpg
from datetime import datetime

from .rpc_manager import SolanaRPCManager

logger = logging.getLogger(__name__)

class TokenTracker:
    """Tracks Solana token prices and information"""
    
    def __init__(self, rpc_manager: SolanaRPCManager, db_pool: asyncpg.Pool):
        self.rpc = rpc_manager
        self.db = db_pool
        self.logger = logging.getLogger(__name__)

    async def update_token_price(self, token_address: str) -> Optional[Decimal]:
        """Update token price in database"""
        try:
            # Get price from RPC
            price = await self.rpc.get_token_price(token_address)
            if not price:
                return None

            # Store in database
            async with self.db.acquire() as conn:
                await conn.execute("""
                    INSERT INTO token_prices (
                        token_address, price_sol, timestamp
                    ) VALUES ($1, $2, $3)
                """, token_address, price, datetime.utcnow())

            return price
            
        except Exception as e:
            self.logger.error(f"Error updating token price: {e}")
            return None

    async def get_token_info(self, token_address: str) -> Optional[Dict]:
        """Get token information"""
        try:
            async with self.db.acquire() as conn:
                info = await conn.fetchrow("""
                    SELECT token_address, symbol, name, decimals
                    FROM solana_tokens
                    WHERE token_address = $1
                """, token_address)
                
                if info:
                    return dict(info)
                    
                # If not in database, fetch from RPC
                supply = await self.rpc.get_token_supply(token_address)
                if supply:
                    # Add to database
                    info = await conn.fetchrow("""
                        INSERT INTO solana_tokens (
                            token_address, symbol, name, decimals, total_supply
                        ) VALUES ($1, $2, $3, $4, $5)
                        RETURNING token_address, symbol, name, decimals
                    """, token_address, 'UNKNOWN', 'Unknown Token', 9, supply)
                    
                    return dict(info)
                    
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting token info: {e}")
            return None

    async def get_latest_price(self, token_address: str) -> Optional[Decimal]:
        """Get latest token price"""
        try:
            async with self.db.acquire() as conn:
                price = await conn.fetchval("""
                    SELECT price_sol
                    FROM token_prices
                    WHERE token_address = $1
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, token_address)
                
                return Decimal(str(price)) if price else None
                
        except Exception as e:
            self.logger.error(f"Error getting latest price: {e}")
            return None

    async def update_all_prices(self):
        """Update prices for all tracked tokens"""
        try:
            async with self.db.acquire() as conn:
                tokens = await conn.fetch("""
                    SELECT token_address
                    FROM solana_tokens
                    WHERE active = true
                """)
                
                for token in tokens:
                    await self.update_token_price(token['token_address'])
                    
        except Exception as e:
            self.logger.error(f"Error updating all prices: {e}")

#!/usr/bin/env python3
import logging
import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal

logger = logging.getLogger(__name__)

class TokenTracker:
    """Core token price tracking functionality"""
    
    def __init__(self, db_pool, birdeye_client):
        self._pool = db_pool
        self._client = birdeye_client
        self.logger = logging.getLogger(__name__)

    async def initialize(self):
        """Initialize database tables"""
        async with self._pool.acquire() as conn:
            # Create tokens table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS solana_tokens (
                    token_address TEXT PRIMARY KEY,
                    is_active BOOLEAN DEFAULT true,
                    last_update TIMESTAMP WITH TIME ZONE
                )
            """)
            
            # Create prices table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS token_prices (
                    token_address TEXT REFERENCES solana_tokens(token_address),
                    price_sol NUMERIC,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB
                )
            """)

    async def track_token(self, token_address: str) -> bool:
        """Start tracking a token"""
        try:
            async with self._pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO solana_tokens (token_address)
                    VALUES ($1)
                    ON CONFLICT (token_address) DO NOTHING
                """, token_address)
            return True
        except Exception as e:
            self.logger.error(f"Error tracking token: {e}")
            return False

    async def update_price(self, token_address: str) -> Optional[Dict]:
        """Update token price"""
        try:
            # Input validation
            if token_address is None:
                raise ValueError("Token address cannot be None")
            if not isinstance(token_address, str):
                raise ValueError("Token address must be a string")
            if not token_address:
                raise ValueError("Token address cannot be empty")
            if len(token_address) > 44:  # Standard Solana address length
                raise ValueError("Token address too long")
            
            # Get price from API
            response = await self._client.get_token_price(token_address)
            if not response or not response.get('success'):
                return None
                
            price_data = response['data']
            
            # Store in database
            async with self._pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO token_prices (token_address, price_sol, metadata)
                    VALUES ($1, $2, $3)
                """,
                token_address,
                Decimal(str(price_data['value'])),
                json.dumps(price_data)
                )
                
                # Update last update time
                await conn.execute("""
                    UPDATE solana_tokens 
                    SET last_update = NOW()
                    WHERE token_address = $1
                """, token_address)
                
            return price_data
            
        except Exception as e:
            self.logger.error(f"Error updating price: {e}")
            if isinstance(e, ValueError):
                raise  # Re-raise ValueError for input validation errors
            return None

    async def get_price(self, token_address: str) -> Optional[Dict]:
        """Get latest price for token"""
        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT price_sol, timestamp, metadata
                    FROM token_prices
                    WHERE token_address = $1
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, token_address)
                
                return dict(row) if row else None
                
        except Exception as e:
            self.logger.error(f"Error getting price: {e}")
            return None

    async def close(self):
        await self._client.close()


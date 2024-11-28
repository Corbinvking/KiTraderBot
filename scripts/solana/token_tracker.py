import asyncio
import logging
import json
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import asyncpg
from solders.pubkey import Pubkey
from .rpc_manager import SolanaRPCManager

class TokenTracker:
    """Tracks Solana token data and manages database updates"""
    
    def __init__(self, rpc_manager: SolanaRPCManager, db_pool: asyncpg.Pool):
        self.rpc = rpc_manager
        self.db = db_pool
        self.tracked_tokens: Dict[str, dict] = {}
        self.update_interval = 60  # seconds
        self.logger = logging.getLogger(__name__)
        
    async def track_new_token(self, token_address: str) -> bool:
        """Add new token to tracking system"""
        try:
            # Get token data from RPC
            token_data = await self.rpc.get_token_data(token_address)
            if not token_data:
                return False
                
            # Extract metadata from token data
            metadata = {
                'owner': str(token_data.get('owner', '')),
                'lamports': int(token_data.get('lamports', 0)),
                'executable': bool(token_data.get('executable', False)),
                'data': str(token_data.get('data', b'').hex())  # Convert bytes to hex string
            }
                
            # Convert metadata to JSON string
            metadata_json = json.dumps(metadata)
                
            # Store in database
            async with self.db.acquire() as conn:
                await conn.execute("""
                    INSERT INTO solana_tokens (
                        token_address, first_seen_timestamp, 
                        last_updated, is_active, metadata
                    ) VALUES ($1, $2, $2, true, $3)
                    ON CONFLICT (token_address) 
                    DO UPDATE SET 
                        last_updated = $2,
                        is_active = true,
                        metadata = $3
                """, token_address, datetime.utcnow(), metadata_json)
                
            self.tracked_tokens[token_address] = token_data
            self.logger.info(f"Started tracking token: {token_address}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error tracking token {token_address}: {e}")
            return False

    async def update_token_prices(self):
        """Update price data for all tracked tokens"""
        for token_address in self.tracked_tokens:
            try:
                # Get latest price data
                token_data = await self.rpc.get_token_data(token_address)
                if not token_data:
                    continue
                    
                # Calculate estimated SOL price (simplified for example)
                price_sol = float(token_data.get('lamports', 0)) / 1e9  # Convert lamports to SOL
                
                # Store price update
                async with self.db.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO token_prices (
                            token_address, price_sol, price_usd,
                            volume_24h_sol, liquidity_sol,
                            source, confidence_score
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """, 
                        token_address, 
                        price_sol,
                        None,  # price_usd not available directly
                        0,     # volume_24h placeholder
                        0,     # liquidity placeholder
                        'solana_rpc', 
                        1.0
                    )
                        
            except Exception as e:
                self.logger.error(f"Error updating prices for {token_address}: {e}")

    async def calculate_metrics(self, token_address: str):
        """Calculate and store token metrics"""
        try:
            async with self.db.acquire() as conn:
                # Get latest price data
                price_data = await conn.fetchrow("""
                    SELECT price_sol, timestamp 
                    FROM token_prices 
                    WHERE token_address = $1 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """, token_address)
                
                if not price_data:
                    return
                    
                # Calculate 24h metrics
                day_ago = datetime.utcnow() - timedelta(days=1)
                old_price = await conn.fetchval("""
                    SELECT price_sol 
                    FROM token_prices 
                    WHERE token_address = $1 
                    AND timestamp >= $2 
                    ORDER BY timestamp ASC 
                    LIMIT 1
                """, token_address, day_ago)
                
                # Calculate price change
                price_change = 0
                if old_price and old_price > 0:
                    price_change = ((price_data['price_sol'] - old_price) / old_price) * 100
                
                # Store metrics
                await conn.execute("""
                    INSERT INTO token_metrics (
                        token_address, price_change_24h,
                        volume_24h_sol, market_cap_sol
                    ) VALUES ($1, $2, $3, $4)
                """, 
                    token_address, 
                    price_change,
                    0,  # volume placeholder
                    0   # market cap placeholder
                )
                
        except Exception as e:
            self.logger.error(f"Error calculating metrics for {token_address}: {e}")

    async def start_tracking(self):
        """Start the token tracking loop"""
        while True:
            try:
                await self.update_token_prices()
                for token_address in self.tracked_tokens:
                    await self.calculate_metrics(token_address)
            except Exception as e:
                self.logger.error(f"Error in tracking loop: {e}")
            finally:
                await asyncio.sleep(self.update_interval)

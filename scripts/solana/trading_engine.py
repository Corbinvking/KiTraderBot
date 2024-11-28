import logging
from typing import Optional, Dict
from datetime import datetime
import asyncpg
from .token_tracker import TokenTracker

class SimulatedTrading:
    """Handles simulated trading operations"""
    
    def __init__(self, db_pool: asyncpg.Pool, token_tracker: TokenTracker):
        self.db = db_pool
        self.tracker = token_tracker
        self.position_limits = {
            'basic': 100,
            'premium': 1000,
            'admin': float('inf')
        }
        self.logger = logging.getLogger(__name__)
        
    async def execute_trade(self, user_id: int, token_address: str, 
                          amount_sol: float, trade_type: str) -> Optional[Dict]:
        """Execute a simulated trade"""
        try:
            # Verify token is tracked
            if token_address not in self.tracker.tracked_tokens:
                if not await self.tracker.track_new_token(token_address):
                    return None
                    
            # Get current price
            async with self.db.acquire() as conn:
                current_price = await conn.fetchval("""
                    SELECT price_sol 
                    FROM token_prices 
                    WHERE token_address = $1 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """, token_address)
                
                if not current_price:
                    return None
                    
                # Create trade record
                trade_id = await conn.fetchval("""
                    INSERT INTO simulated_trades (
                        user_id, token_address, entry_price_sol,
                        position_size_sol, trade_type, status
                    ) VALUES ($1, $2, $3, $4, $5, 'open')
                    RETURNING trade_id
                """, user_id, token_address, current_price,
                    amount_sol, trade_type)
                    
                return {
                    'trade_id': trade_id,
                    'entry_price': current_price,
                    'size': amount_sol,
                    'type': trade_type
                }
                
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return None
            
    async def calculate_pnl(self, trade_id: int) -> Optional[float]:
        """Calculate current PnL for a trade"""
        try:
            async with self.db.acquire() as conn:
                trade = await conn.fetchrow("""
                    SELECT t.*, p.price_sol as current_price 
                    FROM simulated_trades t
                    LEFT JOIN token_prices p ON t.token_address = p.token_address
                    WHERE t.trade_id = $1
                    AND t.status = 'open'
                    ORDER BY p.timestamp DESC
                    LIMIT 1
                """, trade_id)
                
                if not trade:
                    return None
                    
                if trade['trade_type'] == 'long':
                    pnl = (trade['current_price'] - trade['entry_price_sol']) * trade['position_size_sol']
                else:
                    pnl = (trade['entry_price_sol'] - trade['current_price']) * trade['position_size_sol']
                    
                return pnl
                
        except Exception as e:
            self.logger.error(f"Error calculating PnL for trade {trade_id}: {e}")
            return None 

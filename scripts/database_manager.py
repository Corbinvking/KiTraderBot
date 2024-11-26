import asyncpg
import json
from datetime import datetime
from typing import Dict, List, Optional
import os

class DatabaseManager:
    def __init__(self):
        self.pool = None
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        try:
            with open('/opt/KiTraderBot/tokens/database', 'r') as f:
                return json.loads(f.read())
        except FileNotFoundError:
            raise Exception("Database configuration file not found")
        
    async def init_pool(self):
        self.pool = await asyncpg.create_pool(
            user=self.config['user'],
            password=self.config['password'],
            database=self.config['database'],
            host=self.config['host'],
            port=self.config['port'],
            min_size=5,
            max_size=20
        )
    
    # User Management
    async def add_user(self, telegram_id: int, username: str) -> int:
        async with self.pool.acquire() as conn:
            return await conn.fetchval('''
                INSERT INTO users (telegram_id, username)
                VALUES ($1, $2)
                ON CONFLICT (telegram_id) DO UPDATE 
                SET username = $2
                RETURNING user_id
            ''', telegram_id, username)
    
    async def get_user(self, telegram_id: int):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow('''
                SELECT * FROM users WHERE telegram_id = $1
            ''', telegram_id)
    
    # Trade Management
    async def record_trade(self, user_id: int, trade_data: dict) -> int:
        async with self.pool.acquire() as conn:
            return await conn.fetchval('''
                INSERT INTO trades (
                    user_id, symbol, entry_price, 
                    position_size, trade_type, trade_status
                )
                VALUES ($1, $2, $3, $4, $5, 'open')
                RETURNING trade_id
            ''', user_id, trade_data['symbol'], 
                trade_data['entry_price'],
                trade_data['position_size'], 
                trade_data['trade_type'])
    
    async def close_trade(self, trade_id: int, exit_price: float, pnl: float):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                UPDATE trades 
                SET exit_price = $2,
                    pnl = $3,
                    trade_status = 'closed',
                    closed_at = CURRENT_TIMESTAMP
                WHERE trade_id = $1
            ''', trade_id, exit_price, pnl)
    
    async def get_user_trades(self, user_id: int, limit: int = 10):
        async with self.pool.acquire() as conn:
            return await conn.fetch('''
                SELECT * FROM trades 
                WHERE user_id = $1 
                ORDER BY created_at DESC 
                LIMIT $2
            ''', user_id, limit)
    
    # User Settings
    async def get_user_settings(self, user_id: int):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow('''
                SELECT * FROM user_settings WHERE user_id = $1
            ''', user_id)
    
    async def update_user_settings(self, user_id: int, settings: dict):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO user_settings (
                    user_id, notification_preferences, 
                    risk_settings, ui_preferences
                )
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (user_id) DO UPDATE 
                SET notification_preferences = $2,
                    risk_settings = $3,
                    ui_preferences = $4,
                    updated_at = CURRENT_TIMESTAMP
            ''', user_id, json.dumps(settings.get('notifications', {})),
                json.dumps(settings.get('risk', {})),
                json.dumps(settings.get('ui', {})))

    # Helper Methods
    async def get_user_stats(self, user_id: int):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow('''
                SELECT 
                    COUNT(*) as total_trades,
                    COUNT(*) FILTER (WHERE trade_status = 'open') as open_trades,
                    SUM(pnl) as total_pnl
                FROM trades 
                WHERE user_id = $1
            ''', user_id)

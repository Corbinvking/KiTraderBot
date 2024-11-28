import json
import logging
from enum import Enum
import asyncpg
from typing import Dict, Optional
from datetime import datetime

class UserRole(Enum):
    """User role enumeration"""
    ADMIN = 'admin'
    PREMIUM = 'premium'
    BASIC = 'basic'

class UserManager:
    """Manages user roles and permissions"""
    
    def __init__(self):
        self.users: Dict[str, dict] = {}
        self.db_pool = None
        self.logger = logging.getLogger(__name__)
        
    async def init_db(self) -> asyncpg.Pool:
        """Initialize database connection"""
        try:
            self.db_pool = await asyncpg.create_pool(
                user='kitrader',
                password='kitraderpass',
                database='fantasysol',
                host='localhost',
                min_size=5,
                max_size=20
            )
            
            # Load users from database
            async with self.db_pool.acquire() as conn:
                users = await conn.fetch("""
                    SELECT user_id, telegram_id, username, role, 
                           registration_date, account_status
                    FROM users
                """)
                
                for user in users:
                    self.users[str(user['user_id'])] = {
                        'role': UserRole(user['role']),
                        'active': user['account_status'] == 'active',
                        'telegram_id': user['telegram_id'],
                        'username': user['username'],
                        'registration_date': user['registration_date']
                    }
                    
            self.logger.info(f"Loaded {len(self.users)} users from database")
            return self.db_pool
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise

    async def add_user(self, user_id: str, telegram_id: int, username: str, role: UserRole) -> bool:
        """Add a new user with specified role"""
        try:
            # Convert user_id to integer for database
            db_user_id = int(user_id)
            
            # Prepare JSON settings
            notification_prefs = json.dumps({'enabled': True})
            risk_settings = json.dumps({'max_position_size': 100})
            ui_preferences = json.dumps({})
            
            async with self.db_pool.acquire() as conn:
                # Add user to database
                await conn.execute("""
                    INSERT INTO users (
                        user_id, telegram_id, username, role, 
                        registration_date, account_status
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (user_id) DO UPDATE SET
                        telegram_id = $2,
                        username = $3,
                        role = $4,
                        account_status = $6
                """, 
                db_user_id, telegram_id, username, role.value, 
                datetime.utcnow(), 'active'
                )
                
                # Add user settings
                await conn.execute("""
                    INSERT INTO user_settings (
                        user_id, notification_preferences, 
                        risk_settings, ui_preferences
                    ) VALUES ($1, $2::jsonb, $3::jsonb, $4::jsonb)
                    ON CONFLICT (user_id) DO NOTHING
                """,
                db_user_id,
                notification_prefs,
                risk_settings,
                ui_preferences
                )
                
            # Update local cache
            self.users[user_id] = {
                'role': role,
                'active': True,
                'telegram_id': telegram_id,
                'username': username,
                'registration_date': datetime.utcnow()
            }
            
            self.logger.info(f"Added user {username} with role {role.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding user {username}: {e}")
            return False

    async def remove_user(self, user_id: str) -> bool:
        """Remove a user"""
        try:
            if user_id not in self.users:
                return False
                
            # Convert user_id to integer for database
            db_user_id = int(user_id)
                
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE users 
                    SET account_status = 'inactive'
                    WHERE user_id = $1
                """, db_user_id)
            
            self.users[user_id]['active'] = False
            self.logger.info(f"Removed user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing user {user_id}: {e}")
            return False

    def is_authorized(self, user_id: str, required_role: UserRole = UserRole.BASIC) -> bool:
        """Check if user has required role"""
        try:
            if user_id not in self.users:
                return False
            
            user = self.users[user_id]
            if not user['active']:
                return False
                
            user_role = user['role']
            
            # Admin can do everything
            if user_role == UserRole.ADMIN:
                return True
                
            # Premium can do premium and basic
            if user_role == UserRole.PREMIUM:
                return required_role != UserRole.ADMIN
                
            # Basic can only do basic
            return required_role == UserRole.BASIC
            
        except Exception as e:
            self.logger.error(f"Error checking authorization for user {user_id}: {e}")
            return False

    async def save_users(self):
        """Save users to database"""
        if not self.db_pool:
            return
            
        try:
            async with self.db_pool.acquire() as conn:
                for user_id, data in self.users.items():
                    # Convert user_id to integer for database
                    db_user_id = int(user_id)
                    
                    await conn.execute("""
                        UPDATE users SET
                            role = $2,
                            account_status = $3,
                            telegram_id = $4,
                            username = $5
                        WHERE user_id = $1
                    """, 
                    db_user_id,
                    data['role'].value,
                    'active' if data['active'] else 'inactive',
                    data['telegram_id'],
                    data['username']
                    )
                    
            self.logger.info("Users saved to database")
                    
        except Exception as e:
            self.logger.error(f"Error saving users: {e}")

    async def get_user_settings(self, user_id: str) -> Optional[Dict]:
        """Get user settings"""
        try:
            db_user_id = int(user_id)
            
            async with self.db_pool.acquire() as conn:
                settings = await conn.fetchrow("""
                    SELECT notification_preferences, risk_settings, ui_preferences
                    FROM user_settings
                    WHERE user_id = $1
                """, db_user_id)
                
                if settings:
                    return {
                        'notification_preferences': settings['notification_preferences'],
                        'risk_settings': settings['risk_settings'],
                        'ui_preferences': settings['ui_preferences']
                    }
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting settings for user {user_id}: {e}")
            return None

    async def update_user_settings(self, user_id: str, settings: Dict) -> bool:
        """Update user settings"""
        try:
            db_user_id = int(user_id)
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE user_settings SET
                        notification_preferences = $2::jsonb,
                        risk_settings = $3::jsonb,
                        ui_preferences = $4::jsonb
                    WHERE user_id = $1
                """,
                db_user_id,
                json.dumps(settings.get('notification_preferences', {'enabled': True})),
                json.dumps(settings.get('risk_settings', {'max_position_size': 100})),
                json.dumps(settings.get('ui_preferences', {}))
                )
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating settings for user {user_id}: {e}")
            return False

    async def close(self):
        """Close database connection"""
        if self.db_pool and not self.db_pool._closed:
            try:
                await self.save_users()
                await self.db_pool.close()
                self.logger.info("Database connection closed")
            except Exception as e:
                self.logger.error(f"Error closing database connection: {e}")

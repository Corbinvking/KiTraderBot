date, last_active, account_status 
                    FROM users
                """)
                return {str(row['telegram_id']): {
                    'user_id': row['user_id'],
                    'username': row['username'],
                    'role': row['role'],
                    'registration_date': row['registration_date'].isoformat() if row['registration_date'] else None,
                    'last_active': row['last_active'].isoformat() if row['last_active'] else None,
                    'account_status': row['account_status']
                } for row in rows}
        return loop.run_until_complete(_load())
    
    def load_superusers(self):
        """Load superusers from file and add them as ADMIN users."""
        try:
            with open('tokens/superusers', 'r') as f:
                superuser_ids = f.read().strip().split('\n')
                for user_id in superuser_ids:
                    if user_id and user_id.strip():
                        self.add_user(int(user_id.strip()), None, UserRole.ADMIN)
        except FileNotFoundError:
            print("No superusers file found")
    
    def add_user(self, telegram_id: int, username: str = None, role=UserRole.BASIC):
        """
        Add a new user to the database.
        
        Args:
            telegram_id (int): User's Telegram ID
            username (str, optional): User's Telegram username
            role (UserRole): User's role (default: BASIC)
        """
        loop = asyncio.get_event_loop()
        async def _add():
            async with self.pool.acquire() as conn:
                try:
                    user_id = await conn.fetchval("""
                        INSERT INTO users (telegram_id, username, role, registration_date, account_status)
                        VALUES ($1, $2, $3, CURRENT_TIMESTAMP, $4)
                        ON CONFLICT (telegram_id) 
                        DO UPDATE SET 
                            username = EXCLUDED.username,
                            role = EXCLUDED.role,
                            account_status = $4
                        RETURNING user_id
                    """, telegram_id, username, role.value, AccountStatus.ACTIVE.value)
                    
                    # Create default user settings
                    await conn.execute("""
                        INSERT INTO user_settings (user_id)
                        VALUES ($1)
                        ON CONFLICT (user_id) DO NOTHING
                    """, user_id)
                    
                except Exception as e:
                    print(f"Error adding user: {e}")
                    raise
        loop.run_until_complete(_add())
    
    def remove_user(self, telegram_id: int):
        """
        Deactivate a user (soft delete).
        
        Args:
            telegram_id (int): User's Telegram ID
        """
        loop = asyncio.get_event_loop()
        async def _remove():
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE users 
                    SET account_status = $1 
                    WHERE telegram_id = $2
                """, AccountStatus.INACTIVE.value, telegram_id)
        loop.run_until_complete(_remove())
    
    #--------------------------------------------------------------------------
    # AUTHORIZATION
    #--------------------------------------------------------------------------
    
    def is_authorized(self, telegram_id: int, required_role=UserRole.BASIC):
        """
        Check if user has required role or higher.
        
        Args:
            telegram_id (int): User's Telegram ID
            required_role (UserRole): Minimum role required
            
        Returns:
            bool: True if user has sufficient permissions
        """
        loop = asyncio.get_event_loop()
        async def _check():
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT role, account_status 
                    FROM users 
                    WHERE telegram_id = $1
                """, telegram_id)
                
                if not row or row['account_status'] != AccountStatus.ACTIVE.value:
                    return False
                
                user_role = UserRole(row['role'])
                role_levels = {
                    UserRole.ADMIN: 3,
                    UserRole.PREMIUM: 2,
                    UserRole.BASIC: 1
                }
                return role_levels[user_role] >= role_levels[required_role]
        return loop.run_until_complete(_check())
    
    def get_user_role(self, telegram_id: int):
        """
        Get user's current role.
        
        Args:
            telegram_id (int): User's Telegram ID
            
        Returns:
            UserRole: User's role or None if user doesn't exist
        """
        loop = asyncio.get_event_loop()
        async def _get():
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT role, account_status 
                    FROM users 
                    WHERE telegram_id = $1
                """, telegram_id)
                
                if row and row['account_status'] == AccountStatus.ACTIVE.value:
                    return UserRole(row['role'])
                return None
        return loop.run_until_complete(_get())
    
    #--------------------------------------------------------------------------
    # USER ACTIVITY
    #--------------------------------------------------------------------------
    
    def update_last_active(self, telegram_id: int):
        """
        Update user's last active timestamp.
        
        Args:
            telegram_id (int): User's Telegram ID
        """
        loop = asyncio.get_event_loop()
        async def _update():
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE users 
                    SET last_active = CURRENT_TIMESTAMP 
                    WHERE telegram_id = $1
                """, telegram_id)
        loop.run_until_complete(_update())
    
    #--------------------------------------------------------------------------
    # USER SETTINGS
    #--------------------------------------------------------------------------
    
    def get_user_settings(self, telegram_id: int):
        """
        Get user's settings.
        
        Args:
            telegram_id (int): User's Telegram ID
            
        Returns:
            dict: User's settings or None if user doesn't exist
        """
        loop = asyncio.get_event_loop()
        async def _get():
            async with self.pool.acquire() as conn:
                user = await conn.fetchrow("""
                    SELECT u.user_id, us.notification_preferences, us.risk_settings, us.ui_preferences
                    FROM users u
                    LEFT JOIN user_settings us ON u.user_id = us.user_id
                    WHERE u.telegram_id = $1
                """, telegram_id)
                if user:
                    return {
                        'notification_preferences': user['notification_preferences'],
                        'risk_settings': user['risk_settings'],
                        'ui_preferences': user['ui_preferences']
                    }
                return None
        return loop.run_until_complete(_get())
    
    def update_user_settings(self, telegram_id: int, settings_type: str, settings: dict):
        """
        Update user's settings.
        
        Args:
            telegram_id (int): User's Telegram ID
            settings_type (str): Type of settings to update ('notification_preferences', 'risk_settings', or 'ui_preferences')
            settings (dict): New settings values
        """
        loop = asyncio.get_event_loop()
        async def _update():
            async with self.pool.acquire() as conn:
                # First get user_id
                user_id = await conn.fetchval("""
                    SELECT user_id FROM users WHERE telegram_id = $1
                """, telegram_id)
                
                if user_id:
                    await conn.execute(f"""
                        UPDATE user_settings 
                        SET {settings_type} = $1, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = $2
                    """, settings, user_id)
        loop.run_until_complete(_update())
    
    #--------------------------------------------------------------------------
    # CLEANUP
    #--------------------------------------------------------------------------
    
    def __del__(self):
        """Close database connection pool when object is destroyed."""
        if self.pool:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.pool.close())

"""
User Management System for KiTraderBot
=====================================

This module handles user roles and permissions for the KiTraderBot:
- User roles (admin, premium, basic)
- User authorization
- User data persistence
"""

#------------------------------------------------------------------------------
# IMPORTS
#------------------------------------------------------------------------------

import json
from enum import Enum
from datetime import datetime

#------------------------------------------------------------------------------
# USER ROLES
#------------------------------------------------------------------------------

class UserRole(Enum):
    """
    Define user role hierarchy.
    ADMIN    - Full access to all features
    PREMIUM  - Access to premium features
    BASIC    - Access to basic features only
    """
    ADMIN = "admin"
    PREMIUM = "premium"
    BASIC = "basic"

#------------------------------------------------------------------------------
# USER MANAGER
#------------------------------------------------------------------------------

class UserManager:
    """
    Handles user management operations including:
    - User data persistence
    - Role management
    - Authorization checks
    """
    
    def __init__(self):
        """Initialize UserManager and load existing users."""
        self.users = self.load_users()
    
    def load_users(self):
        """
        Load user data from users.json file.
        Returns empty dict if file doesn't exist.
        """
        try:
            with open('users.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_users(self):
        """Persist user data to users.json file."""
        with open('users.json', 'w') as f:
            json.dump(self.users, f, indent=4)
    
    def add_user(self, username, role=UserRole.BASIC):
        """
        Add a new user with specified role.
        
        Args:
            username (str): Telegram username
            role (UserRole): User's role (default: BASIC)
        """
        self.users[username] = {
            "role": role.value,
            "joined_date": datetime.now().isoformat(),
            "active": True
        }
        self.save_users()
    
    def remove_user(self, username):
        """
        Deactivate a user (soft delete).
        
        Args:
            username (str): Telegram username
        """
        if username in self.users:
            self.users[username]["active"] = False
            self.save_users()
    
    def is_authorized(self, username, required_role=UserRole.BASIC):
        """
        Check if user has required role or higher.
        
        Args:
            username (str): Telegram username
            required_role (UserRole): Minimum role required
            
        Returns:
            bool: True if user has sufficient permissions
        """
        if username not in self.users:
            return False
        user = self.users[username]
        return user["active"] and UserRole(user["role"]).value >= required_role.value
    
    def get_user_role(self, username):
        """
        Get user's current role.
        
        Args:
            username (str): Telegram username
            
        Returns:
            UserRole: User's role or None if user doesn't exist
        """
        if username in self.users and self.users[username]["active"]:
            return UserRole(self.users[username]["role"])
        return None
    
    def update_role(self, username, new_role):
        """
        Update user's role.
        
        Args:
            username (str): Telegram username
            new_role (UserRole): New role to assign
        """
        if username in self.users:
            self.users[username]["role"] = new_role.value
            self.save_users()

#------------------------------------------------------------------------------
# UTILITY FUNCTIONS
#------------------------------------------------------------------------------

def get_role_hierarchy():
    """
    Get the role hierarchy as a dictionary.
    Used for comparing role levels.
    """
    return {
        UserRole.ADMIN: 3,
        UserRole.PREMIUM: 2,
        UserRole.BASIC: 1
    }

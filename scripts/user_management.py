from enum import Enum
import json
import os
from pathlib import Path
from datetime import datetime

class UserRole(Enum):
    ADMIN = "admin"
    PREMIUM = "premium"
    BASIC = "basic"

    def __str__(self):
        return self.value

class UserManager:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.users = self.load_users()
        self.load_superusers()
    
    def load_users(self):
        try:
            with open(self.root_dir / 'data' / 'users.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_users(self):
        os.makedirs(self.root_dir / 'data', exist_ok=True)
        with open(self.root_dir / 'data' / 'users.json', 'w') as f:
            json.dump(self.users, f, indent=4)
    
    def load_superusers(self):
        try:
            with open(self.root_dir / 'tokens' / 'superusers', 'r') as f:
                superuser_ids = f.read().strip().split('\n')
                for user_id in superuser_ids:
                    if user_id and user_id.strip():
                        self.add_user(user_id.strip(), UserRole.ADMIN)
        except FileNotFoundError:
            print("No superusers file found")
    
    def add_user(self, user_id, role=UserRole.BASIC):
        user_id = str(user_id)
        if user_id not in self.users:
            self.users[user_id] = {
                "role": role.value,
                "joined_date": datetime.now().isoformat(),
                "active": True
            }
            self.save_users()
    
    def remove_user(self, user_id):
        user_id = str(user_id)
        if user_id in self.users:
            self.users[user_id]["active"] = False
            self.save_users()
    
    def is_authorized(self, user_id, required_role=UserRole.BASIC):
        user_id = str(user_id)
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        if not user["active"]:
            return False
        
        user_role = UserRole(user["role"])
        role_levels = {
            UserRole.ADMIN: 3,
            UserRole.PREMIUM: 2,
            UserRole.BASIC: 1
        }
        return role_levels[user_role] >= role_levels[required_role]

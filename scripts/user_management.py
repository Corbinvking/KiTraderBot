from enum import Enum
import json

class UserPermission(Enum):
    ADMIN = "admin"
    PREMIUM = "premium"
    BASIC = "basic"

class UserManager:
    def __init__(self):
        self.users = {}
        self.load_users()

    def load_users(self):
        try:
            with open('users.json', 'r') as f:
                self.users = json.loads(f.read())
        except FileNotFoundError:
            self.users = {}

    def save_users(self):
        with open('users.json', 'w') as f:
            f.write(json.dumps(self.users))

    def add_user(self, user_id: int, permission: UserPermission):
        self.users[str(user_id)] = permission.value
        self.save_users()

    def remove_user(self, user_id: int):
        if str(user_id) in self.users:
            del self.users[str(user_id)]
            self.save_users()

    def get_user_permission(self, user_id: int) -> UserPermission:
        user_permission = self.users.get(str(user_id), UserPermission.BASIC.value)
        return UserPermission(user_permission)

    def list_users(self):
        return self.users

"""
KiTraderBot Scripts Package
==========================

This package contains all the core functionality for the KiTraderBot:
- User management
- Trading operations
- Alert handling
"""

from .user_management import UserManager, UserRole
from . import gmail
from . import bitstamp

__all__ = ['UserManager', 'UserRole', 'gmail', 'bitstamp']

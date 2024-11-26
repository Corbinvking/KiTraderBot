"""
KiTraderBot Scripts Package
"""

from .user_management import UserManager, UserRole
from . import gmail
from . import bitstamp

__all__ = ['UserManager', 'UserRole', 'gmail', 'bitstamp'] 

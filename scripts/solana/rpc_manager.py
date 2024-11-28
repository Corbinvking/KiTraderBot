"""
Solana RPC Manager
================

Handles RPC connections and requests to Solana nodes
"""

import logging
import aiohttp
import json
from typing import Optional, Dict, List
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)

class SolanaRPCManager:
    """Manages Solana RPC connections and requests"""
    
    def __init__(self):
        # RPC endpoints (using devnet for testing)
        self.endpoints = [
            "https://api.devnet.solana.com",      # Primary devnet endpoint
            "https://api.testnet.solana.com",     # Testnet backup
            "https://api.mainnet-beta.solana.com" # Mainnet as last resort
        ]
        self.current_endpoint = 0
        self.session = None
        self.logger = logging.getLogger(__name__)
        self.request_timeout = 30  # seconds
        self.max_retries = 3

    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.request_timeout)
            )

    async def _make_request(self, method: str, params: List = None, retry_count: int = 0) -> Optional[Dict]:
        """Make RPC request with retry logic"""
        try:
            await self._ensure_session()
            
            data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params or []
            }
            
            endpoint = self.endpoints[self.current_endpoint]
            self.logger.debug(f"Making RPC request to {endpoint}: {method}")
            
            async with self.session.post(endpoint, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if 'result' in result:
                        return result['result']
                    else:
                        error = result.get('error', {})
                        self.logger.error(f"RPC error: {error}")
                        if retry_count < self.max_retries:
                            self.current_endpoint = (self.current_endpoint + 1) % len(self.endpoints)
                            return await self._make_request(method, params, retry_count + 1)
                        return None
                else:
                    self.logger.error(f"RPC request failed with status {response.status}")
                    if retry_count < self.max_retries:
                        self.current_endpoint = (self.current_endpoint + 1) % len(self.endpoints)
                        return await self._make_request(method, params, retry_count + 1)
                    return None
                    
        except Exception as e:
            self.logger.error(f"RPC request failed: {e}")
            if retry_count < self.max_retries:
                self.current_endpoint = (self.current_endpoint + 1) % len(self.endpoints)
                return await self._make_request(method, params, retry_count + 1)
            return None
        finally:
            if retry_count == self.max_retries:
                self.logger.error(f"Max retries ({self.max_retries}) reached for method {method}")

    async def get_version(self) -> Optional[Dict]:
        """Get Solana version"""
        try:
            return await self._make_request("getVersion")
        except Exception as e:
            self.logger.error(f"Error getting version: {e}")
            return None

    async def get_slot(self) -> Optional[int]:
        """Get current slot"""
        try:
            result = await self._make_request("getSlot")
            return int(result) if result else None
        except Exception as e:
            self.logger.error(f"Error getting slot: {e}")
            return None

    async def get_latest_blockhash(self) -> Optional[str]:
        """Get latest blockhash"""
        try:
            # Using newer getLatestBlockhash method with proper params
            params = [
                {
                    "commitment": "confirmed"
                }
            ]
            result = await self._make_request("getLatestBlockhash", params)
            if result and isinstance(result, dict) and 'value' in result:
                return result['value'].get('blockhash')
            
            # Fallback to older method if needed
            result = await self._make_request("getRecentBlockhash", [{"commitment": "confirmed"}])
            if result and isinstance(result, dict) and 'value' in result:
                return result['value'].get('blockhash')
                
            return None
        except Exception as e:
            self.logger.error(f"Error getting latest blockhash: {e}")
            return None

    async def get_token_supply(self, token_address: str) -> Optional[int]:
        """Get token supply"""
        try:
            result = await self._make_request(
                "getTokenSupply",
                [token_address]
            )
            if result and 'value' in result and 'amount' in result['value']:
                return int(result['value']['amount'])
            return None
        except Exception as e:
            self.logger.error(f"Error getting token supply: {e}")
            return None

    async def get_token_balance(self, account: str) -> Optional[int]:
        """Get token account balance"""
        try:
            result = await self._make_request(
                "getTokenAccountBalance",
                [account]
            )
            if result and 'value' in result and 'amount' in result['value']:
                return int(result['value']['amount'])
            return None
        except Exception as e:
            self.logger.error(f"Error getting token balance: {e}")
            return None

    async def get_token_largest_accounts(self, token_address: str) -> Optional[List[Dict]]:
        """Get largest token accounts"""
        try:
            result = await self._make_request(
                "getTokenLargestAccounts",
                [token_address]
            )
            if result and 'value' in result:
                return result['value']
            return None
        except Exception as e:
            self.logger.error(f"Error getting largest accounts: {e}")
            return None

    async def get_token_price(self, token_address: str) -> Optional[Decimal]:
        """Get token price in SOL using liquidity pools"""
        try:
            # For testing, return mock price
            # In production, would calculate from liquidity pools
            return Decimal('0.1')
            
        except Exception as e:
            self.logger.error(f"Error getting token price: {e}")
            return None

    async def get_block_time(self, slot: int) -> Optional[int]:
        """Get block time for slot"""
        try:
            result = await self._make_request(
                "getBlockTime",
                [slot]
            )
            return int(result) if result else None
        except Exception as e:
            self.logger.error(f"Error getting block time: {e}")
            return None

    async def close(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            try:
                await self.session.close()
                self.session = None
                self.logger.debug("RPC session closed")
            except Exception as e:
                self.logger.error(f"Error closing RPC session: {e}")

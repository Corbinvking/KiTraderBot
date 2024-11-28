from typing import Optional, Dict, List
import asyncio
import time
import logging
from solana.rpc.async_api import AsyncClient
from base58 import b58encode, b58decode

class SolanaRPCManager:
    """Manages Solana RPC connections with failover and rate limiting"""

    def __init__(self):
        self.endpoints = {
            'primary': 'https://api.mainnet-beta.solana.com',
            'backup': [
                'https://solana-api.projectserum.com',
                'https://rpc.ankr.com/solana'
            ]
        }
        self.client: Optional[AsyncClient] = None
        self.current_endpoint: Optional[str] = None
        self.retry_count = 3
        self.timeout = 10
        self.last_request_time: Dict[str, float] = {}
        self.min_request_interval = 0.1  # 100ms between requests
        self.logger = logging.getLogger(__name__)

    async def initialize(self) -> bool:
        """Initialize connection to Solana RPC"""
        try:
            # Try primary endpoint first
            self.current_endpoint = self.endpoints['primary']
            self.client = AsyncClient(self.current_endpoint)
            await self.test_connection()
            self.logger.info(f"Connected to primary endpoint: {self.current_endpoint}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to primary endpoint: {e}")
            return await self.failover()

    async def test_connection(self) -> bool:
        """Test if current connection is working"""
        try:
            # Use get_slot instead of get_health
            slot = await self.client.get_slot()
            self.logger.info(f"Connection test successful. Current slot: {slot}")
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    async def failover(self) -> bool:
        """Attempt to connect to backup endpoints"""
        for endpoint in self.endpoints['backup']:
            try:
                self.current_endpoint = endpoint
                self.client = AsyncClient(endpoint)
                if await self.test_connection():
                    self.logger.info(f"Failover successful, connected to: {endpoint}")
                    return True
            except Exception as e:
                self.logger.error(f"Failover attempt failed for {endpoint}: {e}")
        return False

    async def get_token_data(self, token_address: str) -> Optional[Dict]:
        """Fetch token metadata and current state"""
        if not self.client:
            if not await self.initialize():
                return None

        # Rate limiting
        current_time = time.time()
        if token_address in self.last_request_time:
            time_since_last = current_time - self.last_request_time[token_address]
            if time_since_last < self.min_request_interval:
                await asyncio.sleep(self.min_request_interval - time_since_last)

        try:
            response = await self.client.get_account_info(token_address)
            self.last_request_time[token_address] = time.time()

            if response and hasattr(response, 'value'):
                return {
                    'address': token_address,
                    'data': response.value.data,
                    'owner': str(response.value.owner),
                    'lamports': response.value.lamports,
                    'executable': response.value.executable
                }
            return None

        except Exception as e:
            self.logger.error(f"Error fetching token data: {e}")
            return None

    async def close(self):
        """Clean up connections"""
        if self.client:
            await self.client.close()

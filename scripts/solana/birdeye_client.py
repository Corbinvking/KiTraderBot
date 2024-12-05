#!/usr/bin/env python3
import os
import logging
import aiohttp
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class BirdeyeClient:
    """Simple client for Birdeye API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('BIRDEYE_API_KEY', '65cce27c021346ea85203479dae66ccd')
        self.base_url = "https://public-api.birdeye.so/defi"
        self.session = None
        self.headers = {
            "accept": "application/json",
            "X-API-KEY": self.api_key
        }

    async def initialize(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def get_token_price(self, token_address: str) -> Dict[str, Any]:
        """Get current token price"""
        if not self.session:
            await self.initialize()
            
        url = f"{self.base_url}/price"
        params = {"address": token_address}
        
        async with self.session.get(url, headers=self.headers, params=params) as response:
            if response.status == 200:
                return await response.json()
            error_text = await response.text()
            raise Exception(f"API error: {response.status} - {error_text}")

    async def get_token_list(self) -> Dict[str, Any]:
        """Get sorted token list"""
        if not self.session:
            await self.initialize()
            
        url = f"{self.base_url}/tokenlist"
        params = {
            "sort_by": "v24hUSD",
            "sort_type": "desc"
        }
        
        async with self.session.get(url, headers=self.headers, params=params) as response:
            if response.status == 200:
                return await response.json()
            error_text = await response.text()
            raise Exception(f"API error: {response.status} - {error_text}")


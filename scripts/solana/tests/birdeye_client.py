#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Birdeye API Client
=================
Handles all Birdeye API interactions with rate limiting and caching.
"""

import os
import sys
import json
import asyncio
import aiohttp
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from cachetools import TTLCache

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('/var/log/kitraderbot/birdeye.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class BirdeyeClient:
    """Client for Birdeye API with rate limiting and caching"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Birdeye client"""
        self.api_key = api_key or '0c0f43320c214e94bc739469cb1c1ccb'
        self.base_url = "https://public-api.birdeye.so"
        self.headers = {
            "X-API-KEY": api_key,
            "accept": "application/json",
            "x-chain": "solana"  # Add chain header
        }
        self.session = None
        self.last_request = datetime.min
        self.request_interval = 0.2  # 200ms between requests
        self._request_lock = asyncio.Lock()
        self.metrics = {
            'requests': 0,
            'errors': 0
        }

    async def initialize(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    'X-API-KEY': self.api_key,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json', 
                    'User-Agent': 'KiTraderBot/1.0'  # Added User-Agent
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )

    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make API request with rate limiting and retries"""
        if not self.session:
            await self.initialize()

        async with self._request_lock:
            # Rate limiting
            now = datetime.now()
            time_since_last = (now - self.last_request).total_seconds()
            if time_since_last < self.request_interval:
                await asyncio.sleep(self.request_interval - time_since_last)

            url = f"{self.base_url}{endpoint}"
            logger.info(f"Making request to: {url}")
            
            try:
                async with self.session.get(url, headers=self.headers, params=params) as response:
                    self.last_request = datetime.now()
                    self.metrics['requests'] += 1
                    
                    response_text = await response.text()
                    logger.debug(f"Raw response: {response_text}")
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            logger.debug(f"Parsed response: {data}")
                            if isinstance(data, dict) and 'data' in data:
                                return data['data']
                            else:
                                logger.error(f"Unexpected response format: {data}")
                                raise Exception(f"Unexpected response format: {data}")
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON decode error: {e}")
                            raise
                    else:
                        logger.error(f"API error: {response.status} - {response_text}")
                        raise Exception(f"API error: {response.status} - {response_text}")

            except Exception as e:
                self.metrics['errors'] += 1
                logger.error(f"Request error for {endpoint}: {e}")
                raise

    async def get_price(self, token_address: str) -> Dict:
        """Get current price for a token"""
        try:
            endpoint = "/defi/token_overview"
            params = {"address": token_address}
            response = await self._make_request(endpoint, params)
            return response
        except Exception as e:
            logger.error(f"Error getting price for {token_address}: {e}")
            raise

    async def get_metadata(self, token_address: str) -> Dict:
        """Get token metadata"""
        try:
            endpoint = "/defi/token_overview"
            params = {"address": token_address}
            response = await self._make_request(endpoint, params)
            return response
        except Exception as e:
            logger.error(f"Error getting metadata for {token_address}: {e}")
            raise

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get client performance metrics"""
        return {
            **self.metrics,
            'cache_size': len(self.cache),
            'timestamp': datetime.now().isoformat()
        }

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def get_token_list(self, sort_by: str = "v24hUSD", sort_type: str = "desc", 
                            offset: int = 0, limit: int = 50, min_liquidity: float = 100) -> Dict:
        """Get sorted token list"""
        endpoint = "/defi/tokenlist"
        params = {
            "sort_by": sort_by,
            "sort_type": sort_type,
            "offset": offset,
            "limit": limit,
            "min_liquidity": min_liquidity
        }
        return await self._make_request(endpoint, params)

    async def get_token_info(self, token_address: str) -> Optional[Dict]:
        """Get token info from the token list"""
        token_list = await self.get_token_list(limit=100)  # Get a larger list to increase chances of finding the token
        for token in token_list['tokens']:
            if token['address'] == token_address:
                return token
        return None

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the async test
    asyncio.run(main())


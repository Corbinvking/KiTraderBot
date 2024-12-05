#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Basic Birdeye API Integration Tests
=================================

This module implements comprehensive tests for the Birdeye API integration,
including initialization, price fetching, rate limiting, and caching tests.
"""

import os
import sys
import asyncio
import pytest
import logging
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

from scripts.solana.birdeye_client import BirdeyeClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/kitraderbot/birdeye_test.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Test constants
USDC_ADDRESS = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOL_ADDRESS = "So11111111111111111111111111111111111111112"
INVALID_ADDRESS = "Invalid_Address_For_Testing"

# Additional test tokens
TEST_TOKENS = [
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    "So11111111111111111111111111111111111111112",    # SOL
    "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",   # mSOL
    "7dHbWXmci3dT8UFYWYZweBLXgycu7Y3iL6trKn1Y7ARj",   # stSOL
    "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",   # BONK
]

class TestResults:
    """Stores test results for reporting"""
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.start_time = datetime.now()

    def add_result(self, test_name: str, passed: bool, details: str = ""):
        self.results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now()
        })

    def print_summary(self):
        duration = (datetime.now() - self.start_time).total_seconds()
        passed = sum(1 for r in self.results if r["passed"])
        total = len(self.results)
        
        logger.info("\n=== Test Summary ===")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
        logger.info("\nDetailed Results:")
        
        for result in self.results:
            status = "✓" if result["passed"] else "✗"
            logger.info(f"{status} {result['test']}")
            if result["details"]:
                logger.info(f"   {result['details']}")

test_results = TestResults()

@pytest.mark.asyncio
async def test_initialization():
    """Test client initialization"""
    client = BirdeyeClient()
    try:
        result = await client.initialize()
        assert result is True, "Failed to initialize client"
        
        networks = await client.get_supported_networks()
        assert "solana" in networks, "Solana network not supported"
        
        test_results.add_result("Initialization", True)
        logger.info("Initialization test passed")
    except Exception as e:
        test_results.add_result("Initialization", False, str(e))
        raise
    finally:
        await client.close()

@pytest.mark.asyncio
async def test_price_fetch():
    """Test price fetching functionality"""
    client = BirdeyeClient()
    try:
        # Test USDC price
        price_data = await client.get_token_price(USDC_ADDRESS)
        assert price_data is not None, "Failed to fetch USDC price"
        assert 'price' in price_data, "Price data missing price field"
        assert isinstance(price_data['price'], Decimal), "Price not in Decimal format"
        
        # Verify price is reasonable for USDC
        assert 0.9 <= float(price_data['price']) <= 1.1, "USDC price outside expected range"
        
        logger.info(f"USDC Price: ${price_data['price']:.6f}")
        logger.info(f"24h Change: {price_data['change_24h']:.2f}%")
        
        # Test SOL price
        sol_price = await client.get_token_price(SOL_ADDRESS)
        assert sol_price is not None, "Failed to fetch SOL price"
        assert float(sol_price['price']) > 0, "Invalid SOL price"
        
        logger.info(f"SOL Price: ${sol_price['price']:.6f}")
        
        # Test invalid address
        invalid_price = await client.get_token_price(INVALID_ADDRESS)
        assert invalid_price is None, "Invalid address should return None"
        
        test_results.add_result("Price Fetching", True)
        logger.info("Price fetch tests passed")
    except Exception as e:
        test_results.add_result("Price Fetching", False, str(e))
        raise
    finally:
        await client.close()

@pytest.mark.asyncio
async def test_rate_limiting():
    """Test rate limiting functionality"""
    client = BirdeyeClient()
    try:
        start_time = datetime.now()
        
        # Make 25 requests (should definitely trigger rate limiting)
        results = []
        for i, token in enumerate(TEST_TOKENS * 5):  # 25 requests
            logger.info(f"Request {i+1}/25 for token {token[:8]}...")
            price = await client.get_token_price(token)
            results.append(price is not None)
            if price:
                logger.info(f"Price: ${price['price']:.6f}")
        
        duration = (datetime.now() - start_time).total_seconds()
        success_rate = sum(results) / len(results)
        
        logger.info(f"Rate limit test completed in {duration:.2f} seconds")
        logger.info(f"Success rate: {success_rate:.2%}")
        
        # With 25 requests at 10 per second, should take at least 2.5 seconds
        min_expected_duration = 2.5
        assert duration > min_expected_duration, (
            f"Rate limiting not working as expected "
            f"(took {duration:.2f}s, expected > {min_expected_duration:.2f}s)"
        )
        assert success_rate > 0.8, f"Too many failed requests (success rate: {success_rate:.2%})"
        
        # Calculate requests per second
        requests_per_second = len(results) / duration
        logger.info(f"Requests per second: {requests_per_second:.2f}")
        assert requests_per_second <= 11, f"Too many requests per second: {requests_per_second:.2f}"
        
        test_results.add_result("Rate Limiting", True, 
                               f"Processed {len(results)} requests in {duration:.2f}s")
        logger.info("Rate limiting test passed")
    except Exception as e:
        test_results.add_result("Rate Limiting", False, str(e))
        raise
    finally:
        await client.close()

@pytest.mark.asyncio
async def test_caching():
    """Test caching functionality"""
    client = BirdeyeClient()
    try:
        # First request - should hit API
        start_time = datetime.now()
        first_price = await client.get_token_price(USDC_ADDRESS)
        first_duration = (datetime.now() - start_time).total_seconds()
        
        # Second request - should hit cache
        start_time = datetime.now()
        second_price = await client.get_token_price(USDC_ADDRESS)
        second_duration = (datetime.now() - start_time).total_seconds()
        
        assert first_price == second_price, "Cache returned different data"
        assert second_duration < first_duration, "Cache not faster than API call"
        
        logger.info(f"First call: {first_duration:.4f}s, Second call: {second_duration:.4f}s")
        
        test_results.add_result("Caching", True, 
                               f"Cache improved response time by {(first_duration-second_duration)*1000:.0f}ms")
        logger.info("Cache test passed")
    except Exception as e:
        test_results.add_result("Caching", False, str(e))
        raise
    finally:
        await client.close()

def run_all_tests():
    """Run all tests"""
    logger.info("Starting Birdeye API tests...")
    
    try:
        asyncio.run(test_initialization())
        asyncio.run(test_price_fetch())
        asyncio.run(test_rate_limiting())
        asyncio.run(test_caching())
        
        logger.info("All tests completed successfully!")
    except Exception as e:
        logger.error(f"Tests failed: {str(e)}")
    finally:
        test_results.print_summary()

if __name__ == "__main__":
    run_all_tests()

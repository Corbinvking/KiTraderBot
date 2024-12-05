#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database Migration Script for Birdeye Integration
==============================================
"""

import os
import sys
import asyncio
import asyncpg
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def apply_migration(migration_file: str) -> bool:
    """Apply database migration"""
    try:
        # Read migration SQL
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        # Connect using peer authentication
        conn = await asyncpg.connect(
            database='fantasysol',
            host='/var/run/postgresql'  # Use Unix domain socket
        )
        
        try:
            # Start transaction
            async with conn.transaction():
                # Apply migration
                await conn.execute(migration_sql)
                
                # Verify key components
                tables = await conn.fetch("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                
                logger.info("Migration applied successfully")
                logger.info("Verified tables:")
                for table in tables:
                    logger.info(f"  - {table['table_name']}")
                
                return True
                
        finally:
            await conn.close()
            
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return False

async def main():
    """Main migration function"""
    # Migration file path
    migration_path = Path(__file__).parent / "001_birdeye_integration.sql"
    
    logger.info("Starting database migration for Birdeye integration...")
    logger.info(f"Using migration file: {migration_path}")
    
    if not migration_path.exists():
        logger.error(f"Migration file not found: {migration_path}")
        return
    
    success = await apply_migration(migration_path)
    
    if success:
        logger.info("Migration completed successfully")
    else:
        logger.error("Migration failed")

if __name__ == "__main__":
    asyncio.run(main())

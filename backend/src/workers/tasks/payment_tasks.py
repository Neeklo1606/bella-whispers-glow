"""
Payment-related background tasks.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def verify_pending_payments():
    """Verify status of pending payments."""
    async with AsyncSessionLocal() as db:
        try:
            # TODO: Implement payment verification
            # 1. Find payments with status = 'pending' older than 15 minutes
            # 2. Check status with payment provider
            # 3. Update payment status
            # 4. Activate subscription if payment successful
            logger.info("Verifying pending payments...")
        except Exception as e:
            logger.error(f"Error verifying pending payments: {e}")

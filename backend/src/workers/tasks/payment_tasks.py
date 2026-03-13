"""
Payment-related background tasks.
Sync pending payments with YooKassa every 5 minutes.
"""
import logging
from ...core.db import AsyncSessionLocal
from ...modules.payments.service import PaymentService

logger = logging.getLogger(__name__)


async def verify_pending_payments():
    """Sync pending payments with YooKassa. Updates status, activates subscriptions."""
    async with AsyncSessionLocal() as db:
        try:
            service = PaymentService(db)
            result = await service.sync_all_pending_from_provider()
            await db.commit()
            if result.get("updated", 0) > 0:
                logger.info("[PAYMENT] verify_pending: updated %d of %d", result["updated"], result.get("total", 0))
            if result.get("errors"):
                for err in result["errors"]:
                    logger.warning("[PAYMENT] verify_pending error: %s", err)
        except Exception as e:
            logger.error("[PAYMENT] verify_pending failed: %s", e)

"""
YooKassa payment provider implementation.
"""
import hmac
import hashlib
import json
from typing import Dict, Optional
import httpx

from ....core.config import settings
from .base import PaymentProvider


class YooKassaProvider(PaymentProvider):
    """YooKassa payment provider."""

    def __init__(self):
        self.shop_id = settings.YOOKASSA_SHOP_ID
        self.secret_key = settings.YOOKASSA_SECRET_KEY
        self.test_mode = settings.YOOKASSA_TEST_MODE
        self.base_url = (
            "https://api.yookassa.ru/v3"
            if not self.test_mode
            else "https://api.yookassa.ru/v3"
        )

    async def create_payment(
        self,
        amount: float,
        currency: str,
        description: str,
        return_url: str,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """Create payment with YooKassa."""
        import base64

        auth_string = f"{self.shop_id}:{self.secret_key}"
        auth_header = base64.b64encode(auth_string.encode()).decode()

        payload = {
            "amount": {"value": f"{amount:.2f}", "currency": currency.upper()},
            "confirmation": {
                "type": "redirect",
                "return_url": return_url,
            },
            "description": description,
            "capture": True,
        }

        if metadata:
            payload["metadata"] = metadata

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/payments",
                json=payload,
                headers={
                    "Authorization": f"Basic {auth_header}",
                    "Idempotence-Key": metadata.get("idempotence_key", "") if metadata else "",
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            return {
                "payment_id": data["id"],
                "payment_url": data["confirmation"]["confirmation_url"],
                "status": data["status"],
            }

    async def verify_webhook(
        self, payload: Dict, signature: Optional[str] = None
    ) -> bool:
        """Verify YooKassa webhook signature."""
        # YooKassa uses HMAC SHA256 for webhook verification
        if not signature:
            return False

        # Create signature from payload
        payload_str = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        calculated_signature = hmac.new(
            self.secret_key.encode(),
            payload_str.encode(),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(calculated_signature, signature)

    async def get_payment_status(
        self, provider_payment_id: str
    ) -> Optional[str]:
        """Get payment status from YooKassa."""
        import base64

        auth_string = f"{self.shop_id}:{self.secret_key}"
        auth_header = base64.b64encode(auth_string.encode()).decode()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/payments/{provider_payment_id}",
                headers={"Authorization": f"Basic {auth_header}"},
                timeout=30.0,
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("status")
            return None

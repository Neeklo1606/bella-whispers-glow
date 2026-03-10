"""
API client for backend communication.
"""
import httpx
from typing import Optional, Dict, Any
from ..utils.config import get_bot_config

_api_client: Optional["APIClient"] = None


def get_api_client() -> "APIClient":
    """Get or create API client instance."""
    global _api_client
    if _api_client is None:
        _api_client = APIClient()
    return _api_client


class APIClient:
    """Client for backend API."""

    def __init__(self):
        self.config = get_bot_config()
        self.base_url = self.config.API_BASE_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def authenticate_telegram(self, auth_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Authenticate user via Telegram."""
        # TODO: Implement
        response = await self.client.post("/api/auth/telegram", json=auth_data)
        if response.status_code == 200:
            return response.json()
        return None

    async def get_subscription_by_telegram(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """GET /api/bot/subscription?telegram_id=X - bot auth."""
        headers = {}
        if self.config.BOT_API_SECRET:
            headers["X-Bot-Secret"] = self.config.BOT_API_SECRET
        response = await self.client.get(
            f"/api/bot/subscription?telegram_id={telegram_id}",
            headers=headers,
        )
        if response.status_code == 200:
            return response.json()
        return None

    async def create_payment_from_bot(
        self,
        telegram_id: int,
        plan_id: str,
        email: str,
        first_name: str = "",
        last_name: str = "",
        username: str = "",
    ) -> Optional[Dict[str, Any]]:
        """POST /api/bot/create-payment - bot auth."""
        headers = {"Content-Type": "application/json"}
        if self.config.BOT_API_SECRET:
            headers["X-Bot-Secret"] = self.config.BOT_API_SECRET
        response = await self.client.post(
            "/api/bot/create-payment",
            json={
                "telegram_id": telegram_id,
                "plan_id": plan_id,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
            },
            headers=headers,
        )
        if response.status_code == 200:
            return response.json()
        return None

    async def get_plans(self) -> list[Dict[str, Any]]:
        """GET /api/subscriptions/plans - list active plans (no auth)."""
        response = await self.client.get("/api/subscriptions/plans")
        if response.status_code == 200:
            return response.json()
        return []

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

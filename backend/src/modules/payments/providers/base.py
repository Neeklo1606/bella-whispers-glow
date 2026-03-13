"""
Base payment provider interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
from datetime import datetime


class PaymentProvider(ABC):
    """Base class for payment providers."""

    @abstractmethod
    async def create_payment(
        self,
        amount: float,
        currency: str,
        description: str,
        return_url: str,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Create payment with provider.
        
        Args:
            amount: Payment amount
            currency: Currency code
            description: Payment description
            return_url: URL to redirect after payment
            metadata: Additional metadata
            
        Returns:
            Dictionary with payment_id and payment_url
        """
        pass

    @abstractmethod
    async def verify_webhook(
        self, payload: Dict, signature: Optional[str] = None
    ) -> bool:
        """
        Verify webhook signature.
        
        Args:
            payload: Webhook payload
            signature: Webhook signature
            
        Returns:
            True if signature is valid
        """
        pass

    @abstractmethod
    async def get_payment_status(
        self, provider_payment_id: str
    ) -> Optional[str]:
        """
        Get payment status from provider.
        
        Args:
            provider_payment_id: Provider payment ID
            
        Returns:
            Payment status or None
        """
        pass

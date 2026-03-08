"""
Bot authentication dependency for securing bot-to-backend communication.
"""
from fastapi import Header, HTTPException, status
from ...core.config import settings


async def verify_bot_secret(x_bot_secret: str = Header(..., alias="X-Bot-Secret")) -> str:
    """
    Verify bot API secret from header.
    
    Args:
        x_bot_secret: Bot secret from X-Bot-Secret header
        
    Returns:
        Verified secret
        
    Raises:
        HTTPException: If secret is invalid
    """
    if not settings.BOT_API_SECRET:
        # If not configured, allow (for development)
        return x_bot_secret
    
    if x_bot_secret != settings.BOT_API_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid bot secret",
        )
    
    return x_bot_secret

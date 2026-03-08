"""
Telegram WebApp initData verification.
"""
import hmac
import hashlib
import urllib.parse
from typing import Dict, Optional
from ...core.config import settings


def parse_init_data(init_data: str) -> Dict[str, str]:
    """
    Parse Telegram WebApp initData string.
    
    Args:
        init_data: Raw initData string from Telegram WebApp
        
    Returns:
        Dictionary of parsed key-value pairs
    """
    parsed = {}
    for pair in init_data.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            parsed[key] = urllib.parse.unquote(value)
    return parsed


def verify_telegram_init_data(init_data: str) -> bool:
    """
    Verify Telegram WebApp initData signature.
    
    Steps:
    1. Parse initData
    2. Extract hash
    3. Create data_check_string (all fields except hash, sorted alphabetically)
    4. Create secret key using bot token
    5. Generate HMAC SHA256
    6. Compare with hash
    
    Args:
        init_data: Raw initData string from Telegram WebApp
        
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Parse initData
        data = parse_init_data(init_data)
        
        # Extract hash
        received_hash = data.pop("hash", None)
        if not received_hash:
            return False
        
        # Create data_check_string (all fields except hash, sorted alphabetically)
        data_check_string = "\n".join(
            f"{key}={value}" for key, value in sorted(data.items())
        )
        
        # Create secret key using bot token
        # Secret key = HMAC SHA256 of "WebAppData" with bot token as key
        secret_key = hmac.new(
            "WebAppData".encode(),
            settings.TELEGRAM_BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()
        
        # Generate HMAC SHA256
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare with received hash
        return hmac.compare_digest(calculated_hash, received_hash)
    
    except Exception:
        return False


def extract_user_data(init_data: str) -> Optional[Dict]:
    """
    Extract user data from verified initData.
    
    Args:
        init_data: Raw initData string from Telegram WebApp
        
    Returns:
        Dictionary with user data or None if invalid
    """
    try:
        data = parse_init_data(init_data)
        
        # Extract user data from 'user' field (JSON string)
        user_str = data.get("user")
        if not user_str:
            return None
        
        import json
        user_data = json.loads(user_str)
        
        return {
            "id": user_data.get("id"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "username": user_data.get("username"),
            "photo_url": user_data.get("photo_url"),
            "auth_date": int(data.get("auth_date", 0)),
        }
    
    except Exception:
        return None

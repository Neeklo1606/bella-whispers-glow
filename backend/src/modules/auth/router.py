"""
Auth module API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db import get_db
from .service import AuthService
from .schemas import (
    TelegramAuthData,
    TokenResponse,
    LoginRequest,
    RefreshTokenRequest,
    AdminLoginRequest,
    AdminLoginResponse,
    TelegramInitDataRequest,
    TelegramAuthResponse,
)

router = APIRouter()


@router.post("/telegram", response_model=TelegramAuthResponse)
async def authenticate_telegram(
    request: TelegramInitDataRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user via Telegram WebApp initData.
    
    Args:
        request: Telegram initData request
        db: Database session
        
    Returns:
        Telegram auth response with access token and user data
        
    Raises:
        HTTPException: If authentication fails
    """
    from ...core.security.telegram import (
        get_telegram_bot_token,
        verify_telegram_init_data,
        extract_user_data,
    )
    from ...modules.users.repository import UserRepository
    from ...modules.users.enums import UserRole
    from ...core.security import create_access_token
    from ...modules.users.schemas import UserResponse
    
    # Verify Telegram signature (token from system_settings, fallback .env)
    bot_token = await get_telegram_bot_token(db)
    if not verify_telegram_init_data(request.initData, bot_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Telegram initData signature",
        )
    
    # Extract user data from initData
    user_data = extract_user_data(request.initData)
    if not user_data or not user_data.get("id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user data in initData",
        )
    
    # Get or create user
    repository = UserRepository(db)
    user = await repository.get_by_telegram_id(user_data["id"])
    
    if not user:
        # Create new Telegram user
        user = await repository.create({
            "telegram_id": user_data["id"],
            "username": user_data.get("username"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "avatar_url": user_data.get("photo_url"),
            "role": UserRole.USER,
        })
    else:
        # Update user data if needed
        update_data = {}
        if user_data.get("username") and user.username != user_data["username"]:
            update_data["username"] = user_data["username"]
        if user_data.get("first_name") and user.first_name != user_data["first_name"]:
            update_data["first_name"] = user_data["first_name"]
        if user_data.get("last_name") and user.last_name != user_data.get("last_name"):
            update_data["last_name"] = user_data.get("last_name")
        if user_data.get("photo_url") and user.avatar_url != user_data["photo_url"]:
            update_data["avatar_url"] = user_data["photo_url"]
        
        if update_data:
            await repository.update(user.id, update_data)
            await db.refresh(user)
    
    # Generate JWT access token
    token_data = {"sub": str(user.id), "role": user.role.value}
    access_token = create_access_token(token_data)
    
    # Return token and user data
    return TelegramAuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user).model_dump(),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Login with email and password.
    
    Args:
        login_data: Login credentials
        db: Database session
        
    Returns:
        Token response
    """
    service = AuthService(db)
    result = await service.login(login_data.email, login_data.password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return result


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token.
    
    Args:
        refresh_data: Refresh token data
        db: Database session
        
    Returns:
        New token response
    """
    service = AuthService(db)
    result = await service.refresh_token(refresh_data.refresh_token)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    return result


@router.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(
    login_data: AdminLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Admin login endpoint.
    
    Args:
        login_data: Admin login credentials (email and password)
        db: Database session
        
    Returns:
        Admin login response with access token and user data
        
    Raises:
        HTTPException: If authentication fails
    """
    from ...modules.users.repository import UserRepository
    from ...core.security import verify_password, create_access_token
    from ...modules.users.enums import UserRole
    
    # Validate email and password
    if not login_data.email or not login_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )
    
    # Find user by email
    repository = UserRepository(db)
    user = await repository.get_by_email(login_data.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Verify password using passlib bcrypt
    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Check role is ADMIN or SUPER_ADMIN
    if user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin access required.",
        )
    
    # Generate JWT access token
    token_data = {"sub": str(user.id), "role": user.role.value}
    access_token = create_access_token(token_data)
    
    # Return token and user data
    from ...modules.users.schemas import UserResponse
    
    return AdminLoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user).model_dump(),
    )

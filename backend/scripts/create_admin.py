#!/usr/bin/env python3
"""
Script to create the first admin user.
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.modules.users.models import User
from src.modules.users.enums import UserRole
from src.core.security import get_password_hash


async def create_admin_user():
    """Create admin user if it doesn't exist."""
    # Create database engine
    engine = create_async_engine(settings.database_url_async)
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Check if user already exists
        from sqlalchemy import select
        
        result = await session.execute(
            select(User).where(User.email == "dsc-23@yandex.ru")
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print("Admin user already exists. Skipping creation.")
            print(f"User ID: {existing_user.id}")
            print(f"Email: {existing_user.email}")
            print(f"Role: {existing_user.role.value}")
            return
        
        # Hash password with bcrypt
        password_hash = get_password_hash("123123123")
        
        # Create user
        admin_user = User(
            email="dsc-23@yandex.ru",
            password_hash=password_hash,
            first_name="John",
            last_name="Wick",
            role=UserRole.ADMIN,
        )
        
        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)
        
        print("Admin user created successfully!")
        print(f"User ID: {admin_user.id}")
        print(f"Email: {admin_user.email}")
        print(f"Password: 123123123")
        print(f"Role: {admin_user.role.value}")
        print(f"First Name: {admin_user.first_name}")
        print(f"Last Name: {admin_user.last_name}")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_admin_user())

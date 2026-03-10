#!/usr/bin/env python3
"""
Ensure admin user exists. Idempotent: creates only if missing.
Email: admin@bellahasias.ru
Password: Admin123!
Role: admin
"""
import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Load settings from backend src
sys.path.insert(0, str(backend_dir / "src"))
from core.config import settings
from core.security import get_password_hash
from modules.users.models import User
from modules.users.enums import UserRole

ADMIN_EMAIL = "admin@bellahasias.ru"
ADMIN_PASSWORD = "Admin123!"


async def ensure_admin():
    engine = create_async_engine(settings.database_url_async)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == ADMIN_EMAIL))
        existing = result.scalar_one_or_none()
        if existing:
            # Ensure role is admin
            if existing.role != UserRole.ADMIN and existing.role != UserRole.SUPER_ADMIN:
                existing.role = UserRole.ADMIN
                session.add(existing)
                await session.commit()
                print(f"Updated role to admin for {ADMIN_EMAIL}")
            else:
                print(f"Admin user already exists: {ADMIN_EMAIL} (role={existing.role.value})")
            return
        password_hash = get_password_hash(ADMIN_PASSWORD)
        admin_user = User(
            email=ADMIN_EMAIL,
            password_hash=password_hash,
            first_name="Admin",
            last_name="Bella",
            role=UserRole.ADMIN,
        )
        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)
        print(f"Admin user created: {ADMIN_EMAIL} (id={admin_user.id})")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(ensure_admin())

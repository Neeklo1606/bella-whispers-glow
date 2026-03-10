#!/usr/bin/env python3
"""
Standalone: ensure admin exists. No app imports.
Email: admin@bellahasias.ru, Password: Admin123!, Role: admin
"""
import asyncio
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime

# Load .env
backend_dir = Path(__file__).resolve().parent.parent
env_file = backend_dir / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

# Minimal deps
from passlib.context import CryptContext
_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

ADMIN_EMAIL = "admin@bellahasias.ru"
ADMIN_PASSWORD = "Admin123!"


async def main():
    try:
        import sqlalchemy
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
    except ImportError as e:
        print(f"Import error: {e}")
        sys.exit(1)

    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("DATABASE_URL not set")
        sys.exit(1)
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(db_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        r = await session.execute(text("SELECT id, role FROM users WHERE email = :e"), {"e": ADMIN_EMAIL})
        row = r.fetchone()
        if row:
            role = str(row[1]) if row[1] else ""
            if role not in ("admin", "super_admin"):
                await session.execute(
                    text("UPDATE users SET role = 'admin' WHERE email = :e"),
                    {"e": ADMIN_EMAIL}
                )
                await session.commit()
                print(f"Updated role to admin for {ADMIN_EMAIL}")
            else:
                print(f"Admin exists: {ADMIN_EMAIL}")
            await engine.dispose()
            return

        pw_hash = _pwd.hash(ADMIN_PASSWORD)
        uid = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        await session.execute(text("""
            INSERT INTO users (id, email, password_hash, first_name, last_name, role, created_at, updated_at)
            VALUES (:id, :email, :pw, 'Admin', 'Bella', 'admin', :now, :now)
        """), {"id": uid, "email": ADMIN_EMAIL, "pw": pw_hash, "now": now})
        await session.commit()
        print(f"Admin created: {ADMIN_EMAIL}")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

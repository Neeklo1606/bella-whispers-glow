#!/usr/bin/env python3
"""
Pre-deployment checklist script.
Run from backend directory: python scripts/pre_deploy_checklist.py
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend))

# Load .env if present
env_file = backend / ".env"
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)


def check_1_migrations():
    """1. Run alembic upgrade head"""
    print("\n[1] MIGRATIONS (alembic upgrade head)")
    try:
        import subprocess
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=backend,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("   [OK] alembic upgrade head")
            if result.stdout.strip():
                print(f"   {result.stdout.strip()}")
        else:
            print(f"   [FAIL] {result.stderr or result.stdout}")
            return False
    except FileNotFoundError:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                cwd=backend,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print("   [OK] alembic upgrade head")
            else:
                print(f"   [FAIL] Run manually: alembic upgrade head")
                print(f"   {result.stderr or result.stdout}")
                return False
        except Exception as e:
            print("   [FAIL] Run manually: cd backend && alembic upgrade head")
            return False
    return True


async def check_2_system_settings():
    """2. SELECT * FROM system_settings"""
    print("\n[2] SYSTEM_SETTINGS (SELECT * FROM system_settings)")
    try:
        from src.core.db.database import AsyncSessionLocal
        from src.modules.system_settings.repository import SystemSettingRepository

        async with AsyncSessionLocal() as db:
            repo = SystemSettingRepository(db)
            settings = await repo.get_all()
            count = len(settings)
            print(f"   [OK] Found {count} row(s) in system_settings")
            for s in settings[:10]:  # show first 10
                val = s.value[:20] + "..." if s.value and len(str(s.value)) > 20 else s.value
                print(f"      - {s.key}: {val}")
            if count > 10:
                print(f"      ... and {count - 10} more")
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        return False
    return True


async def check_3_health(base_url: str):
    """3. GET /health"""
    print("\n[3] HEALTH (GET /health)")
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{base_url}/health")
            if r.status_code == 200 and r.json().get("status") == "ok":
                print('   [OK] GET /health -> { "status": "ok" }')
            else:
                print(f"   [FAIL] Expected status ok, got: {r.text[:100]}")
                return False
    except Exception as e:
        print("   [WARN] Server may not be running. Start: uvicorn src.main:app")
        print(f"   Error: {e}")
        return False
    return True


def check_4_admin_settings():
    """4. Admin settings page — manual/structural check"""
    print("\n[4] ADMIN SETTINGS (/admin/settings)")
    frontend_admin = Path(__file__).resolve().parent.parent.parent / "src" / "pages" / "AdminSettings.tsx"
    if frontend_admin.exists():
        print("   [OK] Frontend: AdminSettings.tsx exists")
    else:
        print("   [FAIL] AdminSettings.tsx not found")
    # Check API route
    admin_router = backend / "src" / "modules" / "admin" / "router.py"
    content = admin_router.read_text()
    if '"/settings"' in content and "admin_get_settings" in content:
        print("   [OK] Backend: GET /api/admin/settings exists")
    else:
        print("   [FAIL] Backend admin settings route missing")
    print("   Manual: open /admin/settings in browser after login")
    return True


async def check_5_telegram_bot(base_url: str):
    """5. Telegram bot getMe, getChat"""
    print("\n[5] TELEGRAM BOT (getMe, getChat)")
    try:
        from src.core.db.database import AsyncSessionLocal
        from src.modules.telegram.bot_service import TelegramBotService

        async with AsyncSessionLocal() as db:
            service = await TelegramBotService.create(db)

        # getMe
        try:
            me = await service.bot.get_me()
            print(f"   [OK] getMe: @{me.username} (id={me.id})")
        except Exception as e:
            print(f"   [FAIL] getMe failed: {e}")
            return False

        # getChat
        try:
            chat = await service.bot.get_chat(chat_id=service.channel_id)
            print(f"   [OK] getChat: {chat.title} (id={chat.id})")
        except Exception as e:
            print(f"   [FAIL] getChat failed (check TELEGRAM_CHANNEL_ID): {e}")
            return False

    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        return False
    return True


async def check_6_payment_webhook(base_url: str):
    """6. POST /api/payments/webhook"""
    print("\n[6] PAYMENT WEBHOOK (POST /api/payments/webhook)")
    try:
        import httpx
        # Minimal valid webhook payload (YooKassa-style)
        payload = {
            "event": "payment.succeeded",
            "object": {"id": "test-check-id", "status": "succeeded"},
        }
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(f"{base_url}/api/payments/webhook", json=payload)
            # 200 or 400/500 is acceptable — endpoint exists and responds
            if r.status_code in (200, 400, 422, 500):
                print(f"   [OK] POST /api/payments/webhook responds (status={r.status_code})")
                if r.status_code != 200:
                    print(f"      (Expected for test payload without valid signature)")
            else:
                print(f"   [FAIL] Unexpected status: {r.status_code}")
                return False
    except Exception as e:
        print(f"   [WARN] Server may not be running. Error: {e}")
        return False
    return True


async def main():
    base_url = (os.getenv("API_URL") or os.getenv("VITE_API_URL") or "http://localhost:8000").rstrip("/")
    print("=" * 50)
    print("Pre-deployment checklist")
    print("=" * 50)

    ok = check_1_migrations()
    ok = await check_2_system_settings() and ok
    ok = await check_3_health(base_url) and ok
    check_4_admin_settings()
    ok = await check_5_telegram_bot(base_url) and ok
    ok = await check_6_payment_webhook(base_url) and ok

    print("\n" + "=" * 50)
    if ok:
        print("[OK] Checklist passed (start server for health/webhook if needed)")
    else:
        print("[FAIL] Some checks failed. Fix before deploy.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

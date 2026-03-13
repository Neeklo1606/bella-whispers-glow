"""
Production readiness audit script.
Checks all critical components before deployment.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config import settings


class AuditResult:
    """Audit result container."""
    def __init__(self):
        self.passed = []
        self.warnings = []
        self.errors = []
    
    def add_pass(self, message: str):
        self.passed.append(message)
    
    def add_warning(self, message: str):
        self.warnings.append(message)
    
    def add_error(self, message: str):
        self.errors.append(message)
    
    def print_report(self):
        """Print audit report."""
        print("\n" + "="*60)
        print("PRODUCTION READINESS AUDIT REPORT")
        print("="*60)
        
        print(f"\n✅ PASSED: {len(self.passed)}")
        for msg in self.passed:
            print(f"  ✓ {msg}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS: {len(self.warnings)}")
            for msg in self.warnings:
                print(f"  ⚠ {msg}")
        
        if self.errors:
            print(f"\n❌ ERRORS: {len(self.errors)}")
            for msg in self.errors:
                print(f"  ✗ {msg}")
        
        print("\n" + "="*60)
        
        if self.errors:
            print("❌ AUDIT FAILED - Fix errors before deployment")
            return False
        elif self.warnings:
            print("⚠️  AUDIT PASSED WITH WARNINGS - Review warnings")
            return True
        else:
            print("✅ AUDIT PASSED - Ready for deployment")
            return True


def audit_settings(result: AuditResult):
    """Audit environment variables."""
    print("\n[1/10] Auditing Settings...")
    
    required_vars = {
        "DATABASE_URL": settings.DATABASE_URL,
        "SECRET_KEY": settings.SECRET_KEY,
        "TELEGRAM_BOT_TOKEN": settings.TELEGRAM_BOT_TOKEN,
        "TELEGRAM_CHANNEL_ID": settings.TELEGRAM_CHANNEL_ID,
    }
    
    optional_vars = {
        "BOT_API_SECRET": settings.BOT_API_SECRET,
        "YOOKASSA_SHOP_ID": settings.YOOKASSA_SHOP_ID,
        "YOOKASSA_SECRET_KEY": settings.YOOKASSA_SECRET_KEY,
    }
    
    for var_name, var_value in required_vars.items():
        if not var_value:
            result.add_error(f"Required env variable {var_name} is missing")
        else:
            result.add_pass(f"Required env variable {var_name} is set")
    
    for var_name, var_value in optional_vars.items():
        if not var_value:
            result.add_warning(f"Optional env variable {var_name} is not set (may be needed in production)")
        else:
            result.add_pass(f"Optional env variable {var_name} is set")
    
    # Check API_BASE_URL (used by bot)
    if not hasattr(settings, 'API_BASE_URL'):
        result.add_warning("API_BASE_URL not found in settings (bot may need this)")


def audit_migrations(result: AuditResult):
    """Audit database migrations."""
    print("\n[2/10] Auditing Database Migrations...")
    
    migrations_dir = Path(__file__).parent.parent / "alembic" / "versions"
    if not migrations_dir.exists():
        result.add_error("Migrations directory not found")
        return
    
    migration_files = list(migrations_dir.glob("*.py"))
    if not migration_files:
        result.add_error("No migration files found")
        return
    
    result.add_pass(f"Found {len(migration_files)} migration files")
    
    # Check for required migration
    required_migration = "004_extend_platform_security_payments.py"
    if any(required_migration in f.name for f in migration_files):
        result.add_pass(f"Required migration {required_migration} exists")
    else:
        result.add_error(f"Required migration {required_migration} not found")
    
    # Check for required tables in migration
    migration_content = ""
    migration_file = migrations_dir / required_migration
    if migration_file.exists():
        migration_content = migration_file.read_text()
        required_tables = [
            "channel_access_logs",
            "subscriptions",
            "subscription_plans",
            "payments",
            "users",
        ]
        for table in required_tables:
            if table in migration_content:
                result.add_pass(f"Table {table} referenced in migration")
            else:
                result.add_warning(f"Table {table} not found in migration (may be in earlier migration)")


def audit_webhook_security(result: AuditResult):
    """Audit webhook security."""
    print("\n[3/10] Auditing Webhook Security...")
    
    webhook_file = Path(__file__).parent.parent / "src" / "modules" / "payments" / "router.py"
    if not webhook_file.exists():
        result.add_error("Webhook router file not found")
        return
    
    content = webhook_file.read_text()
    
    # Check webhook endpoint exists
    if "/webhook" in content:
        result.add_pass("Webhook endpoint exists")
    else:
        result.add_error("Webhook endpoint not found")
    
    # Check signature validation
    service_file = Path(__file__).parent.parent / "src" / "modules" / "payments" / "service.py"
    if service_file.exists():
        service_content = service_file.read_text()
        if "verify_webhook" in service_content:
            result.add_pass("Webhook signature verification exists")
        else:
            result.add_error("Webhook signature verification not found")
        
        if "idempotency" in service_content.lower() or "already processed" in service_content.lower():
            result.add_pass("Idempotency protection exists")
        else:
            result.add_error("Idempotency protection not found")
    else:
        result.add_error("Payment service file not found")


def audit_bot_security(result: AuditResult):
    """Audit bot security."""
    print("\n[4/10] Auditing Bot Security...")
    
    telegram_router = Path(__file__).parent.parent / "src" / "modules" / "telegram" / "router.py"
    if not telegram_router.exists():
        result.add_error("Telegram router file not found")
        return
    
    content = telegram_router.read_text()
    
    # Check revoke-invite-link endpoint
    if "/revoke-invite-link" in content:
        result.add_pass("revoke-invite-link endpoint exists")
    else:
        result.add_error("revoke-invite-link endpoint not found")
    
    # Check bot authentication
    if "verify_bot_secret" in content:
        result.add_pass("Bot secret verification exists")
    else:
        result.add_error("Bot secret verification not found")
    
    # Check bot_auth module
    bot_auth_file = Path(__file__).parent.parent / "src" / "core" / "security" / "bot_auth.py"
    if bot_auth_file.exists():
        result.add_pass("Bot authentication module exists")
        bot_auth_content = bot_auth_file.read_text()
        if "X-Bot-Secret" in bot_auth_content:
            result.add_pass("X-Bot-Secret header check exists")
        else:
            result.add_error("X-Bot-Secret header check not found")
    else:
        result.add_error("Bot authentication module not found")


def audit_scheduler(result: AuditResult):
    """Audit scheduler configuration."""
    print("\n[5/10] Auditing Scheduler...")
    
    scheduler_file = Path(__file__).parent.parent / "src" / "workers" / "scheduler.py"
    if not scheduler_file.exists():
        result.add_error("Scheduler file not found")
        return
    
    content = scheduler_file.read_text()
    
    # Check check_expired_subscriptions job
    if "check_expired_subscriptions" in content:
        result.add_pass("check_expired_subscriptions job exists")
    else:
        result.add_error("check_expired_subscriptions job not found")
    
    # Check interval (10 minutes)
    if "IntervalTrigger(minutes=10)" in content or "minutes=10" in content:
        result.add_pass("check_expired_subscriptions runs every 10 minutes")
    else:
        result.add_warning("check_expired_subscriptions interval may not be 10 minutes")


def audit_health_check(result: AuditResult):
    """Audit health check endpoint."""
    print("\n[6/10] Auditing Health Check...")
    
    main_file = Path(__file__).parent.parent / "src" / "main.py"
    if not main_file.exists():
        result.add_error("Main file not found")
        return
    
    content = main_file.read_text()
    
    # Check health endpoint
    if "/health" in content:
        result.add_pass("Health check endpoint exists")
    else:
        result.add_error("Health check endpoint not found")
    
    # Check response format
    if '"status": "ok"' in content or "'status': 'ok'" in content:
        result.add_pass("Health check returns correct format")
    else:
        result.add_warning("Health check response format may be incorrect")


def audit_logging(result: AuditResult):
    """Audit logging configuration."""
    print("\n[7/10] Auditing Logging...")
    
    # Check logging in key modules
    modules_to_check = [
        ("payments", "service.py"),
        ("subscriptions", "service.py"),
        ("telegram", "bot_service.py"),
        ("workers/tasks", "subscription_tasks.py"),
    ]
    
    for module_path, file_name in modules_to_check:
        file_path = Path(__file__).parent.parent / "src" / "modules" / module_path / file_name
        if not file_path.exists():
            file_path = Path(__file__).parent.parent / "src" / "workers" / "tasks" / file_name
        
        if file_path.exists():
            content = file_path.read_text()
            if "import logging" in content or "from logging import" in content:
                result.add_pass(f"Logging configured in {module_path}/{file_name}")
            else:
                result.add_warning(f"Logging not found in {module_path}/{file_name}")
        else:
            result.add_warning(f"File {module_path}/{file_name} not found")


def audit_error_handling(result: AuditResult):
    """Audit error handling."""
    print("\n[8/10] Auditing Error Handling...")
    
    # Check telegram bot service
    bot_service = Path(__file__).parent.parent / "src" / "modules" / "telegram" / "bot_service.py"
    if bot_service.exists():
        content = bot_service.read_text()
        if "try:" in content and "except" in content:
            result.add_pass("Telegram bot service has error handling")
        else:
            result.add_warning("Telegram bot service may lack error handling")
    
    # Check payment service
    payment_service = Path(__file__).parent.parent / "src" / "modules" / "payments" / "service.py"
    if payment_service.exists():
        content = payment_service.read_text()
        if "try:" in content and "except" in content:
            result.add_pass("Payment service has error handling")
        else:
            result.add_warning("Payment service may lack error handling")
    
    # Check subscription tasks
    subscription_tasks = Path(__file__).parent.parent / "src" / "workers" / "tasks" / "subscription_tasks.py"
    if subscription_tasks.exists():
        content = subscription_tasks.read_text()
        if "try:" in content and "except" in content:
            result.add_pass("Subscription tasks have error handling")
        else:
            result.add_warning("Subscription tasks may lack error handling")


def audit_service_structure(result: AuditResult):
    """Audit service structure."""
    print("\n[9/10] Auditing Service Structure...")
    
    # Check backend main
    backend_main = Path(__file__).parent.parent / "src" / "main.py"
    if backend_main.exists():
        result.add_pass("Backend main.py exists")
    else:
        result.add_error("Backend main.py not found")
    
    # Check bot main
    bot_main = Path(__file__).parent.parent.parent / "bot" / "src" / "main.py"
    if bot_main.exists():
        result.add_pass("Bot main.py exists")
    else:
        result.add_warning("Bot main.py not found (may be in different location)")
    
    # Check scheduler can run independently
    scheduler_file = Path(__file__).parent.parent / "src" / "workers" / "scheduler.py"
    if scheduler_file.exists():
        content = scheduler_file.read_text()
        if "create_scheduler" in content and "start_scheduler" in content:
            result.add_pass("Scheduler can be initialized independently")
        else:
            result.add_warning("Scheduler structure may need review")


def audit_webhook_endpoint(result: AuditResult):
    """Audit webhook endpoint error handling."""
    print("\n[10/10] Auditing Webhook Endpoint...")
    
    webhook_router = Path(__file__).parent.parent / "src" / "modules" / "payments" / "router.py"
    if webhook_router.exists():
        content = webhook_router.read_text()
        
        # Check if webhook has try/except
        if "try:" in content or "except" in content:
            result.add_pass("Webhook endpoint has error handling")
        else:
            result.add_warning("Webhook endpoint may need error handling")
        
        # Check if webhook returns proper response
        if "return" in content and "status" in content:
            result.add_pass("Webhook endpoint returns proper response")
        else:
            result.add_warning("Webhook endpoint response format may need review")


def main():
    """Run production audit."""
    result = AuditResult()
    
    print("Starting Production Readiness Audit...")
    print("="*60)
    
    audit_settings(result)
    audit_migrations(result)
    audit_webhook_security(result)
    audit_bot_security(result)
    audit_scheduler(result)
    audit_health_check(result)
    audit_logging(result)
    audit_error_handling(result)
    audit_service_structure(result)
    audit_webhook_endpoint(result)
    
    success = result.print_report()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

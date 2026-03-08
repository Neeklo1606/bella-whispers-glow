"""Standalone scheduler runner - runs APScheduler with asyncio event loop."""
import asyncio
import sys
from pathlib import Path

# Ensure backend is in path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.workers.scheduler import create_scheduler, start_scheduler


async def run():
    scheduler = create_scheduler()
    start_scheduler(scheduler)
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(run())

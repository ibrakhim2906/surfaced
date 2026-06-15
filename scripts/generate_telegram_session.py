"""
Run once to generate a Telegram session string for production use.

Usage:
    uv run python scripts/generate_telegram_session.py

Copy the printed session string into your .env as TELEGRAM_SESSION_STRING.
"""

from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 38266199
API_HASH = "3d9a26fc7654f521d265ca4acb63940b"


async def main():
    async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        session_string = client.session.save()
        print("\n✅ Session string generated. Add this to your .env:\n")
        print(f"TELEGRAM_SESSION_STRING={session_string}\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

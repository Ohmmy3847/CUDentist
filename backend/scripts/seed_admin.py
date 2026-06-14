"""
Create the first superadmin user.
Run from the backend/ directory:
    python scripts/seed_admin.py
"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.models.user import User
from app.core.security import hash_password

DATABASE_URL = os.getenv("DATABASE_URL", "")

# ── Change these before running ──────────────────────────────────────
USERNAME   = "admin"
PASSWORD   = "changeme123"   # change this!
FIRST_NAME = "Admin"
LAST_NAME  = "User"
EMAIL      = ""
# ─────────────────────────────────────────────────────────────────────


async def main():
    engine = create_async_engine(DATABASE_URL)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as db:
        existing = await db.execute(select(User).where(User.username == USERNAME))
        if existing.scalar_one_or_none():
            print(f"User '{USERNAME}' already exists — skipping.")
            return

        user = User(
            username=USERNAME,
            password_hash=hash_password(PASSWORD),
            first_name=FIRST_NAME,
            last_name=LAST_NAME,
            email=EMAIL or None,
            role="superadmin",
            roles=["superadmin"],
            is_active=True,
            is_superuser=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"✓ Created superadmin: username='{USERNAME}' (user_id={user.user_id})")
        print(f"  Password: {PASSWORD}")
        print(f"  !! Change the password after first login !!")


asyncio.run(main())

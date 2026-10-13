import asyncio
import sys

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models import Student


async def create_admin(email: str, password: str) -> None:
    email = email.lower()
    async with AsyncSessionLocal() as session:
        existing = await session.scalar(select(Student).where(Student.email == email))
        if existing is not None:
            existing.role = "admin"
            existing.password_hash = hash_password(password)
        else:
            session.add(
                Student(
                    full_name="Administrator",
                    email=email,
                    password_hash=hash_password(password),
                    role="admin",
                )
            )
        await session.commit()
    print(f"Admin ready: {email}")


def main() -> None:
    if len(sys.argv) != 3:
        print("usage: python create_admin.py <email> <password>")
        raise SystemExit(1)
    asyncio.run(create_admin(sys.argv[1], sys.argv[2]))


if __name__ == "__main__":
    main()

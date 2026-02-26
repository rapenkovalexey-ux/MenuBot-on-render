from datetime import datetime, timedelta
from sqlalchemy import (
    Column, Integer, String, DateTime,
    Float, JSON, ForeignKey, select
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from config import TURSO_DATABASE_URL, TURSO_AUTH_TOKEN, USE_TURSO

Base = declarative_base()

# --- Engine ---
# Актуальный способ подключения через sqlalchemy-libsql (пакет от Turso, июнь 2025)
# Документация: https://docs.turso.tech/sdk/python/orm/sqlalchemy
if USE_TURSO:
    # Режим "Remote only" — все запросы идут напрямую в Turso Cloud
    engine = create_async_engine(
        f"sqlite+{TURSO_DATABASE_URL}?secure=true",
        connect_args={
            "auth_token": TURSO_AUTH_TOKEN,
        },
        echo=False,
    )
else:
    # Локальная разработка — обычный SQLite через aiosqlite
    from config import DATABASE_URL
    engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    plan = Column(String, default="free")  # free | trial | paid
    trial_start = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)
    paid_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    menus = relationship("Menu", back_populates="user")
    profiles = relationship("EaterProfile", back_populates="user")


class EaterProfile(Base):
    __tablename__ = "eater_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    preferences = Column(String, nullable=True)
    user = relationship("User", back_populates="profiles")


class Menu(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    diet_type = Column(String, nullable=False)
    num_people = Column(Integer, default=1)
    num_days = Column(Integer, default=1)
    meals_per_day = Column(JSON)
    content = Column(JSON)
    shopping_list = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="draft")  # draft | confirmed
    user = relationship("User", back_populates="menus")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    currency = Column(String, default="RUB")
    status = Column(String)  # pending | success | failed
    payment_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


async def get_or_create_user(session: AsyncSession, telegram_id: int, username: str = None, full_name: str = None):
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(telegram_id=telegram_id, username=username, full_name=full_name)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def get_user_plan(session: AsyncSession, telegram_id: int) -> str:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        return "free"
    if user.plan == "paid" and user.paid_until and user.paid_until > datetime.utcnow():
        return "paid"
    if user.plan == "trial" and user.trial_end and user.trial_end > datetime.utcnow():
        return "trial"
    return "free"

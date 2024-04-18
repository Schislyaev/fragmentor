from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.settings import settings

# DATABASE_URL = (f'postgresql+asyncpg://{settings.db_user}:'
#                 f'{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}')
DATABASE_URL = settings.database_url
engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def init_table(table: str):
    async with engine.begin() as conn:
        # Получаем объект Table для таблицы bookings
        bookings_table = Base.metadata.tables[table]

        # Удаляем таблицу bookings, если она существует
        await conn.run_sync(bookings_table.drop, checkfirst=True)

        # Создаём таблицу bookings
        await conn.run_sync(bookings_table.create, checkfirst=True)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Замените следующие значения на реальные параметры подключения
username = 'domitoch_admin_0'
password = 'g-%tE)w,*bIm'
host = 'localhost'
port = '3306'
database = 'domitoch_objects_database'

# Создание строки подключения
connection_string = f"mysql+aiomysql://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4"

# Создание асинхронного движка SQLAlchemy
engine = create_async_engine(connection_string, echo=True)

# Создание фабрики сессий
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def test_connection():
    # Асинхронное создание сессии
    async with async_session() as session:
        # Асинхронный запрос к базе данных
        result = await session.execute(text("SELECT VERSION();"))
        version = result.fetchone()
        print(f"Успешное подключение к MySQL. Версия сервера: {version[0]}")

async def main():
    await test_connection()
    await engine.dispose()  # Явное закрытие соединения с базой данных

import asyncio
asyncio.run(main())

import asyncio
import aiohttp, schedule
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from database import FlatsSaleObjectsData, Databases
from data_parser import RealtParser


# Асинхронное подключение к базе данных
engine_user_data = create_async_engine("sqlite+aiosqlite:///ObjectData.db")
Base = declarative_base() 
Session_user_data = sessionmaker(bind=engine_user_data,class_=AsyncSession)


# Главная асинхронная функция
async def main():
    await Databases.create_tables() # Создаем таблицы в БД
    async with aiohttp.ClientSession() as session:
        urls = await RealtParser.url_parser(session)
        await Databases.save_urls_to_db(urls)  # Сохраняем URL в БД
        # Парсим данные с каждого URL и сохраняем в БД
        tasks = [RealtParser.get_object_data(session, url) for url in urls]
        await asyncio.gather(*tasks)


# Запуск основной асинхронной функции
if __name__ == '__main__':
    asyncio.run(main())


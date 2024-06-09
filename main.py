import asyncio
import aiohttp, schedule
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import database
from database import FlatsSaleObjectsData, Base
from data_parser import RealtParser


engine_user_data = create_async_engine("sqlite+aiosqlite:///ObjectData.db")
Session_user_data = sessionmaker(bind=engine_user_data,class_=AsyncSession)


async def create_tables():
    async with engine_user_data.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        

# Главная асинхронная функция
async def main():
    async with aiohttp.ClientSession() as session:
        urls = await RealtParser.url_parser(session)
        print(urls)
        await database.Databases.save_urls_to_db(urls, Session_user_data)  # Сохраняем URL в БД
        # Парсим данные с каждого URL и сохраняем в БД
        tasks = [RealtParser.get_object_data(url, Session_user_data) for url in urls]
        await asyncio.gather(*tasks)


# Запуск основной асинхронной функции
if __name__ == '__main__':
    asyncio.run(main())


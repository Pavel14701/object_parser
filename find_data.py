#!/usr/bin/env python3
import asyncio
import aiohttp
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from databases.database import FlatsSaleObjectsData, Base, Databases
from objects_parser.data_parser import RealtParser
from project_configs.configurations import load_bd_configs


password_bd, username_bd, host_bd, database_bd, port_bd = load_bd_configs()
engine_user_data = create_async_engine(f"mysql+aiomysql://{username_bd}:{password_bd}@{host_bd}:{port_bd}/{database_bd}")
Session_user_data = sessionmaker(bind=engine_user_data,class_=AsyncSession)


async def create_tables():
    async with engine_user_data.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        

# Главная асинхронная функция
async def main():
    async with aiohttp.ClientSession() as session:
        urls = await Databases.get_all_urls(Session_user_data)
        print(urls)
        # Парсим данные с каждого URL и сохраняем в БД
        tasks = [RealtParser.get_object_data(url, Session_user_data) for url in urls]
        await asyncio.gather(*tasks)
        tasks = [RealtParser.get_object_pictures(url, Session_user_data) for url in urls]
        await asyncio.gather(*tasks)



# Запуск основной асинхронной функции
if __name__ == '__main__':
    asyncio.run(main())


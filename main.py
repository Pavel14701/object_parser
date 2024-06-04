import asyncio
import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, select, delete

# Асинхронное подключение к базе данных
engine_user_data = create_async_engine("sqlite+aiosqlite:///ObjectData.db")
Base = declarative_base()

# Определение модели данных
class FlatsSaleObjectsData(Base):
    __tablename__ = "FlatsObjectsData"
    url = Column(String, primary_key=True)  # Url каждого объекта
    location_city = Column(String, nullable=True)  # Город, где расположен объект
    location_adress = Column(String, nullable=True)  # Адрес, где расположен объект
    location_coordinates = Column(String, nullable=True)  # Координаты местоположения объекта
    number_of_rooms = Column(String, nullable=True)  # Количество комнат
    total_area = Column(Float, nullable=True)  # Общая площадь
    living_area = Column(Float, nullable=True)  # Жилая площадь
    kitchen_area = Column(Float, nullable=True)  # Площадь кухни
    celling_heights = Column(String, nullable=True)  # Высота потолков
    repair = Column(String, nullable=True)  # Ремонт
    bathroom = Column(String, nullable=True)  # Санузлы
    balcony = Column(String, nullable=True)  # Балконы
    furniture = Column(Boolean, default=False)  # Мебель
    house_type = Column(String, nullable=True)  # Тип дома
    number_of_floors = Column(Integer, nullable=True)  # Этажность
    floor = Column(Integer, nullable=True)  # Этаж
    floor_no_first = Column(Boolean, default=False)  # Тип этажа(не первый)
    floor_no_last = Column(Boolean, default=False)  # Тип этажа(не последний)
    year_of_constraction = Column(Integer, nullable=True)  # Год постройки
    year_of_renovation = Column(Integer, nullable=True)  # Когда был ремонт
    major_repair = Column(Boolean, default=False)  # Наличие кап ремонта
    major_repair_year = Column(Integer, nullable=True)  # Год капитального ремонта(если есть)
    parking = Column(Boolean, default=False)  # Наличие парковки
    terms_of_transaction = Column(String, nullable=True)  # Условия сделки
    ownership = Column(String, nullable=True)  # Тип собственности
    
Session_user_data = sessionmaker(bind=engine_user_data,class_=AsyncSession)

# Создание таблиц асинхронно
async def create_tables():
    async with engine_user_data.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Асинхронный парсер URL
async def url_parser(session):
    links = []
    for i in range(1, 4):
        url = f"https://realt.by/belarus/sale/flats/?agencyUuids=01036310-5165-11ee-9a2f-abc708f86719&page={i}&seller=false"
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            elements = soup.find_all("a", attrs={"aria-label": lambda x: x and x.startswith("Ссылка на объект №")})
            for element in elements:
                href = element.get("href")
                href = "https://realt.by" + href
                links.append(href)
        print(f'operation {i} complete')
    return links

# Функция для парсинга страницы и извлечения данных
async def parse_page(session, url):
    async with session.get(url) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        # Используйте soup и re для извлечения данных
        # ...
        # Создайте словарь с данными
        data = {
            'url': url,
            # 'location_city': ...,
            # 'location_adress': ...,
            # ...
        }
        # Сохраните данные в базу данных
        await save_to_db(data)

# Асинхронная функция для сохранения данных в базу данных
async def save_to_db(data):
    async with Session_user_data() as async_session:
        new_object = FlatsSaleObjectsData(**data)
        async_session.add(new_object)
        await async_session.commit()

# Асинхронная функция для сохранения URL в базу данных
async def save_urls_to_db(urls):
    async with Session_user_data() as session:
        # Получаем список существующих URL из базы данных
        existing_urls = (await session.execute(
            select(FlatsSaleObjectsData.url)
        )).scalars().all()
        # Находим URL для добавления (есть в новом списке, но нет в базе данных)
        urls_to_add = set(urls) - set(existing_urls)
        # Находим URL для удаления (есть в базе данных, но нет в новом списке)
        urls_to_remove = set(existing_urls) - set(urls)
        # Добавляем новые URL в базу данных
        for url in urls_to_add:
            new_entry = FlatsSaleObjectsData(url=url)
            session.add(new_entry)
        # Удаляем старые URL из базы данных
        for url in urls_to_remove:
            await session.execute(
                delete(FlatsSaleObjectsData).where(FlatsSaleObjectsData.url == url)
            )
        # Фиксируем изменения в базе данных
        await session.commit()

# Главная асинхронная функция
async def main():
    await create_tables()  # Создаем таблицы в БД
    async with aiohttp.ClientSession() as session:
        urls = await url_parser(session)  # Получаем список URL
        await save_urls_to_db(urls)  # Сохраняем URL в БД
        # Парсим данные с каждого URL и сохраняем в БД
        tasks = [parse_page(session, url) for url in urls]
        await asyncio.gather(*tasks)

# Запуск асинхронной функции
asyncio.run(main())


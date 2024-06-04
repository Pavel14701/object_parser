from sqlalchemy import Column, Integer, String, Float, Boolean, select, delete
from main import Base, engine_user_data, Session_user_data


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
    
class Databases:
    @staticmethod
    async def create_tables():
        async with engine_user_data.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            

    @staticmethod
    async def save_urls_to_db(urls):
        async with Session_user_data() as session:
            try:
                # Получаем список существующих URL из базы данных
                existing_urls = (await session.execute(
                    select(FlatsSaleObjectsData.url)
                )).scalars().all()
                # Находим URL для добавления и удаления
                urls_to_add = set(urls) - set(existing_urls)
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
            except Exception as e:
                # В случае ошибки откатываем изменения
                await session.rollback()
                print(f'Произошла ошибка: {e}')
            finally:
                # Закрываем сессию
                await session.close()
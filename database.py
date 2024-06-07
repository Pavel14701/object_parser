from sqlalchemy import Column, Integer, String, Float, Boolean, select, delete
from sqlalchemy.orm import declarative_base
from sqlalchemy import ExceptionContext


Base = declarative_base()

class FlatsSaleObjectsData(Base):
    __tablename__ = "FlatsObjectsData"
    url = Column(String, primary_key=True)  # Url каждого объекта
    title = Column(String, nullable=True) # Заголовок
    description = Column(String, nullable=True) # Описание
    district = Column(String, nullable=True) # Область, где расположен объект
    location_city = Column(String, nullable=True)  # Город, где расположен объект
    location_adress = Column(String, nullable=True)  # Адрес, где расположен объект
    location_coordinates = Column(String, nullable=True)  # Координаты местоположения объекта
    number_of_rooms = Column(String, nullable=True)  # Количество комнат
    total_area = Column(String, nullable=True)  # Общая площадь
    living_area = Column(String, nullable=True)  # Жилая площадь
    kitchen_area = Column(String, nullable=True)  # Площадь кухни
    celling_heights = Column(String, nullable=True)  # Высота потолков
    type_of_layout = Column(String, nullable=True)  # Ремонт
    bathroom = Column(String, nullable=True)  # Санузлы
    balcony = Column(String, nullable=True)  # Балконы
    furniture = Column(Boolean, default=True)  # Мебель
    house_type = Column(String, nullable=True)  # Тип дома
    number_of_floors = Column(Integer, nullable=True)  # Этажность
    floor = Column(Integer, nullable=True)  # Этаж
    contract_number = Column(String, nullable=True)
    floor_no_first = Column(Boolean, default=True)  # Тип этажа(не первый)
    floor_no_last = Column(Boolean, default=True)  # Тип этажа(не последний)
    year_of_constraction = Column(Integer, nullable=True)  # Год постройки
    year_of_renovation = Column(Integer, nullable=True)  # Когда был ремонт
    major_repair = Column(Boolean, nullable=True)  # Наличие кап ремонта
    major_repair_year = Column(Integer, nullable=True)  # Год капитального ремонта(если есть)
    parking = Column(Boolean, nullable=True)  # Наличие парковки
    terms_of_transaction = Column(String, nullable=True)  # Условия сделки
    ownership = Column(String, nullable=True)  # Тип собственности
    
class Databases:
    @staticmethod
    async def save_urls_to_db(urls, Session_user_data):
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
                
                
    @staticmethod
    async def insert_or_update_data_to_db(data, Session_user_data):
        async with Session_user_data() as session:
            try:
                data['floor_no_first'] = data['building']['floor'] != '1'
                data['floor_no_last'] = (
                    data['building']['floor'] == data['building']['number_storeys']
                )
                # Создание или обновление объекта данных
                new_or_updated_data = FlatsSaleObjectsData(
                    url=data['url'],
                    title=data['title'],
                    description=data['description'],
                    district=data['address']['district'],
                    location_city=data['address']['city'],
                    location_adress=data['address']['street'],
                    location_coordinates=data['location_coordinates'],
                    number_of_rooms=data['details']['number_of_rooms'],
                    total_area=data['area']['total_area'],
                    living_area=data['area']['living_area'],
                    kitchen_area=data['area']['kitchen_area'],
                    celling_heights=data['details']['ceiling_height'],
                    type_of_layout=data['details']['type_of_layout'],
                    bathroom=data['details']['bathroom'],
                    balcony=data['details']['balcony'],
                    house_type=data['details']['type_of_house'],
                    number_of_floors=data['building']['number_storeys'],
                    floor=data['building']['floor'],
                    contract_number=data['details']['contract_number'],
                    floor_no_first=data['floor_no_first'],
                    floor_no_last=data['floor_no_last'],
                    year_of_constraction=data['details']['year_of_build'],
                    terms_of_transaction=data['details']['terms_of_sale'],
                    ownership=data['details']['own_type']
                )
                # Объединение объекта с сессией, что приведет к обновлению или добавлению
                await session.merge(new_or_updated_data)
                await session.commit()
            except Exception as e:
                # В случае ошибки откатываем изменения
                await session.rollback()
                print(f'Произошла ошибка: {e}')
            finally:
                # Закрытие сессии
                await session.close()

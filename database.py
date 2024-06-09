from sqlalchemy import Column, Integer, String, Boolean, select, delete
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class FlatsSaleObjectsData(Base):
    __tablename__ = "FlatsObjectsData"
    url = Column(String, primary_key=True)  # Url каждого объекта
    title = Column(String, nullable=True) # Заголовок
    description = Column(String, nullable=True) # Описание
    district = Column(String, nullable=True) # Область, где расположен объект
    region = Column(String, nullable=True) # Район, где расположен объект
    subregion = Column(String, nullable=True)
    location_city = Column(String, nullable=True)  # Город, где расположен объект
    location_street = Column(String, nullable=True)  # Адрес, где расположен объект
    house_number = Column(String, nullable=True)
    location_coordinates = Column(String, nullable=True)  # Координаты местоположения объекта
    number_of_floors = Column(Integer, nullable=True)  # Этажность
    floor = Column(Integer, nullable=True)  # Этаж
    floor_no_first = Column(Boolean, nullable=True)  # Тип этажа(не первый)
    floor_no_last = Column(Boolean, nullable=True)  # Тип этажа(не последний)
    floor_last = Column(Boolean, nullable=True) # Тип этажа(последний)
    home_maintenance = Column(String, nullable=True) # Обслуживающая организация
    year_of_build = Column(Integer, nullable=True)  # Год постройки
    type_of_layout = Column(String, nullable=True)  # Тип материала(Панель, Блок)
    type_of_finishing = Column(String, nullable=True) # Ремонт
    number_of_rooms = Column(String, nullable=True)  # Количество комнат
    separated_rooms = Column(String, nullable=True) # Количество раздельных комнат
    all_rooms_separated = Column(Boolean, nullable=True) # Все комнаты раздельные
    total_area = Column(String, nullable=True)  # Общая площадь
    living_area = Column(String, nullable=True)  # Жилая площадь
    kitchen_area = Column(String, nullable=True)  # Площадь кухни
    celling_heights = Column(String, nullable=True)  # Высота потолков
    bathroom = Column(String, nullable=True)  # Санузлы
    balcony = Column(String, nullable=True)  # Балконы
    furniture = Column(String, default=True)  # Мебель
    project = Column(String, nullable=True)  # Тип дома(Чешка, Сталинка, Своб. пл.)
    contract_number = Column(String, nullable=True)
    parking = Column(Boolean, nullable=True)  # Наличие парковки
    view_windows = Column(String, nullable=True) # Вид из окна
    yard_improvement = Column(String, nullable=True) # Удобства двора(список)
    facilities_for_disabled_people = Column(String, nullable=True) # Удобсбва для инвалидов
    terms_of_sale = Column(String, nullable=True)  # Условия сделки
    ownership = Column(String, nullable=True)  # Тип собственности
    pictures_urls = Column(String, nullable=True) # Ссылки на картинки


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
    async def insert_or_update_data_to_db(url, yard_improvement, parking, facilities_for_disabled_people,
                                    view_windows, furniture, ownership, home_maintenance,
                                    contract_number, project, bathroom, celling_heights,
                                    terms_of_sale, balcony, type_of_layout, year_of_build,
                                    type_of_finishing, floor_last, floor_no_last, floor_no_first,
                                    number_floors, floor, kitchen_area, living_area,
                                    total_area, title, description, location_coordinates,
                                    district, region, city,
                                    street, number_of_house, all_rooms_separated, separated_rooms,
                                    number_of_rooms, subregion, Session_user_data
                                    ):
        async with Session_user_data() as session:
            try:
                new_or_updated_data = FlatsSaleObjectsData(
                    url=url,
                    title=title,
                    description=description,
                    total_area = total_area,
                    living_area = living_area,
                    kitchen_area = kitchen_area,
                    floor =  floor,
                    number_of_floors = number_floors,
                    floor_no_first = floor_no_first,
                    floor_no_last = floor_no_last,
                    floor_last = floor_last,
                    number_of_rooms = number_of_rooms,
                    separated_rooms = separated_rooms,
                    all_rooms_separated = all_rooms_separated,
                    year_of_build = year_of_build,
                    type_of_layout = type_of_layout,
                    furniture = furniture,
                    balcony = balcony,
                    type_of_finishing = type_of_finishing,
                    home_maintenance = home_maintenance,
                    terms_of_sale = terms_of_sale,
                    celling_heights = celling_heights,
                    bathroom = bathroom,
                    project = project,
                    facilities_for_disabled_people = facilities_for_disabled_people,
                    view_windows = view_windows,
                    yard_improvement = yard_improvement,
                    ownership = ownership,
                    parking = parking,
                    contract_number = contract_number,
                    location_coordinates = location_coordinates,
                    district = district,
                    region = region,
                    location_city = city,
                    location_street = street,
                    house_number = number_of_house,
                    subregion = subregion
                    )
                await session.merge(new_or_updated_data)
                await session.commit()
            except Exception as e:
                # В случае ошибки откатываем изменения
                await session.rollback()
                print(f'Произошла ошибка: {e}')
            finally:
                await session.close()
                


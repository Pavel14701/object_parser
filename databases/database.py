import re
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, select, delete
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class FlatsSaleObjectsData(Base):
    __tablename__ = "FlatsObjectsData"
    url = Column(String(500), primary_key=True)  # Url каждого объекта
    id = Column(String(150)) # Сформированый id из ссылки
    price = Column(Integer, nullable=True) # Цена
    price_m2 = Column(Integer, nullable=True) # Цена за м2
    title = Column(Text, nullable=True) # Заголовок
    description = Column(Text, nullable=True) # Описание
    district = Column(String(100), nullable=True) # Область, где расположен объект
    region = Column(String(100), nullable=True) # Район, где расположен объект
    subregion = Column(String(100), nullable=True)
    location_city = Column(String(100), nullable=True)  # Город, где расположен объект
    location_street = Column(String(100), nullable=True)  # Адрес, где расположен объект
    house_number = Column(String(100), nullable=True)
    location_coordinates = Column(String(100), nullable=True)  # Координаты местоположения объекта
    number_of_floors = Column(Integer, nullable=True)  # Этажность
    floor = Column(Integer, nullable=True)  # Этаж
    floor_no_first = Column(Boolean, nullable=True)  # Тип этажа(не первый)
    floor_no_last = Column(Boolean, nullable=True)  # Тип этажа(не последний)
    floor_last = Column(Boolean, nullable=True) # Тип этажа(последний)
    home_maintenance = Column(String, nullable=True) # Обслуживающая организация
    year_of_build = Column(Integer, nullable=True)  # Год постройки
    type_of_layout = Column(String(100), nullable=True)  # Тип материала(Панель, Блок)
    type_of_finishing = Column(String(100), nullable=True) # Ремонт
    number_of_rooms = Column(String(100), nullable=True)  # Количество комнат
    separated_rooms = Column(String(100), nullable=True) # Количество раздельных комнат
    all_rooms_separated = Column(Boolean, nullable=True) # Все комнаты раздельные
    total_area = Column(Float, nullable=True)  # Общая площадь
    living_area = Column(Float, nullable=True)  # Жилая площадь
    kitchen_area = Column(Float, nullable=True)  # Площадь кухни
    celling_heights = Column(Float, nullable=True)  # Высота потолков
    bathroom = Column(String(100), nullable=True)  # Санузлы
    balcony = Column(String(100), nullable=True)  # Балконы
    furniture = Column(String(100), default=True)  # Мебель
    project = Column(String(100), nullable=True)  # Тип дома(Чешка, Сталинка, Своб. пл.)
    contract_number = Column(String(100), nullable=True)
    parking = Column(Boolean, nullable=True)  # Наличие парковки
    view_windows = Column(String(100), nullable=True) # Вид из окна
    yard_improvement = Column(String(100), nullable=True) # Удобства двора(список)
    facilities_for_disabled_people = Column(String, nullable=True) # Удобсбва для инвалидов
    terms_of_sale = Column(String(100), nullable=True)  # Условия сделки
    ownership = Column(String(100), nullable=True)  # Тип собственности
    pictures_urls = Column(String(100), nullable=True) # Ссылки на картинки




class Databases:
    @staticmethod
    async def save_urls_to_db(urls, Session_user_data):
        async with Session_user_data() as session:
            try:
                existing_urls = (await session.execute(
                    select(FlatsSaleObjectsData.url)
                )).scalars().all()
                urls_to_add = set(urls) - set(existing_urls)
                urls_to_remove = set(existing_urls) - set(urls)
                for url in urls_to_add:
                    new_entry = FlatsSaleObjectsData(url=url)
                    session.add(new_entry)
                for url in urls_to_remove:
                    await session.execute(
                        delete(FlatsSaleObjectsData).where(FlatsSaleObjectsData.url == url)
                    )
                await session.commit()
            except Exception as e:
                await session.rollback()
                print(f'Произошла ошибка: {e}')
            finally:
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
                                    number_of_rooms, subregion, price_int, price_int_m2, id, Session_user_data
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
                    subregion = subregion,
                    price = price_int,
                    price_m2 = price_int_m2,
                    id = id
                    )
                await session.merge(new_or_updated_data)
                await session.commit()
            except Exception as e:
                await session.rollback()
                print(f'Произошла ошибка: {e}')
            finally:
                await session.close()
                    
    @staticmethod
    async def insert_or_update_pictures(third_links, url, Session_user_data):
        pictures_urls_str = ','.join(third_links)
        async with Session_user_data() as session:
            try:
                new_or_updated_data = FlatsSaleObjectsData(
                    url=url,
                    pictures_urls = pictures_urls_str)
                await session.merge(new_or_updated_data)
                await session.commit()
            except Exception as e:
                await session.rollback()
                print(f'Произошла ошибка: {e}')
            finally:
                await session.close()

    @staticmethod
    async def get_all_urls(Session_user_data):
        # sourcery skip: inline-immediately-returned-variable
        async with Session_user_data() as session:
            try:
                result = await session.execute(select(FlatsSaleObjectsData.url))
                urls = result.scalars().all()
                return urls
            except Exception as e:
                print(f'Произошла ошибка: {e}')
            finally:
                await session.close()
                
                
    @staticmethod
    def save_urls_db(urls, Session):
        session = Session()
        try:
            existing_urls = session.query(FlatsSaleObjectsData.url).all()
            existing_urls = [url[0] for url in existing_urls]
            urls_to_add = set(urls) - set(existing_urls)
            urls_to_remove = set(existing_urls) - set(urls)
            for url in urls_to_add:
                new_entry = FlatsSaleObjectsData(url=url)
                session.add(new_entry)
            for url in urls_to_remove:
                session.query(FlatsSaleObjectsData).filter(FlatsSaleObjectsData.url == url).delete()
            session.commit()
        except Exception as e:
            session.rollback()
            print(f'Произошла ошибка: {e}')
        finally:
            session.close()
            


    @classmethod
    def get_data_by_url(cls, Session, url):
        # sourcery skip: class-method-first-arg-name, inline-immediately-returned-variable, use-named-expression
        try:
            with Session as session:
                # Query the database for the row with the given URL
                result = session.query(cls).filter_by(url=url).one_or_none()
            if not result:
                return None  # Row not found
            # Extract relevant columns and create a dictionary
            data_dict = {
                "id": result.id,
                "title": result.title,
                "price_m2": result.price_m2,
                "description": result.description,
                "price": result.price,
                "price_m2": result.price_m2,
                "district": result.district,
                "region": result.region,
                "subregion": result.subregion,
                "location_city": result.location_city,
                "location_street": result.location_street,
                "house_number": result.house_number,
                "location_coordinates": result.location_coordinates,
                "number_of_floors": result.number_of_floors,
                "floor": result.floor,
                "floor_no_first": result.floor_no_first,
                "floor_no_last": result.floor_no_last,
                "floor_last": result.floor_last,
                "all_rooms_separated": result.all_rooms_separated,
                "separated_rooms": result.separated_rooms,
                "number_of_rooms": result.number_of_rooms,
                "total_area": result.total_area,
                "living_area": result.living_area,
                "kitchen_area": result.kitchen_area,
                "celling_heights": result.celling_heights,
                "bathroom": result.bathroom,
                "balcony": result.balcony,
                "furniture": result.furniture,
                "project": result.project,
                "contract_number": result.contract_number,
                "terms_of_sale": result.terms_of_sale,
                "ownership": result.ownership
            }
            pictures_urls = result.pictures_urls
            return data_dict, pictures_urls
        except Exception as e:
            # Handle exceptions (e.g., database errors)
            print(f"Error retrieving data for URL {url}: {e}")
            return None

                


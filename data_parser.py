import re
import requests, aiohttp
from bs4 import BeautifulSoup
from database import Databases


class RealtParser:
    @staticmethod
    async def url_parser(session):
        links = set()
        pattern = re.compile(r'object/\d{7}')
        for i in range(1, 5):
            url = f"https://realt.by/belarus/sale/flats/?agencyUuids=01036310-5165-11ee-9a2f-abc708f86719&page={i}&seller=false"
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                divs = soup.find_all("div", class_="lg:overflow-x-auto flex-1 w-full p-1.5 sm:p-2.5 sm:py-0 md:px-4")
                for div in divs:
                    elements = div.find_all("a", href=pattern)
                    for element in elements:
                        href = element.get("href")
                        full_link = f"https://realt.by{href}"
                        links.add(full_link)
            print(f'operation {i} complete')
        list(links)
        print(len(links))
        return links


    @staticmethod
    async def get_object_pictures(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    soup = BeautifulSoup(await response.text(), "html.parser")
                    images = soup.find_all("img")
                    third_links = [image["src"] for image in images if image["src"].startswith("https://static.realt.by/user")]
                    third_links = third_links[::3]
                    print(third_links)
                    return third_links
                else:
                    print(f"Ошибка: не удалось получить данные с {url}")
                    return []


    async def get_object_data(url, Session_user_data):  # sourcery skip: merge-dict-assign, use-getitem-for-re-match-groups
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    type_of_finishing = year_of_build = type_of_layout = balcony = None
                    terms_of_sale = celling_heights = bathroom = project = furniture= None
                    contract_number = floor_last = floor_no_last = ownership = subregion = None
                    floor_no_first = floor = number_storeys = home_maintenance = None
                    number_of_house = number_floors = None
                    view_windows  = []
                    facilities_for_disabled_people = []
                    parking = []
                    yard_improvement = []
                    title = soup.find('title').get_text()
                    description_divs = soup.find_all('div', class_='description_wrapper__tlUQE')
                    for div in description_divs:
                        description = div.get_text(separator=' ', strip=True)
                    elements = soup.find_all(class_ = 'text-h3 font-raleway font-bold flex items-center')
                    elements_text = [element.get_text(strip=True) for element in elements]
                    if all(re.match(r'^\d+(\.\d+)?\sм²$', item) for item in elements_text[:3]):
                        total_area = elements_text[0]
                        living_area = elements_text[1]
                        kitchen_area = elements_text[2]
                        if match := re.search(r"(\d+)\D+(\d+)", elements_text[3]):
                            floor = match[1]
                            number_floors = match[2]
                        floor_no_first = floor != '1'
                        floor_no_last = floor != number_storeys
                        floor_last = floor == number_storeys
                    else:
                        total_area = elements_text[0]
                        living_area = elements_text[1]
                        kitchen_area =  None
                        if match := re.search(r"(\d+)\D+(\d+)", elements_text[2]):
                            floor = match[1]
                            number_floors = match[2]
                        floor_no_first = floor != '1'
                        floor_no_last = floor != number_storeys
                        floor_last = floor == number_storeys
                    ul_element = soup.find('ul', class_='w-full -my-1')
                    div_elements = ul_element.find_all('div', class_='w-1/2') if ul_element else []
                    elements = [div.get_text(separator=' ', strip=True) for div in div_elements]
                    number_of_rooms = elements[1]
                    if number_of_rooms == '1':
                        separated_rooms = '1'
                    else:
                        separated_rooms = elements[3]
                    all_rooms_separated = number_of_rooms == separated_rooms
                    types = {
                        'finishing': [
                            'Хороший', 'Нормальный', 'Плохое состояние',
                            'Без отделки', 'Строительная отделка', 'Удовлетворительный',
                            'Отличный', 'Евроремонт', 'Аварийное состояние'
                        ],
                        'layout': [
                            'Панельный', 'Кирпичный', 'Монолитный',
                            'Силикатные блоки', 'Каркасно-блочный',
                            'Блок-комнаты', 'Бревенчатый'
                        ],
                        'balcony': [
                            'Балкон', 'Нет', 'Лоджия',
                            'Балкон и лоджия', 'Терраса'
                        ],
                        'terms': [
                            'Чистая продажа', 'Обмен', 'Обмен - разъезд',
                            'Обмен - съезд', 'Подбираются варианты', 'Съезд'
                        ],
                        'celling_heights': [
                            '2.5 м', '2.6 м', '2.7 м', '2.8 м', '2.9 м', '3 м',
                            '3.1 м', '3.2 м', '3.3 м', '3.4 м' '3.5 м', '3.6 м',
                            '3.7 м', '3.8 м', '3.9 м',  '4 м'
                        ],
                        'bathrooms': ['Раздельный', 'Совмещенный', '2 и более'],
                        'project': [
                            'Чешский проект', 'Брежневка', 'Сталинка',
                            'Хрущевка', 'Малосемейка', 'Пентхаус',
                            'Таунхаус', 'Свободная планировка', 'Студия'
                        ],
                        'home_maintenance': ['ЖЭС', 'ТС'],
                        'view_windows': [
                            'Во двор', 'На улицу', 'Лес',
                            'Парк', 'Водоем'
                            ],
                        'facilities_for_disabled_people': [
                            'Нет', 'Широкий дверной проем',
                            'Грузовые лифты', 'Выделенные места на парковке',
                            'Пандусы/подъемник'
                            ],
                        'parking':[
                            'Подземный (встроенный)', 'Во дворе', 'Охраняемая',
                            'На крыше', 'Есть гараж', 'Открытая'
                            ],
                        'yard_improvement':[
                            'Двор без машин', 'Современные детские площадки',
                            'Закрытая террирория', 'Мусоропровод'
                        ],
                        'ownership': [
                            'Частная', 'Государственная',
                            'Долевое строительство', 'Жилищные облигации'
                        ],
                        'furniture': 'Есть'
                    }
                    for item in elements:
                        if not type_of_finishing and item in types['finishing']:
                            type_of_finishing = item
                        elif not year_of_build and re.fullmatch(r'\d{4}', item):
                            year_of_build = item
                        elif not type_of_layout and item in types['layout']:
                            type_of_layout = item
                        elif not balcony and item in types['balcony']:
                            balcony = item
                        elif not terms_of_sale and item in types['terms']:
                            terms_of_sale = item
                        elif not celling_heights and item in types['celling_heights']:
                            celling_heights = item
                        elif not bathroom and item in types['bathrooms']:
                            bathroom = item
                        elif not project and item in types['project']:
                            project = item
                        elif not contract_number and re.match(r'\d+/\d+\sот\s\d{2}\.\d{2}\.\d{4}', item):
                            contract_number = item
                        elif not home_maintenance and item in types['home_maintenance']:
                            home_maintenance = item
                        elif not ownership and item in types['ownership']:
                            ownership = item
                        elif not furniture and item in types['furniture']:
                            furniture = item
                        elif not view_windows and item in types['view_windows']:
                            try:
                                view_windows.append(item)
                            except Exception as e:
                                view_windows = None
                                print(e)
                        elif not facilities_for_disabled_people and item in types['facilities_for_disabled_people']:
                            facilities_for_disabled_people.append(item)
                        elif not parking and item in types['parking']:
                            parking.append(item)
                        elif not yard_improvement and item in types['yard_improvement']:
                            yard_improvement.append(item)
                        if not yard_improvement:
                            yard_improvement = None
                        if not facilities_for_disabled_people:
                            facilities_for_disabled_people = None
                        if not parking:
                            parking = None
                        if not view_windows:
                            view_windows = None
                    ul_element = soup.find('ul', class_='w-full mb-0.5 -my-1')
                    div_elements = ul_element.find_all('div', class_='w-1/2') if ul_element else []
                    elements = [div.get_text(separator=' ', strip=True) for div in div_elements]
                    for item in elements:
                        if re.compile(r'район', re.IGNORECASE).search(elements[3]):
                            if isinstance(item, str) and re.compile(r'\d+\.\d+,\s*\d+\.\d+').search(item):
                                    location_coordinates = item
                                    district = elements[1]
                                    region = elements[3]
                                    city = elements[5]
                                    street = elements[7]
                                    subregion = elements[11]
                            elif not number_of_house and re.compile(r'^\d').search(item):
                                    number_of_house = item
                        else:
                            if isinstance(item, str) and re.compile(r'\d+\.\d+,\s*\d+\.\d+').search(item):
                                    location_coordinates= item
                                    district = elements[1]
                                    region = elements[9]
                                    city = elements[3]
                                    street = elements[5]
                                    subregion = elements[11]
                            elif not number_of_house and re.compile(r'^\d').search(item):
                                    number_of_house = item
                    await Databases.insert_or_update_data_to_db(url, yard_improvement, parking, facilities_for_disabled_people,
                                                        view_windows, furniture, ownership, home_maintenance,
                                                        contract_number, project, bathroom, celling_heights,
                                                        terms_of_sale, balcony, type_of_layout, year_of_build,
                                                        type_of_finishing, floor_last, floor_no_last, floor_no_first,
                                                        number_floors, floor, kitchen_area, living_area,
                                                        total_area, title, description, location_coordinates,
                                                        district, region, city,
                                                        street, number_of_house, all_rooms_separated, separated_rooms,
                                                        number_of_rooms, subregion, Session_user_data)
                else:
                    print(f'Ошибка при запросе страницы: статус {response.status_code}')

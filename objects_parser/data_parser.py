import re, json
import requests, aiohttp
import paramiko
from bs4 import BeautifulSoup
from databases.database import Databases
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)


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
    async def get_object_pictures(url, Session_user_data):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    third_links = []
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    try:
                        images = soup.find_all("img")
                        third_links = [image["src"] for image in images if image["src"].startswith("https://static.realt.by/user")]
                        third_links = third_links[::3]
                        print(third_links)
                        if not third_links:  # Проверяем, пустой ли список
                            raise ValueError("Список изображений пуст.")
                    except ValueError as e:
                        slides = soup.find_all('div', class_='swiper-slide')
                        for slide in slides:
                            # В каждом слайде ищем <img>
                            img = slide.find('img')
                            if img and 'src' in img.attrs and img['src'].startswith('https://files.realt.by/img'):
                                third_links.append(img['src'])
                        print(third_links)
                    await Databases.insert_or_update_pictures(third_links, url, Session_user_data)
                    return third_links
                else:
                    print(f"Ошибка: не удалось получить данные с {url}")
                    return []


    async def get_object_data(url, Session_user_data):  # sourcery skip: merge-dict-assign, use-getitem-for-re-match-groups
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    try:
                        #Create custom id
                        id = re.search(r'(\d+)/?$', url)
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
                        #Title
                        title = soup.find('title').get_text()
                        span = soup.find('span', class_='text-subhead sm:text-body text-basic inline-block')
                        #Price
                        price_str = span.get_text(separator=' ', strip=True)
                        numbers = re.findall(r'\d+', price_str)
                        price_int = int(''.join(numbers))
                        span = soup.find('span', class_="inline-block text-subhead sm:text-body text-basic")
                        price_str = span.get_text(separator=' ', strip=True)
                        #Atribut
                        numbers = re.findall(r'\d+', price_str)
                        price_int_m2 = int(''.join(numbers))
                        description_divs = soup.find_all('div', class_='description_wrapper__tlUQE')
                        #Description
                        for div in description_divs:
                            description = div.get_text(separator=' ', strip=True)
                        elements = soup.find_all(class_ = 'text-h3 font-raleway font-bold flex items-center')
                        elements_text = [element.get_text(strip=True) for element in elements]
                        #Atributes
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
                        #Atributes
                        number_of_rooms = elements[1]
                        if number_of_rooms == '1':
                            separated_rooms = '1'
                        else:
                            separated_rooms = elements[3]
                        all_rooms_separated = number_of_rooms == separated_rooms
                        #Data dict for atributes search
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
                                'Нет', 'Лоджия',
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
                                'Таунхаус', 'Свободная планировка', 'Студия',
                                'Улучшенный проект', 'Стандартный проект'
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
                            # Atribut
                            if not type_of_finishing and item in types['finishing']:
                                if item == "Хороший":
                                    type_of_finishing = "good"
                                elif item == "Нормальный":
                                    type_of_finishing = "normal"
                                elif item == "Плохое состояние":
                                    type_of_finishing = "bad_condition"
                                elif item == "Без отделки":
                                    type_of_finishing = "no_finishing"
                                elif item == "Строительная отделка":
                                    type_of_finishing = "construction_finishing"
                                elif item == "Удовлетворительный":
                                    type_of_finishing = "satisfactory"
                                elif item == "Отличный":
                                    type_of_finishing = "perfect"
                                elif item == "Евроремонт":
                                    type_of_finishing = "eurorepair"
                                elif item == "Аварийное состояние":
                                    type_of_finishing = "emergency_condition"
                            #Atribut
                            elif not year_of_build and re.fullmatch(r'\d{4}', item):
                                year_of_build = item
                            #Atribut    
                            elif not type_of_layout and item in types['layout']:
                                if item == "Панельный":
                                    type_of_layout = "panel"
                                elif item == "Кирпичный":
                                    type_of_layout = "brick"
                                elif item == "Монолитный":
                                    type_of_layout = "monolith"
                                elif item == "Силикатные блоки":
                                    type_of_layout = "silicat_blocks"
                                elif item == "Каркасно-блочный":
                                    type_of_layout = "frame-block"
                                elif item == "Блок-комнаты":
                                    type_of_layout = "block_rooms"
                                elif item == "Бревенчатый":
                                    type_of_layout = "wood"
                            #Atribut        
                            elif not balcony and item in types['balcony']:
                                if item == 'Балкон':
                                    count_balcony += 1
                                    if count_balcony == 2:
                                        balcony = 'balcon'
                                elif item == "Лоджия":
                                    balcony = "lodjia"
                                elif item == "Балкон и лоджия":
                                    balcony = "balcon_lodjia"
                                elif item == "Терраса":
                                    balcony = "terace"
                                elif item == "Нет":
                                    balcony = "none_balcony"
                            #Tag        
                            elif not terms_of_sale and item in types['terms']:
                                terms_of_sale = item
                            #Atribut
                            elif not celling_heights and item in types['celling_heights']:
                                celling_heights = float(item.replace(" м", ""))
                            #Atribut
                            elif not bathroom and item in types['bathrooms']:
                                if item == "Раздельный":
                                    bathroom = "separated"
                                elif item == "Совмещенный":
                                    bathroom = "combined"
                                if item == "2 и более":
                                    bathroom = "2bath"
                            #Atribut        
                            elif not project and item in types['project']:
                                if item == "Стандартный проект":
                                    project = "standart_project"
                                elif item == "Улучшенный проект":
                                    project = "upgrade_project"
                                elif item == "Хрущевка":
                                    project = "chruzh"
                                elif item == "Чешский проект":
                                    project = "czech_project"
                                elif item == "Брежневка":
                                    project = "brezh"
                                elif item == "Малосемейка":
                                    project = "little_family"
                                elif item == "Пентхаус":
                                    project = "penthouse"
                                elif item == "Сталинка":
                                    project = "stalin"
                                elif item == "Студия":
                                    project = "studio"
                                elif item == "Свободная планировка":
                                    project = "open_plan"
                                elif item == "Таунхаус":
                                    project = "townhouse"
                            #Tag        
                            elif not contract_number and re.match(r'\d+/\d+\sот\s\d{2}\.\d{2}\.\d{4}', item):
                                contract_number = item
                            #Tag    
                            elif item in types['home_maintenance']:
                                home_maintenance = item
                            #Tag    
                            elif not ownership and item in types['ownership']:
                                ownership = item
                            #Atribut    
                            elif not furniture and item in types['furniture']:
                                furniture = item
                            #Tag    
                            elif item in types['view_windows']:
                                try:
                                    view_windows.append(item)
                                except Exception as e:
                                    view_windows = None
                                    print(e)
                            #Tag
                            elif not facilities_for_disabled_people and item in types['facilities_for_disabled_people']:
                                facilities_for_disabled_people.append(item)
                            #Tag
                            elif item in types['parking']:
                                parking.append(item)
                            #Tag  
                            elif item in types['yard_improvement']:
                                yard_improvement.append(item)
                            # If not params in dict
                            if not yard_improvement:
                                yard_improvement = None
                            if not facilities_for_disabled_people:
                                facilities_for_disabled_people = None
                            if not parking:
                                parking = None
                            if not view_windows:
                                view_windows = None
                        #Find adress data
                        ul_element = soup.find('ul', class_='w-full mb-0.5 -my-1')
                        div_elements = ul_element.find_all('div', class_='w-1/2') if ul_element else []
                        elements = [div.get_text(separator=' ', strip=True) for div in div_elements]
                        for item in elements:
                            if re.compile(r'район', re.IGNORECASE).search(elements[3]):
                                if isinstance(item, str) and re.compile(r'\d+\.\d+,\s*\d+\.\d+').search(item):
                                    #Tags
                                    location_coordinates = item
                                    location_coordinates = location_coordinates.replace(',', '')
                                    district = elements[1]
                                    region = elements[3]
                                    city = elements[5]
                                    street = elements[7]
                                    subregion = elements[11]
                                elif not number_of_house and re.compile(r'^\d').search(item):
                                    number_of_house = item
                            else:
                                if isinstance(item, str) and re.compile(r'\d+\.\d+,\s*\d+\.\d+').search(item):
                                    #Tags
                                    location_coordinates= item
                                    district = elements[1]
                                    region = elements[9]
                                    city = elements[3]
                                    street = elements[5]
                                    subregion = elements[11]
                                elif not number_of_house and re.compile(r'^\d').search(item):
                                    #Tag
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
                                                            number_of_rooms, subregion, price_int, price_int_m2, id, Session_user_data)
                    except:
                        print(url)
                else:
                    print(f'Ошибка при запросе страницы: статус {response.status_code}')
                    
    @staticmethod                
    def url_parser():
        try:
            urls_set = set()
            for i in range(1, 4):
                driver.get(f"https://realt.by/belarus/sale/flats/?agencyUuids=01036310-5165-11ee-9a2f-abc708f86719&page={i}&seller=false")
                container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.lg\\:overflow-x-auto.flex-1.w-full.p-1\\.5.sm\\:p-2\\.5.sm\\:py-0.md\\:px-4')))
                links = container.find_elements(By.TAG_NAME, 'a')
                for link in links:
                    href = link.get_attribute('href')
                    if re.compile(r'/sale-flats/object/\d{7}/$').search(href):
                        urls_set.add(str(href.split('?')[0]))
            urls = list(urls_set)
        finally:
            driver.quit()
            return urls
        
    @staticmethod        
    def send_ssh_json(hostname, port, username, password, urls):
        # Преобразование списка в JSON
        list_as_json = json.dumps(urls)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            # Подключение к серверу
            client.connect(hostname, port=port, username=username, password=password)
            
            # Отправка списка в формате JSON и сохранение в файле на сервере
            stdin, stdout, stderr = client.exec_command(f"echo '{list_as_json}' | tee objects_parser/list.json")
            for line in stdout:
                print(line, end='')
            # Активация venv и запуск Python скрипта
            command = 'source /home/domitoch/virtualenv/objects_parser/3.12/bin/activate && cd /home/domitoch/objects_parser && python find_urls.py'
            stdin, stdout, stderr = client.exec_command(command)
            for line in stdout:
                print(line, end='')
            # Печать ошибок из stderr
            for line in stderr:
                print(line, end='')
        except Exception as e:
            print(e)
        finally:
            # Закрытие соединения
            client.close()
import re
import requests
from bs4 import BeautifulSoup

@staticmethod
def get_object_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        print(soup)
        title = soup.find('title').get_text()
        print(title)
        elements = soup.find_all(class_ = 'focus:outline-none transition-colors cursor-pointer text-info-500 hover:text-info-600 active:text-info')
        elements_text = [element.get_text(strip=True) for element in elements]
        region = elements_text[0]
        city = elements_text[1]
        city = re.sub(r'\xa0', ' ', city)
        street = elements_text[2]
        district = elements_text[3]
        print(f'{region}, {city}, {street}, {district}')
        elements = soup.find_all(class_ = 'text-h3 font-raleway font-bold flex items-center')
        elements_text = [element.get_text(strip=True) for element in elements]
        total_area = elements_text[0]
        living_area = elements_text[1]
        kitchen_area = elements_text[2]
        if match := re.search(r"(\d+)\D+(\d+)", elements_text[3]):
            floor = match.group(1)
            number_storeys = match.group(2)
        print(total_area, living_area, kitchen_area, floor, number_storeys)
        description_divs = soup.find_all('div', class_='description_wrapper__tlUQE')
        for div in description_divs:
            description = div.get_text(separator=' ', strip=True)
            print(description)
        ul_element = soup.find('ul', class_='w-full -my-1')
        div_elements = ul_element.find_all('div', class_='w-1/2') if ul_element else []
        elements = []
        for div in div_elements:
            elements_text = (div.get_text(separator=' ', strip=True))
            elements.append(elements_text)
        number_of_rooms = elements[1]
        separated_rooms = elements[3]
        all_rooms_separated = number_of_rooms == separated_rooms
        year_of_build = elements[11]
        type_of_house = elements[15]
        type_of_layout = elements[17]
        balcony = elements[19]
        type_of_finishing = elements[21]
        ceiling_height = elements[23]
        bathroom = elements[25]
        own_type = elements[27]
        terms_of_sale = elements[29]
        contract_number = elements[31]
        print(
                all_rooms_separated, separated_rooms, number_of_rooms,
                year_of_build, type_of_house, type_of_layout,
                balcony, type_of_finishing, ceiling_height,
                bathroom, own_type, terms_of_sale, contract_number
        )
        ul_element = soup.find('ul', class_='w-full mb-0.5 -my-1')
        div_elements = ul_element.find_all('div', class_='w-1/2') if ul_element else []
        elements = []
        for div in div_elements:
            elements_text = (div.get_text(separator=' ', strip=True))
            elements.append(elements_text)
        print(elements)


    else:
        print(f'Ошибка при запросе страницы: статус {response.status_code}')
        

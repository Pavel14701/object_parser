import re
import requests, aiohttp
from bs4 import BeautifulSoup


class RealtParser:
    @staticmethod
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
                    href = f"https://realt.by{href}"
                    links.append(href)
            print(f'operation {i} complete')
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


    @staticmethod
    async def get_object_data(url):  # sourcery skip: merge-dict-assign, use-getitem-for-re-match-groups
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    data = {}
                    data['title'] = soup.find('title').get_text()
                    elements = soup.find_all(class_='focus:outline-none transition-colors cursor-pointer text-info-500 hover:text-info-600 active:text-info')
                    data['address'] = {
                        'region': elements[0].get_text(strip=True),
                        'city': re.sub(r'\xa0', ' ', elements[1].get_text(strip=True)),
                        'street': elements[2].get_text(strip=True),
                        'district': elements[3].get_text(strip=True)
                    }
                    elements = soup.find_all(class_='text-h3 font-raleway font-bold flex items-center')
                    data['area'] = {
                        'total_area': elements[0].get_text(strip=True),
                        'living_area': elements[1].get_text(strip=True),
                        'kitchen_area': elements[2].get_text(strip=True)
                    }
                    if match := re.search(r"(\d+)\D+(\d+)", elements[3].get_text(strip=True)):
                        data['building'] = {
                            'floor': match.group(1),
                            'number_storeys': match.group(2)
                        }
                    description_divs = soup.find_all('div', class_='description_wrapper__tlUQE')
                    data['description'] = [div.get_text(separator=' ', strip=True) for div in description_divs]
                    ul_element = soup.find('ul', class_='w-full -my-1')
                    div_elements = ul_element.find_all('div', class_='w-1/2') if ul_element else []
                    elements = [div.get_text(separator=' ', strip=True) for div in div_elements]
                    data['details'] = {
                        'number_of_rooms': elements[1],
                        'separated_rooms': elements[3],
                        'all_rooms_separated': elements[1] == elements[3],
                        'year_of_build': elements[11],
                        'type_of_house': elements[15],
                        'type_of_layout': elements[17],
                        'balcony': elements[19],
                        'type_of_finishing': elements[21],
                        'ceiling_height': elements[23],
                        'bathroom': elements[25],
                        'own_type': elements[27],
                        'terms_of_sale': elements[29],
                        'contract_number': elements[31]
                    }
                    return data
                else:
                    print(f'Ошибка при запросе страницы: статус {response.status}')
                    return {}

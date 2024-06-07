import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re

async def get_object_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                data = {}
                data['url'] = url
                print(data['url'])
                data['title'] = soup.find('title').get_text()
                print(data['title'])
                elements = soup.find_all(class_='focus:outline-none transition-colors cursor-pointer text-info-500 hover:text-info-600 active:text-info')
                data['address'] = {
                    'region': elements[0].get_text(strip=True),
                    'city': re.sub(r'\xa0', ' ', elements[1].get_text(strip=True)),
                    'street': elements[2].get_text(strip=True),
                    'district': elements[3].get_text(strip=True)
                }
                print(data['address'])
                #data['location_coordinates']
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
                ul2_element = soup.find('ul', class_='w-full mb-0.5 -my-1')
                div2_elements = ul2_element.find_all('div', class_='w-1/2') if ul2_element else []
                elements2 = [div.get_text(separator=' ', strip=True) for div in div2_elements]
                data['location_coordinates'] = elements2[13]
                print(elements2)
                print(data['location_coordinates'])
                """
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
            print(data['details'])
            """
          
async def main():
    async with aiohttp.ClientSession() as session:
        await get_object_data(url='https://realt.by/sale-flats/object/3343360/')
if __name__ == '__main__':
    asyncio.run(main())

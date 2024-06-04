
# Импортируем библиотеки
import requests
from bs4 import BeautifulSoup

url = "https://realt.by/sale-flats/object/1633695/"

class RealtParser:
    @staticmethod
    def object_pictures_parser(url):
        response = requests.get (url)
        if response.status_code == 200:
            soup = BeautifulSoup (response.text, "html.parser")
            images = soup.find_all ("img")
            third_links = []
            for image in images:
                src = image["src"]
                if src.startswith("https://static.realt.by/user"):
                    third_links.append(src)
            third_links = third_links[::3]
            print(third_links)
        else:
            print (f"Ошибка: не удалось получить данные с {url}")
            
RealtParser.object_data_parser(url)
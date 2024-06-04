# Импортируем библиотеки
import requests
from bs4 import BeautifulSoup


class RealtParser:
    @staticmethod
    def objects_url_parser(url):
        url = "https://realt.by/belarus/sale/flats/?agencyUuids=01036310-5165-11ee-9a2f-abc708f86719&page=1&seller=false"
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        elements = soup.find_all("a", attrs={"aria-label": lambda x: x and x.startswith("Ссылка на объект №")})
        links = []
        for element in elements:
            href = element.get("href")
            href = f"https://realt.by{href}"
            links.append(href)


    @staticmethod
    def object_data_parser(url):
        url = "https://realt.by/sale-flats/object/3321063/"
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




        # Заголовок
        # Импортируем необходимые библиотеки
        import requests
        from bs4 import BeautifulSoup

        # Задаем URL-адрес веб-сайта, который хотим парсить
        url ="https://realt.by/sale-flats/object/3321063/"

        # Отправляем запрос на веб-сайт и получаем ответ
        response = requests.get(url)

        # Проверяем статус ответа (200 означает успешный запрос)
        if response.status_code == 200:
            # Используем BeautifulSoup для разбора HTML-кода
            soup = BeautifulSoup(response.text, "html.parser")

            # Находим все элементы с тегом <li> и классом "md:w-auto md:inline w-full align-top" на веб-странице
            list_items = soup.find_all("li", class_="md:w-auto md:inline w-full align-top")

            # Создаем пустой список для хранения текста элементов
            text_list = []

            # Добавляем текст каждого элемента в список
            for li in list_items:
                text_list.append(li.text)

            # Выводим значения из списка через пробел
            print(" ".join(text_list))
        else:
            # Выводим сообщение об ошибке, если запрос не удался
            print(f"Ошибка: не удалось получить данные с {url}")


        # Площади
        # Импортируем необходимые библиотеки
        import requests
        from bs4 import BeautifulSoup
        # Задаем URL-адрес веб-сайта, который хотим парсить
        url ="https://realt.by/sale-flats/object/3321063/"

        # Отправляем запрос на веб-сайт и получаем ответ
        response = requests.get(url)

        # Проверяем статус ответа (200 означает успешный запрос)
        if response.status_code == 200:
            # Используем BeautifulSoup для разбора HTML-кода
            soup = BeautifulSoup(response.text, "html.parser")

            # Находим все элементы с тегом <div> и классом "last:mr-0 pt-6 mr-10" на веб-странице
            div_items = soup.find_all("div", class_="last:mr-0 pt-6 mr-10")

            # Создаем пустой список для хранения текста элементов
            text_list = []

            # Добавляем текст каждого элемента в список
            for div in div_items:
                text_list.append(div.text)

            # Выводим в консоль текст из списка, разделяя элементы пробелом
            print(" ".join(text_list))
        else:
            # Выводим сообщение об ошибке, если запрос не удался
            print(f"Ошибка: не удалось получить данные с {url}")
            
            
            
            
            

        # Описание
        # Текст
        # Импортируем необходимые библиотеки
        import requests
        from bs4 import BeautifulSoup

        # Задаем URL-адрес веб-сайта, который хотим парсить
        url ="https://realt.by/sale-flats/object/3321063/"

        # Отправляем запрос на веб-сайт и получаем ответ
        response = requests.get(url)

        # Проверяем статус ответа (200 означает успешный запрос)
        if response.status_code == 200:
            # Используем BeautifulSoup для разбора HTML-кода
            soup = BeautifulSoup(response.text, "html.parser")

            # Находим элемент с тегом <section> и классом "bg-white flex flex-wrap md:p-6 my-4 rounded-md" на веб-странице
            section_item = soup.find("section", class_="bg-white flex flex-wrap md:p-6 my-4 rounded-md")

            # Проверяем, что элемент существует
            if section_item is not None:
                # Получаем текст из элемента, используя метод .get_text()
                text = section_item.get_text()

                # Выводим в консоль текст из элемента
                print(text)
            else:
                # Выводим сообщение, если элемент не найден
                print("Элемент с тегом <section> и классом 'bg-white flex flex-wrap md:p-6 my-4 rounded-md' не найден на веб-странице")
        else:
            # Выводим сообщение об ошибке, если запрос не удался
            print(f"Ошибка: не удалось получить данные с {url}")

        # Импортируем модуль re
        import re

        # Задаем регулярное выражение для поиска ссылок
        # Оно ищет любую последовательность символов, начинающуюся с http:// или https://
        # и заканчивающуюся символом, который не является буквой, цифрой или знаком подчеркивания (\W)
        # или концом строки ($)
        link_pattern = r"https?://\S+\W?"

        # Задаем регулярное выражение для поиска фразы показать больше
        # Оно ищет точное совпадение с этой фразой, не зависимо от регистра
        show_more_pattern = r"показать больше"

        # Оборачиваем код в блок try except, чтобы обработать возможные исключения
        try:
            # Заменяем найденные ссылки на пустую строку
            # Функция re.sub принимает три аргумента: шаблон, замена и строка
            text = re.sub(link_pattern, "", text)

            # Заменяем найденную фразу показать больше на пустую строку
            text = re.sub(show_more_pattern, "", text, flags=re.IGNORECASE)

            # Выводим обновленный текст
            print(text)
        except Exception as e:
            # Выводим сообщение об ошибке, если что-то пошло не так
            print(f"Ошибка: {e}")

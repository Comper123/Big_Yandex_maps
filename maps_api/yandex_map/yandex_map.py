import requests
import os
from PIL import Image
from random import uniform
from math import radians, cos

# Мой апи ключ geocoder'a
api_key = '42838384-31ec-40af-b8a9-354fb89aa371'

# Лицейский апи ключ geocoder'a
# api_key = '40d1649f-0493-4b70-98ba-98533de7710b'

# Дополнительный апи ключ geocoder'a
# api_key = 'ea7ddb7a-83f0-4e59-84d9-e3ee28a40303'

# Мой api ключ для поиска организаций
# business_api ='1c4198a5-89b5-4f5e-8d5a-6e8dd37b960c'

# Лицейский апи ключ для поиска организаций
business_api = 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3'


def get_coordinates(place: str, format: str="json"):
    """
    Функция возвращает координаты обьекта на карте по его названию
    """
    link = f'http://geocode-maps.yandex.ru/1.x/?apikey={api_key}&geocode={place}&format={format}'
    response = requests.get(link)
    if response:
        data = response.json()
        object = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        coords = object["Point"]["pos"]
        return list(map(float, coords.split()))


def get_territory(place: str):
    """
    Функция для получения территории искомого обьекта
    """
    link = f'http://geocode-maps.yandex.ru/1.x/?apikey={api_key}&geocode={place}&format=json'
    response = requests.get(link)
    print(link)
    if response:
        data = response.json()
        object = data["response"]["GeoObjectCollection"]["featureMember"][0]
        coords = object["GeoObject"]["boundedBy"]["Envelope"]
        result = [list(map(float, coords["lowerCorner"].split())), list(map(float, coords["upperCorner"].split()))]
        return result


def get_map(center: tuple[int], spn: tuple=False, size: tuple[int]=[600, 450], way: tuple[int]=False, 
            map_format: str="map", pt: str=None, z: int=False):
    """
    Функция для создания изображения карты по переданным аргументам

    Параметр map_format может принимать следующие значения:
        map - карта схема местности
        sat - снимок спутника
        trf - карта автодорог
        skl - географические объекты
    """
    # Преобразуем параметры для удобства пользования
    x, y = map(str, center)
    width, height = map(str, size)
    

    map_link = f"https://static-maps.yandex.ru/1.x/?l={map_format}&ll={x},{y}&size={width},{height}"
    # Если передан дополнительный маршрут
    if way:
        map_link += f"&pl={','.join(list(map(str, way)))}"
    if pt is not None:
        map_link += f"&pt={pt}"
    if z:
        map_link += f"&z={str(z)}" 
    if spn:
        x_span, y_span = spn
        map_link += f"&spn={x_span},{y_span}"
    # print(map_link)
    content = requests.get(map_link).content
    map_file = f"{x}-{y}.png"
    with open(map_file, 'wb') as map_1:
        map_1.write(content)
    return map_file 


def del_map(map: str):
    """
    Функция удаления изображения файла из файловой системы
    """
    os.remove(map)


def show_map(map: str):
    """
    Функция для просмотра получившейся карты
    """
    with Image.open(map) as img:
        img.show()


def random_spn(start: float, stop: float):
    """
    Функция генерирует случайный коэфициент масштабирования карты 
    исходя из заданных пределов
    """
    test = uniform(start, stop)
    return [str(test), str(test)]


def get_adres(coord: tuple[float]):
    """
    Получение адреса по координатам
    """
    x, y = list(map(str, coord))
    link = f"http://geocode-maps.yandex.ru/1.x/?apikey={api_key}&geocode={x},{y}&kind=house&format=json"
    response = requests.get(link)
    if response:
        data = response.json()
        object = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        adres = object["metaDataProperty"]["GeocoderMetaData"]["text"]
        mail = object["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
        return adres, mail


def get_place(coord: tuple[int], type_place: str="house"):
    """
    Функция распознавания района по переданным координатам
    Исходя из параметра type_place можно получить следующие данные:
        house — дом;
        street — улица;
        metro — станция метро;
        district — район города;
        locality — населенный пункт (город/поселок/деревня/село)
    """
    x, y = list(map(str, coord))
    link = f"http://geocode-maps.yandex.ru/1.x/?apikey={api_key}&geocode={x},{y}&kind={type_place}&format=json"
    response = requests.get(link)
    if response:
        data = response.json()
        object = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        dist = object["metaDataProperty"]["GeocoderMetaData"]["text"]
        return dist
    

def search_business(text: str, coord: list[float]=False, count: int=10, 
                    info: bool=False, get_object: bool=False, spn=False):
    """
    Функция нахождения объектов инфраструктуры города
    Параметр type_business принимает тип искомого объкта,
    будь это банк или аптека
    """
    search_api_server = "https://search-maps.yandex.ru/v1/"
    search_params = {
        "apikey": business_api,
        "text": text,
        "lang": "ru_RU",
        "type": "biz",
        "results": str(count)
    }
    if coord:
        search_params["ll"] = ",".join(list(map(str, coord)))
    if spn:
        search_params["spn"] = ",".join(list(map(str, spn)))
    response = requests.get(search_api_server, params=search_params)
    if response:
        list_points = []
        data = response.json()
        if info:
            return data
        businesses = []
        for index, business in enumerate(data["features"]):
            coords = (float(business["geometry"]["coordinates"][0]), float(business["geometry"]["coordinates"][1]))
            name = business["properties"]["name"]
            adres = business["properties"]["description"]
            active = business["properties"]["CompanyMetaData"]["Hours"]["text"]
            b = Business(coords, name, adres, active)
            businesses.append(b)
            point = f'{business["geometry"]["coordinates"][0]},{business["geometry"]["coordinates"][1]},pm2'
            try:
                time_work = business["properties"]["CompanyMetaData"]["Hours"]["text"]
                if 'круглосуточно' in time_work:
                    point += "gnm"
                else:
                    point += "blm"
            except Exception:
                point += "grm"
            list_points.append(point)
        if get_object:
            return businesses
        return f"pt={'~'.join(list_points)}"
    

def get_territory_business(place: str, type: str):
    """
    Функция возвращает координаты левого верхнего и правого нижнего угла
    искомой территории
    """
    data = search_business(get_coordinates(place), type_business=type, count=1, info=True)
    coords = data["properties"]["ResponseMetaData"]["SearchResponse"]["boundedBy"]
    return coords


def generate_spn(coords: list[list[int]]):
    """
    Функция определяющее значение spn исходя из макчимального размера объкта
    """
    x_span = str(abs(coords[0][0] - coords[1][0]) / 2.0)
    y_span = str((abs(coords[0][1] * cos(radians(coords[0][1])) - coords[1][1] * cos(radians(coords[1][1]))) ) / 2.0)
    return x_span, y_span


class Business:
    """Класс безнес-объекта"""
    def __init__(self, coords: tuple[float], name: str, adres: str, active: str):
        self.coords = coords
        self.name = name
        self.adres = adres
        self.active = active

    def get_coords(self):
        """Метод получения координат обьекта"""
        return self.coords
    
    def get_adres(self):
        """Метод получения адреса обьекта"""
        return self.adres
    
    def get_name(self):
        """Метод получения названия обьекта"""
        return self.name
    
    def get_active(self):
        """Метод получения времени работы обьекта"""
        return self.active

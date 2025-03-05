import requests
from bs4 import BeautifulSoup
import json

compel_url = 'https://www.compel.ru/catalog/ic/analog/opamp'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}


def get_info():
    """Пролистываем все страницы"""
    products = []
    page_counter = 1

    # очень долго работает (страниц всего больше тысячи), можно оставить while page_counter < 10 если надо проверить
    while True:
        params = {'page_counter': page_counter}
        response = requests.get(compel_url, headers=headers, params=params)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # табличку ищем в классе psearch-data items
        table = soup.find('table', {'class': 'psearch-data items'})
        if not table:
            print('таблица приняла ислам')
            break

        rows = table.find_all('tr')

        for row in rows:
            if not row.find('td'):
                continue

            product = {}
            code_element = row.find('a', {'class': 'item-link'})
            if not code_element:
                continue

            part_number = code_element.text.strip()
            product['part_number'] = part_number

            features = {}
            cells = row.find_all('td')
            if len(cells) < 10:
                continue

            # у всех товаров в характеристиках такие пункты
            # "cells[2].text.strip()" бесполезен, там картинки...

            features['package'] = cells[2].text.strip()
            features['type'] = cells[3].text.strip()
            features['channels'] = cells[4].text.strip()
            features['voltage'] = cells[5].text.strip()
            features['current'] = cells[6].text.strip()
            features['rail_to_rail'] = cells[7].text.strip()
            features['programmable_gain'] = cells[8].text.strip()
            features['gbw'] = cells[9].text.strip()

            product['features'] = features
            products.append(product)

        btn = soup.find('div', {'class': 'j-more-data'})
        if not btn:
            print('Прошли все страницы')
            break

        page_counter += 1

    return products


products = get_info()

json_data = json.dumps(products, ensure_ascii=False, indent=4)
# print(json_data)

with open('products.json', 'w', encoding='utf-8') as f:
    f.write(json_data)

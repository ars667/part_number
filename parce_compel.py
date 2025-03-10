import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json

compel_url = 'https://www.compel.ru'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}


def get_categories():
    """Ищем на странице категории"""
    categories = []

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(compel_url + '/catalog')
    time.sleep(5)

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, 'html.parser')

    # Дерево категорий внутри <nav class="bigTree">

    nav = soup.find('nav', {'class': 'bigTree'})
    if not nav:
        print("Категории приняли ислам")
        return categories

    # Ссылки на категории внутри дерева
    category_links = nav.find_all('a', href=True)

    for link in category_links:
        href = link['href']
        if '/cat/' in href:
            full_url = compel_url + href
            if full_url not in categories: 
                categories.append(full_url)

    # print(f"Нашлось категорий: {len(categories)}")
    return categories


def get_info(url, output_file):
    """Пролистываем страницы в категории и записываем"""
    page_counter = 1

    # Выполняется ОЧЕНЬ ОЧЕНЬ ОЧЕНЬ долго
    while True:
        params = {'page_counter': page_counter}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        table = soup.find('table', {'class': 'psearch-data items'})
        if not table:
            print(f'Таблица не найдена на странице {url}')
            break

        rows = table.find_all('tr')
        print(f"Найдено строк в таблице: {len(rows)}")

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

            features['package'] = cells[2].text.strip()
            features['type'] = cells[3].text.strip()
            features['channels'] = cells[4].text.strip()
            features['voltage'] = cells[5].text.strip()
            features['current'] = cells[6].text.strip()
            features['rail_to_rail'] = cells[7].text.strip()
            features['programmable_gain'] = cells[8].text.strip()
            features['gbw'] = cells[9].text.strip()

            product['features'] = features

            with open(output_file, 'a', encoding='utf-8') as f:
                json.dump(product, f, ensure_ascii=False, indent=4)
                f.write(',\n')
                f.flush()

            # print(f"Записано: {part_number}")

        btn = soup.find('div', {'class': 'j-more-data'})
        if not btn:
            print(f'Закончились страницы в категории {url}')
            break

        page_counter += 1


def run():
    categories = get_categories()
    # print("Список категорий:")
    # print(categories)

    output_file = 'all_products.json'

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('[\n')

    for category_url in categories:
        # print(f'Категория на очереди: {category_url}')
        get_info(category_url, output_file)

    with open(output_file, 'a', encoding='utf-8') as f:
        f.write('\n]')


run()

import requests
from bs4 import BeautifulSoup
import time
import random
import json
from urllib.parse import urljoin

BASE_URL = "https://www.chipfind.ru"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
}

CATALOG_URL ="https://www.chipfind.ru/catalog/"

def get_categories(catalog_url):
    response = requests.get(catalog_url)
    soup = BeautifulSoup(response.text, "html.parser")

    categories = []

    for category in soup.find_all("h3"):
        parent_div = category.find_next("div")
        for li in parent_div.find_all("li"):
            category = urljoin(catalog_url, li.find("a")["href"])
            categories.append(category)
    return categories

cat_links = get_categories(CATALOG_URL)

#for link in cat_links:
#    print(link)

def get_products(subcategory_url):
    products = []
    page = 1
    start_subcategory_url = subcategory_url

    while True:
        if page > 1:
            url = f"{subcategory_url}{page}.htm?"
        else:
            url = subcategory_url
        print(f"Страничка {url}\n")

        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            print("Ошибка")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.select("table tr")
        rows = rows[1:] # на каждой странице первая строка - хуйня, здесь обрезано, но все равно не работает

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 4:
                continue
            name_tag = cols[1].find("a")
            if not name_tag or not name_tag.text.strip():
                continue

            name = name_tag.text.strip()
            fabrica = cols[2].text.strip()
            first_line = cols[3].text.split("<div>")[0].strip() # первая строка из характеристик, что это вообще

            specs_div  = cols[3].find("div")
            if specs_div :
                specs = specs_div.get_text(separator=" ").replace("\xa0", " ").strip() # должен убирать \xa0 из json, но не работает(
                full_specs = f"{first_line} {specs}" # без пробела записывается хз почему
            else: full_specs = "Нет характеристик"

            products.append({
                "Название": name,
                "Производитель": fabrica,
                "Характеристики": full_specs
            })

        pagination = soup.find("div", class_="pages")
        if pagination:
            next_page_tag = pagination.find("a", text="следующая")
        else: next_page_tag = None

        if not next_page_tag:
            break

        next_page_url = next_page_tag["href"]
        subcategory_url = start_subcategory_url + next_page_url
        time.sleep(random.uniform(1, 2))

    return products

for subcategory_url in cat_links:
    products = get_products(subcategory_url)

#print("Всего:", len(products))

#for idx, p in enumerate(products):
#    print(f"{idx}. {p['Название']}\n{p['Производитель']}\n{p['Характеристики']}")

with open("products.json", "w", encoding="utf-8") as file:
    json.dump(products, file, ensure_ascii=False, indent=4)

#with open("products.json", "r", encoding="utf-8") as file:
#    data = json.load(file)
#
#print(data)
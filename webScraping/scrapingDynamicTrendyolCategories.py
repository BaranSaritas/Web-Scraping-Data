import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class Product:
    def __init__(self, category: str, subtitles: list):
        self.category = category
        self.subtitles = subtitles

    def __repr__(self):
        return f"Product(category={self.category}, subtitles={self.subtitles})"

    def to_dict(self):
        return {
            'categoryName': self.category,
            'titleIds': [{'titleUrl': subtitle.url, 'titleName': subtitle.title} for subtitle in self.subtitles]
        }

class Subtitle:
    def __init__(self, url: str, title: str):
        self.url = url
        self.title = title

    def __repr__(self):
        return f"Subtitle(url={self.url}, title={self.title})"

class SubCategory:
    def __init__(self, name: str, url: str, items: list):
        self.name = name
        self.url = url
        self.items = items

    def __repr__(self):
        return f"SubCategory(name={self.name}, url={self.url}, items={self.items})"

    def to_dict(self):
        return {
            'titleName': self.name,
            'titleUrl': self.url,
            'subTitleList': [{'titleUrl': item.url, 'titleName': item.title} for item in self.items]
        }

class Category:
    def __init__(self, name: str, url: str, titleList: list):
        self.name = name
        self.url = url
        self.titleList = sub_categories

    def __repr__(self):
        return f"Category(name={self.name}, url={self.url}, sub_categories={self.titleList})"

    def to_dict(self):
        return {
            'categoryName': self.name,
            'categoryUrl': self.url,
            'titleIds': [sub_cat.to_dict() for sub_cat in self.titleList]
        }

chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

products = []
categories = []

try:
    driver.get("https://www.trendyol.com/")

    tab_links = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.enhanced-navigation li.tab-link'))
    )

    for tab_link in tab_links:
        category_boxes = tab_link.find_elements(By.CSS_SELECTOR, 'div.category-box')

        category_headers = tab_link.find_elements(By.CSS_SELECTOR, 'a.category-header')

        for category_header in category_headers:
            categoryName = category_header.get_attribute('innerText')
            categoryLink = category_header.get_attribute('href')


            sub_categories = []
            if len(category_boxes) >= 1:
                second_category_box = category_boxes[1]
                for sub_category_header in category_boxes:

                        a_tag = sub_category_header.find_element(By.CSS_SELECTOR, 'a.sub-category-header')

                        sub_category_name = a_tag.get_attribute('innerText')

                        sub_category_url = a_tag.get_attribute('href')
                        sub_items = []

                        try:
                            parent_element = sub_category_header.find_element(By.XPATH, '..')
                            sub_item_list = parent_element.find_element(By.CSS_SELECTOR, 'ul.sub-item-list')
                            sub_items_elements = sub_item_list.find_elements(By.TAG_NAME, 'a')
                            sub_items = [Subtitle(url=item.get_attribute('href'), title=item.get_attribute('innerText')) for item in sub_items_elements]
                        except Exception as e:
                            print(f"Error fetching sub-item list for sub-category {sub_category_name}: {e}")

                        sub_category = SubCategory(name=sub_category_name, url=sub_category_url, items=sub_items)
                        sub_categories.append(sub_category)

                category = Category(name=categoryName , url= categoryLink,titleList=sub_categories)
                categories.append(category)
finally:
    driver.quit()

categories_json = json.dumps([category.to_dict() for category in categories], ensure_ascii=False, indent=4)
print(categories_json)


# Send to API
api_url = 'http://localhost:8080/v1/categories/list'
try:
    response = requests.post(api_url, json=json.loads(categories_json))
    response.raise_for_status()  # Raise an exception for HTTP errors
    print('Successfully sent:', response.json())
except requests.exceptions.RequestException as e:
    print(f"Error sending to API: {e}")

# Optional: Write JSON to file
with open('categories.json', 'w', encoding='utf-8') as f:
    f.write(categories_json)

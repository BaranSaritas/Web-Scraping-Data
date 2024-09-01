from decimal import Decimal
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class Product:
    def __init__(self, brand, name, category, favorited_count, rating_score, rating_count, price):
        self.brand = brand
        self.name = name
        self.category = category
        self.favorited_count = favorited_count
        self.rating_score = rating_score
        self.rating_count = rating_count
        self.price = price

    def __repr__(self):
        return (f"Product(brand={self.brand}, name={self.name}, category={self.category}, "
                f"favorited_count={self.favorited_count}, rating_score={self.rating_score}, "
                f"rating_count={self.rating_count}, price={self.price})")

def get_element_text(element, by, value, default=""):
    try:
        return element.find_element(by, value).text
    except:
        return default

def safe_split(text, index=0, delimiter=' '):
    parts = text.split(delimiter)
    return parts[index] if index < len(parts) else ""

def convert_price_to_bigdecimal(price_str):
    cleaned_price = price_str.replace('.', '').replace(',', '').replace(' TL', '').strip()
    return Decimal(cleaned_price)

# Step 1: Fetch subtitleId from API
response = requests.get("http://localhost:8080/subtitles/find?titleName=Bilgisayarlar&page=0&size=5&")
data = response.json()

subtitle_data = data.get('content', [])
subtitle_id = None
urls = []

if subtitle_data:
    subtitle_id = subtitle_data[0]['id']
    urls = [item['titleUrl'] for item in subtitle_data]

if not subtitle_id:
    print("Subtitle ID not found")
    exit()

pageCount = 3
modified_urls = [f"{url}?pi={pageIndex}" for pageIndex in range(1, pageCount + 1) for url in urls]

print(modified_urls)
chrome_options = Options()
chrome_options.add_argument("--headless") 

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

unique_products = set()
products = []

try:
    for url in modified_urls:
        driver.get(url)

        try:
            product_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.product-down'))
            )
        except Exception as e:
            print(f"Error while waiting for elements on {url}: {e}")
            continue

        for element in product_elements:
            brand = get_element_text(element, By.CSS_SELECTOR, 'span.prdct-desc-cntnr-ttl')
            name = get_element_text(element, By.CSS_SELECTOR, 'span.prdct-desc-cntnr-name')
            category = get_element_text(element, By.CSS_SELECTOR, 'div.product-desc-sub-text')

            favorited_text = get_element_text(element, By.CSS_SELECTOR, 'span.social-proof-text span.focused-text')
            favorited_count = safe_split(favorited_text, 0)

            rating_score = get_element_text(element, By.CSS_SELECTOR, 'span.rating-score')
            rating_count = get_element_text(element, By.CSS_SELECTOR, 'span.ratingCount').strip('()')

            price_str = get_element_text(element, By.CSS_SELECTOR, 'div.prc-box-dscntd')
            price = convert_price_to_bigdecimal(price_str) if price_str else Decimal('0.0')

            product_key = (brand, name, category, favorited_count, rating_score, rating_count, price)

            if product_key not in unique_products:
                unique_products.add(product_key)
                product = Product(brand, name, category, favorited_count, rating_score, rating_count, price)
                products.append(product)

finally:
    driver.quit()

product_list = [{
    "brand": product.brand,
    "name": product.name,
    "subCategory": product.category,
    "favoriteCount": int(product.favorited_count) if product.favorited_count else 0,
    "ratingCount": int(product.rating_count) if product.rating_count else 0,
    "ratingScore": float(product.rating_score) if product.rating_score else 0.0,
    "price": float(product.price) if product.price else 0.0,  # Decimal to float
    "titleId": subtitle_id
} for product in products]

list_create_product = {
    "productCreateDTOS": product_list,
    "subtitleId": subtitle_id
}

post_response = requests.post("http://localhost:8080/v1/product", json=list_create_product)

if post_response.status_code == 201:
    print("Products created successfully")
else:
    print(f"Failed to create products: {post_response.status_code}")
